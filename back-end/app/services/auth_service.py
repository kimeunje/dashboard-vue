# app/services/auth_service.py
import jwt
import secrets
from datetime import datetime, timedelta
from flask import current_app
from app.utils.constants import TEST_USERS, DEFAULT_VERIFICATION_CODE
from app.utils.database import execute_query


class AuthService:
    """인증 관련 서비스"""

    def __init__(self):
        self.verification_codes = {}  # 실제 환경에서는 Redis 등 사용 권장

    def authenticate_ldap(self, username: str, password: str) -> dict:
        """모의 LDAP 인증"""
        if username in TEST_USERS and TEST_USERS[username]["password"] == password:
            user_data = TEST_USERS[username]
            return {
                "success": True,
                "username": username,
                "email": user_data["email"],
                "name": user_data["name"],
                "dept": user_data["dept"],
            }
        else:
            return {
                "success": False,
                "message": "아이디 또는 비밀번호가 올바르지 않습니다.",
            }

    def send_verification_code(self, email: str) -> dict:
        """이메일 인증 코드 발송 (모의)"""
        if not email:
            return {"success": False, "message": "이메일 주소가 필요합니다."}

        # 6자리 인증 코드 생성 (테스트용 고정 코드)
        verification_code = DEFAULT_VERIFICATION_CODE

        # 인증 코드 저장 (15분 유효)
        expiry = datetime.now() + timedelta(minutes=15)
        self.verification_codes[email] = {"code": verification_code, "expiry": expiry}

        # 콘솔에 출력 (실제 이메일 발송 대신)
        print(f"이메일 인증 코드: {verification_code} (수신자: {email})")

        return {"success": True, "message": "인증 코드가 발송되었습니다."}

    def verify_code(self, email: str, code: str) -> bool:
        """인증 코드 확인"""
        # 테스트 모드: 모든 코드 허용 (123456 또는 DB에 저장된 코드)
        is_valid_code = code == DEFAULT_VERIFICATION_CODE

        # 저장된 코드가 있으면 확인
        if email in self.verification_codes:
            verification_info = self.verification_codes[email]
            is_valid_code = is_valid_code or (verification_info["code"] == code
                                              and datetime.now()
                                              <= verification_info["expiry"])

        return is_valid_code

    def generate_token(self, username: str, user_info: dict) -> str:
        """JWT 토큰 생성"""
        token_payload = {
            "username": username,
            "name": user_info.get("name"),
            "dept": user_info.get("dept"),
            "exp": datetime.now() +
            timedelta(seconds=current_app.config['TOKEN_EXPIRATION']),
        }

        return jwt.encode(token_payload, current_app.config['JWT_SECRET'],
                          algorithm="HS256")

    def verify_token(self, token: str) -> dict:
        """JWT 토큰 검증"""
        try:
            payload = jwt.decode(token, current_app.config['JWT_SECRET'],
                                 algorithms=["HS256"])
            return {"valid": True, "payload": payload}
        except jwt.ExpiredSignatureError:
            return {"valid": False, "error": "토큰이 만료되었습니다."}
        except jwt.InvalidTokenError:
            return {"valid": False, "error": "유효하지 않은 토큰입니다."}

    def clear_verification_code(self, email: str):
        """인증 코드 삭제"""
        if email in self.verification_codes:
            del self.verification_codes[email]

    def authenticate_user_in_db(self, username: str) -> dict:
        """데이터베이스에서 사용자 검증 및 감사 로그 초기화"""
        try:
            # 사용자 확인
            user = execute_query("SELECT uid FROM users WHERE username = %s",
                                 (username, ), fetch_one=True)

            if not user:
                return {
                    "success": False,
                    "message": "사용자 검증에 실패했습니다. 운영실에 문의해주세요.",
                }

            user_id = user["uid"]

            # 오늘 날짜의 감사 로그가 이미 있는지 확인
            existing_logs = execute_query(
                """
                SELECT COUNT(*) as log_count
                FROM audit_log
                WHERE user_id = %s AND DATE(checked_at) = DATE(NOW())
                """, (user_id, ), fetch_one=True)["log_count"]

            # 오늘 감사 로그가 없으면 모든 체크리스트 항목에 대해 기본 로그 생성
            if existing_logs == 0:
                self._create_initial_audit_logs(user_id)
                current_app.logger.info(
                    f"사용자 {username} ({user_id})에 대해 감사 로그를 생성했습니다.")

            return {"success": True, "user_id": user_id}

        except Exception as e:
            current_app.logger.error(f"사용자 검증 오류: {str(e)}")
            return {
                "success": False,
                "message": "서버 오류가 발생했습니다.",
            }

    def _create_initial_audit_logs(self, user_id: int):
        """초기 감사 로그 생성"""
        # 모든 체크리스트 항목 조회
        checklist_items = execute_query(
            """
            SELECT item_id, item_name, category, description
            FROM checklist_items
            ORDER BY item_id
            """, fetch_all=True)

        # 각 항목에 대해 기본 감사 로그 생성
        import json
        default_actual_value = json.dumps({
            "status": "pending",
            "message": "검사 대기 중"
        }, ensure_ascii=False)

        for item in checklist_items:
            execute_query(
                """
                INSERT INTO audit_log (user_id, item_id, actual_value, passed, notes, checked_at)
                VALUES (%s, %s, %s, 0, '검사 대기 중', NOW())
                """, (user_id, item["item_id"], default_actual_value))