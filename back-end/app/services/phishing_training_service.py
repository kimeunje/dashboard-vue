# app/services/phishing_training_service.py
from datetime import datetime
from typing import Dict, List, Optional, Any
import pandas as pd
import logging
import io
import csv
from werkzeug.datastructures import FileStorage
from app.utils.database import execute_query, DatabaseManager

logger = logging.getLogger(__name__)


class PhishingTrainingService:
    """피싱 훈련 데이터 관리 서비스"""

    def get_user_training_status(self, user_id: int, year: int) -> Dict[str, Any]:
        """사용자별 훈련 현황 조회"""
        try:
            # 사용자 기본 정보
            user_query = """
            SELECT uid, user_id, username, department, mail
            FROM users WHERE uid = %s
            """
            user = execute_query(user_query, (user_id, ), fetch_one=True)

            if not user:
                return {"error": "사용자를 찾을 수 없습니다."}

            # 사용자 훈련 기록
            records_query = """
            SELECT 
                pt.training_id,
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
                pt.notes
            FROM phishing_training pt
            JOIN phishing_training_periods ptp ON pt.period_id = ptp.period_id
            WHERE pt.user_id = %s AND pt.training_year = %s
            ORDER BY pt.email_sent_time DESC
            """

            records = execute_query(records_query, (user_id, year), fetch_all=True)

            # 통계 계산
            total_trainings = len(records)
            success_count = len([
                r for r in records
                if r['training_result'] == 'success' and not r['exclude_from_scoring']
            ])
            fail_count = len([
                r for r in records
                if r['training_result'] == 'fail' and not r['exclude_from_scoring']
            ])
            no_response_count = len([
                r for r in records if r['training_result'] == 'no_response'
                and not r['exclude_from_scoring']
            ])
            excluded_count = len([r for r in records if r['exclude_from_scoring']])

            scored_trainings = total_trainings - excluded_count
            success_rate = (success_count / scored_trainings *
                            100) if scored_trainings > 0 else 0

            # KPI 감점 계산 (실패 횟수당 0.5점)
            penalty_score = fail_count * 0.5

            return {
                "user_info": {
                    "user_id": user['uid'],
                    "username": user['username'],
                    "department": user['department'],
                    "email": user['mail']
                },
                "year": year,
                "summary": {
                    "total_trainings": total_trainings,
                    "scored_trainings": scored_trainings,
                    "success_count": success_count,
                    "fail_count": fail_count,
                    "no_response_count": no_response_count,
                    "excluded_count": excluded_count,
                    "success_rate": round(success_rate, 2),
                    "penalty_score": penalty_score
                },
                "records": [self._format_record(record) for record in records]
            }

        except Exception as e:
            logger.error(f"사용자 훈련 현황 조회 오류: {str(e)}")
            raise

    def get_training_records(self, year: int, period_id: Optional[int] = None,
                             training_type: Optional[str] = None,
                             result_filter: Optional[str] = None,
                             search_query: str = "", page: int = 1,
                             per_page: int = 20) -> Dict[str, Any]:
        """훈련 기록 목록 조회 (관리자용)"""
        try:
            # 기본 쿼리
            base_query = """
            SELECT 
                pt.training_id,
                pt.user_id,
                u.username,
                u.department,
                pt.period_id,
                ptp.period_name,
                ptp.training_type,
                pt.target_email,
                pt.mail_type,
                pt.log_type,
                pt.email_sent_time,
                pt.action_time,
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

            # 필터 조건 추가
            conditions = [year]

            if period_id:
                base_query += " AND pt.period_id = %s"
                conditions.append(period_id)

            if training_type:
                base_query += " AND ptp.training_type = %s"
                conditions.append(training_type)

            if result_filter:
                base_query += " AND pt.training_result = %s"
                conditions.append(result_filter)

            if search_query:
                base_query += " AND (u.username LIKE %s OR u.department LIKE %s OR pt.target_email LIKE %s OR pt.mail_type LIKE %s)"
                search_pattern = f"%{search_query}%"
                conditions.extend(
                    [search_pattern, search_pattern, search_pattern, search_pattern])

            # 전체 레코드 수 조회
            count_query = f"SELECT COUNT(*) as total FROM ({base_query}) as count_query"
            total_count = execute_query(count_query, conditions,
                                        fetch_one=True)['total']

            # 페이지네이션 적용
            offset = (page - 1) * per_page
            base_query += " ORDER BY pt.email_sent_time DESC LIMIT %s OFFSET %s"
            conditions.extend([per_page, offset])

            records = execute_query(base_query, conditions, fetch_all=True)

            return {
                "records": [self._format_record(record) for record in records],
                "pagination": {
                    "total": total_count,
                    "page": page,
                    "per_page": per_page,
                    "total_pages": (total_count + per_page - 1) // per_page
                }
            }

        except Exception as e:
            logger.error(f"훈련 기록 조회 오류: {str(e)}")
            raise

    def _format_record(self, record: Dict) -> Dict:
        """레코드 포맷팅"""
        return {
            "training_id": record['training_id'],
            "user_id": record['user_id'],
            "username": record['username'],
            "department": record['department'],
            "period_id": record['period_id'],
            "period_name": record['period_name'],
            "training_type": record['training_type'],
            "target_email": record['target_email'],
            "mail_type": record['mail_type'],
            "log_type": record['log_type'],
            "email_sent_time": record['email_sent_time'].isoformat()
            if record['email_sent_time'] else None,
            "action_time": record['action_time'].isoformat()
            if record['action_time'] else None,
            "training_result": record['training_result'],
            "response_time_minutes": record['response_time_minutes'],
            "exclude_from_scoring": bool(record['exclude_from_scoring']),
            "exclude_reason": record['exclude_reason'],
            "notes": record['notes'],
            "created_at": record['created_at'].isoformat()
            if record['created_at'] else None,
            "updated_at": record['updated_at'].isoformat()
            if record['updated_at'] else None
        }

    def update_training_record(self, record_id: int, data: Dict[str,
                                                                Any]) -> Dict[str, Any]:
        """훈련 기록 수정"""
        try:
            # 기록 존재 확인
            record = self._get_record_by_id(record_id)
            if not record:
                return {"success": False, "error": "훈련 기록을 찾을 수 없습니다."}

            # 업데이트 쿼리
            update_fields = []
            values = []

            if 'training_result' in data:
                update_fields.append("training_result = %s")
                values.append(data['training_result'])

            if 'notes' in data:
                update_fields.append("notes = %s")
                values.append(data['notes'])

            if 'exclude_from_scoring' in data:
                update_fields.append("exclude_from_scoring = %s")
                values.append(data['exclude_from_scoring'])

            if 'exclude_reason' in data:
                update_fields.append("exclude_reason = %s")
                values.append(data['exclude_reason'])

            if not update_fields:
                return {"success": False, "error": "수정할 필드가 지정되지 않았습니다."}

            update_fields.append("updated_at = NOW()")
            values.append(record_id)

            query = f"""
            UPDATE phishing_training 
            SET {', '.join(update_fields)}
            WHERE training_id = %s
            """

            execute_query(query, values)

            return {"success": True, "message": "훈련 기록이 수정되었습니다."}

        except Exception as e:
            logger.error(f"훈련 기록 수정 오류: {str(e)}")
            return {"success": False, "error": f"기록 수정 중 오류가 발생했습니다: {str(e)}"}

    def toggle_record_exclude(self, record_id: int, exclude: bool,
                              reason: str = "") -> Dict[str, Any]:
        """훈련 기록 제외/포함 토글"""
        try:
            record = self._get_record_by_id(record_id)
            if not record:
                return {"success": False, "error": "훈련 기록을 찾을 수 없습니다."}

            query = """
            UPDATE phishing_training 
            SET exclude_from_scoring = %s, exclude_reason = %s, updated_at = NOW()
            WHERE training_id = %s
            """

            execute_query(query, (exclude, reason if exclude else None, record_id))

            action = "제외" if exclude else "포함"
            return {"success": True, "message": f"훈련 기록이 점수 계산에서 {action} 처리되었습니다."}

        except Exception as e:
            logger.error(f"훈련 기록 제외/포함 처리 오류: {str(e)}")
            return {"success": False, "error": f"처리 중 오류가 발생했습니다: {str(e)}"}

    def delete_training_record(self, record_id: int) -> Dict[str, Any]:
        """훈련 기록 삭제"""
        try:
            record = self._get_record_by_id(record_id)
            if not record:
                return {"success": False, "error": "훈련 기록을 찾을 수 없습니다."}

            query = "DELETE FROM phishing_training WHERE training_id = %s"
            execute_query(query, (record_id, ))

            return {"success": True, "message": "훈련 기록이 삭제되었습니다."}

        except Exception as e:
            logger.error(f"훈련 기록 삭제 오류: {str(e)}")
            return {"success": False, "error": f"삭제 중 오류가 발생했습니다: {str(e)}"}

    def _get_record_by_id(self, record_id: int) -> Optional[Dict]:
        """ID로 훈련 기록 조회"""
        query = "SELECT * FROM phishing_training WHERE training_id = %s"
        return execute_query(query, (record_id, ), fetch_one=True)

    def process_excel_upload(self, file: FileStorage, period_id: int) -> Dict[str, Any]:
        """엑셀 파일 업로드 처리"""
        try:
            # 기간 정보 확인
            period_query = """
            SELECT period_id, training_year, period_name, training_type, is_completed
            FROM phishing_training_periods WHERE period_id = %s
            """
            period = execute_query(period_query, (period_id, ), fetch_one=True)

            if not period:
                return {"success": False, "error": "선택한 훈련 기간을 찾을 수 없습니다."}

            if period['is_completed']:
                return {"success": False, "error": "완료된 훈련 기간에는 데이터를 업로드할 수 없습니다."}

            # 엑셀 파일 읽기
            df = pd.read_excel(file, engine='openpyxl')

            # 필수 컬럼 확인
            required_columns = ['메일발송시각', '수행시각', '로그유형', '메일유형', '이메일']
            missing_columns = [col for col in required_columns if col not in df.columns]

            if missing_columns:
                return {
                    "success": False,
                    "error": f"필수 컬럼이 누락되었습니다: {', '.join(missing_columns)}"
                }

            # 데이터 처리
            success_count = 0
            error_count = 0
            errors = []

            for index, row in df.iterrows():
                try:
                    # 이메일로 사용자 찾기
                    target_email = str(row['이메일']).strip()
                    user_query = "SELECT uid FROM users WHERE mail = %s"
                    user = execute_query(user_query, (target_email, ), fetch_one=True)

                    if not user:
                        error_count += 1
                        errors.append(f"행 {index+2}: 사용자를 찾을 수 없습니다 ({target_email})")
                        continue

                    # 중복 체크
                    duplicate_query = """
                    SELECT COUNT(*) as count FROM phishing_training 
                    WHERE user_id = %s AND period_id = %s AND target_email = %s
                    """
                    duplicate = execute_query(duplicate_query,
                                              (user['uid'], period_id, target_email),
                                              fetch_one=True)

                    if duplicate['count'] > 0:
                        error_count += 1
                        errors.append(f"행 {index+2}: 중복된 기록입니다 ({target_email})")
                        continue

                    # 훈련 결과 판정
                    training_result = self._determine_training_result(row)

                    # 응답 시간 계산
                    response_time = self._calculate_response_time(row)

                    # 데이터 삽입
                    insert_query = """
                    INSERT INTO phishing_training 
                    (user_id, period_id, training_year, email_sent_time, action_time, 
                     log_type, mail_type, target_email, training_result, response_time_minutes)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """

                    values = (user['uid'], period_id, period['training_year'],
                              pd.to_datetime(row['메일발송시각']) if pd.notna(
                                  row['메일발송시각']) else None, pd.to_datetime(row['수행시각'])
                              if pd.notna(row['수행시각']) else None, str(row['로그유형']),
                              str(row['메일유형']), target_email, training_result,
                              response_time)

                    execute_query(insert_query, values)
                    success_count += 1

                except Exception as e:
                    error_count += 1
                    errors.append(f"행 {index+2}: {str(e)}")
                    logger.error(f"데이터 처리 오류 (행 {index+2}): {str(e)}")

            return {
                "success": True,
                "message": f"총 {len(df)}건 중 {success_count}건 성공, {error_count}건 실패",
                "details": {
                    "total_rows": len(df),
                    "success_count": success_count,
                    "error_count": error_count,
                    "errors": errors[:10]  # 최대 10개 오류만 반환
                }
            }

        except Exception as e:
            logger.error(f"엑셀 업로드 오류: {str(e)}")
            return {"success": False, "error": f"파일 처리 중 오류가 발생했습니다: {str(e)}"}

    def _determine_training_result(self, row: pd.Series) -> str:
        """훈련 결과 판정 로직"""
        log_type = str(row['로그유형']).lower()

        # 위험한 행동 패턴 (실패)
        dangerous_patterns = [
            '스크립트 첨부파일 열람', '첨부파일 다운로드', '링크 클릭', '개인정보 입력', '비밀번호 입력', '계정정보 입력'
        ]

        if any(pattern.lower() in log_type for pattern in dangerous_patterns):
            return 'fail'

        # 무응답 처리
        if pd.isna(row['수행시각']) or str(row['수행시각']).strip() == '':
            return 'no_response'

        # 안전한 행동 패턴 (성공)
        return 'success'

    def _calculate_response_time(self, row: pd.Series) -> Optional[int]:
        """응답 시간 계산 (분 단위)"""
        try:
            if pd.isna(row['메일발송시각']) or pd.isna(row['수행시각']):
                return None

            sent_time = pd.to_datetime(row['메일발송시각'])
            action_time = pd.to_datetime(row['수행시각'])

            if action_time <= sent_time:
                return 0

            diff = action_time - sent_time
            return int(diff.total_seconds() / 60)

        except Exception:
            return None

    def export_training_data(self, year: int,
                             format_type: str = "csv") -> Dict[str, Any]:
        """훈련 데이터 내보내기"""
        try:
            query = """
            SELECT 
                u.username as '사용자명',
                u.department as '부서',
                ptp.period_name as '훈련기간',
                ptp.training_type as '훈련유형',
                pt.target_email as '대상이메일',
                pt.mail_type as '메일유형',
                pt.log_type as '로그유형',
                pt.email_sent_time as '발송시각',
                pt.action_time as '수행시각',
                pt.response_time_minutes as '응답시간_분',
                CASE pt.training_result
                    WHEN 'success' THEN '성공'
                    WHEN 'fail' THEN '실패'
                    WHEN 'no_response' THEN '무응답'
                    ELSE pt.training_result
                END as '훈련결과',
                CASE pt.exclude_from_scoring
                    WHEN 1 THEN '제외'
                    ELSE '포함'
                END as '점수계산포함여부',
                pt.exclude_reason as '제외사유',
                pt.notes as '비고'
            FROM phishing_training pt
            JOIN users u ON pt.user_id = u.uid
            JOIN phishing_training_periods ptp ON pt.period_id = ptp.period_id
            WHERE pt.training_year = %s
            ORDER BY u.department, u.username, pt.email_sent_time
            """

            records = execute_query(query, (year, ), fetch_all=True)

            if not records:
                return {"success": False, "error": "내보낼 데이터가 없습니다."}

            if format_type == "csv":
                # CSV 생성
                output = io.StringIO()
                fieldnames = records[0].keys()
                writer = csv.DictWriter(output, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(records)

                csv_content = output.getvalue()
                output.close()

                return {
                    "success": True,
                    "data": csv_content.encode("utf-8-sig"),  # BOM 추가로 한글 깨짐 방지
                    "content_type": "text/csv; charset=utf-8-sig",
                    "filename": f'attachment; filename="피싱훈련데이터_{year}.csv"'
                }

            else:
                return {"success": False, "error": "지원하지 않는 형식입니다."}

        except Exception as e:
            logger.error(f"데이터 내보내기 오류: {str(e)}")
            return {"success": False, "error": f"내보내기 중 오류가 발생했습니다: {str(e)}"}

    def get_training_statistics(self, year: int,
                                period_id: Optional[int] = None) -> Dict[str, Any]:
        """훈련 통계 조회"""
        try:
            base_query = """
            SELECT 
                ptp.period_name,
                ptp.training_type,
                u.department,
                COUNT(*) as total_count,
                COUNT(CASE WHEN pt.training_result = 'success' AND pt.exclude_from_scoring = 0 THEN 1 END) as success_count,
                COUNT(CASE WHEN pt.training_result = 'fail' AND pt.exclude_from_scoring = 0 THEN 1 END) as fail_count,
                COUNT(CASE WHEN pt.training_result = 'no_response' AND pt.exclude_from_scoring = 0 THEN 1 END) as no_response_count,
                COUNT(CASE WHEN pt.exclude_from_scoring = 1 THEN 1 END) as excluded_count
            FROM phishing_training pt
            JOIN users u ON pt.user_id = u.uid
            JOIN phishing_training_periods ptp ON pt.period_id = ptp.period_id
            WHERE pt.training_year = %s
            """

            conditions = [year]

            if period_id:
                base_query += " AND pt.period_id = %s"
                conditions.append(period_id)

            base_query += """
            GROUP BY ptp.period_name, ptp.training_type, u.department
            ORDER BY ptp.period_name, u.department
            """

            statistics = execute_query(base_query, conditions, fetch_all=True)

            # 부서별, 기간별 통계 정리
            result = {
                "overall": {
                    "total_participants": 0,
                    "total_success": 0,
                    "total_fail": 0,
                    "total_no_response": 0,
                    "total_excluded": 0,
                    "overall_success_rate": 0
                },
                "by_period": {},
                "by_department": {},
                "detailed_stats": statistics
            }

            department_stats = {}
            period_stats = {}

            for stat in statistics:
                # 전체 통계 누적
                scored_count = stat['total_count'] - stat['excluded_count']
                result["overall"]["total_participants"] += stat['total_count']
                result["overall"]["total_success"] += stat['success_count']
                result["overall"]["total_fail"] += stat['fail_count']
                result["overall"]["total_no_response"] += stat['no_response_count']
                result["overall"]["total_excluded"] += stat['excluded_count']

                # 기간별 통계
                period_key = f"{stat['period_name']} ({stat['training_type']})"
                if period_key not in period_stats:
                    period_stats[period_key] = {
                        "total_participants": 0,
                        "success_count": 0,
                        "fail_count": 0,
                        "no_response_count": 0,
                        "excluded_count": 0,
                        "success_rate": 0
                    }

                period_stats[period_key]["total_participants"] += stat['total_count']
                period_stats[period_key]["success_count"] += stat['success_count']
                period_stats[period_key]["fail_count"] += stat['fail_count']
                period_stats[period_key]["no_response_count"] += stat[
                    'no_response_count']
                period_stats[period_key]["excluded_count"] += stat['excluded_count']

                # 부서별 통계
                dept = stat['department']
                if dept not in department_stats:
                    department_stats[dept] = {
                        "total_participants": 0,
                        "success_count": 0,
                        "fail_count": 0,
                        "no_response_count": 0,
                        "excluded_count": 0,
                        "success_rate": 0
                    }

                department_stats[dept]["total_participants"] += stat['total_count']
                department_stats[dept]["success_count"] += stat['success_count']
                department_stats[dept]["fail_count"] += stat['fail_count']
                department_stats[dept]["no_response_count"] += stat['no_response_count']
                department_stats[dept]["excluded_count"] += stat['excluded_count']

            # 성공률 계산
            total_scored = result["overall"]["total_participants"] - result["overall"][
                "total_excluded"]
            if total_scored > 0:
                result["overall"]["overall_success_rate"] = round(
                    (result["overall"]["total_success"] / total_scored) * 100, 2)

            # 기간별 성공률 계산
            for period_key in period_stats:
                period_data = period_stats[period_key]
                scored = period_data["total_participants"] - period_data[
                    "excluded_count"]
                if scored > 0:
                    period_data["success_rate"] = round(
                        (period_data["success_count"] / scored) * 100, 2)

            # 부서별 성공률 계산
            for dept in department_stats:
                dept_data = department_stats[dept]
                scored = dept_data["total_participants"] - dept_data["excluded_count"]
                if scored > 0:
                    dept_data["success_rate"] = round(
                        (dept_data["success_count"] / scored) * 100, 2)

            result["by_period"] = period_stats
            result["by_department"] = department_stats

            return result

        except Exception as e:
            logger.error(f"훈련 통계 조회 오류: {str(e)}")
            raise
