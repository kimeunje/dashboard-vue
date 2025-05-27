# app/controllers/admin_controller.py
from datetime import datetime
from flask import Blueprint, request, jsonify
from app.services.admin_service import AdminService
from app.utils.decorators import admin_required, validate_json, handle_exceptions
from app.utils.constants import HTTP_STATUS

admin_bp = Blueprint('admin', __name__)
admin_service = AdminService()


@admin_bp.route('/dashboard', methods=['GET'])
@admin_required
@handle_exceptions
def get_admin_dashboard():
    """관리자 대시보드 전체 현황 조회"""
    dashboard_data = admin_service.get_admin_dashboard()
    return jsonify(dashboard_data)


@admin_bp.route('/users', methods=['GET'])
@admin_required
@handle_exceptions
def get_all_users():
    """전체 사용자 목록 조회"""
    users = admin_service.get_all_users()
    return jsonify(users)


@admin_bp.route('/education/bulk-update', methods=['POST'])
@admin_required
@validate_json(['records'])
@handle_exceptions
def bulk_update_education():
    """교육 결과 일괄 등록/수정"""
    data = request.json
    education_records = data.get('records', [])

    try:
        result = admin_service.bulk_update_education(education_records)
        return jsonify(result)
    except ValueError as e:
        return jsonify({"error": str(e)}), HTTP_STATUS['BAD_REQUEST']


@admin_bp.route('/training/bulk-update', methods=['POST'])
@admin_required
@validate_json(['records'])
@handle_exceptions
def bulk_update_training():
    """모의훈련 결과 일괄 등록/수정"""
    data = request.json
    training_records = data.get('records', [])

    try:
        result = admin_service.bulk_update_training(training_records)
        return jsonify(result)
    except ValueError as e:
        return jsonify({"error": str(e)}), HTTP_STATUS['BAD_REQUEST']


@admin_bp.route('/scores/recalculate', methods=['POST'])
@admin_required
@handle_exceptions
def recalculate_all_scores():
    """전체 사용자 점수 재계산"""
    data = request.json or {}
    year = data.get('year', datetime.now().year)

    result = admin_service.recalculate_all_scores(year)
    return jsonify(result)


@admin_bp.route('/users/<int:user_id>/details', methods=['GET'])
@admin_required
@handle_exceptions
def get_user_details(user_id):
    """특정 사용자의 상세 정보 조회"""
    year = request.args.get('year', datetime.now().year, type=int)

    try:
        result = admin_service.get_user_details(user_id, year)
        return jsonify(result)
    except ValueError as e:
        return jsonify({"error": str(e)}), HTTP_STATUS['NOT_FOUND']