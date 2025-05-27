# app/services/audit_service.py
import json
from datetime import datetime
from app.utils.database import execute_query, DatabaseManager
from app.utils.validation import validate_security_item, generate_notes
from app.utils.constants import EXCEPTION_ITEM_NAMES


class AuditService:
    """보안 감사 관련 서비스"""

    def get_user_stats(self, username: str) -> dict:
        """사용자별 보안 통계 데이터 조회"""
        # 사용자 ID 가져오기
        user = execute_query("SELECT uid FROM users WHERE user_id = %s", (username, ),
                             fetch_one=True)

        if not user:
            raise ValueError("사용자 정보를 찾을 수 없습니다.")

        user_id = user["uid"]

        with DatabaseManager.get_db_cursor(commit=False) as cursor:
            # 총 체크리스트 항목 수 조회
            cursor.execute("SELECT COUNT(*) as total_items FROM checklist_items")
            total_checks = cursor.fetchone()["total_items"]

            # 해당 사용자의 가장 최근 감사 날짜 조회
            cursor.execute(
                """
                SELECT MAX(checked_at) as last_audit_date
                FROM audit_log
                WHERE user_id = %s
                """, (user_id, ))
            last_audit_result = cursor.fetchone()
            last_audit_date = last_audit_result["last_audit_date"]

            # 해당 사용자가 통과한 검사 항목 수 조회
            cursor.execute(
                """
                SELECT COUNT(DISTINCT item_id) as completed_checks
                FROM audit_log
                WHERE passed = 1 AND user_id = %s
                """, (user_id, ))
            completed_checks = cursor.fetchone()["completed_checks"]

            # 해당 사용자의 심각한 문제(통과하지 못한 항목) 수 조회
            cursor.execute(
                """
                SELECT COUNT(DISTINCT item_id) as critical_issues
                FROM audit_log
                WHERE passed = 0 AND user_id = %s
                """, (user_id, ))
            critical_issues = cursor.fetchone()["critical_issues"]

        # 날짜 포맷 변환
        formatted_date = last_audit_date.strftime("%Y-%m-%d") if last_audit_date else ""

        return {
            "lastAuditDate": formatted_date,
            "totalChecks": total_checks,
            "completedChecks": completed_checks,
            "criticalIssues": critical_issues,
        }

    def get_user_logs(self, username: str) -> list:
        """사용자별 보안 감사 로그 목록 조회"""
        # 사용자 ID 가져오기
        user = execute_query("SELECT uid FROM users WHERE user_id = %s", (username, ),
                             fetch_one=True)

        if not user:
            raise ValueError("사용자 정보를 찾을 수 없습니다.")

        user_id = user["uid"]

        # 특정 사용자의 로그만 날짜 역순으로 가져오기
        logs = execute_query(
            """
            SELECT log_id, user_id, item_id, actual_value, passed, notes, checked_at
            FROM audit_log
            WHERE user_id = %s
            ORDER BY checked_at DESC
            """, (user_id, ), fetch_all=True)

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
            })

        return result

    def get_checklist_items(self) -> list:
        """체크리스트 항목 조회"""
        return execute_query(
            """
            SELECT item_id, category, item_name as name, description
            FROM checklist_items
            ORDER BY item_id ASC
            """, fetch_all=True)

    def validate_check(self, data: dict) -> dict:
        """항목 검증 및 로그 업데이트"""
        required_fields = ["user_id", "item_type", "actual_value"]
        missing_fields = [field for field in required_fields if field not in data]

        if missing_fields:
            raise ValueError(f"필수 필드가 누락되었습니다: {', '.join(missing_fields)}")

        # 체크리스트 항목 조회
        item_result = execute_query(
            """
            SELECT item_id, item_name
            FROM checklist_items
            WHERE item_name LIKE %s
            """, (data["item_type"], ), fetch_one=True)

        if not item_result:
            raise ValueError(f"[{data['item_type']}] 체크리스트 항목을 찾을 수 없습니다")

        user_id = data["user_id"]
        item_id = item_result["item_id"]
        item_name = item_result["item_name"]
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

        # 기존 로그 업데이트 또는 새로 생성
        log_action = self._update_or_create_log(user_id, item_id, actual_value_json,
                                                passed, notes)

        return {
            "status": "success",
            "item_id": item_id,
            "item_name": item_name,
            "passed": passed,
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