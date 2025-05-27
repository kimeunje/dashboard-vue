# app/controllers/training_controller.py
from datetime import datetime
from flask import Blueprint, request, jsonify, make_response
from app.services.training_service import TrainingService
from app.utils.decorators import token_required, admin_required, handle_exceptions
from app.utils.constants import HTTP_STATUS

training_bp = Blueprint('training', __name__)
training_service = TrainingService()


@training_bp.route('/status', methods=['GET'])
@token_required
@handle_exceptions
def get_phishing_training_status():
    """사용자의 악성메일 모의훈련 현황 조회"""
    user = request.current_user
    username = user["username"]

    year = request.args.get('year', datetime.now().year, type=int)

    try:
        result = training_service.get_training_status(username, year)
        return jsonify(result)
    except ValueError as e:
        return jsonify({"message": str(e)}), HTTP_STATUS['NOT_FOUND']


@training_bp.route('/template/download', methods=['GET'])
@admin_required
@handle_exceptions
def download_training_template():
    """모의훈련 업로드 템플릿 다운로드"""
    template_csv = training_service.get_training_excel_template()
    
    response = make_response(template_csv)
    response.headers['Content-Type'] = 'text/csv; charset=utf-8'
    response.headers['Content-Disposition'] = 'attachment; filename=모의훈련_업로드_템플릿.csv'
    
    return response


@training_bp.route('/records', methods=['GET'])
@admin_required
@handle_exceptions
def get_all_training_records():
    """모든 모의훈련 기록 조회 (관리자용)"""
    year = request.args.get('year', datetime.now().year, type=int)
    period = request.args.get('period', None)
    result = request.args.get('result', None)
    
    records = training_service.get_all_training_records(year, period, result)
    return jsonify(records)


@training_bp.route('/update', methods=['POST'])
@admin_required
@handle_exceptions
def update_training_record():
    """단일 모의훈련 기록 수정"""
    data = request.json
    
    try:
        success = training_service.update_training_record(data)
        if success:
            return jsonify({"message": "모의훈련 기록이 수정되었습니다."})
        else:
            return jsonify({"error": "수정에 실패했습니다."}), HTTP_STATUS['BAD_REQUEST']
    except ValueError as e:
        return jsonify({"error": str(e)}), HTTP_STATUS['BAD_REQUEST']


@training_bp.route('/delete', methods=['DELETE'])
@admin_required
@handle_exceptions
def delete_training_record():
    """모의훈련 기록 삭제"""
    data = request.json
    
    try:
        success = training_service.delete_training_record(
            data['user_id'], 
            data['training_year'], 
            data['training_period']
        )
        if success:
            return jsonify({"message": "모의훈련 기록이 삭제되었습니다."})
        else:
            return jsonify({"error": "삭제할 기록을 찾을 수 없습니다."}), HTTP_STATUS['NOT_FOUND']
    except ValueError as e:
        return jsonify({"error": str(e)}), HTTP_STATUS['BAD_REQUEST']