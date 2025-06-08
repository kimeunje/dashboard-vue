# app/controllers/training_controller.py - 점수 관련 기능 제거
from datetime import datetime
from flask import Blueprint, request, jsonify, make_response
from app.services.phishing_training_service import TrainingService
from app.utils.decorators import token_required, admin_required, handle_exceptions
from app.utils.constants import HTTP_STATUS
from urllib.parse import quote
from app.utils.database import execute_query, DatabaseManager

training_bp = Blueprint("training", __name__)
training_service = TrainingService()


@training_bp.route("/status", methods=["GET"])
@token_required
@handle_exceptions
def get_phishing_training_status():
    """사용자의 악성메일 모의훈련 현황 조회"""
    user = request.current_user
    username = user["username"]

    year = request.args.get("year", datetime.now().year, type=int)

    try:
        result = training_service.get_training_status(username, year)
        return jsonify(result)
    except ValueError as e:
        return jsonify({"message": str(e)}), HTTP_STATUS["NOT_FOUND"]


@training_bp.route("/template/download", methods=["GET"])
@admin_required
@handle_exceptions
def download_training_template():
    """모의훈련 업로드 템플릿 다운로드"""
    template_csv = training_service.get_training_excel_template()

    response = make_response(template_csv)
    response.headers["Content-Type"] = "text/csv; charset=utf-8"
    response.headers["Content-Disposition"] = (
        "attachment; filename=모의훈련_업로드_템플릿.csv"
    )

    return response


@training_bp.route("/records", methods=["GET"])
@admin_required
@handle_exceptions
def get_all_training_records():
    """모든 모의훈련 기록 조회 (관리자용)"""
    year = request.args.get("year", datetime.now().year, type=int)
    period = request.args.get("period", None)
    result = request.args.get("result", None)

    records = training_service.get_all_training_records(year, period, result)
    return jsonify(records)


@training_bp.route("/update", methods=["POST"])
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
            return (
                jsonify({"error": "수정에 실패했습니다."}),
                HTTP_STATUS["BAD_REQUEST"],
            )
    except ValueError as e:
        return jsonify({"error": str(e)}), HTTP_STATUS["BAD_REQUEST"]


@training_bp.route("/delete", methods=["DELETE"])
@admin_required
@handle_exceptions
def delete_training_record():
    """모의훈련 기록 삭제"""
    data = request.json

    try:
        success = training_service.delete_training_record(
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


@training_bp.route("/bulk-upload", methods=["POST"])
@admin_required
@handle_exceptions
def bulk_upload_training():
    """모의훈련 결과 일괄 업로드"""
    data = request.json
    records = data.get("records", [])

    if not records:
        return (
            jsonify({"error": "업로드할 기록이 없습니다."}),
            HTTP_STATUS["BAD_REQUEST"],
        )

    try:
        result = training_service.bulk_update_training(records)
        return jsonify(result)
    except ValueError as e:
        return jsonify({"error": str(e)}), HTTP_STATUS["BAD_REQUEST"]


@training_bp.route("/statistics", methods=["GET"])
@admin_required
@handle_exceptions
def get_training_statistics():
    """모의훈련 통계 조회"""
    year = request.args.get("year", datetime.now().year, type=int)

    try:
        stats = training_service.get_training_statistics(year)
        return jsonify(stats)
    except Exception as e:
        return (
            jsonify({"error": f"통계 조회 실패: {str(e)}"}),
            HTTP_STATUS["INTERNAL_SERVER_ERROR"],
        )


@training_bp.route("/user/<string:user_id>/status", methods=["GET"])
@admin_required
@handle_exceptions
def get_user_training_status(user_id):
    """특정 사용자의 모의훈련 현황 조회 (관리자용)"""
    year = request.args.get("year", datetime.now().year, type=int)

    try:
        result = training_service.get_training_status(user_id, year)
        return jsonify(result)
    except ValueError as e:
        return jsonify({"error": str(e)}), HTTP_STATUS["NOT_FOUND"]


@training_bp.route("/export", methods=["GET"])
@admin_required
@handle_exceptions
def export_training_data():
    """모의훈련 데이터 내보내기 - 한글 인코딩 문제 완전 해결"""
    year = request.args.get("year", datetime.now().year, type=int)
    format_type = request.args.get("format", "csv")

    try:
        if format_type == "csv":
            csv_data = training_service.export_training_to_csv(year)

            # UTF-8로 인코딩된 바이트 데이터로 변환
            csv_bytes = csv_data.encode("utf-8")
            response = make_response(csv_bytes)

            # 올바른 Content-Type 설정
            response.headers["Content-Type"] = "text/csv; charset=utf-8"

            # 브라우저 캐시 방지
            response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"

            # 한글 파일명을 RFC 5987 방식으로 인코딩
            filename = f"모의훈련_데이터_{year}.csv"
            encoded_filename = quote(filename.encode("utf-8"))

            # Content-Disposition 헤더에 인코딩된 파일명 설정
            response.headers["Content-Disposition"] = (
                f"attachment; "
                f"filename*=UTF-8''{encoded_filename}; "
                f'filename="training_data_{year}.csv"'
            )

            return response
        else:
            return (
                jsonify({"error": "지원하지 않는 형식입니다."}),
                HTTP_STATUS["BAD_REQUEST"],
            )
    except Exception as e:
        return (
            jsonify({"error": f"내보내기 실패: {str(e)}"}),
            HTTP_STATUS["INTERNAL_SERVER_ERROR"],
        )


@training_bp.route("/periods", methods=["GET"])
@token_required
@handle_exceptions
def get_training_periods():
    """훈련 기간 목록 조회"""
    periods = [
        {"value": "first_half", "label": "상반기"},
        {"value": "second_half", "label": "하반기"},
    ]
    return jsonify(periods)


@training_bp.route("/results", methods=["GET"])
@admin_required
@handle_exceptions
def get_training_results():
    """훈련 결과 옵션 조회"""
    results = [
        {"value": "pass", "label": "통과"},
        {"value": "fail", "label": "실패"},
        {"value": "pending", "label": "미실시"},
    ]
    return jsonify(results)


# admin_controller.py에 추가할 엔드포인트


@training_bp.route("/toggle-training-exception", methods=["POST"])
@admin_required
@handle_exceptions
def toggle_training_exception():
    """모의훈련 제외 상태 토글"""
    data = request.json

    user_id = data["user_id"]
    training_year = data["training_year"]
    training_period = data["training_period"]
    exclude = data["exclude"]  # True: 제외, False: 포함
    exclude_reason = data.get("exclude_reason", "")

    try:
        # ExceptionService 인스턴스 생성
        from app.services.admin_exception_service import ExceptionService

        exception_service = ExceptionService()

        # 사용자 uid 조회
        user = execute_query(
            "SELECT uid FROM users WHERE user_id = %s", (user_id,), fetch_one=True
        )

        if not user:
            return (
                jsonify({"error": "사용자를 찾을 수 없습니다."}),
                HTTP_STATUS["NOT_FOUND"],
            )

        user_uid = user["uid"]

        if exclude:
            # 제외 설정 추가
            item_id = f"training_{training_year}_{training_period}"
            item_name = f"{training_year}년 {training_period}({'상반기' if training_period == 'first_half' else '하반기'}) 모의훈련"

            result = exception_service.add_user_exception(
                user_uid=user_uid,
                item_id=item_id,
                item_type="training_period",
                item_name=item_name,
                item_category="모의훈련",
                exclude_reason=exclude_reason or "관리자 설정",
                exclude_type="permanent",
                created_by=request.current_user.get("username", "admin"),
            )
        else:
            # 제외 설정 제거
            item_id = f"training_{training_year}_{training_period}"
            result = exception_service.remove_user_exception(user_uid, item_id)

        if result.get("success", False):
            action = "제외" if exclude else "포함"
            return jsonify(
                {
                    "message": f"모의훈련이 점수 계산에서 {action}되었습니다.",
                    "success": True,
                }
            )
        else:
            return (
                jsonify(
                    {
                        "error": result.get(
                            "message", "제외 상태 변경에 실패했습니다."
                        ),
                        "success": False,
                    }
                ),
                HTTP_STATUS["BAD_REQUEST"],
            )

    except Exception as e:
        return (
            jsonify({"error": f"제외 상태 변경 실패: {str(e)}", "success": False}),
            HTTP_STATUS["INTERNAL_SERVER_ERROR"],
        )
