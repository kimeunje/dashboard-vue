# app/services/phishing_training_service.py
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any, Tuple
import pandas as pd
import logging
from app.utils.database import execute_query, DatabaseManager

logger = logging.getLogger(__name__)


class PhishingTrainingService:
    """피싱 훈련 관리 서비스 - security_education 구조 참조"""

    def get_training_periods(self, year: int = None) -> List[Dict]:
        """훈련 기간 목록 조회"""
        if year is None:
            year = datetime.now().year

        query = """
        SELECT 
            ptp.period_id,
            ptp.training_year,
            ptp.period_name,
            ptp.training_type,
            ptp.start_date,
            ptp.end_date,
            ptp.is_completed,
            ptp.completed_at,
            ptp.completed_by,
            ptp.description,
            ptp.auto_pass_setting,
            ptp.created_by,
            ptp.created_at,
            ptp.updated_at,
            -- 통계 정보
            COUNT(DISTINCT pt.user_id) as total_participants,
            COUNT(DISTINCT CASE WHEN pt.training_result = 'success' THEN pt.user_id END) as success_user_count,
            COUNT(DISTINCT CASE WHEN pt.training_result = 'fail' THEN pt.user_id END) as failure_user_count,
            COALESCE(
                CASE 
                    WHEN COUNT(DISTINCT pt.user_id) > 0 
                    THEN ROUND(
                        (COUNT(DISTINCT CASE WHEN pt.training_result = 'success' THEN pt.user_id END) / COUNT(DISTINCT pt.user_id)) * 100, 
                        2
                    )
                    ELSE 0 
                END, 
                0
            ) as success_rate
        FROM phishing_training_periods ptp
        LEFT JOIN phishing_training pt ON ptp.period_id = pt.period_id
        WHERE ptp.training_year = %s
        GROUP BY ptp.period_id
        ORDER BY ptp.training_type, ptp.start_date DESC
        """

        periods = execute_query(query, (year, ), fetch_all=True)

        # 교육 유형별로 그룹화
        training_types = {}

        for period in periods:
            training_type = period['training_type']

            if training_type not in training_types:
                training_types[training_type] = {
                    'type_name': training_type,
                    'periods': [],
                    'total_participants': 0,
                    'total_success': 0,
                    'total_failure': 0
                }

            # 기간별 상태 결정
            status = self._determine_period_status(period)

            period_info = {
                'period_id': period['period_id'],
                'period_name': period['period_name'],
                'training_year': period['training_year'],
                'training_type': period['training_type'],
                'start_date': period['start_date'].isoformat()
                if period['start_date'] else None,
                'end_date': period['end_date'].isoformat()
                if period['end_date'] else None,
                'status': status,
                'is_completed': bool(period['is_completed']),
                'completed_at': period['completed_at'].isoformat()
                if period['completed_at'] else None,
                'completed_by': period['completed_by'],
                'description': period['description'],
                'auto_pass_setting': bool(period['auto_pass_setting']),
                'created_by': period['created_by'],
                'participants': int(period['total_participants'] or 0),
                'success_count': int(period['success_user_count'] or 0),
                'failure_count': int(period['failure_user_count'] or 0),
                'success_rate': float(period['success_rate'] or 0),
            }

            training_types[training_type]['periods'].append(period_info)
            training_types[training_type]['total_participants'] += period_info[
                'participants']
            training_types[training_type]['total_success'] += period_info[
                'success_count']
            training_types[training_type]['total_failure'] += period_info[
                'failure_count']

        return list(training_types.values())

    def _determine_period_status(self, period: Dict) -> str:
        """기간 상태 판정"""
        if period['is_completed']:
            return "완료됨"

        start_date = period['start_date']
        end_date = period['end_date']
        today = datetime.now().date()

        if start_date and end_date:
            if today < start_date:
                return "예정됨"
            elif start_date <= today <= end_date:
                return "진행중"
            else:  # today > end_date
                return "종료됨"

        return "설정됨"

    def create_training_period(self, period_data: Dict, created_by: str) -> int:
        """훈련 기간 생성"""
        query = """
        INSERT INTO phishing_training_periods 
        (training_year, period_name, training_type, start_date, end_date, description, created_by)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """

        return execute_query(
            query,
            (period_data['training_year'], period_data['period_name'],
             period_data['training_type'], period_data['start_date'],
             period_data['end_date'], period_data.get('description', ''), created_by),
            fetch_insert_id=True)

    def update_training_period(self, period_id: int, period_data: Dict) -> bool:
        """훈련 기간 수정"""
        query = """
        UPDATE phishing_training_periods 
        SET training_year = %s, period_name = %s, training_type = %s,
            start_date = %s, end_date = %s, description = %s,
            updated_at = current_timestamp()
        WHERE period_id = %s
        """

        rows_affected = execute_query(
            query,
            (period_data['training_year'], period_data['period_name'],
             period_data['training_type'], period_data['start_date'],
             period_data['end_date'], period_data.get('description', ''), period_id),
            fetch_affected_rows=True)

        return rows_affected > 0

    def delete_training_period(self, period_id: int) -> bool:
        """훈련 기간 삭제"""
        # 먼저 관련 훈련 기록이 있는지 확인
        count_query = "SELECT COUNT(*) as count FROM phishing_training WHERE period_id = %s"
        result = execute_query(count_query, (period_id, ), fetch_one=True)

        if result['count'] > 0:
            raise ValueError("훈련 기록이 있는 기간은 삭제할 수 없습니다.")

        # 기간 삭제
        delete_query = "DELETE FROM phishing_training_periods WHERE period_id = %s"
        rows_affected = execute_query(delete_query, (period_id, ),
                                      fetch_affected_rows=True)

        return rows_affected > 0

    def upload_training_data(self, excel_file, period_id: int,
                             uploaded_by: str) -> Dict:
        """엑셀 파일에서 피싱 훈련 데이터 업로드"""
        try:
            # 엑셀 파일 읽기
            df = pd.read_excel(excel_file)

            # 필수 컬럼 확인
            required_columns = ['메일발송시각', '수행시각', '로그유형', '메일유형', '이메일']
            missing_columns = [col for col in required_columns if col not in df.columns]

            if missing_columns:
                raise ValueError(f"필수 컬럼이 누락되었습니다: {', '.join(missing_columns)}")

            # 기간 정보 조회
            period_info = execute_query(
                "SELECT training_year FROM phishing_training_periods WHERE period_id = %s",
                (period_id, ), fetch_one=True)

            if not period_info:
                raise ValueError("존재하지 않는 훈련 기간입니다.")

            training_year = period_info['training_year']

            # 데이터 처리 및 저장
            success_count = 0
            error_count = 0
            errors = []

            with DatabaseManager.get_db_cursor(commit=True) as cursor:
                for index, row in df.iterrows():
                    try:
                        # 사용자 조회
                        target_email = row['이메일']
                        user = execute_query("SELECT uid FROM users WHERE mail = %s",
                                             (target_email, ), fetch_one=True)

                        if not user:
                            error_count += 1
                            errors.append(
                                f"행 {index+2}: 사용자를 찾을 수 없습니다 ({target_email})")
                            continue

                        # 훈련 결과 판정
                        training_result = self._determine_training_result(row)
                        response_time = self._calculate_response_time(row)

                        # 중복 확인 및 업서트
                        existing = execute_query(
                            "SELECT training_id FROM phishing_training WHERE user_id = %s AND period_id = %s AND target_email = %s",
                            (user['uid'], period_id, target_email), fetch_one=True)

                        if existing:
                            # 업데이트
                            execute_query(
                                """
                                UPDATE phishing_training 
                                SET email_sent_time = %s, action_time = %s, log_type = %s, 
                                    mail_type = %s, training_result = %s, response_time_minutes = %s,
                                    updated_at = current_timestamp()
                                WHERE training_id = %s
                            """, (pd.to_datetime(row['메일발송시각'])
                                  if pd.notna(row['메일발송시각']) else None,
                                  pd.to_datetime(row['수행시각']) if pd.notna(row['수행시각'])
                                  else None, row['로그유형'], row['메일유형'], training_result,
                                  response_time, existing['training_id']))
                        else:
                            # 삽입
                            execute_query(
                                """
                                INSERT INTO phishing_training 
                                (user_id, period_id, training_year, email_sent_time, action_time, 
                                 log_type, mail_type, target_email, training_result, response_time_minutes)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                            """, (user['uid'], period_id, training_year,
                                  pd.to_datetime(row['메일발송시각'])
                                  if pd.notna(row['메일발송시각']) else None,
                                  pd.to_datetime(row['수행시각']) if pd.notna(
                                      row['수행시각']) else None, row['로그유형'], row['메일유형'],
                                  target_email, training_result, response_time))

                        success_count += 1

                    except Exception as e:
                        error_count += 1
                        errors.append(f"행 {index+2}: {str(e)}")
                        logger.error(f"데이터 처리 오류 (행 {index+2}): {str(e)}")

            return {
                "success": True,
                "total_rows": len(df),
                "success_count": success_count,
                "error_count": error_count,
                "errors": errors[:10]  # 최대 10개 오류만 반환
            }

        except Exception as e:
            logger.error(f"엑셀 업로드 오류: {str(e)}")
            return {"success": False, "error": str(e)}

    def _determine_training_result(self, row: pd.Series) -> str:
        """훈련 결과 판정 로직"""
        log_type = str(row['로그유형']).lower()

        # 위험한 행동 패턴 (실패)
        dangerous_patterns = [
            '스크립트 첨부파일 열람', '첨부파일 다운로드', '링크 클릭', '개인정보 입력', '비밀번호 입력'
        ]

        if any(pattern in log_type for pattern in dangerous_patterns):
            return 'fail'

        # 단순 열람 (성공적인 대응)
        safe_patterns = ['이메일 열람', '메일 확인', '신고']

        if any(pattern in log_type for pattern in safe_patterns):
            return 'success'

        # 무응답 처리
        if pd.isna(row['수행시각']) or str(row['수행시각']).strip() == '':
            return 'no_response'

        return 'success'  # 기본값

    def _calculate_response_time(self, row: pd.Series) -> Optional[int]:
        """응답 시간 계산 (분 단위)"""
        try:
            if pd.isna(row['메일발송시각']) or pd.isna(row['수행시각']):
                return None

            sent_time = pd.to_datetime(row['메일발송시각'])
            action_time = pd.to_datetime(row['수행시각'])

            if action_time > sent_time:
                delta = action_time - sent_time
                return int(delta.total_seconds() / 60)

            return None
        except:
            return None

    def get_training_records(self, year: int = None,
                             period_id: int = None) -> List[Dict]:
        """훈련 기록 조회"""
        if year is None:
            year = datetime.now().year

        base_query = """
        SELECT 
            pt.training_id,
            pt.user_id,
            u.user_id as username,
            u.department,
            u.mail as email,
            pt.training_year,
            pt.period_id,
            ptp.period_name,
            ptp.training_type,
            pt.email_sent_time,
            pt.action_time,
            pt.log_type,
            pt.mail_type,
            pt.target_email,
            pt.training_result,
            pt.response_time_minutes,
            pt.exclude_from_scoring,
            pt.exclude_reason,
            pt.notes,
            pt.created_at,
            pt.updated_at
        FROM phishing_training pt
        JOIN users u ON pt.user_id = u.uid
        JOIN phishing_training_periods ptp ON pt.period_id = ptp.period_id
        WHERE pt.training_year = %s
        """

        params = [year]

        if period_id:
            base_query += " AND pt.period_id = %s"
            params.append(period_id)

        base_query += " ORDER BY u.user_id, ptp.period_name, pt.created_at"

        records = execute_query(base_query, params, fetch_all=True)

        result_records = []
        for record in records:
            result_record = {
                "training_id": record["training_id"],
                "user_id": record["user_id"],
                "username": record["username"],
                "department": record["department"],
                "email": record["email"],
                "training_year": record["training_year"],
                "period_id": record["period_id"],
                "period_name": record["period_name"],
                "training_type": record["training_type"],
                "email_sent_time": record["email_sent_time"].isoformat()
                if record["email_sent_time"] else None,
                "action_time": record["action_time"].isoformat()
                if record["action_time"] else None,
                "log_type": record["log_type"],
                "mail_type": record["mail_type"],
                "target_email": record["target_email"],
                "training_result": record["training_result"],
                "response_time_minutes": record["response_time_minutes"],
                "status_text": self._get_status_text(record),
                "exclude_from_scoring": bool(record["exclude_from_scoring"]),
                "exclude_reason": record["exclude_reason"],
                "notes": record["notes"],
                "created_at": record["created_at"].isoformat()
                if record["created_at"] else None,
                "updated_at": record["updated_at"].isoformat()
                if record["updated_at"] else None,
            }
            result_records.append(result_record)

        return result_records

    def _get_status_text(self, record: Dict) -> str:
        """상태 텍스트 생성"""
        if record["exclude_from_scoring"]:
            return "제외"

        result = record["training_result"]
        if result == 'success':
            return "성공"
        elif result == 'fail':
            return "실패"
        elif result == 'no_response':
            return "무응답"
        else:
            return "미정"

    def update_training_record(self, training_id: int, update_data: Dict) -> bool:
        """훈련 기록 수정"""
        query = """
        UPDATE phishing_training 
        SET training_result = %s, exclude_from_scoring = %s, exclude_reason = %s, 
            notes = %s, updated_at = current_timestamp()
        WHERE training_id = %s
        """

        rows_affected = execute_query(
            query,
            (update_data.get('training_result'),
             update_data.get('exclude_from_scoring', 0),
             update_data.get('exclude_reason'), update_data.get('notes'), training_id),
            fetch_affected_rows=True)

        return rows_affected > 0

    def delete_training_record(self, training_id: int) -> bool:
        """훈련 기록 삭제"""
        query = "DELETE FROM phishing_training WHERE training_id = %s"
        rows_affected = execute_query(query, (training_id, ), fetch_affected_rows=True)
        return rows_affected > 0

    def get_training_statistics(self, year: int = None) -> Dict:
        """훈련 통계 조회"""
        if year is None:
            year = datetime.now().year

        # 전체 통계
        total_stats = execute_query(
            """
            SELECT 
                COUNT(*) as total_records,
                COUNT(DISTINCT user_id) as total_users,
                COUNT(CASE WHEN training_result = 'success' THEN 1 END) as success_count,
                COUNT(CASE WHEN training_result = 'fail' THEN 1 END) as fail_count,
                COUNT(CASE WHEN training_result = 'no_response' THEN 1 END) as no_response_count,
                ROUND(AVG(response_time_minutes), 2) as avg_response_time
            FROM phishing_training 
            WHERE training_year = %s AND exclude_from_scoring = 0
        """, (year, ), fetch_one=True)

        # 기간별 통계
        period_stats = execute_query(
            """
            SELECT 
                ptp.period_name,
                ptp.training_type,
                COUNT(*) as total_records,
                COUNT(DISTINCT pt.user_id) as total_users,
                COUNT(CASE WHEN pt.training_result = 'success' THEN 1 END) as success_count,
                COUNT(CASE WHEN pt.training_result = 'fail' THEN 1 END) as fail_count,
                COUNT(CASE WHEN pt.training_result = 'no_response' THEN 1 END) as no_response_count,
                ROUND(
                    (COUNT(CASE WHEN pt.training_result = 'success' THEN 1 END) / COUNT(*)) * 100, 
                    2
                ) as success_rate
            FROM phishing_training pt
            JOIN phishing_training_periods ptp ON pt.period_id = ptp.period_id
            WHERE pt.training_year = %s AND pt.exclude_from_scoring = 0
            GROUP BY ptp.period_id, ptp.period_name, ptp.training_type
            ORDER BY ptp.period_name
        """, (year, ), fetch_all=True)

        return {"year": year, "total_stats": total_stats, "period_stats": period_stats}
