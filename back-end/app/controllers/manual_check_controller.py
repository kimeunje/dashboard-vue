# app/controllers/manual_check_controller.py
import io
from datetime import datetime
from flask import Blueprint, request, jsonify, send_file
from app.services.manual_check_service import ManualCheckService
from app.utils.decorators import token_required, handle_exceptions
from app.utils.constants import HTTP_STATUS

manual_check_bp = Blueprint("manual_check", __name__)
manual_check_service = ManualCheckService()


@manual_check_bp.route("/upload/preview", methods=["POST"])
@token_required
@handle_exceptions
def preview_upload_file():
    """파일 업로드 미리보기 - 구조 검증 및 샘플 데이터 표시"""
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
        filename = file.filename

        # 파일 읽기
        if filename.lower().endswith('.csv'):
            df = pd.read_csv(file, encoding='utf-8-sig')
        elif filename.lower().endswith(('.xlsx', '.xls')):
            df = pd.read_excel(file)
        else:
            raise ValueError("지원하지 않는 파일 형식입니다. (Excel, CSV만 지원)")

        # 빈 데이터프레임 체크
        if df.empty:
            raise ValueError("파일에 데이터가 없습니다.")

        # 점검 유형 자동 감지
        check_type = manual_check_service.detect_file_type(df, filename)

        if not check_type:
            return jsonify({
                "success": False,
                "error": "점검 유형을 자동으로 감지할 수 없습니다.",
                "suggestions": [
                    "파일명에 '개인정보', '암호화', '봉인씰', '악성코드' 등의 키워드를 포함해주세요.",
                    "필수 컬럼이 포함되어 있는지 확인해주세요.",
                    "지원하는 점검 유형: 개인정보 파일 암호화, PC 봉인씰 확인, 악성코드 전체 검사"
                ]
            }), HTTP_STATUS["BAD_REQUEST"]

        # 파일 구조 검증
        is_valid, message = manual_check_service.validate_file_structure(df, check_type)

        if not is_valid:
            return jsonify({
                "success": False,
                "error": message,
                "detected_type": manual_check_service.get_check_type_name(check_type),
                "required_columns": manual_check_service.check_type_patterns[check_type]
                ['required_columns'],
                "found_columns": list(df.columns)
            }), HTTP_STATUS["BAD_REQUEST"]

        # 미리보기 데이터 생성
        preview_data = []
        sample_size = min(5, len(df))  # 최대 5행까지 미리보기

        for i in range(sample_size):
            row_data = {}
            for col in df.columns:
                value = df.iloc[i][col]
                if pd.isna(value):
                    row_data[col] = ""
                else:
                    row_data[col] = str(value)
            preview_data.append(row_data)

        # 예상 결과 분석
        expected_results = manual_check_service._analyze_expected_results(
            df, check_type)

        return jsonify({
            "success": True,
            "data": {
                "detected_type": check_type,
                "type_name": manual_check_service.get_check_type_name(check_type),
                "total_records": len(df),
                "columns": list(df.columns),
                "preview_data": preview_data,
                "expected_results": expected_results,
                "validation_message": message
            }
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"파일 미리보기 처리 중 오류가 발생했습니다: {str(e)}"
        }), HTTP_STATUS["BAD_REQUEST"]


@manual_check_bp.route("/upload", methods=["POST"])
@token_required
@handle_exceptions
def upload_excel_file():
    """엑셀 파일 업로드 및 일괄 처리 (수정된 버전)"""
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
            file=file, uploaded_by=request.current_user["username"])

        return jsonify({
            "success": True,
            "message": result["message"],
            "data": {
                "file_type": result["file_type"],
                "total_records": result["total_records"],
                "success_count": result["success_count"],
                "error_count": result["error_count"],
                "errors": result["errors"][:10]
                if result["errors"] else []  # 최대 10개 오류만 반환
            }
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), HTTP_STATUS["BAD_REQUEST"]


@manual_check_bp.route("/results", methods=["GET"])
@token_required
@handle_exceptions
def get_check_results():
    """점검 결과 목록 조회 (기존 유지)"""
    year = request.args.get("year", datetime.now().year, type=int)
    check_type = request.args.get("check_type")
    result_filter = request.args.get("result")
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
            result["check_type_name"] = type_mapping.get(result["check_item_code"],
                                                         result["check_item_code"])
            result["result_id"] = result["check_id"]
            result["check_result"] = result["overall_result"]
            result["user_email"] = result.get("email", "")

        return jsonify({
            "success": True,
            "data": results["results"],
            "pagination": {
                "current_page": results["page"],
                "total_pages": results["total_pages"],
                "page_size": results["size"],
                "total_count": results["total"],
            },
            "type_mapping": type_mapping,
        })

    except Exception as e:
        return (
            jsonify({
                "success": False,
                "error": str(e)
            }),
            HTTP_STATUS["INTERNAL_SERVER_ERROR"],
        )


@manual_check_bp.route("/results/update", methods=["POST"])
@token_required
@handle_exceptions
def update_check_result():
    """점검 결과 수정 (기존 유지)"""
    data = request.json

    if not data or "check_id" not in data:
        return (
            jsonify({"error": "수정할 결과 ID가 필요합니다."}),
            HTTP_STATUS["BAD_REQUEST"],
        )

    try:
        result = manual_check_service.update_check_result(
            check_id=data["check_id"], check_result=data.get("check_result"),
            notes=data.get("notes"), check_type=data.get("check_type"))

        return jsonify({"success": True, "message": result["message"]})

    except Exception as e:
        return (
            jsonify({
                "success": False,
                "error": str(e)
            }),
            HTTP_STATUS["INTERNAL_SERVER_ERROR"],
        )


@manual_check_bp.route("/results/<int:check_id>", methods=["DELETE"])
@token_required
@handle_exceptions
def delete_check_result(check_id):
    """점검 결과 삭제 (기존 유지)"""
    try:
        result = manual_check_service.delete_check_result(check_id)

        return jsonify({"success": True, "message": result["message"]})

    except Exception as e:
        return (
            jsonify({
                "success": False,
                "error": str(e)
            }),
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

        return jsonify({
            "success": True,
            "message": result["message"],
            "deleted_count": result["deleted_count"],
        })

    except Exception as e:
        return (
            jsonify({
                "success": False,
                "error": str(e)
            }),
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
            jsonify({
                "success": False,
                "error": f"템플릿 생성 실패: {str(e)}"
            }),
            HTTP_STATUS["INTERNAL_SERVER_ERROR"],
        )


@manual_check_bp.route("/check-types", methods=["GET"])
@handle_exceptions
def get_check_types():
    """점검 유형 목록 조회"""
    try:
        type_mapping = manual_check_service.get_check_type_mapping()

        return jsonify({
            "success": True,
            "data": [{
                "code": code,
                "name": name
            } for code, name in type_mapping.items()],
        })

    except Exception as e:
        return (
            jsonify({
                "success": False,
                "error": str(e)
            }),
            HTTP_STATUS["INTERNAL_SERVER_ERROR"],
        )