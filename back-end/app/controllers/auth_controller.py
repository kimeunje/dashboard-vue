# back-end/app/controllers/auth_controller.py - IP 인증으로 수정

from flask import Blueprint, request, jsonify, current_app
from app.services.auth_service import AuthService
from app.utils.decorators import token_required, validate_json, handle_exceptions
from app.utils.constants import HTTP_STATUS, MESSAGES

auth_bp = Blueprint('auth', __name__)
auth_service = AuthService()


@auth_bp.route('/check-ip', methods=['POST'])
@handle_exceptions
def check_ip_authentication():
    """IP 기반 인증 확인 (기존 check-credentials 대체)"""
    # 클라이언트 IP 추출
    client_ip = auth_service.get_client_ip(request)
    current_app.logger.info(f"IP 인증 요청: {client_ip}")

    # IP 기반 인증
    result = auth_service.authenticate_by_ip(client_ip)
    print(result)
    if result["success"]:
        return jsonify({
            "success": True,
            "email": result["email"],
            "username": result["username"],
            "name": result["name"],
            "dept": result["dept"],
            "role": result.get("role", "user"),
            "client_ip": client_ip
        })
    else:
        # 에러 코드에 따른 HTTP 상태 코드 설정
        if result.get("code") == "OUTSIDE_BUSINESS_HOURS":
            status_code = HTTP_STATUS['FORBIDDEN']
        elif result.get("code") in ["IP_RANGE_NOT_ALLOWED", "USER_NOT_FOUND"]:
            status_code = HTTP_STATUS['UNAUTHORIZED']
        else:
            status_code = HTTP_STATUS['UNAUTHORIZED']

        return jsonify({
            "success": False,
            "message": result["message"],
            "code": result.get("code", "AUTH_FAILED")
        }), status_code


@auth_bp.route('/email-verification', methods=['POST'])
@handle_exceptions
@validate_json(['email'])
def send_verification():
    """이메일 인증 코드 발송 (기존 유지)"""
    data = request.json
    email = data.get("email")

    result = auth_service.send_verification_code(email)

    if result["success"]:
        return jsonify(result)
    else:
        return jsonify(result), HTTP_STATUS['BAD_REQUEST']


@auth_bp.route('/verify-and-login', methods=['POST'])
@handle_exceptions
@validate_json(['email', 'code', 'username'])
def verify_and_login():
    """인증 코드 확인 및 로그인 (IP 기반으로 수정)"""
    data = request.json
    email = data.get("email")
    code = data.get("code")
    username = data.get("username")

    # 클라이언트 IP 추출
    client_ip = auth_service.get_client_ip(request)
    current_app.logger.info(f"최종 로그인 시도: {username} ({client_ip})")

    # 1. 인증 코드 확인
    if not auth_service.verify_code(email, code):
        current_app.logger.warning(f"잘못된 인증 코드: {email}")
        return jsonify({
            "success": False,
            "message": MESSAGES['INVALID_VERIFICATION_CODE'],
        }), HTTP_STATUS['BAD_REQUEST']

    # 2. IP 기반 재인증 (보안 강화)
    auth_result = auth_service.authenticate_by_ip(client_ip)

    if not auth_result["success"]:
        current_app.logger.warning(f"IP 재인증 실패: {client_ip}")
        return jsonify({
            "success": False,
            "message": auth_result["message"]
        }), HTTP_STATUS['UNAUTHORIZED']

    # 3. 사용자명 일치 확인
    if auth_result["username"] != username:
        current_app.logger.warning(
            f"사용자명 불일치: 요청={username}, IP인증={auth_result['username']}")
        return jsonify({
            "success": False,
            "message": "인증 정보가 일치하지 않습니다."
        }), HTTP_STATUS['UNAUTHORIZED']

    # 4. JWT 토큰 생성 (IP 정보 포함)
    token = auth_service.generate_token(username, auth_result, client_ip)

    # 5. 인증 코드 삭제 (사용 완료)
    auth_service.clear_verification_code(email)

    # 6. 성공 로그 기록
    current_app.logger.info(
        f"로그인 성공: {username} ({auth_result['name']}) from {client_ip}")

    # 7. 토큰 반환
    response = jsonify({"success": True, "message": MESSAGES['LOGIN_SUCCESS']})
    response.set_cookie(
        "auth_token",
        token,
        httponly=True,
        max_age=current_app.config['TOKEN_EXPIRATION'],
        samesite="Lax",
        domain=None,
        path="/",
    )

    return response


@auth_bp.route('/me', methods=['GET'])
@token_required
@handle_exceptions
def get_user_info():
    """사용자 정보 조회 (IP 정보 추가)"""
    user = request.current_user

    return jsonify({
        "authenticated": True,
        "username": user["username"],
        "name": user.get("name", "사용자"),
        "dept": user.get("dept", "부서없음"),
        "role": user.get("role", "user"),
        "client_ip": user.get("client_ip")
    })


@auth_bp.route('/logout', methods=['POST'])
@handle_exceptions
def logout():
    """로그아웃 (IP 로그 추가)"""
    client_ip = auth_service.get_client_ip(request)
    current_app.logger.info(f"로그아웃: IP {client_ip}")

    response = jsonify({"success": True, "message": MESSAGES['LOGOUT_SUCCESS']})
    response.delete_cookie("auth_token")
    return response


@auth_bp.route('/authenticate', methods=['POST'])
@handle_exceptions
@validate_json(['username'])
def authenticate():
    """사용자 인증 및 감사 로그 초기화 (기존 유지)"""
    data = request.json
    username = data.get("username")

    result = auth_service.authenticate_user_in_db(username)

    if result["success"]:
        return jsonify({"user_id": result["user_id"]})
    else:
        status_code = HTTP_STATUS['UNAUTHORIZED'] if "검증에 실패" in result[
            "message"] else HTTP_STATUS['INTERNAL_SERVER_ERROR']
        return jsonify({
            "status": "failed",
            "message": result["message"],
            "statusCode": status_code,
        }), status_code


@auth_bp.route('/ip-info', methods=['GET'])
@handle_exceptions
def get_ip_info():
    """현재 클라이언트 IP 정보 조회 (디버깅/테스트용)"""
    client_ip = auth_service.get_client_ip(request)

    return jsonify({
        "client_ip": client_ip,
        "headers": {
            "X-Forwarded-For": request.headers.get('X-Forwarded-For'),
            "X-Real-IP": request.headers.get('X-Real-IP'),
            "Remote-Addr": request.remote_addr,
            "User-Agent": request.headers.get('User-Agent')
        },
        "message": "현재 클라이언트 IP 정보입니다."
    })


# 기존 LDAP 인증 엔드포인트는 호환성을 위해 잠시 유지 (향후 제거 예정)
@auth_bp.route('/check-credentials', methods=['POST'])
@handle_exceptions
def check_credentials_deprecated():
    """기존 LDAP 인증 (사용 중단 예정 - IP 인증으로 대체됨)"""
    current_app.logger.warning("Deprecated endpoint accessed: /check-credentials")

    return jsonify({
        "success": False,
        "message": "이 인증 방식은 더 이상 사용되지 않습니다. IP 기반 인증을 사용하세요.",
        "deprecated": True
    }), HTTP_STATUS['BAD_REQUEST']