# app/services/audit_service.py - 제외 설정 반영 버전 (수정)
import json
from datetime import datetime
from app.utils.database import execute_query, DatabaseManager
from app.utils.validation import validate_security_item, generate_notes
from app.utils.constants import EXCEPTION_ITEM_NAMES
from app.services.exception_service import ExceptionService


class AuditService:
    """보안 감사 관련 서비스 - 제외 설정 반영 (수정된 버전)"""

    def __init__(self):
        self.exception_service = ExceptionService()

    def get_user_stats(self, username: str, check_type: str = None) -> dict:
        """사용자별 보안 통계 데이터 조회 (제외 설정 반영)"""
        # 사용자 ID 가져오기
        user = execute_query("SELECT uid FROM users WHERE user_id = %s", (username, ),
                             fetch_one=True)

        if not user:
            raise ValueError("사용자 정보를 찾을 수 없습니다.")

        user_id = user["uid"]

        with DatabaseManager.get_db_cursor(commit=False) as cursor:
            # 체크리스트 항목 조건 설정
            if check_type:
                checklist_condition = "WHERE ci.check_type = %s"
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
            cursor.execute(f"SELECT COUNT(*) as total_items FROM checklist_items ci {checklist_condition}", 
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

            # 제외 설정 반영하여 통계 계산 (수정된 버전)
            # 뷰 대신 직접 조인하여 제외 설정 확인
            cursor.execute(
                f"""
                SELECT 
                    COUNT(DISTINCT al.item_id) as completed_checks,
                    SUM(CASE 
                        WHEN (uie.exception_id IS NOT NULL OR die.dept_exception_id IS NOT NULL) THEN 0
                        WHEN al.passed = 1 THEN 1 
                        ELSE 0 
                    END) as passed_count,
                    SUM(CASE 
                        WHEN (uie.exception_id IS NOT NULL OR die.dept_exception_id IS NOT NULL) THEN 0
                        WHEN al.passed = 0 THEN 1 
                        ELSE 0 
                    END) as failed_count,
                    SUM(CASE 
                        WHEN (uie.exception_id IS NOT NULL OR die.dept_exception_id IS NOT NULL) THEN 0
                        WHEN al.passed = 0 THEN COALESCE(ci.penalty_weight, 0.5) 
                        ELSE 0 
                    END) as total_penalty
                FROM audit_log al
                INNER JOIN (
                    SELECT item_id, MAX(checked_at) as max_checked_at
                    FROM audit_log 
                    WHERE user_id = %s
                    GROUP BY item_id
                ) latest ON al.item_id = latest.item_id AND al.checked_at = latest.max_checked_at
                INNER JOIN checklist_items ci ON al.item_id = ci.item_id
                LEFT JOIN user_item_exceptions uie ON (
                    uie.user_id = al.user_id 
                    AND uie.item_id = al.item_id 
                    AND uie.is_active = 1
                    AND (uie.exclude_type = 'permanent' OR 
                         (uie.exclude_type = 'temporary' AND CURDATE() BETWEEN uie.start_date AND uie.end_date))
                )
                LEFT JOIN department_item_exceptions die ON (
                    die.department = (SELECT department FROM users WHERE uid = al.user_id)
                    AND die.item_id = al.item_id 
                    AND die.is_active = 1
                    AND (die.exclude_type = 'permanent' OR 
                         (die.exclude_type = 'temporary' AND CURDATE() BETWEEN die.start_date AND die.end_date))
                )
                WHERE al.user_id = %s
                {(' AND ci.check_type = %s' if check_type else '')}
                """, 
                (user_id, user_id) + ((check_type,) if check_type else ()))
            
            stats_result = cursor.fetchone()

            completed_checks = stats_result["completed_checks"] or 0
            passed_count = stats_result["passed_count"] or 0
            failed_count = stats_result["failed_count"] or 0
            total_penalty = float(stats_result["total_penalty"] or 0)

            # 제외된 항목 수 조회 (수정된 버전)
            cursor.execute(
                f"""
                SELECT COUNT(DISTINCT COALESCE(uie.item_id, die.item_id)) as excluded_count
                FROM checklist_items ci
                LEFT JOIN user_item_exceptions uie ON (
                    uie.item_id = ci.item_id 
                    AND uie.user_id = %s 
                    AND uie.is_active = 1
                    AND (uie.exclude_type = 'permanent' OR 
                         (uie.exclude_type = 'temporary' AND CURDATE() BETWEEN uie.start_date AND uie.end_date))
                )
                LEFT JOIN department_item_exceptions die ON (
                    die.item_id = ci.item_id 
                    AND die.department = (SELECT department FROM users WHERE uid = %s)
                    AND die.is_active = 1
                    AND (die.exclude_type = 'permanent' OR 
                         (die.exclude_type = 'temporary' AND CURDATE() BETWEEN die.start_date AND die.end_date))
                )
                WHERE (uie.exception_id IS NOT NULL OR die.dept_exception_id IS NOT NULL)
                {('AND ci.check_type = %s' if check_type else '')}
                """, 
                (user_id, user_id) + ((check_type,) if check_type else ()))
            
            excluded_count = cursor.fetchone()["excluded_count"] or 0

        # 날짜 포맷 변환
        formatted_date = last_audit_date.strftime("%Y-%m-%d") if last_audit_date else ""

        return {
            "lastAuditDate": formatted_date,
            "totalChecks": total_checks,
            "completedChecks": passed_count,  # 통과한 항목
            "criticalIssues": failed_count,   # 실패한 항목 (감점 대상)
            "excludedItems": excluded_count,  # 제외된 항목
            "totalPenalty": round(total_penalty, 1),
            "checkType": check_type
        }

    def get_user_logs(self, username: str, check_type: str = None) -> list:
        """사용자별 보안 감사 로그 목록 조회 (제외 설정 정보 포함)"""
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

        # 제외 설정 정보를 포함하여 로그 조회 (수정된 버전)
        logs = execute_query(
            f"""
            SELECT 
                al.log_id, al.user_id, al.item_id, al.actual_value, al.passed, al.notes, al.checked_at,
                ci.check_type, ci.check_frequency, ci.penalty_weight, ci.item_name,
                CASE 
                    WHEN (uie.exception_id IS NOT NULL OR die.dept_exception_id IS NOT NULL) THEN 0
                    WHEN al.passed = 0 THEN COALESCE(ci.penalty_weight, 0.5) 
                    ELSE 0 
                END as penalty_applied,
                COALESCE(uie.exclude_reason, die.exclude_reason) as exclude_reason,
                COALESCE(uie.exclude_type, die.exclude_type) as exclude_type,
                CASE 
                    WHEN uie.exception_id IS NOT NULL THEN 'user'
                    WHEN die.dept_exception_id IS NOT NULL THEN 'department'
                    ELSE NULL
                END as exception_type,
                CASE WHEN (uie.exception_id IS NOT NULL OR die.dept_exception_id IS NOT NULL) THEN 1 ELSE 0 END as is_excluded
            FROM audit_log al
            LEFT JOIN checklist_items ci ON al.item_id = ci.item_id
            LEFT JOIN user_item_exceptions uie ON (
                uie.user_id = al.user_id 
                AND uie.item_id = al.item_id 
                AND uie.is_active = 1
                AND (uie.exclude_type = 'permanent' OR 
                     (uie.exclude_type = 'temporary' AND CURDATE() BETWEEN uie.start_date AND uie.end_date))
            )
            LEFT JOIN department_item_exceptions die ON (
                die.department = (SELECT department FROM users WHERE uid = al.user_id)
                AND die.item_id = al.item_id 
                AND die.is_active = 1
                AND (die.exclude_type = 'permanent' OR 
                     (die.exclude_type = 'temporary' AND CURDATE() BETWEEN die.start_date AND die.end_date))
            )
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
                "item_name": log["item_name"],
                "actual_value": actual_value,
                "passed": log["passed"],
                "notes": log["notes"],
                "checked_at": checked_at,
                "check_type": log["check_type"],
                "check_frequency": log["check_frequency"],
                "penalty_weight": float(log["penalty_weight"] or 0),
                "penalty_applied": float(log["penalty_applied"] or 0),
                "is_excluded": bool(log["is_excluded"]),
                "exception_type": log["exception_type"],
                "exclude_reason": log["exclude_reason"],
                "exclude_type": log["exclude_type"]
            })

        return result

    def validate_check(self, data: dict) -> dict:
        """항목 검증 및 로그 업데이트 (제외 설정 반영)"""
        required_fields = ["user_id", "item_type", "actual_value"]
        missing_fields = [field for field in required_fields if field not in data]

        if missing_fields:
            raise ValueError(f"필수 필드가 누락되었습니다: {', '.join(missing_fields)}")

        # 체크리스트 항목 조회
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
        penalty_weight = float(item_result["penalty_weight"] or 0.5)
        actual_value = data["actual_value"]
        notes = data.get("notes", "")

        # 제외 설정 확인 (수정된 버전)
        exception_info = self._check_item_excluded_for_user(user_id, item_id)

        # 검증 로직
        passed = None

        # 예외 목록에 없는 경우만 검증
        if item_name not in EXCEPTION_ITEM_NAMES:
            # 검증 수행
            passed = 1 if validate_security_item(item_name, actual_value) else 0

            # 검증 결과에 따라 자동으로 notes 생성
            if notes == "":
                notes = generate_notes(item_name, passed, actual_value)

        # 제외 설정이 있는 경우 notes에 추가
        if exception_info["is_excluded"]:
            if notes:
                notes += f" [제외사유: {exception_info['exclude_reason']}]"
            else:
                notes = f"제외사유: {exception_info['exclude_reason']}"

        # JSON 문자열로 변환
        actual_value_json = json.dumps(actual_value, ensure_ascii=False)

        # 감점 계산 (제외 설정 반영)
        if exception_info["is_excluded"]:
            penalty_applied = 0
        else:
            penalty_applied = penalty_weight if passed == 0 else 0

        # 기존 로그 업데이트 또는 새로 생성
        log_action = self._update_or_create_log(user_id, item_id, actual_value_json,
                                                passed, notes, exception_info.get('exclude_reason'))

        return {
            "status": "success",
            "item_id": item_id,
            "item_name": item_name,
            "passed": passed,
            "penalty_weight": penalty_weight,
            "penalty_applied": penalty_applied,
            "is_excluded": exception_info["is_excluded"],
            "exclude_reason": exception_info.get("exclude_reason"),
            "log_action": log_action,
        }

    def _check_item_excluded_for_user(self, user_id: int, item_id: int) -> dict:
        """특정 사용자-항목이 제외 대상인지 확인 (직접 쿼리 버전)"""
        result = execute_query(
            """
            SELECT 
                CASE 
                    WHEN uie.exception_id IS NOT NULL THEN 'user'
                    WHEN die.dept_exception_id IS NOT NULL THEN 'department'
                    ELSE NULL
                END as exception_type,
                COALESCE(uie.exclude_reason, die.exclude_reason) as exclude_reason,
                COALESCE(uie.exclude_type, die.exclude_type) as exclude_type,
                COALESCE(uie.start_date, die.start_date) as start_date,
                COALESCE(uie.end_date, die.end_date) as end_date
            FROM users u
            LEFT JOIN user_item_exceptions uie ON (
                uie.user_id = u.uid 
                AND uie.item_id = %s 
                AND uie.is_active = 1
                AND (uie.exclude_type = 'permanent' OR 
                     (uie.exclude_type = 'temporary' AND CURDATE() BETWEEN uie.start_date AND uie.end_date))
            )
            LEFT JOIN department_item_exceptions die ON (
                die.department = u.department
                AND die.item_id = %s 
                AND die.is_active = 1
                AND (die.exclude_type = 'permanent' OR 
                     (die.exclude_type = 'temporary' AND CURDATE() BETWEEN die.start_date AND die.end_date))
            )
            WHERE u.uid = %s
            AND (uie.exception_id IS NOT NULL OR die.dept_exception_id IS NOT NULL)
            LIMIT 1
            """,
            (item_id, item_id, user_id),
            fetch_one=True,
        )

        if result:
            return {
                "is_excluded": True,
                "exception_type": result["exception_type"],
                "exclude_reason": result["exclude_reason"],
                "exclude_type": result["exclude_type"],
                "start_date": result["start_date"],
                "end_date": result["end_date"],
            }

        return {"is_excluded": False}

    # 나머지 메서드들은 기존과 동일하게 유지
    def get_checklist_items(self, check_type: str = None) -> list:
        """체크리스트 항목 조회 (감점 가중치 포함)"""
        if check_type:
            condition = "WHERE check_type = %s"
            params = (check_type,)
        else:
            condition = ""
            params = ()

        return execute_query(
            f"""
            SELECT item_id, category, item_name as name, description, check_type, check_frequency, penalty_weight
            FROM checklist_items
            {condition}
            ORDER BY check_type, item_id ASC
            """, params, fetch_all=True)

    def execute_manual_check(self, user_id: int, item_id: int, check_result: dict) -> dict:
        """수시 점검 실행 및 결과 저장 (제외 설정 확인)"""
        # 제외 설정 확인
        exception_info = self._check_item_excluded_for_user(user_id, item_id)
        
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

        # 감점 계산 (제외 설정 반영)
        if exception_info["is_excluded"]:
            penalty_applied = 0
            if notes:
                notes += f" [제외사유: {exception_info['exclude_reason']}]"
            else:
                notes = f"제외사유: {exception_info['exclude_reason']}"
        else:
            penalty_applied = penalty_weight if passed == 0 else 0

        # 로그 저장 (수시 점검은 매번 새로 생성)
        execute_query(
            """
            INSERT INTO audit_log (user_id, item_id, actual_value, passed, notes, exclude_reason)
            VALUES (%s, %s, %s, %s, %s, %s)
            """, (user_id, item_id, actual_value_json, passed, notes, 
                  exception_info.get('exclude_reason') if exception_info["is_excluded"] else None))

        return {
            "status": "success",
            "item_id": item_id,
            "item_name": item_name,
            "passed": passed,
            "penalty_weight": penalty_weight,
            "penalty_applied": penalty_applied,
            "is_excluded": exception_info["is_excluded"],
            "exclude_reason": exception_info.get("exclude_reason"),
            "log_action": "created",
            "message": "수시 점검 결과가 성공적으로 저장되었습니다."
        }

    def _update_or_create_log(self, user_id: int, item_id: int, actual_value_json: str,
                              passed: int, notes: str, exclude_reason: str = None) -> str:
        """기존 로그 업데이트 또는 새로 생성 (제외 사유 포함)"""
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
                SET actual_value = %s, passed = %s, notes = %s, exclude_reason = %s, checked_at = NOW()
                WHERE log_id = %s
                """, (actual_value_json, passed, notes, exclude_reason, existing_log["log_id"]))
            return "updated"
        else:
            # 새로 생성
            execute_query(
                """
                INSERT INTO audit_log (user_id, item_id, actual_value, passed, notes, exclude_reason)
                VALUES (%s, %s, %s, %s, %s, %s)
                """, (user_id, item_id, actual_value_json, passed, notes, exclude_reason))
            return "created"

    def get_penalty_summary(self, username: str, check_type: str = None) -> dict:
        """사용자 감점 요약 조회 (제외 설정 반영)"""
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
            "excluded_items": user_stats.get("excludedItems", 0),
            "check_type": check_type,
            "last_audit_date": user_stats.get("lastAuditDate", "")
        }

    def get_manual_check_items(self):
        """수시 점검 가능한 항목 목록 조회 (감점 가중치 포함)"""
        return execute_query(
            """
            SELECT item_id, category, item_name as name, description, penalty_weight
            FROM checklist_items
            WHERE check_type = 'manual'
            ORDER BY category, item_name
            """, fetch_all=True)

    def get_user_exceptions_summary(self, username: str) -> dict:
        """사용자의 제외 설정 요약"""
        user = execute_query("SELECT uid FROM users WHERE user_id = %s", (username, ),
                             fetch_one=True)
        
        if not user:
            raise ValueError("사용자 정보를 찾을 수 없습니다.")

        exceptions = self.exception_service.get_active_exceptions_for_user(user["uid"])
        
        return {
            "total_exceptions": len(exceptions),
            "user_specific": len([e for e in exceptions if e["exception_type"] == "user"]),
            "department_based": len([e for e in exceptions if e["exception_type"] == "department"]),
            "exceptions": exceptions
        }