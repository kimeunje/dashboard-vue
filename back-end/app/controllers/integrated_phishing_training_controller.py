# app/controllers/integrated_phishing_training_controller.py
# 기존 두 컨트롤러를 통합한 새로운 컨트롤러

from datetime import datetime
from flask import Blueprint, request, jsonify, make_response
from app.services.integrated_phishing_training_service import (
    IntegratedPhishingTrainingService,
)
from app.utils.decorators import token_required, admin_required, handle_exceptions
from app.utils.constants import HTTP_STATUS

# 블루프린트 생성
phishing_training_bp = Blueprint("phishing_training", __name__)
training_service = IntegratedPhishingTrainingService()

# ================== 기간 관리 엔드포인트 ==================


@phishing_training_bp.route("/periods", methods=["GET"])
@admin_required
@handle_exceptions
def get_training_periods():
    """훈련 기간 목록 조회"""
    year = request.args.get("year", type=int)
    active_only = request.args.get("active_only", "true").lower() == "true"

    try:
        periods = training_service.get_training_periods(
            year=year, active_only=active_only
        )
        return jsonify({"periods": periods, "total_count": len(periods)})
    except ValueError as e:
        return jsonify({"error": str(e)}), HTTP_STATUS["BAD_REQUEST"]


@phishing_training_bp.route("/periods/<int:period_id>", methods=["GET"])
@admin_required
@handle_exceptions
def get_training_period_detail(period_id):
    """특정 훈련 기간 상세 조회"""
    try:
        period = training_service.get_training_period_by_id(period_id)
        if not period:
            return (
                jsonify({"error": "존재하지 않는 훈련 기간입니다."}),
                HTTP_STATUS["NOT_FOUND"],
            )

        return jsonify({"period": period})
    except ValueError as e:
        return jsonify({"error": str(e)}), HTTP_STATUS["BAD_REQUEST"]


@phishing_training_bp.route("/periods", methods=["POST"])
@admin_required
@handle_exceptions
def create_training_period():
    """훈련 기간 생성"""
    data = request.json
    user = request.current_user

    if not data:
        return jsonify({"error": "요청 데이터가 없습니다."}), HTTP_STATUS["BAD_REQUEST"]

    try:
        # 데이터 유효성 검사
        training_service.validate_period_data(data)

        # 기간 생성
        new_period = training_service.create_training_period(data, user["username"])

        return (
            jsonify({"message": "훈련 기간이 생성되었습니다.", "period": new_period}),
            HTTP_STATUS["CREATED"],
        )

    except ValueError as e:
        return jsonify({"error": str(e)}), HTTP_STATUS["BAD_REQUEST"]


@phishing_training_bp.route("/periods/<int:period_id>", methods=["PUT"])
@admin_required
@handle_exceptions
def update_training_period(period_id):
    """훈련 기간 수정"""
    data = request.json

    if not data:
        return jsonify({"error": "요청 데이터가 없습니다."}), HTTP_STATUS["BAD_REQUEST"]

    try:
        success = training_service.update_training_period(period_id, data)
        if success:
            # 수정된 기간 정보 반환
            updated_period = training_service.get_training_period_by_id(period_id)
            return jsonify(
                {"message": "훈련 기간이 수정되었습니다.", "period": updated_period}
            )
        else:
            return (
                jsonify({"error": "수정에 실패했습니다."}),
                HTTP_STATUS["BAD_REQUEST"],
            )

    except ValueError as e:
        return jsonify({"error": str(e)}), HTTP_STATUS["BAD_REQUEST"]


@phishing_training_bp.route("/periods/<int:period_id>", methods=["DELETE"])
@admin_required
@handle_exceptions
def delete_training_period(period_id):
    """훈련 기간 삭제"""
    try:
        success = training_service.delete_training_period(period_id)
        if success:
            return jsonify({"message": "훈련 기간이 삭제되었습니다."})
        else:
            return (
                jsonify({"error": "삭제에 실패했습니다."}),
                HTTP_STATUS["BAD_REQUEST"],
            )

    except ValueError as e:
        return jsonify({"error": str(e)}), HTTP_STATUS["BAD_REQUEST"]


@phishing_training_bp.route("/periods/<int:period_id>/complete", methods=["POST"])
@admin_required
@handle_exceptions
def complete_training_period(period_id):
    """
    훈련 기간 완료 처리 - 기간 완료 + 미실시 사용자 성공 처리를 동시에 수행
    """
    user = request.current_user

    try:
        # 통합된 완료 처리 메서드 사용
        result = training_service.complete_training_period(period_id, user["username"])

        # 성공 응답에 상세 정보 포함
        response_data = {
            "message": "훈련 기간이 완료 처리되었습니다.",
            "details": {
                "period": f"{result['period_info']['training_year']}년 {result['period_info']['training_period']}",
                "pending_users_processed": result["users_updated"],
                "total_pending": result["pending_count"],
                "final_statistics": result["final_stats"],
            },
        }

        # 처리된 사용자가 있을 경우 메시지에 추가
        if result["users_updated"] > 0:
            response_data[
                "message"
            ] += f" {result['users_updated']}명의 미실시 사용자가 성공으로 처리되었습니다."

        return jsonify(response_data)

    except ValueError as e:
        return jsonify({"error": str(e)}), HTTP_STATUS["BAD_REQUEST"]
    except Exception as e:
        print(f"완료 처리 중 예외 발생: {str(e)}")
        return (
            jsonify({"error": "완료 처리 중 오류가 발생했습니다."}),
            HTTP_STATUS["INTERNAL_SERVER_ERROR"],
        )


@phishing_training_bp.route("/periods/<int:period_id>/reopen", methods=["POST"])
@admin_required
@handle_exceptions
def reopen_training_period(period_id):
    """훈련 기간 재개 (완료 상태 취소)"""
    try:
        success = training_service.reopen_training_period(period_id)
        if success:
            return jsonify(
                {
                    "message": "훈련 기간이 재개되었습니다.",
                    "note": "완료 처리로 변경된 사용자 결과는 수동으로 재설정해야 합니다.",
                }
            )
        else:
            return (
                jsonify({"error": "재개 처리에 실패했습니다."}),
                HTTP_STATUS["BAD_REQUEST"],
            )
    except ValueError as e:
        return jsonify({"error": str(e)}), HTTP_STATUS["BAD_REQUEST"]


@phishing_training_bp.route("/periods/<int:period_id>/status", methods=["GET"])
@admin_required
@handle_exceptions
def get_period_completion_status(period_id):
    """특정 기간의 완료 처리 상태 및 통계 조회"""
    try:
        status = training_service.get_period_completion_status(period_id)
        return jsonify(status)

    except ValueError as e:
        if "존재하지 않는" in str(e):
            return jsonify({"error": str(e)}), HTTP_STATUS["NOT_FOUND"]
        return jsonify({"error": str(e)}), HTTP_STATUS["BAD_REQUEST"]
    except Exception as e:
        return (
            jsonify({"error": f"상태 조회 실패: {str(e)}"}),
            HTTP_STATUS["INTERNAL_SERVER_ERROR"],
        )


# ================== 훈련 기록 관리 엔드포인트 ==================


@phishing_training_bp.route("/records", methods=["GET"])
@admin_required
@handle_exceptions
def get_training_records():
    """훈련 기록 조회 (관리자용) - 필터링 및 페이지네이션 지원"""
    # 쿼리 파라미터 파싱
    year = request.args.get("year", datetime.now().year, type=int)
    period = request.args.get("period", None)
    result = request.args.get("result", None)
    page = request.args.get("page", 1, type=int)
    page_size = request.args.get("page_size", 50, type=int)

    # 페이지 사이즈 제한
    page_size = min(page_size, 200)  # 최대 200개

    try:
        records_data = training_service.get_all_training_records(
            year=year, period=period, result=result, page=page, page_size=page_size
        )
        return jsonify(records_data)

    except ValueError as e:
        return jsonify({"error": str(e)}), HTTP_STATUS["BAD_REQUEST"]


@phishing_training_bp.route("/records", methods=["POST"])
@admin_required
@handle_exceptions
def create_training_record():
    """개별 훈련 기록 생성"""
    data = request.json

    if not data:
        return jsonify({"error": "요청 데이터가 없습니다."}), HTTP_STATUS["BAD_REQUEST"]

    try:
        success = training_service.create_training_record(data)
        if success:
            return (
                jsonify({"message": "훈련 기록이 생성되었습니다."}),
                HTTP_STATUS["CREATED"],
            )
        else:
            return (
                jsonify({"error": "생성에 실패했습니다."}),
                HTTP_STATUS["BAD_REQUEST"],
            )

    except ValueError as e:
        return jsonify({"error": str(e)}), HTTP_STATUS["BAD_REQUEST"]


@phishing_training_bp.route(
    "/records/<int:user_id>/<int:year>/<period>", methods=["PUT"]
)
@admin_required
@handle_exceptions
def update_training_record(user_id, year, period):
    """개별 훈련 기록 수정"""
    data = request.json

    if not data:
        return jsonify({"error": "요청 데이터가 없습니다."}), HTTP_STATUS["BAD_REQUEST"]

    # URL 파라미터를 데이터에 추가
    data.update({"user_id": user_id, "training_year": year, "training_period": period})

    try:
        success = training_service.update_training_record(data)
        if success:
            return jsonify({"message": "훈련 기록이 수정되었습니다."})
        else:
            return (
                jsonify({"error": "수정에 실패했습니다."}),
                HTTP_STATUS["BAD_REQUEST"],
            )

    except ValueError as e:
        return jsonify({"error": str(e)}), HTTP_STATUS["BAD_REQUEST"]


@phishing_training_bp.route(
    "/records/<int:user_id>/<int:year>/<period>", methods=["DELETE"]
)
@admin_required
@handle_exceptions
def delete_training_record(user_id, year, period):
    """개별 훈련 기록 삭제"""
    try:
        success = training_service.delete_training_record(user_id, year, period)
        if success:
            return jsonify({"message": "훈련 기록이 삭제되었습니다."})
        else:
            return (
                jsonify({"error": "삭제할 기록을 찾을 수 없습니다."}),
                HTTP_STATUS["NOT_FOUND"],
            )

    except ValueError as e:
        return jsonify({"error": str(e)}), HTTP_STATUS["BAD_REQUEST"]


@phishing_training_bp.route("/records/batch", methods=["POST"])
@admin_required
@handle_exceptions
def bulk_upload_training_records():
    """훈련 기록 일괄 업로드"""
    user = request.current_user

    # 파일 업로드 또는 텍스트 데이터 처리
    if "file" in request.files:
        file = request.files["file"]
        if file.filename == "":
            return (
                jsonify({"error": "파일이 선택되지 않았습니다."}),
                HTTP_STATUS["BAD_REQUEST"],
            )

        try:
            csv_data = file.read().decode("utf-8")
        except UnicodeDecodeError:
            try:
                csv_data = file.read().decode("cp949")  # 한글 엑셀 파일 지원
            except UnicodeDecodeError:
                return (
                    jsonify(
                        {"error": "파일 인코딩을 확인해주세요. (UTF-8 또는 CP949)"}
                    ),
                    HTTP_STATUS["BAD_REQUEST"],
                )
    elif request.json and "csv_data" in request.json:
        csv_data = request.json["csv_data"]
    else:
        return (
            jsonify({"error": "CSV 파일 또는 데이터가 필요합니다."}),
            HTTP_STATUS["BAD_REQUEST"],
        )

    try:
        result = training_service.bulk_upload_training_records(
            csv_data, user["username"]
        )

        response_data = {
            "message": f'업로드 완료: 성공 {result["success_count"]}건, 실패 {result["error_count"]}건',
            "summary": {
                "success_count": result["success_count"],
                "error_count": result["error_count"],
                "total_processed": result["success_count"] + result["error_count"],
            },
            "details": {
                "success_records": result["success_records"],
                "error_records": result["error_records"],
            },
        }

        # 오류가 있으면 경고, 없으면 성공
        status_code = (
            HTTP_STATUS["OK"]
            if result["error_count"] == 0
            else HTTP_STATUS["PARTIAL_CONTENT"]
        )

        return jsonify(response_data), status_code

    except ValueError as e:
        return jsonify({"error": str(e)}), HTTP_STATUS["BAD_REQUEST"]
    except Exception as e:
        return (
            jsonify({"error": f"업로드 처리 중 오류: {str(e)}"}),
            HTTP_STATUS["INTERNAL_SERVER_ERROR"],
        )


@phishing_training_bp.route("/records/export", methods=["GET"])
@admin_required
@handle_exceptions
def export_training_data():
    """훈련 데이터 CSV 내보내기"""
    year = request.args.get("year", datetime.now().year, type=int)
    period = request.args.get("period", None)
    result = request.args.get("result", None)

    try:
        csv_data = training_service.export_training_data(year, period, result)

        # 파일명 생성
        filename_parts = [f"{year}년"]
        if period:
            period_names = {"first_half": "상반기", "second_half": "하반기"}
            filename_parts.append(period_names.get(period, period))
        if result:
            result_names = {"pass": "성공", "fail": "실패", "pending": "미실시"}
            filename_parts.append(result_names.get(result, result))

        filename = f"악성메일훈련_{'_'.join(filename_parts)}.csv"

        response = make_response(csv_data)
        response.headers["Content-Type"] = "text/csv; charset=utf-8"
        response.headers["Content-Disposition"] = f"attachment; filename={filename}"

        return response

    except ValueError as e:
        return jsonify({"error": str(e)}), HTTP_STATUS["BAD_REQUEST"]
    except Exception as e:
        return (
            jsonify({"error": f"데이터 내보내기 실패: {str(e)}"}),
            HTTP_STATUS["INTERNAL_SERVER_ERROR"],
        )


# ================== 현황 조회 엔드포인트 ==================


@phishing_training_bp.route("/status/personal", methods=["GET"])
@token_required
@handle_exceptions
def get_personal_training_status():
    """개인 악성메일 모의훈련 현황 조회"""
    user = request.current_user
    username = user["username"]
    year = request.args.get("year", datetime.now().year, type=int)

    try:
        result = training_service.get_training_status(username, year)
        return jsonify(result)
    except ValueError as e:
        return jsonify({"error": str(e)}), HTTP_STATUS["NOT_FOUND"]


@phishing_training_bp.route("/status/summary", methods=["GET"])
@admin_required
@handle_exceptions
def get_training_summary():
    """전체 훈련 요약 통계 (관리자용)"""
    year = request.args.get("year", datetime.now().year, type=int)

    try:
        summary = training_service.get_training_summary(year)
        return jsonify(summary)
    except ValueError as e:
        return jsonify({"error": str(e)}), HTTP_STATUS["BAD_REQUEST"]


# ================== 템플릿 및 옵션 엔드포인트 ==================


@phishing_training_bp.route("/templates/upload", methods=["GET"])
@admin_required
@handle_exceptions
def download_training_template():
    """모의훈련 업로드 템플릿 다운로드"""
    try:
        template_csv = training_service.get_training_excel_template()

        response = make_response(template_csv)
        response.headers["Content-Type"] = "text/csv; charset=utf-8"
        response.headers["Content-Disposition"] = (
            "attachment; filename=악성메일훈련_업로드_템플릿.csv"
        )

        return response
    except Exception as e:
        return (
            jsonify({"error": f"템플릿 생성 실패: {str(e)}"}),
            HTTP_STATUS["INTERNAL_SERVER_ERROR"],
        )


@phishing_training_bp.route("/options/periods", methods=["GET"])
@token_required
@handle_exceptions
def get_period_options():
    """훈련 기간 옵션 조회"""
    try:
        options = training_service.get_period_options()
        return jsonify({"options": options})
    except Exception as e:
        return (
            jsonify({"error": f"옵션 조회 실패: {str(e)}"}),
            HTTP_STATUS["INTERNAL_SERVER_ERROR"],
        )


@phishing_training_bp.route("/options/results", methods=["GET"])
@admin_required
@handle_exceptions
def get_result_options():
    """훈련 결과 옵션 조회"""
    try:
        options = training_service.get_result_options()
        return jsonify({"options": options})
    except Exception as e:
        return (
            jsonify({"error": f"옵션 조회 실패: {str(e)}"}),
            HTTP_STATUS["INTERNAL_SERVER_ERROR"],
        )


@phishing_training_bp.route("/options/years", methods=["GET"])
@token_required
@handle_exceptions
def get_available_years():
    """사용 가능한 훈련 연도 목록 조회"""
    try:
        years = training_service.get_available_years()
        return jsonify({"years": years})
    except Exception as e:
        return (
            jsonify({"error": f"연도 목록 조회 실패: {str(e)}"}),
            HTTP_STATUS["INTERNAL_SERVER_ERROR"],
        )


# ================== 개발 및 디버그 엔드포인트 ==================


@phishing_training_bp.route("/debug/routes", methods=["GET"])
@admin_required
def debug_routes():
    """등록된 라우트 확인용 (개발용)"""
    from flask import current_app

    routes = []

    for rule in current_app.url_map.iter_rules():
        if "phishing-training" in rule.rule:
            routes.append(
                {
                    "url": rule.rule,
                    "methods": list(rule.methods - {"HEAD", "OPTIONS"}),
                    "endpoint": rule.endpoint,
                }
            )

    return jsonify(
        {"total_routes": len(routes), "routes": sorted(routes, key=lambda x: x["url"])}
    )


@phishing_training_bp.route("/debug/statistics", methods=["GET"])
@admin_required
def debug_statistics():
    """통계 정보 디버그용"""
    try:
        year = request.args.get("year", datetime.now().year, type=int)

        # 기본 통계
        from app.database.connection import execute_query

        stats = {
            "periods": execute_query(
                "SELECT COUNT(*) as count FROM phishing_training_periods WHERE is_active = 1"
            )[0]["count"],
            "total_records": execute_query(
                "SELECT COUNT(*) as count FROM phishing_training"
            )[0]["count"],
            "yearly_records": execute_query(
                "SELECT COUNT(*) as count FROM phishing_training WHERE training_year = %s",
                (year,),
            )[0]["count"],
            "user_count": execute_query(
                "SELECT COUNT(DISTINCT user_id) as count FROM phishing_training WHERE training_year = %s",
                (year,),
            )[0]["count"],
        }

        return jsonify(
            {"year": year, "statistics": stats, "timestamp": datetime.now().isoformat()}
        )

    except Exception as e:
        return (
            jsonify({"error": f"통계 조회 실패: {str(e)}"}),
            HTTP_STATUS["INTERNAL_SERVER_ERROR"],
        )


# ================== 에러 핸들러 ==================


@phishing_training_bp.errorhandler(400)
def bad_request(error):
    return jsonify({"error": "잘못된 요청입니다."}), HTTP_STATUS["BAD_REQUEST"]


@phishing_training_bp.errorhandler(404)
def not_found(error):
    return (
        jsonify({"error": "요청한 리소스를 찾을 수 없습니다."}),
        HTTP_STATUS["NOT_FOUND"],
    )


@phishing_training_bp.errorhandler(500)
def internal_error(error):
    return (
        jsonify({"error": "서버 내부 오류가 발생했습니다."}),
        HTTP_STATUS["INTERNAL_SERVER_ERROR"],
    )


# 블루프린트 정보
def get_blueprint_info():
    """블루프린트 정보 반환"""
    return {
        "name": "phishing_training",
        "description": "악성메일 모의훈련 통합 관리 API",
        "version": "2.0",
        "endpoints": {
            "periods": "기간 관리",
            "records": "훈련 기록 관리",
            "status": "현황 조회",
            "templates": "템플릿 관리",
            "options": "옵션 데이터",
        },
    }
