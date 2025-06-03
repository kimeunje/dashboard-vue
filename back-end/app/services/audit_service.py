# app/services/audit_service.py - KPI 감점 시스템으로 수정
import json
from datetime import datetime
from app.utils.database import execute_query, DatabaseManager
from app.utils.validation import validate_security_item, generate_notes
from app.utils.constants import EXCEPTION_ITEM_NAMES


class AuditService:
    """보안 감사 관련 서비스 - KPI 감점 시스템"""

    def get_user_stats(self, username: str, check_type: str = None) -> dict:
        """사용자별 보안 통계 데이터 조회 (감점 기준으로 수정)"""
        # 사용자 ID 가져오기
        user = execute_query("SELECT uid FROM users WHERE user_id = %s", (username, ),
                             fetch_one=True)

        if not user:
            raise ValueError("사용자 정보를 찾을 수 없습니다.")

        user_id = user["uid"]

        with DatabaseManager.get_db_cursor(commit=False) as cursor:
            # 체크리스트 항목 조건 설정
            if check_type:
                checklist_condition = "WHERE check_type = %s"
                checklist_params = (check_type,)
                log_condition = """
                    WHERE al.user_id = %s 
                    AND ci.check_type = %s
                """
                log_params = (user_id, check_type)
            else:
                checklist_condition = ""
                checklist_params = ()
                log_condition = "WHERE al.user_id = %s"
                log_params = (user_id,)

            # 총 체크리스트 항목 수 조회
            cursor.execute(f"SELECT COUNT(*) as total_items FROM checklist_items {checklist_condition}", 
                          checklist_params)
            total_checks = cursor.fetchone()["total_items"]

            # 해당 사용자의 가장 최근 감사 날짜 조회
            cursor.execute(
                f"""
                SELECT MAX(al.checked_at) as last_audit_date
                FROM audit_log al
                LEFT JOIN checklist_items ci ON al.item_id = ci.item_id
                {log_condition}
                """, log_params)
            last_audit_result = cursor.fetchone()
            last_audit_date = last_audit_result["last_audit_date"]

            # 해당 사용자가 통과한 검사 항목 수 조회
            cursor.execute(
                f"""
                SELECT COUNT(DISTINCT al.item_id) as completed_checks
                FROM audit_log al
                LEFT JOIN checklist_items ci ON al.item_id = ci.item_id
                {log_condition.replace('WHERE', 'WHERE al.passed = 1 AND')}
                """, log_params)
            completed_checks = cursor.fetchone()["completed_checks"]

            # 해당 사용자의 실패 항목 수 조회
            cursor.execute(
                f"""
                SELECT COUNT(DISTINCT al.item_id) as critical_issues
                FROM audit_log al
                LEFT JOIN checklist_items ci ON al.item_id = ci.item_id
                {log_condition.replace('WHERE', 'WHERE al.passed = 0 AND')}
                """, log_params)
            critical_issues = cursor.fetchone()["critical_issues"]

            # 수정: 감점 계산 (실패 항목별 가중치 적용)
            cursor.execute(
                f"""
                SELECT 
                    SUM(CASE WHEN al.passed = 0 THEN COALESCE(ci.penalty_weight, 0.5) ELSE 0 END) as total_penalty
                FROM audit_log al
                LEFT JOIN checklist_items ci ON al.item_id = ci.item_id
                {log_condition}
                """, log_params)
            penalty_result = cursor.fetchone()
            total_penalty = float(penalty_result["total_penalty"] or 0)

        # 날짜 포맷 변환
        formatted_date = last_audit_date.strftime("%Y-%m-%d") if last_audit_date else ""

        return {
            "lastAuditDate": formatted_date,
            "totalChecks": total_checks,
            "completedChecks": completed_checks,
            "criticalIssues": critical_issues,
            "totalPenalty": round(total_penalty, 1),  # 수정: 감점 추가
            "checkType": check_type
        }

    def get_user_logs(self, username: str, check_type: str = None) -> list:
        """사용자별 보안 감사 로그 목록 조회 (감점 정보 포함)"""
        # 사용자 ID 가져오기
        user = execute_query("SELECT uid FROM users WHERE user_id = %s", (username, ),
                             fetch_one=True)

        if not user:
            raise ValueError("사용자 정보를 찾을 수 없습니다.")

        user_id = user["uid"]

        # 점검 유형별 필터링 조건
        if check_type:
            condition = """
                WHERE al.user_id = %s AND ci.check_type = %s
                ORDER BY al.checked_at DESC
            """
            params = (user_id, check_type)
        else:
            condition = """
                WHERE al.user_id = %s
                ORDER BY al.checked_at DESC
            """
            params = (user_id,)

        # 수정: 감점 정보 포함하여 로그 조회
        logs = execute_query(
            f"""
            SELECT al.log_id, al.user_id, al.item_id, al.actual_value, al.passed, al.notes, al.checked_at,
                   ci.check_type, ci.check_frequency, ci.penalty_weight,
                   CASE WHEN al.passed = 0 THEN COALESCE(ci.penalty_weight, 0.5) ELSE 0 END as penalty_applied
            FROM audit_log al
            LEFT JOIN checklist_items ci ON al.item_id = ci.item_id
            {condition}
            """, params, fetch_all=True)

        result = []
        for log in logs:
            # MariaDB의 JSON 타입이 자동으로 파싱되지 않을 수 있으므로 확인
            if isinstance(log["actual_value"], str):
                actual_value = json.loads(log["actual_value"])
            else:
                actual_value = log["actual_value"]

            # checked_at이 datetime 객체라면 문자열로 변환
            if isinstance(log["checked_at"], datetime):
                checked_at = log["checked_at"].strftime("%Y-%m-%d %H:%M:%S")
            else:
                checked_at = log["checked_at"]

            result.append({
                "log_id": log["log_id"],
                "user_id": log["user_id"],
                "item_id": log["item_id"],
                "actual_value": actual_value,
                "passed": log["passed"],
                "notes": log["notes"],
                "checked_at": checked_at,
                "check_type": log["check_type"],
                "check_frequency": log["check_frequency"],
                "penalty_weight": float(log["penalty_weight"] or 0),  # 수정: 감점 가중치 추가
                "penalty_applied": float(log["penalty_applied"] or 0)  # 수정: 적용된 감점 추가
            })

        return result

    def get_checklist_items(self, check_type: str = None) -> list:
        """체크리스트 항목 조회 (감점 가중치 포함)"""
        if check_type:
            condition = "WHERE check_type = %s"
            params = (check_type,)
        else:
            condition = ""
            params = ()

        # 수정: penalty_weight 필드 추가
        return execute_query(
            f"""
            SELECT item_id, category, item_name as name, description, check_type, check_frequency, penalty_weight
            FROM checklist_items
            {condition}
            ORDER BY check_type, item_id ASC
            """, params, fetch_all=True)

    def execute_manual_check(self, user_id: int, item_id: int, check_result: dict) -> dict:
        """수시 점검 실행 및 결과 저장 (감점 계산 포함)"""
        # 항목 정보 확인
        item_info = execute_query(
            """
            SELECT item_id, item_name, check_type, penalty_weight
            FROM checklist_items
            WHERE item_id = %s AND check_type = 'manual'
            """, (item_id,), fetch_one=True)

        if not item_info:
            raise ValueError("해당 수시 점검 항목을 찾을 수 없습니다.")

        item_name = item_info["item_name"]
        penalty_weight = float(item_info["penalty_weight"] or 0.5)
        actual_value = check_result.get("actual_value", {})
        passed = check_result.get("passed")
        notes = check_result.get("notes", "")

        # 수시 점검은 수동 입력이므로 passed 값이 반드시 필요
        if passed is None:
            raise ValueError("점검 결과(통과/실패)를 반드시 입력해야 합니다.")

        # JSON 문자열로 변환
        actual_value_json = json.dumps(actual_value, ensure_ascii=False)

        # 수정: 감점 계산
        penalty_applied = penalty_weight if passed == 0 else 0

        # 로그 저장 (수시 점검은 매번 새로 생성)
        execute_query(
            """
            INSERT INTO audit_log (user_id, item_id, actual_value, passed, notes)
            VALUES (%s, %s, %s, %s, %s)
            """, (user_id, item_id, actual_value_json, passed, notes))

        return {
            "status": "success",
            "item_id": item_id,
            "item_name": item_name,
            "passed": passed,
            "penalty_weight": penalty_weight,  # 수정: 감점 가중치 추가
            "penalty_applied": penalty_applied,  # 수정: 적용된 감점 추가
            "log_action": "created",
            "message": "수시 점검 결과가 성공적으로 저장되었습니다."
        }

    def get_manual_check_items(self) -> list:
        """수시 점검 가능한 항목 목록 조회 (감점 가중치 포함)"""
        # 수정: penalty_weight 필드 추가
        return execute_query(
            """
            SELECT item_id, category, item_name as name, description, penalty_weight
            FROM checklist_items
            WHERE check_type = 'manual'
            ORDER BY item_id ASC
            """, fetch_all=True)

    def validate_check(self, data: dict) -> dict:
        """항목 검증 및 로그 업데이트 (기존 메서드 - 정기 점검용, 감점 계산 포함)"""
        required_fields = ["user_id", "item_type", "actual_value"]
        missing_fields = [field for field in required_fields if field not in data]

        if missing_fields:
            raise ValueError(f"필수 필드가 누락되었습니다: {', '.join(missing_fields)}")

        # 체크리스트 항목 조회 (정기 점검만, 감점 가중치 포함)
        item_result = execute_query(
            """
            SELECT item_id, item_name, penalty_weight
            FROM checklist_items
            WHERE item_name LIKE %s AND check_type = 'daily'
            """, (data["item_type"], ), fetch_one=True)

        if not item_result:
            raise ValueError(f"[{data['item_type']}] 정기 점검 항목을 찾을 수 없습니다")

        user_id = data["user_id"]
        item_id = item_result["item_id"]
        item_name = item_result["item_name"]
        penalty_weight = float(item_result["penalty_weight"] or 0.5)  # 수정: 감점 가중치
        actual_value = data["actual_value"]
        notes = data.get("notes", "")

        # 검증 로직
        passed = None

        # 예외 목록에 없는 경우만 검증
        if item_name not in EXCEPTION_ITEM_NAMES:
            # 검증 수행
            passed = 1 if validate_security_item(item_name, actual_value) else 0

            # 검증 결과에 따라 자동으로 notes 생성
            if notes == "":
                notes = generate_notes(item_name, passed, actual_value)

        # JSON 문자열로 변환
        actual_value_json = json.dumps(actual_value, ensure_ascii=False)

        # 수정: 감점 계산
        penalty_applied = penalty_weight if passed == 0 else 0

        # 기존 로그 업데이트 또는 새로 생성
        log_action = self._update_or_create_log(user_id, item_id, actual_value_json,
                                                passed, notes)

        return {
            "status": "success",
            "item_id": item_id,
            "item_name": item_name,
            "passed": passed,
            "penalty_weight": penalty_weight,  # 수정: 감점 가중치 추가
            "penalty_applied": penalty_applied,  # 수정: 적용된 감점 추가
            "log_action": log_action,
        }

    def _update_or_create_log(self, user_id: int, item_id: int, actual_value_json: str,
                              passed: int, notes: str) -> str:
        """기존 로그 업데이트 또는 새로 생성"""
        # 오늘 날짜의 해당 항목 로그를 찾아서 업데이트
        existing_log = execute_query(
            """
            SELECT log_id 
            FROM audit_log 
            WHERE user_id = %s AND item_id = %s AND DATE(checked_at) = DATE(NOW())
            ORDER BY checked_at DESC
            LIMIT 1
            """, (user_id, item_id), fetch_one=True)

        if existing_log:
            # 기존 로그 업데이트
            execute_query(
                """
                UPDATE audit_log 
                SET actual_value = %s, passed = %s, notes = %s, checked_at = NOW()
                WHERE log_id = %s
                """, (actual_value_json, passed, notes, existing_log["log_id"]))
            return "updated"
        else:
            # 새로 생성 (예외 상황)
            execute_query(
                """
                INSERT INTO audit_log (user_id, item_id, actual_value, passed, notes)
                VALUES (%s, %s, %s, %s, %s)
                """, (user_id, item_id, actual_value_json, passed, notes))
            return "created"

    def get_penalty_summary(self, username: str, check_type: str = None) -> dict:
        """사용자 감점 요약 조회 (새로운 메서드)"""
        user_stats = self.get_user_stats(username, check_type)
        
        # 감점 레벨 계산
        total_penalty = user_stats.get("totalPenalty", 0)
        penalty_level = "none"
        if total_penalty > 0:
            if total_penalty <= 1.0:
                penalty_level = "low"
            elif total_penalty <= 2.5:
                penalty_level = "medium"
            else:
                penalty_level = "high"
        
        return {
            "total_penalty": total_penalty,
            "penalty_level": penalty_level,
            "failed_items": user_stats.get("criticalIssues", 0),
            "total_items": user_stats.get("totalChecks", 0),
            "check_type": check_type,
            "last_audit_date": user_stats.get("lastAuditDate", "")
        }