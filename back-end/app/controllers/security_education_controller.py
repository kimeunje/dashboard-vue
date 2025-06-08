# app/controllers/education_controller.py
from datetime import datetime
from flask import Blueprint, request, jsonify
from app.services.security_education_service import EducationService
from app.utils.decorators import token_required, handle_exceptions
from app.utils.constants import HTTP_STATUS

education_bp = Blueprint('education', __name__)
education_service = EducationService()


@education_bp.route('/status', methods=['GET'])
@token_required
@handle_exceptions
def get_education_status():
    """사용자의 정보보호 교육 현황 조회"""
    user = request.current_user
    username = user["username"]

    year = request.args.get('year', datetime.now().year, type=int)

    try:
        result = education_service.get_education_status(username, year)
        return jsonify(result)
    except ValueError as e:
        return jsonify({"message": str(e)}), HTTP_STATUS['NOT_FOUND']