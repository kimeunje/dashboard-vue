# app/controllers/admin_controller.py
from datetime import datetime
from flask import Blueprint, request, jsonify
from app.services.admin_service import AdminService
from app.utils.decorators import admin_required, validate_json, handle_exceptions
from app.utils.constants import HTTP_STATUS

admin_bp = Blueprint("admin", __name__)
admin_service = AdminService()


@admin_bp.route("/dashboard", methods=["GET"])
@admin_required
@handle_exceptions
def get_admin_dashboard():
    """관리자 대시보드 전체 현황 조회"""
    dashboard_data = admin_service.get_admin_dashboard()
    return jsonify(dashboard_data)


@admin_bp.route("/users", methods=["GET"])
@admin_required
@handle_exceptions
def get_all_users():
    """전체 사용자 목록 조회"""
    users = admin_service.get_all_users()
    return jsonify(users)


@admin_bp.route("/users/<int:user_id>/details", methods=["GET"])
@admin_required
@handle_exceptions
def get_user_details(user_id):
    """특정 사용자의 상세 정보 조회"""
    year = request.args.get("year", datetime.now().year, type=int)

    try:
        result = admin_service.get_user_details(user_id, year)
        return jsonify(result)
    except ValueError as e:
        return jsonify({"error": str(e)}), HTTP_STATUS["NOT_FOUND"]


# 교육 관련 엔드포인트들
@admin_bp.route("/education", methods=["GET"])
@admin_required
@handle_exceptions
def get_all_education_records():
    """모든 교육 기록 조회 (관리자용)"""
    year = request.args.get("year", datetime.now().year, type=int)
    period = request.args.get("period", None)
    status = request.args.get("status", None)

    records = admin_service.get_all_education_records(year, period, status)
    return jsonify(records)


@admin_bp.route("/education/update", methods=["POST"])
@admin_required
@handle_exceptions
def update_education_record():
    """단일 교육 기록 수정"""
    data = request.json

    try:
        success = admin_service.update_education_record(data)
        if success:
            return jsonify({"message": "교육 기록이 수정되었습니다."})
        else:
            return (
                jsonify({"error": "수정에 실패했습니다."}),
                HTTP_STATUS["BAD_REQUEST"],
            )
    except ValueError as e:
        return jsonify({"error": str(e)}), HTTP_STATUS["BAD_REQUEST"]


@admin_bp.route("/education/delete", methods=["DELETE"])
@admin_required
@handle_exceptions
def delete_education_record():
    """교육 기록 삭제"""
    data = request.json

    try:
        success = admin_service.delete_education_record(
            data["user_id"], data["education_year"], data["education_period"]
        )
        if success:
            return jsonify({"message": "교육 기록이 삭제되었습니다."})
        else:
            return (
                jsonify({"error": "삭제할 기록을 찾을 수 없습니다."}),
                HTTP_STATUS["NOT_FOUND"],
            )
    except ValueError as e:
        return jsonify({"error": str(e)}), HTTP_STATUS["BAD_REQUEST"]


@admin_bp.route("/education/bulk-update", methods=["POST"])
@admin_required
@validate_json(["records"])
@handle_exceptions
def bulk_update_education():
    """교육 결과 일괄 등록/수정"""
    data = request.json
    education_records = data.get("records", [])

    try:
        result = admin_service.bulk_update_education(education_records)
        return jsonify(result)
    except ValueError as e:
        return jsonify({"error": str(e)}), HTTP_STATUS["BAD_REQUEST"]


# 모의훈련 관련 엔드포인트들
@admin_bp.route("/training", methods=["GET"])
@admin_required
@handle_exceptions
def get_all_training_records():
    """모든 모의훈련 기록 조회 (관리자용)"""
    year = request.args.get("year", datetime.now().year, type=int)
    period = request.args.get("period", None)
    result = request.args.get("result", None)

    records = admin_service.get_all_training_records(year, period, result)
    return jsonify(records)


@admin_bp.route("/training/update", methods=["POST"])
@admin_required
@handle_exceptions
def update_training_record():
    """단일 모의훈련 기록 수정"""
    data = request.json

    try:
        success = admin_service.update_training_record(data)
        if success:
            return jsonify({"message": "모의훈련 기록이 수정되었습니다."})
        else:
            return (
                jsonify({"error": "수정에 실패했습니다."}),
                HTTP_STATUS["BAD_REQUEST"],
            )
    except ValueError as e:
        return jsonify({"error": str(e)}), HTTP_STATUS["BAD_REQUEST"]


@admin_bp.route("/training/delete", methods=["DELETE"])
@admin_required
@handle_exceptions
def delete_training_record():
    """모의훈련 기록 삭제"""
    data = request.json

    try:
        success = admin_service.delete_training_record(
            data["user_id"], data["training_year"], data["training_period"]
        )
        if success:
            return jsonify({"message": "모의훈련 기록이 삭제되었습니다."})
        else:
            return (
                jsonify({"error": "삭제할 기록을 찾을 수 없습니다."}),
                HTTP_STATUS["NOT_FOUND"],
            )
    except ValueError as e:
        return jsonify({"error": str(e)}), HTTP_STATUS["BAD_REQUEST"]


@admin_bp.route("/training/bulk-update", methods=["POST"])
@admin_required
@validate_json(["records"])
@handle_exceptions
def bulk_update_training():
    """모의훈련 결과 일괄 등록/수정"""
    data = request.json
    training_records = data.get("records", [])

    try:
        result = admin_service.bulk_update_training(training_records)
        return jsonify(result)
    except ValueError as e:
        return jsonify({"error": str(e)}), HTTP_STATUS["BAD_REQUEST"]


# 점수 관련 엔드포인트들
@admin_bp.route("/scores/recalculate", methods=["POST"])
@admin_required
@handle_exceptions
def recalculate_all_scores():
    """전체 사용자 점수 재계산"""
    data = request.json or {}
    year = data.get("year", datetime.now().year)

    result = admin_service.recalculate_all_scores(year)
    return jsonify(result)


@admin_bp.route("/toggle-scoring", methods=["POST"])
@admin_required
@handle_exceptions
def toggle_scoring_exclusion():
    """점수 계산 제외/포함 토글"""
    data = request.json

    try:
        success = admin_service.toggle_scoring_exclusion(
            data["user_id"],
            data["year"],
            data["record_type"],
            data["period"],
            data["exclude"],
        )
        if success:
            return jsonify({"message": "점수 계산 설정이 변경되었습니다."})
        else:
            return (
                jsonify({"error": "설정 변경에 실패했습니다."}),
                HTTP_STATUS["BAD_REQUEST"],
            )
    except ValueError as e:
        return jsonify({"error": str(e)}), HTTP_STATUS["BAD_REQUEST"]


# 통계 관련 엔드포인트들
@admin_bp.route("/training/statistics", methods=["GET"])
@admin_required
@handle_exceptions
def get_training_statistics():
    """모의훈련 통계 조회"""
    year = request.args.get("year", datetime.now().year, type=int)

    try:
        # AdminService에 통계 메서드가 있다면 사용, 없다면 기본 구현
        stats = admin_service.get_training_statistics(year)
        return jsonify(stats)
    except AttributeError:
        # 기본 통계 반환
        basic_stats = {
            "year": year,
            "period_stats": [],
            "department_stats": [],
            "log_type_stats": [],
        }
        return jsonify(basic_stats)
