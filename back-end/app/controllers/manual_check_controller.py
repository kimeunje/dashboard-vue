# app/controllers/manual_check_controller.py
import io
from datetime import datetime
from flask import Blueprint, request, jsonify, send_file
from app.services.manual_check_service import ManualCheckService
from app.utils.decorators import token_required, handle_exceptions
from app.utils.constants import HTTP_STATUS

manual_check_bp = Blueprint("manual_check", __name__)
manual_check_service = ManualCheckService()


@manual_check_bp.route("/upload", methods=["POST"])
@token_required
@handle_exceptions
def upload_excel_file():
    """엑셀 파일 업로드 및 일괄 처리"""
    if "file" not in request.files:
        return (
            jsonify({"error": "파일이 제공되지 않았습니다."}),
            HTTP_STATUS["BAD_REQUEST"],
        )

    file = request.files["file"]
    if file.filename == "":
        return (
            jsonify({"error": "파일이 선택되지 않았습니다."}),
            HTTP_STATUS["BAD_REQUEST"],
        )

    try:
        result = manual_check_service.process_bulk_upload(
            file=file, uploaded_by=request.current_user["username"]
        )

        return jsonify(
            {
                "success": True,
                "message": result["message"],
                "data": {
                    "file_type": result["file_type"],
                    "total_records": result["total_records"],
                    "success_count": result["success_count"],
                    "error_count": result["error_count"],
                    "errors": result["errors"][:10],  # 최대 10개 오류만 반환
                },
            }
        )

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), HTTP_STATUS["BAD_REQUEST"]


@manual_check_bp.route("/results", methods=["GET"])
@token_required
@handle_exceptions
def get_check_results():
    """점검 결과 목록 조회 (수정된 버전)"""
    # 쿼리 파라미터 추출
    year = request.args.get("year", datetime.now().year, type=int)
    check_type = request.args.get(
        "check_type"
    )  # seal_check, malware_scan, file_encryption
    result_filter = request.args.get("result")  # pass, fail
    search = request.args.get("search")
    page = request.args.get("page", 1, type=int)
    size = request.args.get("size", 20, type=int)

    try:
        results = manual_check_service.get_check_results(
            year=year,
            check_type=check_type,
            result_filter=result_filter,
            search=search,
            page=page,
            size=size,
        )

        # 점검 유형 매핑 정보 추가
        type_mapping = manual_check_service.get_check_type_mapping()

        # 결과 데이터 변환
        for result in results["results"]:
            result["check_type_name"] = type_mapping.get(
                result["check_item_code"], result["check_item_code"]
            )
            result["result_id"] = result["check_id"]  # 프론트엔드 호환성
            result["check_result"] = result["overall_result"]  # 프론트엔드 호환성
            result["user_email"] = result.get("email", "")  # 이메일 필드 추가

        return jsonify(
            {
                "success": True,
                "data": results["results"],
                "pagination": {
                    "current_page": results["page"],
                    "total_pages": results["total_pages"],
                    "page_size": results["size"],
                    "total_count": results["total"],
                },
                "type_mapping": type_mapping,
            }
        )

    except Exception as e:
        return (
            jsonify({"success": False, "error": str(e)}),
            HTTP_STATUS["INTERNAL_SERVER_ERROR"],
        )


@manual_check_bp.route("/results/update", methods=["POST"])
@token_required
@handle_exceptions
def update_check_result():
    """점검 결과 수정"""
    data = request.json

    if not data or "check_id" not in data:
        return (
            jsonify({"error": "수정할 결과 ID가 필요합니다."}),
            HTTP_STATUS["BAD_REQUEST"],
        )

    try:
        # 수정할 데이터 구성
        update_data = {
            "overall_result": data.get("check_result"),
            "notes": data.get("notes", ""),
        }

        # 점검 유형에 따른 추가 필드 처리
        check_type = data.get("check_type")
        if check_type == "seal_check":
            update_data.update(
                {
                    "seal_status": data.get("seal_status"),
                    "seal_notes": data.get("seal_notes"),
                }
            )
        elif check_type == "malware_scan":
            update_data.update(
                {
                    "malware_scan_result": data.get("malware_scan_result"),
                    "threats_found": data.get("threats_found", 0),
                    "malware_notes": data.get("malware_notes"),
                }
            )
        elif check_type == "file_encryption":
            update_data.update(
                {
                    "encryption_status": data.get("encryption_status"),
                    "ssn_included": data.get("ssn_included", 0),
                    "encryption_notes": data.get("encryption_notes"),
                }
            )

        result = manual_check_service._update_check_result(
            check_id=data["check_id"],
            data=update_data,
            updated_by=request.current_user["username"],
        )

        return jsonify(
            {"success": True, "message": "점검 결과가 성공적으로 수정되었습니다."}
        )

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), HTTP_STATUS["BAD_REQUEST"]


@manual_check_bp.route("/results/<int:check_id>", methods=["DELETE"])
@token_required
@handle_exceptions
def delete_check_result(check_id):
    """점검 결과 삭제"""
    try:
        result = manual_check_service.delete_check_result(check_id)

        if result["success"]:
            return jsonify({"success": True, "message": result["message"]})
        else:
            return (
                jsonify({"success": False, "error": result["message"]}),
                HTTP_STATUS["NOT_FOUND"],
            )

    except Exception as e:
        return (
            jsonify({"success": False, "error": str(e)}),
            HTTP_STATUS["INTERNAL_SERVER_ERROR"],
        )


@manual_check_bp.route("/results/bulk-delete", methods=["POST"])
@token_required
@handle_exceptions
def bulk_delete_results():
    """점검 결과 일괄 삭제"""
    data = request.json

    if not data or "result_ids" not in data:
        return (
            jsonify({"error": "삭제할 결과 ID 목록이 필요합니다."}),
            HTTP_STATUS["BAD_REQUEST"],
        )

    result_ids = data["result_ids"]
    if not isinstance(result_ids, list) or not result_ids:
        return (
            jsonify({"error": "유효한 결과 ID 목록이 필요합니다."}),
            HTTP_STATUS["BAD_REQUEST"],
        )

    try:
        result = manual_check_service.bulk_delete_results(result_ids)

        return jsonify(
            {
                "success": True,
                "message": result["message"],
                "deleted_count": result["deleted_count"],
            }
        )

    except Exception as e:
        return (
            jsonify({"success": False, "error": str(e)}),
            HTTP_STATUS["INTERNAL_SERVER_ERROR"],
        )


@manual_check_bp.route("/template", methods=["GET"])
@token_required
@handle_exceptions
def download_template():
    """업로드 템플릿 다운로드"""
    try:
        template_content = manual_check_service.generate_upload_template()

        # CSV 파일로 반환
        output = io.StringIO()
        output.write(template_content)
        output.seek(0)

        return send_file(
            io.BytesIO(output.getvalue().encode("utf-8-sig")),
            mimetype="text/csv",
            as_attachment=True,
            download_name="manual_check_template.csv",
        )

    except Exception as e:
        return (
            jsonify({"success": False, "error": f"템플릿 생성 실패: {str(e)}"}),
            HTTP_STATUS["INTERNAL_SERVER_ERROR"],
        )


@manual_check_bp.route("/check-types", methods=["GET"])
@handle_exceptions
def get_check_types():
    """점검 유형 목록 조회"""
    try:
        type_mapping = manual_check_service.get_check_type_mapping()

        return jsonify(
            {
                "success": True,
                "data": [
                    {"code": code, "name": name} for code, name in type_mapping.items()
                ],
            }
        )

    except Exception as e:
        return (
            jsonify({"success": False, "error": str(e)}),
            HTTP_STATUS["INTERNAL_SERVER_ERROR"],
        )


# 기존 import 추가 필요
from app.utils.database import execute_query
