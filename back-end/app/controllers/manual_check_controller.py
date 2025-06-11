# back-end/app/controllers/manual_check_controller.py
# 기존 파일을 완전히 교체

import os
import logging
from datetime import datetime
from flask import Blueprint, request, jsonify, send_file, current_app
from werkzeug.utils import secure_filename
from app.services.excel_upload_service import ExcelUploadService
from app.services.manual_check_service import ManualCheckService
from app.utils.decorators import token_required, validate_json, handle_exceptions
from app.utils.constants import HTTP_STATUS
import tempfile

manual_check_bp = Blueprint("manual_check_management", __name__)  # Blueprint 이름 변경
excel_service = ExcelUploadService()
manual_service = ManualCheckService()

logger = logging.getLogger(__name__)

# 허용된 파일 확장자
ALLOWED_EXTENSIONS = {"xlsx", "xls", "csv"}


def allowed_file(filename):
    """파일 확장자 검증"""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@manual_check_bp.route("/upload", methods=["POST"], endpoint="excel_upload")
@token_required
@handle_exceptions
def upload_excel_file():  # 함수명 변경
    """엑셀 파일 업로드 및 처리"""
    user = request.current_user

    # 파일 확인
    if "file" not in request.files:
        return (
            jsonify({"error": "파일이 선택되지 않았습니다."}),
            HTTP_STATUS["BAD_REQUEST"],
        )

    file = request.files["file"]
    check_type = request.form.get("check_type")

    if file.filename == "":
        return (
            jsonify({"error": "파일이 선택되지 않았습니다."}),
            HTTP_STATUS["BAD_REQUEST"],
        )

    if not check_type:
        return (
            jsonify({"error": "점검 유형을 선택해주세요."}),
            HTTP_STATUS["BAD_REQUEST"],
        )

    if check_type not in ["seal_check", "malware_scan", "file_encryption"]:
        return (
            jsonify({"error": "유효하지 않은 점검 유형입니다."}),
            HTTP_STATUS["BAD_REQUEST"],
        )

    if not allowed_file(file.filename):
        return (
            jsonify(
                {"error": "지원하지 않는 파일 형식입니다. (.xlsx, .xls, .csv만 가능)"}
            ),
            HTTP_STATUS["BAD_REQUEST"],
        )

    try:
        # 파일 처리
        result = excel_service.process_excel_upload(
            file=file, check_type=check_type, uploaded_by=user["username"]
        )

        return jsonify(
            {
                "success": True,
                "message": "엑셀 파일이 성공적으로 처리되었습니다.",
                "data": result,
            }
        )

    except Exception as e:
        logger.error(f"엑셀 업로드 처리 실패: {str(e)}")
        return jsonify({"error": str(e)}), HTTP_STATUS["INTERNAL_SERVER_ERROR"]


@manual_check_bp.route("/upload/history", methods=["GET"], endpoint="upload_history")
@token_required
@handle_exceptions
def get_upload_history_list():  # 함수명 변경
    """업로드 이력 조회"""
    check_type = request.args.get("check_type")
    limit = int(request.args.get("limit", 50))

    try:
        history = excel_service.get_upload_history(check_type, limit)

        return jsonify({"success": True, "data": history})

    except Exception as e:
        logger.error(f"업로드 이력 조회 실패: {str(e)}")
        return jsonify({"error": str(e)}), HTTP_STATUS["INTERNAL_SERVER_ERROR"]


@manual_check_bp.route(
    "/upload/batch/<batch_id>", methods=["GET"], endpoint="batch_details"
)
@token_required
@handle_exceptions
def get_batch_detail_info(batch_id):  # 함수명 변경
    """배치 상세 정보 조회"""
    try:
        details = excel_service.get_batch_details(batch_id)

        return jsonify({"success": True, "data": details})

    except Exception as e:
        logger.error(f"배치 상세 조회 실패: {str(e)}")
        return jsonify({"error": str(e)}), HTTP_STATUS["INTERNAL_SERVER_ERROR"]


@manual_check_bp.route("/results", methods=["GET"], endpoint="check_results")
@token_required
@handle_exceptions
def get_manual_check_results():  # 함수명 변경
    """점검 결과 목록 조회"""
    year = request.args.get("year", datetime.now().year, type=int)
    period = request.args.get("period")
    department = request.args.get("department")
    result_filter = request.args.get("result")
    page = request.args.get("page", 1, type=int)
    size = request.args.get("size", 20, type=int)

    try:
        results = manual_service.get_check_results(
            year=year,
            period=period,
            department=department,
            result_filter=result_filter,
            page=page,
            size=size,
        )

        return jsonify({"success": True, "data": results})

    except Exception as e:
        logger.error(f"점검 결과 조회 실패: {str(e)}")
        return jsonify({"error": str(e)}), HTTP_STATUS["INTERNAL_SERVER_ERROR"]


@manual_check_bp.route(
    "/results/<int:check_id>", methods=["GET"], endpoint="check_result_detail"
)
@token_required
@handle_exceptions
def get_manual_check_result_detail(check_id):  # 함수명 변경
    """점검 결과 상세 조회"""
    try:
        result = manual_service.get_check_result_by_id(check_id)

        if not result:
            return (
                jsonify({"error": "점검 결과를 찾을 수 없습니다."}),
                HTTP_STATUS["NOT_FOUND"],
            )

        return jsonify({"success": True, "data": result})

    except Exception as e:
        logger.error(f"점검 결과 상세 조회 실패: {str(e)}")
        return jsonify({"error": str(e)}), HTTP_STATUS["INTERNAL_SERVER_ERROR"]


@manual_check_bp.route(
    "/results/<int:check_id>", methods=["PUT"], endpoint="update_check_result"
)
@token_required
@validate_json
@handle_exceptions
def update_manual_check_result(check_id):  # 함수명 변경
    """점검 결과 수정"""
    user = request.current_user
    data = request.json

    try:
        result = manual_service.update_check_result(check_id, data, user["username"])

        return jsonify({"success": True, "message": result["message"]})

    except Exception as e:
        logger.error(f"점검 결과 수정 실패: {str(e)}")
        return jsonify({"error": str(e)}), HTTP_STATUS["INTERNAL_SERVER_ERROR"]


@manual_check_bp.route(
    "/results/<int:check_id>", methods=["DELETE"], endpoint="delete_check_result"
)
@token_required
@handle_exceptions
def delete_manual_check_result(check_id):  # 함수명 변경
    """점검 결과 삭제"""
    try:
        result = manual_service.delete_check_result(check_id)

        if not result["success"]:
            return jsonify({"error": result["message"]}), HTTP_STATUS["NOT_FOUND"]

        return jsonify({"success": True, "message": result["message"]})

    except Exception as e:
        logger.error(f"점검 결과 삭제 실패: {str(e)}")
        return jsonify({"error": str(e)}), HTTP_STATUS["INTERNAL_SERVER_ERROR"]


@manual_check_bp.route("/statistics", methods=["GET"], endpoint="check_statistics")
@token_required
@handle_exceptions
def get_manual_check_statistics():  # 함수명 변경
    """점검 통계 조회"""
    year = request.args.get("year", datetime.now().year, type=int)
    period = request.args.get("period")

    try:
        stats = manual_service.get_check_statistics(year, period)

        return jsonify({"success": True, "data": stats})

    except Exception as e:
        logger.error(f"통계 조회 실패: {str(e)}")
        return jsonify({"error": str(e)}), HTTP_STATUS["INTERNAL_SERVER_ERROR"]


@manual_check_bp.route("/export/csv", methods=["GET"], endpoint="export_csv")
@token_required
@handle_exceptions
def export_manual_check_csv():  # 함수명 변경
    """점검 결과 CSV 내보내기"""
    year = request.args.get("year", datetime.now().year, type=int)
    period = request.args.get("period")

    try:
        csv_content = manual_service.export_results_to_csv(year, period)

        # 임시 파일 생성
        with tempfile.NamedTemporaryFile(
            mode="w", delete=False, suffix=".csv", encoding="utf-8-sig"
        ) as temp_file:
            temp_file.write(csv_content)
            temp_file_path = temp_file.name

        filename = f"manual_check_results_{year}"
        if period:
            filename += f"_{period}"
        filename += ".csv"

        def cleanup_temp_file():
            try:
                os.unlink(temp_file_path)
            except:
                pass

        return send_file(
            temp_file_path,
            as_attachment=True,
            download_name=filename,
            mimetype="text/csv",
        )

    except Exception as e:
        logger.error(f"CSV 내보내기 실패: {str(e)}")
        return jsonify({"error": str(e)}), HTTP_STATUS["INTERNAL_SERVER_ERROR"]


@manual_check_bp.route(
    "/template/<check_type>", methods=["GET"], endpoint="download_template"
)
@token_required
@handle_exceptions
def download_excel_template(check_type):  # 함수명 변경
    """엑셀 업로드용 템플릿 다운로드"""
    if check_type not in ["seal_check", "malware_scan", "file_encryption"]:
        return (
            jsonify({"error": "유효하지 않은 점검 유형입니다."}),
            HTTP_STATUS["BAD_REQUEST"],
        )

    try:
        # 점검 유형별 템플릿 생성
        template_content = _generate_template_content(check_type)

        # 임시 파일 생성
        with tempfile.NamedTemporaryFile(
            mode="w", delete=False, suffix=".csv", encoding="utf-8-sig"
        ) as temp_file:
            temp_file.write(template_content)
            temp_file_path = temp_file.name

        filename = f"{_get_check_type_korean(check_type)}_template.csv"

        return send_file(
            temp_file_path,
            as_attachment=True,
            download_name=filename,
            mimetype="text/csv",
        )

    except Exception as e:
        logger.error(f"템플릿 다운로드 실패: {str(e)}")
        return jsonify({"error": str(e)}), HTTP_STATUS["INTERNAL_SERVER_ERROR"]


@manual_check_bp.route("/periods", methods=["GET"], endpoint="get_periods")
@token_required
@handle_exceptions
def get_manual_check_periods():  # 함수명 변경
    """점검 기간 목록 조회"""
    year = request.args.get("year", datetime.now().year, type=int)
    check_type = request.args.get("check_type")

    try:
        periods = manual_service.get_check_periods(year, check_type)

        return jsonify({"success": True, "data": periods})

    except Exception as e:
        logger.error(f"점검 기간 조회 실패: {str(e)}")
        return jsonify({"error": str(e)}), HTTP_STATUS["INTERNAL_SERVER_ERROR"]


@manual_check_bp.route("/periods", methods=["POST"], endpoint="create_period")
@token_required
@validate_json
@handle_exceptions
def create_manual_check_period():  # 함수명 변경
    """점검 기간 생성"""
    user = request.current_user
    data = request.json

    # 필수 필드 검증
    required_fields = [
        "check_type",
        "period_year",
        "period_name",
        "start_date",
        "end_date",
    ]
    missing_fields = [field for field in required_fields if field not in data]

    if missing_fields:
        return (
            jsonify(
                {"error": f'필수 필드가 누락되었습니다: {", ".join(missing_fields)}'}
            ),
            HTTP_STATUS["BAD_REQUEST"],
        )

    try:
        result = manual_service.create_check_period(data, user["username"])

        return jsonify(
            {"success": True, "message": "점검 기간이 생성되었습니다.", "data": result}
        )

    except Exception as e:
        logger.error(f"점검 기간 생성 실패: {str(e)}")
        return jsonify({"error": str(e)}), HTTP_STATUS["INTERNAL_SERVER_ERROR"]


@manual_check_bp.route(
    "/periods/<int:period_id>", methods=["PUT"], endpoint="update_period"
)
@token_required
@validate_json
@handle_exceptions
def update_manual_check_period(period_id):  # 함수명 변경
    """점검 기간 수정"""
    user = request.current_user
    data = request.json

    try:
        result = manual_service.update_check_period(period_id, data, user["username"])

        return jsonify({"success": True, "message": result["message"]})

    except Exception as e:
        logger.error(f"점검 기간 수정 실패: {str(e)}")
        return jsonify({"error": str(e)}), HTTP_STATUS["INTERNAL_SERVER_ERROR"]


@manual_check_bp.route(
    "/periods/<int:period_id>/complete", methods=["POST"], endpoint="complete_period"
)
@token_required
@handle_exceptions
def complete_manual_check_period(period_id):  # 함수명 변경
    """점검 기간 완료 처리"""
    user = request.current_user

    try:
        result = manual_service.complete_check_period(period_id, user["username"])

        return jsonify({"success": True, "message": result["message"]})

    except Exception as e:
        logger.error(f"점검 기간 완료 처리 실패: {str(e)}")
        return jsonify({"error": str(e)}), HTTP_STATUS["INTERNAL_SERVER_ERROR"]


def _generate_template_content(check_type: str) -> str:
    """점검 유형별 템플릿 내용 생성"""

    if check_type == "malware_scan":
        return """일시,사용자명,부서명,IP,악성코드명,악성코드 분류,탐지 방법,치료 여부,경로,탐지 항목,다운로드 URL
2025-06-12 14:30:00,홍길동,개발팀,192.168.1.100,Trojan.Generic.123,트로이목마/트로잔,정밀 검사,치료,C:\\temp\\virus.exe,virus.exe,"""

    elif check_type == "seal_check":
        return """일시,이름,부서,봉인씰 확인
2025-06-12 14:30:00,홍길동,개발팀,정상
2025-06-12 15:00:00,김철수,운영팀,훼손"""

    elif check_type == "file_encryption":
        return """에이전트 NO,접근 IP,로컬 IP,호스트명,소속,사용자 ID,사용자명,161회차,,,,,160회차,,,,,159회차
,,,,,,,총 검출 파일,총 검출 건수,미검사 파일,휴대전화번호,주민등록번호,총 검출 파일,총 검출 건수,미검사 파일,휴대전화번호,주민등록번호,총 검출 파일,총 검출 건수,미검사 파일,휴대전화번호,주민등록번호
1,192.168.1.100,192.168.1.100,PC001,개발팀,user01,홍길동,50,100,0,0,0,45,90,0,0,0,40,80,0,0,0"""

    return ""


def _get_check_type_korean(check_type: str) -> str:
    """점검 유형 한국어 이름 반환"""
    mapping = {
        "seal_check": "PC_봉인씰_확인",
        "malware_scan": "악성코드_전체_검사",
        "file_encryption": "개인정보_파일_암호화",
    }
    return mapping.get(check_type, check_type)


# 에러 핸들러
@manual_check_bp.errorhandler(413)
def file_too_large_error(error):  # 함수명 변경
    """파일 크기 초과 에러 처리"""
    return (
        jsonify({"error": "파일 크기가 너무 큽니다. 최대 16MB까지 업로드 가능합니다."}),
        413,
    )


@manual_check_bp.errorhandler(400)
def bad_request_error(error):  # 함수명 변경
    """잘못된 요청 에러 처리"""
    return jsonify({"error": "잘못된 요청입니다."}), 400
