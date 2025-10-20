# app/controllers/admin_user_management_controller.py
"""
관리자 사용자 관리 API 컨트롤러
- 사용자 목록 조회 (필터링, 정렬, 페이징)
- 사용자 검색
- 일괄 내보내기
- 사용자 선택 및 관리
"""

from flask import Blueprint, request, jsonify
from datetime import datetime
from app.utils.decorators import token_required, handle_exceptions, admin_required
from app.utils.constants import HTTP_STATUS
from app.utils.database import execute_query
import logging
import csv
import io
from flask import make_response

# 블루프린트 생성
admin_user_management_bp = Blueprint(
    "admin_user_management", __name__, url_prefix="/api/admin/dashboard"
)


@admin_user_management_bp.route("/users", methods=["GET"])
@token_required
@admin_required
@handle_exceptions
def get_users_list():
    """사용자 목록 조회 (필터링, 검색, 페이징)"""
    year = request.args.get("year", datetime.now().year, type=int)
    department = request.args.get("department", "")
    position = request.args.get("position", "")
    risk_level = request.args.get("risk_level", "")
    search = request.args.get("search", "")
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    sort_by = request.args.get("sort_by", "total_penalty")
    sort_order = request.args.get("sort_order", "desc")

    try:
        logging.info(f"사용자 목록 조회: year={year}, dept={department}, page={page}")

        # 필터링된 사용자 데이터 조회
        users_data, total_count = _get_filtered_users(
            year,
            department,
            position,
            risk_level,
            search,
            page,
            per_page,
            sort_by,
            sort_order,
        )

        response_data = {
            "users": users_data,
            "pagination": {
                "current_page": page,
                "per_page": per_page,
                "total_count": total_count,
                "total_pages": (total_count + per_page - 1) // per_page,
            },
            "filters": {
                "year": year,
                "department": department,
                "position": position,
                "risk_level": risk_level,
                "search": search,
                "sort_by": sort_by,
                "sort_order": sort_order,
            },
        }

        return jsonify(response_data)

    except Exception as e:
        logging.error(f"Users list error: {str(e)}")
        return (
            jsonify(
                {"error": "사용자 목록 조회 중 오류가 발생했습니다.", "details": str(e)}
            ),
            HTTP_STATUS["INTERNAL_SERVER_ERROR"],
        )


@admin_user_management_bp.route("/users/export", methods=["GET"])
@token_required
@admin_required
@handle_exceptions
def export_users():
    """사용자 데이터 내보내기"""
    year = request.args.get("year", datetime.now().year, type=int)
    user_ids = request.args.get("user_ids", "")
    format_type = request.args.get("format", "csv")
    export_type = request.args.get("type", "selected")

    # 추가 필터 파라미터
    department = request.args.get("department", "")
    position = request.args.get("position", "")
    risk_level = request.args.get("risk_level", "")
    search = request.args.get("search", "")

    try:
        if export_type == "selected" and user_ids:
            # 선택된 사용자만 내보내기
            user_id_list = [
                int(uid.strip()) for uid in user_ids.split(",") if uid.strip()
            ]
            return _export_selected_users(user_id_list, year, format_type)
        elif export_type == "filtered":
            # 필터된 사용자 전체 내보내기
            return _export_filtered_users(
                year, department, position, risk_level, search, format_type
            )
        else:
            # 전체 사용자 내보내기
            return _export_all_users(year, format_type)

    except Exception as e:
        logging.error(f"Export users error: {str(e)}")
        return (
            jsonify(
                {
                    "error": "사용자 데이터 내보내기 중 오류가 발생했습니다.",
                    "details": str(e),
                }
            ),
            HTTP_STATUS["INTERNAL_SERVER_ERROR"],
        )


@admin_user_management_bp.route("/users/filters", methods=["GET"])
@token_required
@admin_required
@handle_exceptions
def get_filter_options():
    """필터 옵션 조회 (부서, 직급 목록)"""
    try:
        # 부서 목록 조회
        departments_query = """
            SELECT DISTINCT department 
            FROM users 
            WHERE is_active = 1 AND department IS NOT NULL AND department != ''
            ORDER BY department
        """
        departments = [row["department"] for row in execute_query(departments_query)]

        # 직급 목록 조회
        positions_query = """
            SELECT DISTINCT position 
            FROM users 
            WHERE is_active = 1 AND position IS NOT NULL AND position != ''
            ORDER BY position
        """
        positions = [row["position"] for row in execute_query(positions_query)]

        return jsonify(
            {
                "departments": departments,
                "positions": positions,
                "risk_levels": [
                    {"value": "low", "label": "낮음"},
                    {"value": "medium", "label": "보통"},
                    {"value": "high", "label": "높음"},
                    {"value": "critical", "label": "매우 높음"},
                    {"value": "not_evaluated", "label": "미평가"},
                ],
            }
        )

    except Exception as e:
        logging.error(f"Filter options error: {str(e)}")
        return (
            jsonify(
                {"error": "필터 옵션 조회 중 오류가 발생했습니다.", "details": str(e)}
            ),
            HTTP_STATUS["INTERNAL_SERVER_ERROR"],
        )


@admin_user_management_bp.route("/users/search", methods=["GET"])
@token_required
@admin_required
@handle_exceptions
def search_users():
    """사용자 실시간 검색"""
    query = request.args.get("q", "").strip()
    limit = request.args.get("limit", 10, type=int)

    if not query or len(query) < 2:
        return jsonify({"users": []})

    try:
        search_query = """
            SELECT 
                u.uid,
                u.name,
                u.user_id as employee_id,
                u.department,
                u.position,
                u.email
            FROM users u
            WHERE u.is_active = 1 
            AND (
                u.name LIKE %s 
                OR u.user_id LIKE %s 
                OR u.email LIKE %s
                OR u.department LIKE %s
            )
            ORDER BY 
                CASE 
                    WHEN u.name LIKE %s THEN 1
                    WHEN u.user_id LIKE %s THEN 2
                    WHEN u.email LIKE %s THEN 3
                    ELSE 4
                END,
                u.name
            LIMIT %s
        """

        search_term = f"%{query}%"
        exact_term = f"{query}%"

        users = execute_query(
            search_query,
            (
                search_term,
                search_term,
                search_term,
                search_term,
                exact_term,
                exact_term,
                exact_term,
                limit,
            ),
        )

        return jsonify({"users": users})

    except Exception as e:
        logging.error(f"Search users error: {str(e)}")
        return (
            jsonify(
                {"error": "사용자 검색 중 오류가 발생했습니다.", "details": str(e)}
            ),
            HTTP_STATUS["INTERNAL_SERVER_ERROR"],
        )


# === 헬퍼 함수들 ===


def _get_filtered_users(
    search_query="",
    department_filter="",
    risk_filter="",
    year=None,
    sort_field="name",
    order="ASC",
    page=1,
    per_page=50,
):
    """훈련 감점이 올바르게 계산된 사용자 목록 조회"""
    return _get_filtered_users_with_training_penalty(
        search_query,
        department_filter,
        risk_filter,
        year,
        sort_field,
        order,
        page,
        per_page,
    )


def _export_selected_users(user_ids, year, format_type):
    """선택된 사용자 내보내기"""
    try:
        if not user_ids:
            raise ValueError("내보낼 사용자가 선택되지 않았습니다.")

        placeholders = ",".join(["%s"] * len(user_ids))
        users_query = f"""
            SELECT 
                u.name,
                u.user_id as employee_id,
                u.department,
                u.position,
                u.email,
                COALESCE(sss.total_penalty, 0) as total_penalty,
                COALESCE(sss.audit_penalty, 0) as audit_penalty,
                COALESCE(sss.education_penalty, 0) as education_penalty,
                COALESCE(sss.training_penalty, 0) as training_penalty,
                COALESCE(sss.audit_failed_count, 0) as audit_failed_count,
                COALESCE(sss.education_incomplete_count, 0) as education_incomplete_count,
                COALESCE(sss.training_failed_count, 0) as training_failed_count,
                sss.last_calculated,
                CASE 
                    WHEN sss.total_penalty IS NULL THEN '미평가'
                    WHEN sss.total_penalty > 3.0 THEN '매우 높음'
                    WHEN sss.total_penalty > 2.0 THEN '높음'
                    WHEN sss.total_penalty > 1.0 THEN '보통'
                    ELSE '낮음'
                END as risk_level
            FROM users u
            LEFT JOIN security_score_summary sss ON u.uid = sss.user_id AND sss.evaluation_year = %s
            WHERE u.uid IN ({placeholders}) AND u.is_active = 1
            ORDER BY sss.total_penalty DESC, u.name
        """

        users_data = execute_query(users_query, [year] + user_ids)

        return _create_csv_response(
            users_data, f"selected_users_{len(user_ids)}_members_{year}"
        )

    except Exception as e:
        logging.error(f"Export selected users error: {str(e)}")
        raise e


def _export_filtered_users(year, department, position, risk_level, search, format_type):
    """필터된 사용자 전체 내보내기"""
    try:
        # 필터 조건과 동일한 로직으로 모든 데이터 조회
        users_data, _ = _get_filtered_users(
            year,
            department,
            position,
            risk_level,
            search,
            1,
            999999,
            "total_penalty",
            "desc",  # 모든 데이터 조회
        )

        filename_parts = ["filtered_users"]
        if department:
            filename_parts.append(f"dept_{department}")
        if position:
            filename_parts.append(f"pos_{position}")
        if risk_level:
            filename_parts.append(f"risk_{risk_level}")
        filename_parts.append(str(year))

        filename = "_".join(filename_parts)

        return _create_csv_response(users_data, filename)

    except Exception as e:
        logging.error(f"Export filtered users error: {str(e)}")
        raise e


def _export_all_users(year, format_type):
    """전체 사용자 내보내기"""
    try:
        users_data, _ = _get_filtered_users(
            year, "", "", "", "", 1, 999999, "total_penalty", "desc"
        )

        return _create_csv_response(users_data, f"all_users_{year}")

    except Exception as e:
        logging.error(f"Export all users error: {str(e)}")
        raise e


def _create_csv_response(users_data, filename):
    """CSV 응답 생성"""
    try:
        output = io.StringIO()
        writer = csv.writer(output)

        # 헤더
        writer.writerow(
            [
                "이름",
                "사번",
                "부서",
                "직급",
                "이메일",
                "총 감점",
                "감사 감점",
                "교육 감점",
                "훈련 감점",
                "감사 실패",
                "교육 미완료",
                "훈련 실패",
                "위험도",
                "마지막 업데이트",
            ]
        )

        # 데이터
        for user in users_data:
            writer.writerow(
                [
                    user.get("name", ""),
                    user.get("employee_id", ""),
                    user.get("department", ""),
                    user.get("position", ""),
                    user.get("email", ""),
                    f"{user.get('total_penalty', 0):.2f}",
                    f"{user.get('audit_penalty', 0):.2f}",
                    f"{user.get('education_penalty', 0):.2f}",
                    f"{user.get('training_penalty', 0):.2f}",
                    user.get("audit_failed_count", 0),
                    user.get("education_incomplete_count", 0),
                    user.get("training_failed_count", 0),
                    user.get("risk_level", "미평가"),
                    user.get("last_updated", "미평가"),
                ]
            )

        csv_content = output.getvalue()
        output.close()

        # UTF-8 BOM 추가 (Excel 호환성)
        csv_content = "\ufeff" + csv_content

        response = make_response(csv_content.encode("utf-8"))
        response.headers["Content-Type"] = "text/csv; charset=utf-8"
        response.headers["Content-Disposition"] = f"attachment; filename={filename}.csv"
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"

        return response

    except Exception as e:
        logging.error(f"Create CSV response error: {str(e)}")
        raise e


def _get_user_statistics_summary():
    """사용자 통계 요약"""
    try:
        current_year = datetime.now().year

        stats_query = """
            SELECT 
                COUNT(*) as total_active_users,
                COUNT(CASE WHEN sss.total_penalty IS NOT NULL THEN 1 END) as evaluated_users,
                COUNT(CASE WHEN sss.total_penalty <= 0.5 THEN 1 END) as excellent_users,
                COUNT(CASE WHEN sss.total_penalty > 2.0 THEN 1 END) as risk_users,
                COALESCE(AVG(sss.total_penalty), 0) as avg_penalty
            FROM users u
            LEFT JOIN security_score_summary sss ON u.uid = sss.user_id AND sss.evaluation_year = %s
            WHERE u.is_active = 1
        """

        result = execute_query(stats_query, (current_year,), fetch_one=True)
        return dict(result) if result else {}

    except Exception as e:
        logging.error(f"User statistics summary error: {str(e)}")
        return {}


def _get_filtered_users_with_training_penalty(
    search_query="",
    department_filter="",
    risk_filter="",
    year=None,
    sort_field="name",
    order="ASC",
    page=1,
    per_page=50,
):
    """훈련 감점을 포함한 사용자 목록 조회 (user_phishing_summary VIEW 사용)"""
    try:
        if year is None:
            year = datetime.now().year

        # WHERE 조건 구성
        where_conditions = ["u.is_active = 1"]
        params = []

        if search_query:
            where_conditions.append(
                "(u.name LIKE %s OR u.user_id LIKE %s OR u.department LIKE %s)"
            )
            search_param = f"%{search_query}%"
            params.extend([search_param, search_param, search_param])

        if department_filter:
            where_conditions.append("u.department = %s")
            params.append(department_filter)

        where_clause = " AND ".join(where_conditions)

        # 정렬 필드 검증
        allowed_sort_fields = {
            "name": "u.name",
            "department": "u.department",
            "total_penalty": "sss.total_penalty",
            "last_updated": "sss.last_calculated",
        }

        sort_field = allowed_sort_fields.get(sort_field, "u.name")
        order = "DESC" if order.upper() == "DESC" else "ASC"

        # 전체 개수 조회
        count_query = f"""
            SELECT COUNT(DISTINCT u.uid)
            FROM users u
            LEFT JOIN security_score_summary sss ON u.uid = sss.user_id AND sss.evaluation_year = %s
            LEFT JOIN user_phishing_summary ups ON u.uid = ups.user_id AND ups.training_year = %s
            WHERE {where_clause}
        """

        count_params = [year, year] + params
        total_count = execute_query(count_query, count_params, fetch_one=True)[
            "COUNT(DISTINCT u.uid)"
        ]

        # 페이지네이션
        offset = (page - 1) * per_page

        # 메인 데이터 조회 (훈련 감점 포함)
        data_query = f"""
            SELECT 
                u.uid,
                u.name,
                u.user_id as employee_id,
                u.department,
                u.position,
                u.mail as email,
                COALESCE(sss.total_penalty, 0) as total_penalty,
                COALESCE(sss.audit_penalty, 0) as audit_penalty,
                COALESCE(sss.education_penalty, 0) as education_penalty,
                -- 훈련 감점은 user_phishing_summary에서 가져오기
                COALESCE(ups.penalty_score, 0) as training_penalty,
                COALESCE(sss.audit_failed_count, 0) as audit_failed_count,
                COALESCE(sss.education_incomplete_count, 0) as education_incomplete_count,
                -- 훈련 실패 건수는 user_phishing_summary에서 계산
                COALESCE(ups.fail_count, 0) as training_failed_count,
                sss.last_calculated,
                CASE 
                    WHEN sss.total_penalty IS NULL THEN 'not_evaluated'
                    WHEN sss.total_penalty > 3.0 THEN 'critical'
                    WHEN sss.total_penalty > 2.0 THEN 'high'
                    WHEN sss.total_penalty > 1.0 THEN 'medium'
                    ELSE 'low'
                END as risk_level
            FROM users u
            LEFT JOIN security_score_summary sss ON u.uid = sss.user_id AND sss.evaluation_year = %s
            LEFT JOIN user_phishing_summary ups ON u.uid = ups.user_id AND ups.training_year = %s
            WHERE {where_clause}
            ORDER BY {sort_field} {order}, u.name ASC
            LIMIT %s OFFSET %s
        """

        data_params = [year, year] + params + [per_page, offset]
        users_data = execute_query(data_query, data_params)

        # 데이터 후처리
        for user in users_data:
            # training_penalty를 실제 user_phishing_summary의 penalty_score로 업데이트
            user["training_penalty"] = float(user["training_penalty"])
            user["total_penalty"] = float(user["total_penalty"])
            user["audit_penalty"] = float(user["audit_penalty"])
            user["education_penalty"] = float(user["education_penalty"])

            # 총 감점에 훈련 감점 반영 (기존 교육+감사 + 새로운 훈련 감점)
            recalculated_total = (
                float(user["audit_penalty"])
                + float(user["education_penalty"])
                + float(user["training_penalty"])
            )
            user["total_penalty"] = min(5.0, recalculated_total)

            if user["last_calculated"]:
                user["last_updated"] = user["last_calculated"].strftime(
                    "%Y-%m-%d %H:%M"
                )
            else:
                user["last_updated"] = None

        return users_data, total_count

    except Exception as e:
        logging.error(f"Filtered users with training penalty error: {str(e)}")
        return [], 0
