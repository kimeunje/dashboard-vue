# app/controllers/training_controller.py
from datetime import datetime
from flask import Blueprint, request, jsonify
from app.services.training_service import TrainingService
from app.utils.decorators import token_required, handle_exceptions
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