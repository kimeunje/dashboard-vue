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

    stats = audit_service.get_user_stats(username)
    return jsonify(stats)


@audit_bp.route('/logs', methods=['GET'])
@token_required
@handle_exceptions
def get_audit_logs():
    """사용자별 보안 감사 로그 목록 조회"""
    user = request.current_user
    username = user["username"]

    logs = audit_service.get_user_logs(username)
    return jsonify(logs)


@audit_bp.route('/checklist-items', methods=['GET'])
@handle_exceptions
def get_checklist_items():
    """체크리스트 항목 조회"""
    items = audit_service.get_checklist_items()
    return jsonify(items)


# 기존 mock_app.py의 validate_check 엔드포인트를 이동
@audit_bp.route('/validate_check', methods=['POST'])
@handle_exceptions
def validate_check():
    """항목 검증 API"""
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