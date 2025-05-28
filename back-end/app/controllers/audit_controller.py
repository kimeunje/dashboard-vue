# app/controllers/audit_controller.py
import os
import io
import logging
from datetime import datetime
from flask import Blueprint, request, jsonify, send_file, current_app
from app.services.audit_service import AuditService
from app.utils.decorators import token_required, validate_json, handle_exceptions
from app.utils.constants import HTTP_STATUS

audit_bp = Blueprint('audit', __name__)
audit_service = AuditService()


@audit_bp.route('/stats', methods=['GET'])
@token_required
@handle_exceptions
def get_security_stats():
    """사용자별 보안 통계 데이터 조회"""
    user = request.current_user
    username = user["username"]
    
    # 점검 유형 파라미터 (daily, manual, 또는 전체)
    check_type = request.args.get('type', None)
    
    stats = audit_service.get_user_stats(username, check_type)
    return jsonify(stats)


@audit_bp.route('/logs', methods=['GET'])
@token_required
@handle_exceptions
def get_audit_logs():
    """사용자별 보안 감사 로그 목록 조회"""
    user = request.current_user
    username = user["username"]
    
    # 점검 유형 파라미터 (daily, manual, 또는 전체)
    check_type = request.args.get('type', None)

    logs = audit_service.get_user_logs(username, check_type)
    return jsonify(logs)


@audit_bp.route('/checklist-items', methods=['GET'])
@handle_exceptions
def get_checklist_items():
    """체크리스트 항목 조회"""
    # 점검 유형 파라미터 (daily, manual, 또는 전체)
    check_type = request.args.get('type', None)
    
    items = audit_service.get_checklist_items(check_type)
    return jsonify(items)


@audit_bp.route('/manual-check-items', methods=['GET'])
@token_required
@handle_exceptions
def get_manual_check_items():
    """수시 점검 가능한 항목 목록 조회"""
    items = audit_service.get_manual_check_items()
    return jsonify(items)


@audit_bp.route('/manual-check', methods=['POST'])
@token_required
@validate_json
@handle_exceptions
def execute_manual_check():
    """수시 점검 실행"""
    user = request.current_user
    data = request.json

    # 필수 필드 검증
    required_fields = ["item_id", "actual_value", "passed"]
    missing_fields = [field for field in required_fields if field not in data]

    if missing_fields:
        return jsonify({
            "error": f"필수 필드가 누락되었습니다: {', '.join(missing_fields)}"
        }), HTTP_STATUS['BAD_REQUEST']

    try:
        # 사용자 ID 가져오기
        from app.utils.database import execute_query
        user_info = execute_query("SELECT uid FROM users WHERE user_id = %s", 
                                (user["username"],), fetch_one=True)
        
        if not user_info:
            return jsonify({"error": "사용자 정보를 찾을 수 없습니다."}), HTTP_STATUS['BAD_REQUEST']

        user_id = user_info["uid"]
        
        # 수시 점검 실행
        check_result = {
            "actual_value": data["actual_value"],
            "passed": data["passed"],
            "notes": data.get("notes", "")
        }
        
        result = audit_service.execute_manual_check(user_id, data["item_id"], check_result)
        return jsonify(result), HTTP_STATUS['OK']

    except ValueError as e:
        current_app.logger.error(f"수시 점검 오류: {str(e)}")
        return jsonify({"error": str(e)}), HTTP_STATUS['BAD_REQUEST']
    except Exception as e:
        current_app.logger.error(f"서버 오류: {str(e)}")
        return jsonify({
            "status": "failed",
            "message": "서버 오류가 발생했습니다.",
            "details": str(e) if current_app.debug else None
        }), HTTP_STATUS['INTERNAL_SERVER_ERROR']


@audit_bp.route('/dashboard-stats', methods=['GET'])
@token_required
@handle_exceptions
def get_dashboard_stats():
    """대시보드용 통합 통계 데이터 조회"""
    user = request.current_user
    username = user["username"]

    try:
        # 정기 점검 통계
        daily_stats = audit_service.get_user_stats(username, 'daily')
        
        # 수시 점검 통계
        manual_stats = audit_service.get_user_stats(username, 'manual')
        
        # 전체 통계
        total_stats = audit_service.get_user_stats(username)

        return jsonify({
            "daily": daily_stats,
            "manual": manual_stats,
            "total": total_stats
        }), HTTP_STATUS['OK']

    except Exception as e:
        current_app.logger.error(f"대시보드 통계 조회 오류: {str(e)}")
        return jsonify({
            "error": "통계 데이터를 불러오는 중 오류가 발생했습니다."
        }), HTTP_STATUS['INTERNAL_SERVER_ERROR']


# 기존 validate_check 엔드포인트 (정기 점검용)
@audit_bp.route('/validate_check', methods=['POST'])
@handle_exceptions
def validate_check():
    """항목 검증 API (정기 점검용)"""
    data = request.json

    if not data:
        return jsonify({"error": "요청 데이터가 필요합니다."}), HTTP_STATUS['BAD_REQUEST']

    try:
        result = audit_service.validate_check(data)
        return jsonify(result)
    except ValueError as e:
        current_app.logger.error(f"검증 오류: {str(e)}")
        return jsonify({"error": str(e)}), HTTP_STATUS['BAD_REQUEST']
    except Exception as e:
        current_app.logger.error(f"서버 오류: {str(e)}")
        return jsonify({
            "status": "failed",
            "message": "서버 오류가 발생했습니다.",
            "details": str(e) if current_app.debug else None
        }), HTTP_STATUS['INTERNAL_SERVER_ERROR']


# 로그 수신 엔드포인트 (기존 mock_app.py에서 이동)
@audit_bp.route('/log', methods=['POST'])
@handle_exceptions
def receive_log():
    """클라이언트 로그 수신"""
    try:
        data = request.get_json()
        client_ip = request.remote_addr

        # 필수 필드 검증
        required_fields = ["timestamp", "level", "message"]
        if not all(field in data for field in required_fields):
            return jsonify({"error": "필수 필드가 누락되었습니다"}), HTTP_STATUS['BAD_REQUEST']

        # 로그 저장
        log_dir = current_app.config['LOG_DIR']
        os.makedirs(log_dir, exist_ok=True)

        log_file = f"{log_dir}/{datetime.now().strftime('%Y-%m-%d')}.log"
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(
                f"[{data['timestamp']}] [{client_ip}] [{data['level']}] {data['message']}\n"
            )

        # 로그 레벨에 따른 처리
        if data["level"] == "FAIL":
            logging.error(data["message"])
        elif data["level"] == "PASS":
            logging.info(data["message"])
        else:
            logging.info(data["message"])

        return jsonify({"status": "연결 성공"}), HTTP_STATUS['OK']

    except Exception as e:
        logging.error(f"로그 처리 오류: {str(e)}")
        return jsonify({"error": "로그 처리 중 오류 발생"}), HTTP_STATUS['INTERNAL_SERVER_ERROR']


# 수시 점검 실행 결과 조회 (추가 기능)
@audit_bp.route('/manual-check-history/<int:item_id>', methods=['GET'])
@token_required
@handle_exceptions
def get_manual_check_history(item_id):
    """특정 수시 점검 항목의 실행 이력 조회"""
    user = request.current_user
    username = user["username"]
    
    try:
        from app.utils.database import execute_query
        
        # 사용자 ID 가져오기
        user_info = execute_query("SELECT uid FROM users WHERE user_id = %s", 
                                (username,), fetch_one=True)
        
        if not user_info:
            return jsonify({"error": "사용자 정보를 찾을 수 없습니다."}), HTTP_STATUS['BAD_REQUEST']

        user_id = user_info["uid"]
        
        # 특정 항목의 수시 점검 이력 조회
        history = execute_query(
            """
            SELECT al.log_id, al.actual_value, al.passed, al.notes, al.checked_at,
                   ci.item_name, ci.category
            FROM audit_log al
            LEFT JOIN checklist_items ci ON al.item_id = ci.item_id
            WHERE al.user_id = %s AND al.item_id = %s AND ci.check_type = 'manual'
            ORDER BY al.checked_at DESC
            LIMIT 10
            """, (user_id, item_id), fetch_all=True)

        # 결과 포맷팅
        result = []
        for record in history:
            # JSON 파싱
            if isinstance(record["actual_value"], str):
                actual_value = json.loads(record["actual_value"])
            else:
                actual_value = record["actual_value"]

            # 날짜 포맷팅
            if isinstance(record["checked_at"], datetime):
                checked_at = record["checked_at"].strftime("%Y-%m-%d %H:%M:%S")
            else:
                checked_at = record["checked_at"]

            result.append({
                "log_id": record["log_id"],
                "item_name": record["item_name"],
                "category": record["category"],
                "actual_value": actual_value,
                "passed": record["passed"],
                "notes": record["notes"],
                "checked_at": checked_at
            })

        return jsonify(result), HTTP_STATUS['OK']

    except Exception as e:
        current_app.logger.error(f"수시 점검 이력 조회 오류: {str(e)}")
        return jsonify({
            "error": "이력 조회 중 오류가 발생했습니다."
        }), HTTP_STATUS['INTERNAL_SERVER_ERROR']