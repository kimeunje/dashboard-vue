# app/controllers/score_controller.py
from datetime import datetime
from flask import Blueprint, request, jsonify
from app.services.score_service import ScoreService
from app.utils.decorators import token_required, handle_exceptions
from app.utils.constants import HTTP_STATUS

score_bp = Blueprint('score', __name__)
score_service = ScoreService()


@score_bp.route('/summary', methods=['GET'])
@token_required
@handle_exceptions
def get_security_score_summary():
    """사용자의 종합 보안 점수 요약 조회"""
    user = request.current_user
    username = user["username"]

    # 요청 파라미터에서 연도 가져오기 (기본값: 현재 연도)
    year = request.args.get('year', datetime.now().year, type=int)

    try:
        score_data = score_service.get_user_security_score(username, year)
        return jsonify(score_data)
    except ValueError as e:
        return jsonify({"message": str(e)}), HTTP_STATUS['NOT_FOUND']


@score_bp.route('/dashboard/overview', methods=['GET'])
@token_required
@handle_exceptions
def get_security_dashboard_overview():
    """종합 보안 대시보드 데이터 조회"""
    user = request.current_user
    username = user["username"]

    year = request.args.get('year', datetime.now().year, type=int)

    try:
        dashboard_data = score_service.get_dashboard_overview(username, year)
        return jsonify(dashboard_data)
    except ValueError as e:
        return jsonify({"message": str(e)}), HTTP_STATUS['NOT_FOUND']