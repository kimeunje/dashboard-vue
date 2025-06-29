# app/controllers/admin_user_controller.py
"""
관리자 사용자 CRUD API 컨트롤러
- 사용자 생성, 조회, 수정, 삭제
- 사용자 계정 관리
- 사용자 권한 관리
"""

from flask import Blueprint, request, jsonify
from datetime import datetime
from app.utils.decorators import token_required, handle_exceptions, admin_required
from app.utils.constants import HTTP_STATUS
from app.utils.database import execute_query, DatabaseManager
import logging
import re

# 블루프린트 생성
admin_user_bp = Blueprint(
    "admin_user", __name__, url_prefix="/api/admin"
)


@admin_user_bp.route("/users", methods=["POST"])
@token_required
@admin_required
@handle_exceptions
def create_user():
    """새 사용자 생성"""
    # JSON 요청 검증
    if not request.is_json:
        return jsonify({
            "success": False,
            "message": "Content-Type은 application/json이어야 합니다."
        }), HTTP_STATUS["BAD_REQUEST"]
    
    data = request.json
    if not data:
        return jsonify({
            "success": False,
            "message": "요청 본문이 필요합니다."
        }), HTTP_STATUS["BAD_REQUEST"]
    
    try:
        logging.info(f"새 사용자 생성 요청: {data.get('name', 'Unknown')}")
        
        # 필수 필드 검증 (실제 DB 스키마에 맞춤)
        required_fields = ["name", "uid", "email", "department"]
        missing_fields = [field for field in required_fields if not data.get(field, "").strip()]
        
        if missing_fields:
            return jsonify({
                "success": False,
                "message": f"필수 필드가 누락되었습니다: {', '.join(missing_fields)}"
            }), HTTP_STATUS["BAD_REQUEST"]
        
        # 데이터 검증
        validation_result = _validate_user_data(data)
        if not validation_result["valid"]:
            return jsonify({
                "success": False,
                "message": validation_result["message"]
            }), HTTP_STATUS["BAD_REQUEST"]
        
        # 중복 검사
        duplicate_check = _check_duplicates(data["uid"], data["email"])
        if not duplicate_check["valid"]:
            return jsonify({
                "success": False,
                "message": duplicate_check["message"]
            }), HTTP_STATUS["CONFLICT"]
        
        # 사용자 생성
        user_id = _create_user_record(data)
        
        # 생성된 사용자 정보 조회
        created_user = _get_user_by_id(user_id)
        
        logging.info(f"사용자 생성 완료: {data['name']} (ID: {user_id})")
        
        return jsonify({
            "success": True,
            "message": f"사용자 '{data['name']}'가 성공적으로 생성되었습니다.",
            "user": created_user
        }), HTTP_STATUS["CREATED"]
        
    except Exception as e:
        logging.error(f"사용자 생성 실패: {str(e)}")
        return jsonify({
            "success": False,
            "message": "사용자 생성 중 오류가 발생했습니다.",
            "details": str(e)
        }), HTTP_STATUS["INTERNAL_SERVER_ERROR"]


@admin_user_bp.route("/users/<int:user_id>", methods=["GET"])
@token_required
@admin_required
@handle_exceptions
def get_user(user_id):
    """특정 사용자 정보 조회"""
    try:
        user = _get_user_by_id(user_id)
        
        if not user:
            return jsonify({
                "success": False,
                "message": "사용자를 찾을 수 없습니다."
            }), HTTP_STATUS["NOT_FOUND"]
        
        return jsonify({
            "success": True,
            "user": user
        })
        
    except Exception as e:
        logging.error(f"사용자 조회 실패: {str(e)}")
        return jsonify({
            "success": False,
            "message": "사용자 조회 중 오류가 발생했습니다.",
            "details": str(e)
        }), HTTP_STATUS["INTERNAL_SERVER_ERROR"]


@admin_user_bp.route("/users/<int:user_id>", methods=["PUT"])
@token_required
@admin_required
@handle_exceptions
def update_user(user_id):
    """사용자 정보 수정"""
    # JSON 요청 검증
    if not request.is_json:
        return jsonify({
            "success": False,
            "message": "Content-Type은 application/json이어야 합니다."
        }), HTTP_STATUS["BAD_REQUEST"]
    
    data = request.json
    if not data:
        return jsonify({
            "success": False,
            "message": "요청 본문이 필요합니다."
        }), HTTP_STATUS["BAD_REQUEST"]
    
    try:
        # 사용자 존재 확인
        existing_user = _get_user_by_id(user_id)
        if not existing_user:
            return jsonify({
                "success": False,
                "message": "사용자를 찾을 수 없습니다."
            }), HTTP_STATUS["NOT_FOUND"]
        
        # 데이터 검증 (수정 시에는 선택적 검증)
        if any(field in data for field in ["uid", "email"]):
            validation_result = _validate_user_data(data, is_update=True)
            if not validation_result["valid"]:
                return jsonify({
                    "success": False,
                    "message": validation_result["message"]
                }), HTTP_STATUS["BAD_REQUEST"]
        
        # 중복 검사 (수정하려는 필드가 있을 경우)
        if "uid" in data or "email" in data:
            duplicate_check = _check_duplicates(
                data.get("uid", existing_user["user_id"]), 
                data.get("email", existing_user["email"]),
                exclude_user_id=user_id
            )
            if not duplicate_check["valid"]:
                return jsonify({
                    "success": False,
                    "message": duplicate_check["message"]
                }), HTTP_STATUS["CONFLICT"]
        
        # 사용자 정보 업데이트
        _update_user_record(user_id, data)
        
        # 업데이트된 사용자 정보 조회
        updated_user = _get_user_by_id(user_id)
        
        logging.info(f"사용자 수정 완료: {updated_user['name']} (ID: {user_id})")
        
        return jsonify({
            "success": True,
            "message": f"사용자 '{updated_user['name']}'의 정보가 성공적으로 수정되었습니다.",
            "user": updated_user
        })
        
    except Exception as e:
        logging.error(f"사용자 수정 실패: {str(e)}")
        return jsonify({
            "success": False,
            "message": "사용자 수정 중 오류가 발생했습니다.",
            "details": str(e)
        }), HTTP_STATUS["INTERNAL_SERVER_ERROR"]


@admin_user_bp.route("/users/<int:user_id>", methods=["DELETE"])
@token_required
@admin_required
@handle_exceptions
def delete_user(user_id):
    """사용자 삭제 (실제 삭제)"""
    try:
        # 사용자 존재 확인
        existing_user = _get_user_by_id(user_id)
        if not existing_user:
            return jsonify({
                "success": False,
                "message": "사용자를 찾을 수 없습니다."
            }), HTTP_STATUS["NOT_FOUND"]
        
        # 자기 자신 삭제 방지
        current_user = request.current_user
        if existing_user["user_id"] == current_user["username"]:
            return jsonify({
                "success": False,
                "message": "자기 자신의 계정은 삭제할 수 없습니다."
            }), HTTP_STATUS["FORBIDDEN"]
        
        # 사용자 삭제 (실제 삭제)
        _delete_user(user_id)
        
        logging.info(f"사용자 삭제 완료: {existing_user['name']} (ID: {user_id})")
        
        return jsonify({
            "success": True,
            "message": f"사용자 '{existing_user['name']}'가 성공적으로 삭제되었습니다."
        })
        
    except Exception as e:
        logging.error(f"사용자 삭제 실패: {str(e)}")
        return jsonify({
            "success": False,
            "message": "사용자 삭제 중 오류가 발생했습니다.",
            "details": str(e)
        }), HTTP_STATUS["INTERNAL_SERVER_ERROR"]


# === 헬퍼 함수들 ===

def _validate_user_data(data, is_update=False):
    """사용자 데이터 유효성 검증 (실제 DB 스키마에 맞춤)"""
    try:
        # 이름 검증
        if "name" in data and not data["name"].strip():
            return {"valid": False, "message": "이름은 필수입니다."}
        
        # 사번 검증
        if "uid" in data:
            uid = data["uid"].strip()
            if not uid:
                return {"valid": False, "message": "사번은 필수입니다."}
            if not re.match(r'^[A-Za-z0-9]+$', uid):
                return {"valid": False, "message": "사번은 영문자와 숫자만 사용할 수 있습니다."}
            if len(uid) < 3 or len(uid) > 20:
                return {"valid": False, "message": "사번은 3자 이상 20자 이하여야 합니다."}
        
        # 이메일 검증
        if "email" in data:
            email = data["email"].strip()
            if not email:
                return {"valid": False, "message": "이메일은 필수입니다."}
            if not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', email):
                return {"valid": False, "message": "올바른 이메일 형식을 입력해주세요."}
        
        # 부서 검증
        if "department" in data and not data["department"].strip():
            return {"valid": False, "message": "부서는 필수입니다."}
        
        # 역할 검증
        if "role" in data and data["role"] not in ["user", "admin"]:
            return {"valid": False, "message": "역할은 'user' 또는 'admin'이어야 합니다."}
        
        return {"valid": True}
        
    except Exception as e:
        logging.error(f"데이터 검증 오류: {str(e)}")
        return {"valid": False, "message": "데이터 검증 중 오류가 발생했습니다."}


def _check_duplicates(uid, email, exclude_user_id=None):
    """중복 검사 (실제 DB 스키마에 맞춤)"""
    try:
        # 사번 중복 검사
        uid_query = "SELECT uid FROM users WHERE user_id = %s"
        uid_params = [uid]
        
        if exclude_user_id:
            uid_query += " AND uid != %s"
            uid_params.append(exclude_user_id)
        
        existing_uid = execute_query(uid_query, uid_params, fetch_one=True)
        if existing_uid:
            return {"valid": False, "message": f"사번 '{uid}'는 이미 사용 중입니다."}
        
        # 이메일 중복 검사
        email_query = "SELECT uid FROM users WHERE mail = %s"
        email_params = [email]
        
        if exclude_user_id:
            email_query += " AND uid != %s"
            email_params.append(exclude_user_id)
        
        existing_email = execute_query(email_query, email_params, fetch_one=True)
        if existing_email:
            return {"valid": False, "message": f"이메일 '{email}'는 이미 사용 중입니다."}
        
        return {"valid": True}
        
    except Exception as e:
        logging.error(f"중복 검사 오류: {str(e)}")
        return {"valid": False, "message": "중복 검사 중 오류가 발생했습니다."}


def _create_user_record(data):
    """사용자 레코드 생성 (실제 DB 스키마에 맞춤)"""
    try:
        insert_query = """
            INSERT INTO users (
                user_id, username, mail, department, role,
                created_at, updated_at
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s
            )
        """
        
        current_time = datetime.now()
        
        params = (
            data["uid"].strip(),          # user_id (사번)
            data["name"].strip(),         # username (실명)
            data["email"].strip(),        # mail (이메일)
            data["department"].strip(),   # department (부서)
            data.get("role", "user"),     # role (역할)
            current_time,                 # created_at
            current_time                  # updated_at
        )
        
        # execute_query는 INSERT 후 affected_rows를 반환하므로 다른 방법 사용
        with DatabaseManager.get_db_cursor() as cursor:
            cursor.execute(insert_query, params)
            user_id = cursor.lastrowid  # 새로 생성된 ID 가져오기
            return user_id
        
    except Exception as e:
        logging.error(f"사용자 레코드 생성 오류: {str(e)}")
        raise


def _get_user_by_id(user_id, include_inactive=False):
    """ID로 사용자 정보 조회 (실제 DB 스키마에 맞춤)"""
    try:
        query = """
            SELECT 
                uid,
                user_id,
                username as name,
                mail as email,
                department,
                role,
                created_at,
                updated_at
            FROM users 
            WHERE uid = %s
        """
        
        user = execute_query(query, (user_id,), fetch_one=True)
        
        if user:
            # datetime 객체를 문자열로 변환
            if user.get("created_at"):
                user["created_at"] = user["created_at"].isoformat()
            if user.get("updated_at"):
                user["updated_at"] = user["updated_at"].isoformat()
        
        return user
        
    except Exception as e:
        logging.error(f"사용자 조회 오류: {str(e)}")
        return None


def _update_user_record(user_id, data):
    """사용자 레코드 업데이트 (실제 DB 스키마에 맞춤)"""
    try:
        # 업데이트할 필드와 값 준비
        update_fields = []
        params = []
        
        field_mapping = {
            "uid": "user_id",      # 사번
            "name": "username",    # 실명
            "email": "mail",       # 이메일
            "department": "department",
            "role": "role"
        }
        
        for field, db_field in field_mapping.items():
            if field in data:
                value = data[field]
                if field in ["uid", "name", "email", "department"]:
                    value = value.strip() if value else None
                
                update_fields.append(f"{db_field} = %s")
                params.append(value)
        
        if not update_fields:
            return
        
        # updated_at 필드 추가
        update_fields.append("updated_at = %s")
        params.append(datetime.now())
        
        # user_id 파라미터 추가
        params.append(user_id)
        
        update_query = f"""
            UPDATE users 
            SET {', '.join(update_fields)}
            WHERE uid = %s
        """
        
        execute_query(update_query, params)
        
    except Exception as e:
        logging.error(f"사용자 업데이트 오류: {str(e)}")
        raise


def _delete_user(user_id):
    """사용자 실제 삭제 (현재 DB에는 is_active 필드가 없으므로)"""
    try:
        delete_query = """
            DELETE FROM users 
            WHERE uid = %s
        """
        
        execute_query(delete_query, (user_id,))
        
    except Exception as e:
        logging.error(f"사용자 삭제 오류: {str(e)}")
        raise