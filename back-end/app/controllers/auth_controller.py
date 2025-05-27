# app/controllers/auth_controller.py
from flask import Blueprint, request, jsonify, current_app
from app.services.auth_service import AuthService
from app.utils.decorators import token_required, validate_json, handle_exceptions
from app.utils.constants import HTTP_STATUS, MESSAGES

auth_bp = Blueprint('auth', __name__)
auth_service = AuthService()


@auth_bp.route('/check-credentials', methods=['POST'])
@handle_exceptions
@validate_json(['username', 'password'])
def check_credentials():
    """자격증명 확인"""
    data = request.json
    username = data.get("username")
    password = data.get("password")

    # 모의 LDAP 인증
    result = auth_service.authenticate_ldap(username, password)

    if result["success"]:
        return jsonify({"success": True, "email": result["email"]})
    else:
        return jsonify(result), HTTP_STATUS['UNAUTHORIZED']


@auth_bp.route('/email-verification', methods=['POST'])
@handle_exceptions
@validate_json(['email'])
def send_verification():
    """이메일 인증 코드 발송"""
    data = request.json
    email = data.get("email")

    result = auth_service.send_verification_code(email)

    if result["success"]:
        return jsonify(result)
    else:
        return jsonify(result), HTTP_STATUS['BAD_REQUEST']


@auth_bp.route('/verify-and-login', methods=['POST'])
@handle_exceptions
@validate_json(['email', 'code', 'username', 'password'])
def verify_and_login():
    """인증 코드 확인 및 로그인"""
    data = request.json
    email = data.get("email")
    code = data.get("code")
    username = data.get("username")
    password = data.get("password")

    # 인증 코드 확인
    if not auth_service.verify_code(email, code):
        return jsonify({
            "success": False,
            "message": MESSAGES['INVALID_VERIFICATION_CODE'],
        }), HTTP_STATUS['BAD_REQUEST']

    # 다시 LDAP 인증 (보안 강화)
    result = auth_service.authenticate_ldap(username, password)

    if not result["success"]:
        return jsonify(result), HTTP_STATUS['UNAUTHORIZED']

    # JWT 토큰 생성
    token = auth_service.generate_token(username, result)

    # 인증 코드 삭제 (사용 완료)
    auth_service.clear_verification_code(email)

    # 토큰 반환
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
    """사용자 정보 조회"""
    user = request.current_user

    return jsonify({
        "authenticated": True,
        "username": user["username"],
        "name": user.get("name", "사용자"),
        "dept": user.get("dept", "부서없음"),
    })


@auth_bp.route('/logout', methods=['POST'])
@handle_exceptions
def logout():
    """로그아웃"""
    response = jsonify({"success": True, "message": MESSAGES['LOGOUT_SUCCESS']})
    response.delete_cookie("auth_token")
    return response


@auth_bp.route('/authenticate', methods=['POST'])
@handle_exceptions
@validate_json(['username'])
def authenticate():
    """사용자 인증 및 감사 로그 초기화"""
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