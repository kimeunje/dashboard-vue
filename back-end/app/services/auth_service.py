# back-end/app/services/auth_service.py - IP 인증으로 수정

import jwt
import ipaddress
from datetime import datetime, timedelta
from flask import current_app
from app.utils.constants import (
    TEST_USERS,
    ALLOWED_IP_RANGES,
    IP_AUTH_CONFIG,
    DEFAULT_VERIFICATION_CODE,
)
from app.utils.database import execute_query


class AuthService:
    """인증 관련 서비스 - IP 기반 인증"""

    def __init__(self):
        self.verification_codes = {}  # 실제 환경에서는 Redis 등 사용 권장

    def authenticate_by_ip(self, client_ip: str) -> dict:
        """users 테이블 기반 IP 인증"""
        try:
            current_app.logger.info(f"IP 인증 시도: {client_ip}")

            # 1. 업무시간 체크 (설정에 따라)
            if not self._check_business_hours():
                return {
                    "success": False,
                    "message": "업무시간(평일 08:00-19:00) 외에는 접근할 수 없습니다.",
                    "code": "OUTSIDE_BUSINESS_HOURS",
                }

            # 2. IP 대역 체크
            if not self._is_ip_in_allowed_ranges(client_ip):
                return {
                    "success": False,
                    "message": f"허용되지 않은 네트워크({client_ip})에서의 접근입니다.",
                    "code": "IP_RANGE_NOT_ALLOWED",
                }

            # 3. users 테이블에서 IP로 사용자 찾기
            user_info = self._find_user_by_ip_from_db(client_ip)
            if not user_info:
                return {
                    "success": False,
                    "message": f"IP {client_ip}에 등록된 사용자를 찾을 수 없습니다. IT팀에 문의하세요.",
                    "code": "USER_NOT_FOUND",
                }

            # 4. 인증 성공
            current_app.logger.info(f"IP 인증 성공: {user_info['user_id']} ({client_ip})")
            return {
                "success": True,
                "username": user_info["user_id"],  # 로그인 ID
                "email": user_info["mail"],
                "name": user_info["username"],  # 실명
                "dept": user_info["department"],
                "role": user_info.get("role", "user"),
                "client_ip": client_ip,
            }

        except Exception as e:
            current_app.logger.error(f"IP 인증 오류: {str(e)}")
            return {
                "success": False,
                "message": "인증 처리 중 오류가 발생했습니다.",
                "code": "AUTH_ERROR",
            }

    def _find_user_by_ip_from_db(self, client_ip: str) -> dict:
        """users 테이블에서 IP로 사용자 찾기 - role 컬럼 사용"""
        try:
            users = execute_query(
                """
                SELECT uid, user_id, username, mail, department, ip, role
                FROM users 
                WHERE ip IS NOT NULL 
                AND ip != ''
                AND (
                    FIND_IN_SET(%s, REPLACE(ip, ' ', '')) > 0
                    OR ip LIKE %s
                    OR ip = %s
                )
                """,
                (client_ip, f"%{client_ip}%", client_ip),
                fetch_all=True,
            )

            if not users:
                current_app.logger.warning(f"IP {client_ip}에 매칭되는 사용자가 없습니다.")
                return None

            user = users[0]

            if self._verify_ip_match(client_ip, user["ip"]):
                current_app.logger.info(f"사용자 매칭: {user['user_id']} <- {client_ip}")

                # DB의 role 컬럼 사용 (기본값: 'user')
                role = user.get("role", "user") or "user"

                return {
                    "uid": user["uid"],
                    "user_id": user["user_id"],
                    "username": user["username"],
                    "mail": user["mail"],
                    "department": user["department"],
                    "role": role,  # DB에서 가져온 역할 사용
                }
            else:
                current_app.logger.warning(f"IP 정확성 검증 실패: {client_ip} vs {user['ip']}")
                return None

        except Exception as e:
            current_app.logger.error(f"DB에서 사용자 조회 오류: {str(e)}")
            return None

    def _verify_ip_match(self, client_ip: str, stored_ips: str) -> bool:
        """저장된 IP 목록과 클라이언트 IP 정확히 매칭 확인"""
        if not stored_ips:
            return False

        # 쉼표와 공백으로 분리
        ip_list = [
            ip.strip() for ip in stored_ips.replace(" ", "").split(",") if ip.strip()
        ]

        return client_ip in ip_list

    def _check_business_hours(self) -> bool:
        """업무시간 체크"""
        if not IP_AUTH_CONFIG.get("enable_time_restriction", False):
            return True

        now = datetime.now()
        business_hours = IP_AUTH_CONFIG["business_hours"]

        # 주말 체크
        if business_hours.get("weekdays_only", False) and now.weekday() >= 5:
            current_app.logger.info("주말 접근 시도")
            return False

        # 시간 체크
        current_hour = now.hour
        if (current_hour < business_hours["start"]
                or current_hour >= business_hours["end"]):
            current_app.logger.info(f"업무시간 외 접근 시도: {current_hour}시")
            return False

        return True

    def _is_ip_in_allowed_ranges(self, client_ip: str) -> bool:
        """허용된 IP 대역 체크"""
        if not IP_AUTH_CONFIG.get("enable_range_check", False):
            return True

        try:
            client_ip_obj = ipaddress.IPv4Address(client_ip)

            for ip_range in ALLOWED_IP_RANGES:
                network = ipaddress.IPv4Network(ip_range, strict=False)
                if client_ip_obj in network:
                    current_app.logger.info(f"IP 대역 매칭: {client_ip} in {ip_range}")
                    return True

            current_app.logger.warning(f"허용되지 않은 IP 대역: {client_ip}")
            return False

        except ipaddress.AddressValueError:
            current_app.logger.warning(f"잘못된 IP 주소 형식: {client_ip}")
            return False

    def _find_user_by_ip(self, client_ip: str) -> dict:
        """IP로 사용자 찾기"""
        for username, user_data in TEST_USERS.items():
            allowed_ips = user_data.get("allowed_ips", [])

            if client_ip in allowed_ips:
                current_app.logger.info(f"사용자 매칭: {username} <- {client_ip}")
                return {
                    "username": username,
                    "email": user_data["email"],
                    "name": user_data["name"],
                    "dept": user_data["dept"],
                    "role": user_data.get("role", "user"),
                }

        current_app.logger.warning(f"매칭되지 않은 IP: {client_ip}")
        return None

    # 기존 이메일 인증 관련 메서드들은 그대로 유지
    def send_verification_code(self, email: str) -> dict:
        """이메일 인증 코드 발송 (기존 유지)"""
        if not email:
            return {"success": False, "message": "이메일 주소가 필요합니다."}

        verification_code = DEFAULT_VERIFICATION_CODE
        expiry = datetime.now() + timedelta(minutes=15)
        self.verification_codes[email] = {"code": verification_code, "expiry": expiry}

        print(f"[이메일 인증] 인증 코드: {verification_code} (수신자: {email})")
        return {"success": True, "message": "인증 코드가 발송되었습니다."}

    def verify_code(self, email: str, code: str) -> bool:
        """인증 코드 확인 (기존 유지)"""
        is_valid_code = code == DEFAULT_VERIFICATION_CODE

        if email in self.verification_codes:
            verification_info = self.verification_codes[email]
            is_valid_code = is_valid_code or (verification_info["code"] == code
                                              and datetime.now()
                                              <= verification_info["expiry"])

        return is_valid_code

    def generate_token(self, username: str, user_info: dict, client_ip: str) -> str:
        """JWT 토큰 생성 (IP 정보 포함)"""
        token_payload = {
            "username": username,
            "name": user_info.get("name"),
            "dept": user_info.get("dept"),
            "role": user_info.get("role", "user"),
            "client_ip": client_ip,  # IP 정보 추가
            "exp": datetime.now() +
            timedelta(seconds=current_app.config["TOKEN_EXPIRATION"]),
        }

        return jwt.encode(token_payload, current_app.config["JWT_SECRET"],
                          algorithm="HS256")

    def verify_token(self, token: str, client_ip: str = None) -> dict:
        """JWT 토큰 검증 (IP 검증 포함)"""
        try:
            payload = jwt.decode(token, current_app.config["JWT_SECRET"],
                                 algorithms=["HS256"])

            # IP 검증 (옵션 - 경고만 기록)
            if client_ip and payload.get("client_ip"):
                if payload["client_ip"] != client_ip:
                    current_app.logger.warning(
                        f"토큰 IP 불일치: 토큰={payload['client_ip']}, 현재={client_ip}")
                    # DHCP 환경을 고려해 경고만 기록하고 통과

            return {"valid": True, "payload": payload}

        except jwt.ExpiredSignatureError:
            return {"valid": False, "error": "토큰이 만료되었습니다."}
        except jwt.InvalidTokenError:
            return {"valid": False, "error": "유효하지 않은 토큰입니다."}

    def clear_verification_code(self, email: str):
        """인증 코드 삭제 (기존 유지)"""
        if email in self.verification_codes:
            del self.verification_codes[email]

    def get_client_ip(self, request) -> str:
        """클라이언트 IP 주소 추출 (프록시 환경 고려)"""
        # X-Forwarded-For 헤더 확인 (프록시/로드밸런서 환경)
        if request.headers.get("X-Forwarded-For"):
            ip = request.headers.get("X-Forwarded-For").split(",")[0].strip()
            current_app.logger.info(f"X-Forwarded-For에서 IP 추출: {ip}")
            return ip
        elif request.headers.get("X-Real-IP"):
            ip = request.headers.get("X-Real-IP")
            current_app.logger.info(f"X-Real-IP에서 IP 추출: {ip}")
            return ip
        else:
            ip = request.remote_addr
            current_app.logger.info(f"Remote-Addr에서 IP 추출: {ip}")
            return ip

    # 기존 데이터베이스 관련 메서드들 유지
    def authenticate_user_in_db(self, username: str) -> dict:
        """데이터베이스에서 사용자 검증 및 감사 로그 초기화 (기존 유지)"""
        try:
            user = execute_query("SELECT uid FROM users WHERE username = %s",
                                 (username, ), fetch_one=True)

            if not user:
                return {
                    "success": False,
                    "message": "사용자 검증에 실패했습니다. 운영실에 문의해주세요.",
                }

            user_id = user["uid"]

            existing_logs = execute_query(
                """
                SELECT COUNT(*) as log_count
                FROM audit_log
                WHERE user_id = %s AND DATE(checked_at) = DATE(NOW())
                """,
                (user_id, ),
                fetch_one=True,
            )["log_count"]

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
        """초기 감사 로그 생성 (기존 유지)"""
        checklist_items = execute_query(
            """
            SELECT item_id, item_name, category, description
            FROM checklist_items
            ORDER BY item_id
            """,
            fetch_all=True,
        )

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
                """,
                (user_id, item["item_id"], default_actual_value),
            )