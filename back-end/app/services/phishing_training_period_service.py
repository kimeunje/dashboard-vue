# app/services/phishing_training_period_service.py
from datetime import datetime, date
from typing import Dict, List, Optional, Any
import logging
from app.utils.database import execute_query, DatabaseManager

logger = logging.getLogger(__name__)


class PhishingTrainingPeriodService:
    """피싱 훈련 기간 관리 서비스"""

    def get_period_status(self, year: int) -> Dict[str, Any]:
        """훈련 기간 현황 조회 (훈련 유형별 그룹화)"""
        try:
            # 기간별 통계와 함께 조회
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
                COALESCE(pts.total_targets, 0) as total_targets,
                COALESCE(pts.success_count, 0) as success_count,
                COALESCE(pts.fail_count, 0) as fail_count,
                COALESCE(pts.no_response_count, 0) as no_response_count,
                COALESCE(pts.success_rate, 0) as success_rate,
                COALESCE(pts.fail_rate, 0) as fail_rate
            FROM phishing_training_periods ptp
            LEFT JOIN phishing_training_stats pts ON ptp.period_id = pts.period_id
            WHERE ptp.training_year = %s
            ORDER BY ptp.training_type, ptp.start_date DESC
            """

            periods = execute_query(query, (year, ), fetch_all=True)

            if not periods:
                return {"training_types": {}}

            # 훈련 유형별로 그룹화
            training_types = {}

            for period in periods:
                training_type = period['training_type']

                if training_type not in training_types:
                    training_types[training_type] = {
                        'periods': [],
                        'total_periods': 0,
                        'completed_periods': 0,
                        'total_participants': 0,
                        'overall_success_rate': 0
                    }

                # 기간 상태 결정
                status = self._determine_period_status(period)

                period_info = {
                    'period_id': period['period_id'],
                    'training_year': period['training_year'],
                    'period_name': period['period_name'],
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
                    'created_at': period['created_at'].isoformat()
                    if period['created_at'] else None,
                    'updated_at': period['updated_at'].isoformat()
                    if period['updated_at'] else None,
                    'stats': {
                        'total_targets': int(period['total_targets'] or 0),
                        'success_count': int(period['success_count'] or 0),
                        'fail_count': int(period['fail_count'] or 0),
                        'no_response_count': int(period['no_response_count'] or 0),
                        'success_rate': float(period['success_rate'] or 0),
                        'fail_rate': float(period['fail_rate'] or 0)
                    }
                }

                training_types[training_type]['periods'].append(period_info)
                training_types[training_type]['total_periods'] += 1

                if period['is_completed']:
                    training_types[training_type]['completed_periods'] += 1

                training_types[training_type]['total_participants'] += int(
                    period['total_targets'] or 0)

            # 각 유형별 전체 성공률 계산
            for training_type in training_types:
                type_data = training_types[training_type]
                total_success = sum(p['stats']['success_count']
                                    for p in type_data['periods'])
                total_participants = type_data['total_participants']

                if total_participants > 0:
                    type_data['overall_success_rate'] = round(
                        (total_success / total_participants) * 100, 2)

            return {"training_types": training_types}

        except Exception as e:
            logger.error(f"훈련 기간 현황 조회 오류: {str(e)}")
            raise

    def _determine_period_status(self, period: Dict) -> str:
        """기간 상태 판정"""
        if period['is_completed']:
            return "completed"

        today = date.today()
        start_date = period['start_date']
        end_date = period['end_date']

        if start_date and end_date:
            if today < start_date:
                return "pending"
            elif start_date <= today <= end_date:
                return "active"
            else:  # today > end_date
                return "expired"

        return "pending"

    def create_period(self, data: Dict[str, Any], created_by: str) -> Dict[str, Any]:
        """새 훈련 기간 생성"""
        try:
            # 중복 체크
            duplicate_check = self._check_duplicate_period(data['training_year'],
                                                           data['period_name'],
                                                           data['training_type'])

            if duplicate_check:
                return {
                    "success": False,
                    "error": f"동일한 연도({data['training_year']})의 '{data['training_type']}'에 '{data['period_name']}' 기간이 이미 존재합니다."
                }

            # 날짜 유효성 검사
            start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
            end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()

            if start_date >= end_date:
                return {"success": False, "error": "종료일은 시작일보다 늦어야 합니다."}

            # 데이터베이스에 삽입
            query = """
            INSERT INTO phishing_training_periods 
            (training_year, period_name, training_type, start_date, end_date, 
             description, auto_pass_setting, created_by)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """

            values = (data['training_year'], data['period_name'], data['training_type'],
                      start_date, end_date, data.get('description', ''),
                      data.get('auto_pass_setting', True), created_by)

            result = execute_query(query, values)

            if result:
                return {
                    "success": True,
                    "message": "훈련 기간이 생성되었습니다.",
                    "period_id": result
                }
            else:
                return {"success": False, "error": "훈련 기간 생성에 실패했습니다."}

        except Exception as e:
            logger.error(f"훈련 기간 생성 오류: {str(e)}")
            return {"success": False, "error": f"훈련 기간 생성 중 오류가 발생했습니다: {str(e)}"}

    def _check_duplicate_period(self, year: int, period_name: str,
                                training_type: str) -> bool:
        """중복 기간 체크"""
        query = """
        SELECT COUNT(*) as count 
        FROM phishing_training_periods 
        WHERE training_year = %s AND period_name = %s AND training_type = %s
        """

        result = execute_query(query, (year, period_name, training_type),
                               fetch_one=True)
        return result['count'] > 0

    def update_period(self, period_id: int, data: Dict[str, Any],
                      updated_by: str) -> Dict[str, Any]:
        """훈련 기간 수정"""
        try:
            # 기간 존재 확인
            period = self._get_period_by_id(period_id)
            if not period:
                return {"success": False, "error": "훈련 기간을 찾을 수 없습니다."}

            # 완료된 기간 수정 체크
            if period['is_completed']:
                return {
                    "success": False,
                    "message": "완료된 훈련 기간은 수정할 수 없습니다. 먼저 기간을 재개해주세요."
                }

            # 중복 체크 (자기 자신 제외)
            if self._check_duplicate_period_exclude_self(period_id,
                                                         data['training_year'],
                                                         data['period_name'],
                                                         data['training_type']):
                return {
                    "success": False,
                    "error": f"동일한 연도({data['training_year']})의 '{data['training_type']}'에 '{data['period_name']}' 기간이 이미 존재합니다."
                }

            # 날짜 유효성 검사
            start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
            end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()

            if start_date >= end_date:
                return {"success": False, "error": "종료일은 시작일보다 늦어야 합니다."}

            # 업데이트 쿼리
            query = """
            UPDATE phishing_training_periods 
            SET training_year = %s, period_name = %s, training_type = %s,
                start_date = %s, end_date = %s, description = %s,
                auto_pass_setting = %s, updated_at = NOW()
            WHERE period_id = %s
            """

            values = (data['training_year'], data['period_name'], data['training_type'],
                      start_date, end_date, data.get('description', ''),
                      data.get('auto_pass_setting', True), period_id)

            execute_query(query, values)

            return {"success": True, "message": "훈련 기간이 수정되었습니다."}

        except Exception as e:
            logger.error(f"훈련 기간 수정 오류: {str(e)}")
            return {"success": False, "error": f"훈련 기간 수정 중 오류가 발생했습니다: {str(e)}"}

    def _check_duplicate_period_exclude_self(self, period_id: int, year: int,
                                             period_name: str,
                                             training_type: str) -> bool:
        """중복 기간 체크 (자기 자신 제외)"""
        query = """
        SELECT COUNT(*) as count 
        FROM phishing_training_periods 
        WHERE period_id != %s AND training_year = %s AND period_name = %s AND training_type = %s
        """

        result = execute_query(query, (period_id, year, period_name, training_type),
                               fetch_one=True)
        return result['count'] > 0

    def _get_period_by_id(self, period_id: int) -> Optional[Dict]:
        """ID로 기간 조회"""
        query = """
        SELECT * FROM phishing_training_periods WHERE period_id = %s
        """

        return execute_query(query, (period_id, ), fetch_one=True)

    def complete_period(self, period_id: int, completed_by: str) -> Dict[str, Any]:
        """훈련 기간 완료 처리"""
        try:
            period = self._get_period_by_id(period_id)
            if not period:
                return {"success": False, "error": "훈련 기간을 찾을 수 없습니다."}

            if period['is_completed']:
                return {"success": False, "error": "이미 완료된 훈련 기간입니다."}

            # 자동 통과 처리
            if period['auto_pass_setting']:
                self._process_auto_pass(period_id)

            # 완료 상태로 변경
            query = """
            UPDATE phishing_training_periods 
            SET is_completed = 1, completed_at = NOW(), completed_by = %s
            WHERE period_id = %s
            """

            execute_query(query, (completed_by, period_id))

            return {"success": True, "message": "훈련 기간이 완료 처리되었습니다."}

        except Exception as e:
            logger.error(f"훈련 기간 완료 처리 오류: {str(e)}")
            return {"success": False, "error": f"완료 처리 중 오류가 발생했습니다: {str(e)}"}

    def _process_auto_pass(self, period_id: int):
        """자동 통과 처리 (무응답자를 성공으로 변경)"""
        try:
            query = """
            UPDATE phishing_training 
            SET training_result = 'success'
            WHERE period_id = %s AND training_result = 'no_response'
            """

            execute_query(query, (period_id, ))
            logger.info(f"기간 {period_id}: 무응답자 자동 통과 처리 완료")

        except Exception as e:
            logger.error(f"자동 통과 처리 오류: {str(e)}")
            raise

    def reopen_period(self, period_id: int) -> Dict[str, Any]:
        """훈련 기간 재개"""
        try:
            period = self._get_period_by_id(period_id)
            if not period:
                return {"success": False, "error": "훈련 기간을 찾을 수 없습니다."}

            if not period['is_completed']:
                return {"success": False, "error": "완료되지 않은 훈련 기간입니다."}

            # 재개 처리
            query = """
            UPDATE phishing_training_periods 
            SET is_completed = 0, completed_at = NULL, completed_by = NULL
            WHERE period_id = %s
            """

            execute_query(query, (period_id, ))

            return {"success": True, "message": "훈련 기간이 재개되었습니다."}

        except Exception as e:
            logger.error(f"훈련 기간 재개 오류: {str(e)}")
            return {"success": False, "error": f"재개 처리 중 오류가 발생했습니다: {str(e)}"}

    def delete_training_period(self, period_id: int) -> Dict[str, Any]:
        """훈련 기간 삭제 (확인 요청)"""
        try:
            period = self._get_period_by_id(period_id)
            if not period:
                return {"success": False, "error": "훈련 기간을 찾을 수 없습니다."}

            # 연관된 훈련 기록 수 확인
            training_count = self._get_training_count(period_id)

            if training_count > 0:
                return {
                    "success": False,
                    "error": f"이 기간에 {training_count}건의 훈련 기록이 있습니다.",
                    "requires_confirmation": True,
                    "training_count": training_count
                }

            # 훈련 기록이 없으면 바로 삭제
            query = "DELETE FROM phishing_training_periods WHERE period_id = %s"
            execute_query(query, (period_id, ))

            return {"success": True, "message": "훈련 기간이 삭제되었습니다."}

        except Exception as e:
            logger.error(f"훈련 기간 삭제 오류: {str(e)}")
            return {"success": False, "error": f"삭제 처리 중 오류가 발생했습니다: {str(e)}"}

    def force_delete_training_period(self, period_id: int) -> Dict[str, Any]:
        """훈련 기간 강제 삭제 (훈련 기록 포함)"""
        try:
            period = self._get_period_by_id(period_id)
            if not period:
                return {"success": False, "error": "훈련 기간을 찾을 수 없습니다."}

            # 트랜잭션으로 안전하게 삭제
            with DatabaseManager() as db:
                # 훈련 기록 먼저 삭제
                db.execute_query("DELETE FROM phishing_training WHERE period_id = %s",
                                 (period_id, ))

                # 기간 삭제
                db.execute_query(
                    "DELETE FROM phishing_training_periods WHERE period_id = %s",
                    (period_id, ))

            return {"success": True, "message": "훈련 기간과 관련 기록이 모두 삭제되었습니다."}

        except Exception as e:
            logger.error(f"훈련 기간 강제 삭제 오류: {str(e)}")
            return {"success": False, "error": f"강제 삭제 중 오류가 발생했습니다: {str(e)}"}

    def _get_training_count(self, period_id: int) -> int:
        """기간별 훈련 기록 수 조회"""
        query = "SELECT COUNT(*) as count FROM phishing_training WHERE period_id = %s"
        result = execute_query(query, (period_id, ), fetch_one=True)
        return result['count'] if result else 0
