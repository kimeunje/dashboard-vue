# app/controllers/admin_dashboard_controller_fixed.py
"""
실제 데이터베이스 스키마에 맞춘 관리자 대시보드 API
"""

import csv
import io
from flask import Blueprint, make_response, request, jsonify
from datetime import datetime, timedelta
from app.utils.decorators import token_required, handle_exceptions, admin_required
from app.utils.constants import HTTP_STATUS
from app.utils.database import execute_query
import logging

# 블루프린트 생성
admin_dashboard_bp = Blueprint("admin_dashboard", __name__,
                               url_prefix="/api/admin/dashboard")


# 대시보드 overview 함수도 수정 - 자동 계산을 선택적으로
@admin_dashboard_bp.route("/overview", methods=["GET"])
@token_required
@admin_required
@handle_exceptions
def get_dashboard_overview():
    """관리자 대시보드 종합 현황 - 자동 점수 계산을 선택적으로"""
    year = request.args.get("year", datetime.now().year, type=int)
    auto_calculate = request.args.get("auto_calculate",
                                      "false").lower() == "true"  # 기본값을 false로 변경

    try:
        logging.info(f"관리자 대시보드 현황 조회: year={year}, auto_calculate={auto_calculate}")

        calculated_count = 0

        # 자동 계산이 활성화된 경우에만 미계산 사용자들의 점수를 계산
        if auto_calculate:
            calculated_count = _auto_calculate_missing_scores(year)
            if calculated_count > 0:
                logging.info(f"자동 계산 완료: {calculated_count}명의 점수 계산됨")

        # 대시보드 데이터 조회
        user_stats = _get_user_statistics_fixed(year)
        score_distribution = _get_score_distribution_fixed(year)
        monthly_trends = _get_monthly_trends_fixed(year)
        department_overview = _get_department_overview_fixed(year)
        recent_activities = _get_recent_activities_fixed()
        risk_users = _get_risk_users_fixed(year)

        response_data = {
            "year": year,
            "user_stats": user_stats,
            "score_distribution": score_distribution,
            "monthly_trends": monthly_trends,
            "department_overview": department_overview,
            "position_overview": [],
            "recent_activities": recent_activities,
            "risk_users": risk_users,
            "last_updated": datetime.now().isoformat(),
            "auto_calculated_users": calculated_count
        }

        return jsonify(response_data)

    except Exception as e:
        logging.error(f"Dashboard overview error: {str(e)}")
        return jsonify({
            "error": "대시보드 현황 조회 중 오류가 발생했습니다.",
            "details": str(e)
        }), HTTP_STATUS["INTERNAL_SERVER_ERROR"]


def _auto_calculate_missing_scores(year):
    """미계산된 사용자들의 점수를 자동으로 계산 - 개선된 버전"""
    from app.services.total_score_service import ScoreService

    try:
        # 해당 연도에 점수 데이터가 없는 사용자들 조회
        missing_users_query = """
            SELECT u.uid, u.user_id, u.username 
            FROM users u
            LEFT JOIN security_score_summary sss ON u.uid = sss.user_id AND sss.evaluation_year = %s
            WHERE sss.summary_id IS NULL
            ORDER BY u.uid
        """

        missing_users = execute_query(missing_users_query, (year, ), fetch_all=True)

        if not missing_users:
            logging.info("미계산 사용자가 없습니다.")
            return 0

        logging.info(f"미계산 사용자 {len(missing_users)}명 발견, 자동 계산 시작")

        score_service = ScoreService()
        calculated_count = 0

        for user in missing_users:
            try:
                # 개별 사용자 점수 계산
                score_service.calculate_security_score(user["uid"], year)
                calculated_count += 1
                logging.debug(f"사용자 {user['user_id']} 자동 계산 완료")

            except Exception as user_error:
                logging.error(f"사용자 {user['user_id']} 자동 계산 실패: {str(user_error)}")
                continue

        logging.info(f"자동 계산 완료: {calculated_count}/{len(missing_users)}명 성공")
        return calculated_count

    except Exception as e:
        logging.error(f"자동 점수 계산 중 오류: {str(e)}")
        return 0


def _get_user_statistics_fixed(year):
    """전체 사용자 통계 - 수정된 스키마"""
    try:
        stats_query = """
            SELECT 
                COUNT(*) as total_users,
                COUNT(CASE WHEN sss.total_penalty IS NOT NULL THEN 1 END) as evaluated_users,
                COUNT(CASE WHEN sss.total_penalty <= 0.5 THEN 1 END) as excellent_users,
                COUNT(CASE WHEN sss.total_penalty > 0.5 AND sss.total_penalty <= 2.0 THEN 1 END) as warning_users,
                COUNT(CASE WHEN sss.total_penalty > 2.0 THEN 1 END) as critical_users,
                COALESCE(AVG(sss.total_penalty), 0) as avg_penalty,
                COALESCE(MAX(sss.total_penalty), 0) as max_penalty,
                COALESCE(MIN(sss.total_penalty), 0) as min_penalty,
                COUNT(DISTINCT u.department) as total_departments
            FROM users u
            LEFT JOIN security_score_summary sss ON u.uid = sss.user_id AND sss.evaluation_year = %s
        """

        result = execute_query(stats_query, (year, ), fetch_one=True)
        return dict(result) if result else {}

    except Exception as e:
        logging.error(f"User statistics error: {str(e)}")
        return {}


def _get_score_distribution_fixed(year):
    """보안 점수 분포 - 수정된 스키마"""
    try:
        distribution_query = """
            SELECT 
                CASE 
                    WHEN sss.total_penalty IS NULL THEN 'not_evaluated'
                    WHEN sss.total_penalty = 0 THEN 'perfect'
                    WHEN sss.total_penalty <= 0.5 THEN 'excellent'
                    WHEN sss.total_penalty <= 1.0 THEN 'good'
                    WHEN sss.total_penalty <= 2.0 THEN 'warning'
                    WHEN sss.total_penalty <= 3.0 THEN 'danger'
                    ELSE 'critical'
                END as score_range,
                COUNT(*) as user_count,
                ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM users), 2) as percentage
            FROM users u
            LEFT JOIN security_score_summary sss ON u.uid = sss.user_id AND sss.evaluation_year = %s
            GROUP BY score_range
            ORDER BY 
                CASE score_range
                    WHEN 'perfect' THEN 1
                    WHEN 'excellent' THEN 2
                    WHEN 'good' THEN 3
                    WHEN 'warning' THEN 4
                    WHEN 'danger' THEN 5
                    WHEN 'critical' THEN 6
                    WHEN 'not_evaluated' THEN 7
                END
        """

        return execute_query(distribution_query, (year, ))

    except Exception as e:
        logging.error(f"Score distribution error: {str(e)}")
        return []


def _get_monthly_trends_fixed(year):
    """월별 트렌드 분석 - 수정된 스키마"""
    try:
        trends_query = """
            SELECT 
                MONTH(al.checked_at) as month,
                COUNT(DISTINCT al.user_id) as active_users,
                COUNT(al.log_id) as total_checks,
                COUNT(CASE WHEN al.passed = 0 THEN 1 END) as failed_checks,
                ROUND(COUNT(CASE WHEN al.passed = 0 THEN 1 END) * 100.0 / COUNT(al.log_id), 2) as failure_rate
            FROM audit_log al
            WHERE YEAR(al.checked_at) = %s
            GROUP BY MONTH(al.checked_at)
            ORDER BY month
        """

        return execute_query(trends_query, (year, ))

    except Exception as e:
        logging.error(f"Monthly trends error: {str(e)}")
        return []


# 새로운 엔드포인트: 실시간 점수 계산 상태 확인
@admin_dashboard_bp.route("/calculation-status", methods=["GET"])
@token_required
@admin_required
@handle_exceptions
def get_calculation_status():
    """점수 계산 상태 조회"""
    year = request.args.get("year", datetime.now().year, type=int)

    try:
        # 전체 사용자 수
        total_users = execute_query("SELECT COUNT(*) as count FROM users",
                                    fetch_one=True)["count"]

        # 계산된 사용자 수
        calculated_users = execute_query(
            "SELECT COUNT(*) as count FROM security_score_summary WHERE evaluation_year = %s",
            (year, ), fetch_one=True)["count"]

        # 최근 계산 시간
        last_calculation = execute_query(
            """
            SELECT MAX(last_calculated) as last_time, COUNT(*) as recent_count
            FROM security_score_summary 
            WHERE evaluation_year = %s AND last_calculated >= DATE_SUB(NOW(), INTERVAL 1 HOUR)
            """, (year, ), fetch_one=True)

        response_data = {
            "year": year,
            "total_users": total_users,
            "calculated_users": calculated_users,
            "missing_users": total_users - calculated_users,
            "calculation_percentage": round(
                (calculated_users / total_users) * 100, 1) if total_users > 0 else 0,
            "last_calculation_time": last_calculation["last_time"].isoformat()
            if last_calculation["last_time"] else None,
            "recent_calculations": last_calculation["recent_count"] or 0,
            "needs_calculation": (total_users - calculated_users) > 0
        }

        return jsonify(response_data)

    except Exception as e:
        logging.error(f"Calculation status error: {str(e)}")
        return jsonify({
            "error": "계산 상태 조회 중 오류가 발생했습니다.",
            "details": str(e)
        }), HTTP_STATUS["INTERNAL_SERVER_ERROR"]


@admin_dashboard_bp.route("/trigger-calculation", methods=["POST"])
@token_required
@admin_required
@handle_exceptions
def trigger_full_calculation():
    """모든 사용자 점수 강제 재계산 - 개선된 버전"""
    data = request.json or {}
    year = data.get("year", datetime.now().year)
    force_recalculate = data.get("force_recalculate", False)

    try:
        logging.info(f"점수 계산 요청: year={year}, force_recalculate={force_recalculate}")

        if force_recalculate:
            # 모든 사용자 강제 재계산
            users_query = "SELECT uid, user_id, username FROM users ORDER BY uid"
            users = execute_query(users_query, fetch_all=True)

            if not users:
                return jsonify({"message": "계산할 사용자가 없습니다.", "calculated_count": 0})

            success_count = 0
            error_count = 0
            errors = []

            logging.info(f"전체 사용자 {len(users)}명의 점수를 강제 재계산 시작")

            from app.services.total_score_service import ScoreService
            score_service = ScoreService()

            for user in users:
                try:
                    # 기존 점수 데이터 삭제 (강제 재계산)
                    execute_query(
                        "DELETE FROM security_score_summary WHERE user_id = %s AND evaluation_year = %s",
                        (user["uid"], year))

                    # 새로 계산
                    score_service.calculate_security_score(user["uid"], year)
                    success_count += 1

                    logging.debug(f"사용자 {user['user_id']} 점수 재계산 완료")

                except Exception as user_error:
                    error_count += 1
                    error_msg = f"사용자 {user['user_id']} 계산 실패: {str(user_error)}"
                    errors.append(error_msg)
                    logging.error(error_msg)

            message = f"전체 재계산 완료: 성공 {success_count}명, 실패 {error_count}명"
            logging.info(message)

            response_data = {
                "message": message,
                "calculated_count": success_count,
                "error_count": error_count,
                "total_users": len(users),
                "year": year,
                "force_recalculate": True
            }

            if errors:
                response_data["errors"] = errors[:10]  # 최대 10개의 에러만 반환

            return jsonify(response_data)

        else:
            # 미계산 사용자만 계산 (기존 로직)
            calculated_count = _auto_calculate_missing_scores(year)

            return jsonify({
                "message": f"{calculated_count}명의 미계산 사용자 점수를 계산했습니다.",
                "calculated_count": calculated_count,
                "year": year,
                "force_recalculate": False
            })

    except Exception as e:
        logging.error(f"점수 계산 실행 중 오류: {str(e)}")
        return jsonify({
            "error": "점수 계산 중 오류가 발생했습니다.",
            "details": str(e)
        }), HTTP_STATUS["INTERNAL_SERVER_ERROR"]


def _get_department_overview_fixed(year):
    """부서별 현황 - 수정된 스키마"""
    try:
        dept_query = """
            SELECT 
                u.department,
                COUNT(*) as total_users,
                COUNT(CASE WHEN sss.total_penalty IS NOT NULL THEN 1 END) as evaluated_users,
                COALESCE(AVG(sss.total_penalty), 0) as avg_penalty,
                COUNT(CASE WHEN sss.total_penalty <= 0.5 THEN 1 END) as excellent_count,
                COUNT(CASE WHEN sss.total_penalty > 0.5 AND sss.total_penalty <= 2.0 THEN 1 END) as warning_count,
                COUNT(CASE WHEN sss.total_penalty > 2.0 THEN 1 END) as critical_count,
                ROUND(COUNT(CASE WHEN sss.total_penalty <= 0.5 THEN 1 END) * 100.0 / COUNT(*), 2) as excellent_rate
            FROM users u
            LEFT JOIN security_score_summary sss ON u.uid = sss.user_id AND sss.evaluation_year = %s
            WHERE u.department IS NOT NULL
            GROUP BY u.department
            ORDER BY avg_penalty DESC, total_users DESC
        """

        return execute_query(dept_query, (year, ))

    except Exception as e:
        logging.error(f"Department overview error: {str(e)}")
        return []


def _get_recent_activities_fixed(limit=10):
    """최근 활동 현황 - 수정된 스키마"""
    try:
        activities_query = """
            SELECT 
                'audit' as activity_type,
                u.username as user_name,
                u.department,
                ci.item_name as activity_description,
                al.checked_at as activity_time,
                CASE WHEN al.passed = 1 THEN 'success' 
                     WHEN al.passed = 0 THEN 'failure' 
                     ELSE 'pending' END as status
            FROM audit_log al
            JOIN users u ON al.user_id = u.uid
            JOIN checklist_items ci ON al.item_id = ci.item_id
            WHERE al.checked_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)
            ORDER BY al.checked_at DESC
            LIMIT %s
        """

        return execute_query(activities_query, (limit, ))

    except Exception as e:
        logging.error(f"Recent activities error: {str(e)}")
        return []


def _get_risk_users_fixed(year, limit=10):
    """위험 사용자 목록 - 수정된 스키마"""
    try:
        risk_query = """
            SELECT 
                u.uid,
                u.username as name,
                u.user_id as employee_id,
                u.department,
                '' as position,  -- position 컬럼이 없으므로 빈 문자열
                sss.total_penalty,
                sss.audit_penalty,
                sss.education_penalty,
                sss.training_penalty,
                sss.audit_failed_count,
                sss.education_incomplete_count,
                sss.training_failed_count,
                CASE 
                    WHEN sss.total_penalty > 3.0 THEN 'critical'
                    WHEN sss.total_penalty > 2.0 THEN 'high'
                    WHEN sss.total_penalty > 1.0 THEN 'medium'
                    ELSE 'low'
                END as risk_level
            FROM users u
            JOIN security_score_summary sss ON u.uid = sss.user_id AND sss.evaluation_year = %s
            WHERE sss.total_penalty > 1.0
            ORDER BY sss.total_penalty DESC, sss.audit_failed_count DESC
            LIMIT %s
        """

        return execute_query(risk_query, (year, limit))

    except Exception as e:
        logging.error(f"Risk users error: {str(e)}")
        return []


# === 사용자 관리 API 수정 ===


@admin_dashboard_bp.route("/users", methods=["GET"])
@token_required
@admin_required
@handle_exceptions
def get_users_list():
    """사용자 목록 조회 - 수정된 스키마"""
    year = request.args.get("year", datetime.now().year, type=int)
    department = request.args.get("department", "")
    risk_level = request.args.get("risk_level", "")
    search = request.args.get("search", "")
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    sort_by = request.args.get("sort_by", "total_penalty")
    sort_order = request.args.get("sort_order", "desc")

    try:
        users_data, total_count = _get_filtered_users_fixed(year, department,
                                                            risk_level, search, page,
                                                            per_page, sort_by,
                                                            sort_order)

        response_data = {
            "users": users_data,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total_count": total_count,
                "total_pages": (total_count + per_page - 1) // per_page
            },
            "filters": {
                "year": year,
                "department": department,
                "risk_level": risk_level,
                "search": search,
                "sort_by": sort_by,
                "sort_order": sort_order
            }
        }

        return jsonify(response_data)

    except Exception as e:
        logging.error(f"Users list error: {str(e)}")
        return jsonify({
            "error": "사용자 목록 조회 중 오류가 발생했습니다.",
            "details": str(e)
        }), HTTP_STATUS["INTERNAL_SERVER_ERROR"]



def _get_filtered_users_fixed(year, department, risk_level, search, page, per_page, sort_by, sort_order):
    """필터링된 사용자 목록 조회 - audit_log 기반 마지막 업데이트 시간 포함"""
    try:
        # WHERE 절 조건 구성
        where_conditions = []
        params = []

        # 부서 필터
        if department:
            where_conditions.append("u.department LIKE %s")
            params.append(f"%{department}%")

        # 위험도 필터
        if risk_level:
            if risk_level == 'low':
                where_conditions.append("(sss.total_penalty IS NULL OR sss.total_penalty <= 1.0)")
            elif risk_level == 'medium':
                where_conditions.append("sss.total_penalty > 1.0 AND sss.total_penalty <= 2.0")
            elif risk_level == 'high':
                where_conditions.append("sss.total_penalty > 2.0 AND sss.total_penalty <= 3.0")
            elif risk_level == 'critical':
                where_conditions.append("sss.total_penalty > 3.0")
            elif risk_level == 'not_evaluated':
                where_conditions.append("sss.total_penalty IS NULL")

        # 검색 필터
        if search:
            search_condition = "(u.username LIKE %s OR u.user_id LIKE %s OR u.mail LIKE %s)"
            where_conditions.append(search_condition)
            search_param = f"%{search}%"
            params.extend([search_param, search_param, search_param])

        where_clause = "WHERE " + " AND ".join(where_conditions) if where_conditions else ""

        # 전체 개수 조회
        count_query = f"""
            SELECT COUNT(*) as total
            FROM users u
            LEFT JOIN security_score_summary sss ON u.uid = sss.user_id AND sss.evaluation_year = %s
            {where_clause}
        """
        count_params = [year] + params
        count_result = execute_query(count_query, count_params, fetch_one=True)
        total_count = count_result['total'] if count_result else 0

        # 정렬 필드 매핑
        sort_fields = {
            'name': 'u.username',
            'department': 'u.department',
            'total_penalty': 'COALESCE(sss.total_penalty, 0)',
            'updated_at': 'last_audit_time'  # audit_log 기반 정렬
        }
        sort_field = sort_fields.get(sort_by, 'COALESCE(sss.total_penalty, 0)')
        order = 'ASC' if sort_order.lower() == 'asc' else 'DESC'

        # 페이징
        offset = (page - 1) * per_page

        # 메인 데이터 조회 - audit_log에서 마지막 업데이트 시간 조회
        data_query = f"""
            SELECT 
                u.uid,
                u.user_id,
                u.username as name,
                u.mail as email,
                u.department,
                u.ip,
                u.role,
                u.created_at,
                u.updated_at,
                COALESCE(sss.total_penalty, 0.0) as total_penalty,
                COALESCE(sss.audit_penalty, 0.0) as audit_penalty,
                COALESCE(sss.education_penalty, 0.0) as education_penalty,
                COALESCE(sss.training_penalty, 0.0) as training_penalty,
                COALESCE(sss.audit_failed_count, 0) as security_audit_penalty,
                COALESCE(sss.education_incomplete_count, 0) as education_penalty_count,
                COALESCE(sss.training_failed_count, 0) as training_penalty_count,
                sss.last_calculated,
                -- audit_log에서 사용자별 가장 최근 checked_at 시간 조회
                (SELECT MAX(al.checked_at) 
                 FROM audit_log al 
                 WHERE al.user_id = u.uid) as last_audit_time,
                CASE 
                    WHEN sss.total_penalty IS NULL THEN 'not_evaluated'
                    WHEN sss.total_penalty > 3.0 THEN 'critical'
                    WHEN sss.total_penalty > 2.0 THEN 'high'
                    WHEN sss.total_penalty > 1.0 THEN 'medium'
                    ELSE 'low'
                END as risk_level
            FROM users u
            LEFT JOIN security_score_summary sss ON u.uid = sss.user_id AND sss.evaluation_year = %s
            {where_clause}
            ORDER BY {sort_field} {order}, u.username ASC
            LIMIT %s OFFSET %s
        """

        data_params = [year] + params + [per_page, offset]
        users_data = execute_query(data_query, data_params)

        # 데이터 후처리
        for user in users_data:
            user['total_penalty'] = float(user['total_penalty'])
            user['audit_penalty'] = float(user['audit_penalty'])
            user['education_penalty'] = float(user['education_penalty'])
            user['training_penalty'] = float(user['training_penalty'])
            
            # 마지막 업데이트 시간을 audit_log 기반으로 설정
            if user['last_audit_time']:
                user['updated_at'] = user['last_audit_time']
                user['last_updated'] = user['last_audit_time'].strftime('%Y-%m-%d %H:%M:%S')
            elif user['last_calculated']:
                user['updated_at'] = user['last_calculated']
                user['last_updated'] = user['last_calculated'].strftime('%Y-%m-%d %H:%M:%S')
            else:
                user['last_updated'] = None

        return users_data, total_count

    except Exception as e:
        logging.error(f"Filtered users error: {str(e)}")
        return [], 0
# === 사용자 상세 API 수정 ===


@admin_dashboard_bp.route("/users/<int:user_id>/detail", methods=["GET"])
@token_required
@admin_required
@handle_exceptions
def get_user_detail(user_id):
    """특정 사용자의 상세 점수 정보 조회 - 수정된 스키마"""
    year = request.args.get("year", datetime.now().year, type=int)

    try:
        # 사용자 기본 정보 조회
        user_info = _get_user_info_fixed(user_id)
        if not user_info:
            return jsonify({"error": "사용자를 찾을 수 없습니다."}), HTTP_STATUS["NOT_FOUND"]

        # 상세 점수 계산
        score_detail = _calculate_user_detail_scores_fixed(user_id, year)

        response_data = {
            "user_info": user_info,
            "year": year,
            "score_detail": score_detail,
            "last_updated": datetime.now().isoformat()
        }

        return jsonify(response_data)

    except Exception as e:
        logging.error(f"User detail error: {str(e)}")
        return jsonify({
            "error": "사용자 상세 정보 조회 중 오류가 발생했습니다.",
            "details": str(e)
        }), HTTP_STATUS["INTERNAL_SERVER_ERROR"]


def _get_user_info_fixed(user_id):
    """사용자 기본 정보 조회 - audit_log 기반 마지막 업데이트 포함"""
    try:
        user_query = """
            SELECT 
                u.uid,
                u.user_id,
                u.username as name,
                u.mail as email,
                u.department,
                u.ip,
                u.role,
                u.created_at,
                u.updated_at,
                -- audit_log에서 사용자의 가장 최근 checked_at 시간
                (SELECT MAX(al.checked_at) 
                 FROM audit_log al 
                 WHERE al.user_id = u.uid) as last_audit_time
            FROM users u
            WHERE u.uid = %s
        """
        
        user_info = execute_query(user_query, (user_id,), fetch_one=True)
        
        if user_info:
            # 마지막 업데이트 시간을 audit_log 기반으로 설정
            if user_info['last_audit_time']:
                user_info['updated_at'] = user_info['last_audit_time']
            
            # datetime 객체를 문자열로 변환
            if user_info.get("created_at"):
                user_info["created_at"] = user_info["created_at"].isoformat()
            if user_info.get("updated_at"):
                user_info["updated_at"] = user_info["updated_at"].isoformat()

        return user_info

    except Exception as e:
        logging.error(f"사용자 정보 조회 오류: {str(e)}")
        return None


def _calculate_user_detail_scores_fixed(user_id, year):
    """사용자 상세 점수 계산 - 수정된 스키마"""
    try:
        # security_score_summary에서 직접 조회
        summary_query = """
            SELECT 
                total_penalty,
                audit_penalty,
                education_penalty,
                training_penalty,
                audit_failed_count,
                education_incomplete_count,
                training_failed_count
            FROM security_score_summary
            WHERE user_id = %s AND evaluation_year = %s
        """

        summary_result = execute_query(summary_query, (user_id, year), fetch_one=True)

        if not summary_result:
            # 데이터가 없으면 0으로 초기화
            return {
                "total_penalty": 0.0,
                "audit_penalty": 0.0,
                "education_penalty": 0.0,
                "training_penalty": 0.0,
                "audit_stats": {
                    "failed_count": 0,
                    "total_count": 0,
                    "failed_items": []
                },
                "education_stats": {
                    "incomplete_count": 0,
                    "total_count": 0,
                    "incomplete_items": []
                },
                "training_stats": {
                    "failed_count": 0,
                    "total_count": 0,
                    "failed_items": []
                }
            }

        # 상세 내역 조회
        audit_stats = _get_audit_details_fixed(user_id, year)
        education_stats = _get_education_details_fixed(user_id, year)
        training_stats = _get_training_details_fixed(user_id, year)

        return {
            "total_penalty": float(summary_result["total_penalty"] or 0),
            "audit_penalty": float(summary_result["audit_penalty"] or 0),
            "education_penalty": float(summary_result["education_penalty"] or 0),
            "training_penalty": float(summary_result["training_penalty"] or 0),
            "audit_stats": audit_stats,
            "education_stats": education_stats,
            "training_stats": training_stats
        }

    except Exception as e:
        logging.error(f"User detail calculation error: {str(e)}")
        return {
            "total_penalty": 0.0,
            "audit_penalty": 0.0,
            "education_penalty": 0.0,
            "training_penalty": 0.0,
            "audit_stats": {},
            "education_stats": {},
            "training_stats": {}
        }


def _get_audit_details_fixed(user_id, year):
    """감사 상세 내역 조회 - 수정된 스키마"""
    try:
        audit_query = """
            SELECT 
                ci.item_name,
                al.checked_at,
                ci.penalty_weight
            FROM audit_log al
            JOIN checklist_items ci ON al.item_id = ci.item_id
            WHERE al.user_id = %s 
            AND YEAR(al.checked_at) = %s 
            AND al.passed = 0
            ORDER BY al.checked_at DESC
        """

        failed_items = execute_query(audit_query, (user_id, year))

        return {
            "failed_count": len(failed_items),
            "total_count": len(failed_items),  # 간단하게 처리
            "failed_items": [{
                "item_name": item["item_name"],
                "checked_at": item["checked_at"].isoformat()
                if item["checked_at"] else None,
                "penalty": float(item["penalty_weight"] or 0.5)
            } for item in failed_items]
        }

    except Exception as e:
        logging.error(f"Audit details error: {str(e)}")
        return {"failed_count": 0, "total_count": 0, "failed_items": []}


def _get_education_details_fixed(user_id, year):
    """교육 상세 내역 조회 - 수정된 스키마"""
    try:
        # security_education 테이블 구조에 맞게 조회
        education_query = """
            SELECT
                completion_status,
                completion_date
            FROM security_education
            WHERE user_id = %s 
            AND education_year = %s 
            AND completion_status != 'completed'
        """

        incomplete_items = execute_query(education_query, (user_id, year))

        return {
            "incomplete_count": len(incomplete_items),
            "total_count": len(incomplete_items),
            "incomplete_items": [
                {
                    "education_name": f"{year}년 정보보호 교육",
                    "due_date": None,  # 마감일 정보가 없음
                    "penalty": 0.5
                } for item in incomplete_items
            ]
        }

    except Exception as e:
        logging.error(f"Education details error: {str(e)}")
        return {"incomplete_count": 0, "total_count": 0, "incomplete_items": []}


def _get_training_details_fixed(user_id, year):
    """훈련 상세 내역 조회 - 수정된 스키마"""
    try:
        # phishing_training 테이블 구조에 맞게 조회
        training_query = """
            SELECT 
                training_period,
                training_result,
                email_sent_time,
                action_time
            FROM phishing_training
            WHERE user_id = %s 
            AND training_year = %s 
            AND training_result = 'fail'
        """

        failed_items = execute_query(training_query, (user_id, year))

        return {
            "failed_count": len(failed_items),
            "total_count": len(failed_items),
            "failed_items": [{
                "training_name": f"{year}년 {item['training_period']} 악성메일 모의훈련",
                "conducted_at": item["email_sent_time"].isoformat()
                if item["email_sent_time"] else None,
                "result": item["training_result"],
                "penalty": 0.5
            } for item in failed_items]
        }

    except Exception as e:
        logging.error(f"Training details error: {str(e)}")
        return {"failed_count": 0, "total_count": 0, "failed_items": []}


# 필터 옵션 API
@admin_dashboard_bp.route("/users/filters", methods=["GET"])
@token_required
@admin_required
@handle_exceptions
def get_filter_options():
    """필터 옵션 조회 - 수정된 스키마"""
    try:
        # 부서 목록 조회
        departments_query = """
            SELECT DISTINCT department 
            FROM users 
            WHERE department IS NOT NULL AND department != ''
            ORDER BY department
        """
        departments = [row['department'] for row in execute_query(departments_query)]

        return jsonify({
            "departments": departments,
            "positions": [],  # position 컬럼이 없으므로 빈 배열
            "risk_levels": [{
                "value": "low",
                "label": "낮음"
            }, {
                "value": "medium",
                "label": "보통"
            }, {
                "value": "high",
                "label": "높음"
            }, {
                "value": "critical",
                "label": "매우 높음"
            }, {
                "value": "not_evaluated",
                "label": "미평가"
            }]
        })

    except Exception as e:
        logging.error(f"Filter options error: {str(e)}")
        return jsonify({
            "error": "필터 옵션 조회 중 오류가 발생했습니다.",
            "details": str(e)
        }), HTTP_STATUS["INTERNAL_SERVER_ERROR"]


# 추가: 계산 진행 상황을 실시간으로 확인할 수 있는 API
@admin_dashboard_bp.route("/calculation-progress", methods=["GET"])
@token_required
@admin_required
@handle_exceptions
def get_calculation_progress():
    """점수 계산 진행 상황 조회 (실시간)"""
    year = request.args.get("year", datetime.now().year, type=int)

    try:
        # 전체 사용자 수
        total_users = execute_query("SELECT COUNT(*) as count FROM users",
                                    fetch_one=True)["count"]

        # 해당 연도에 계산된 사용자 수
        calculated_users = execute_query(
            "SELECT COUNT(*) as count FROM security_score_summary WHERE evaluation_year = %s",
            (year, ), fetch_one=True)["count"]

        # 최근 1분간 계산된 사용자 수 (실시간 진행률 확인용)
        recent_calculations = execute_query(
            """
            SELECT COUNT(*) as count FROM security_score_summary 
            WHERE evaluation_year = %s 
            AND last_calculated >= DATE_SUB(NOW(), INTERVAL 1 MINUTE)
            """, (year, ), fetch_one=True)["count"]

        progress_percentage = round(
            (calculated_users / total_users) * 100, 1) if total_users > 0 else 0

        return jsonify({
            "year": year,
            "total_users": total_users,
            "calculated_users": calculated_users,
            "missing_users": total_users - calculated_users,
            "progress_percentage": progress_percentage,
            "recent_calculations": recent_calculations,
            "is_complete": calculated_users >= total_users,
            "timestamp": datetime.now().isoformat()
        })

    except Exception as e:
        logging.error(f"Calculation progress error: {str(e)}")
        return jsonify({
            "error": "계산 진행 상황 조회 중 오류가 발생했습니다.",
            "details": str(e)
        }), HTTP_STATUS["INTERNAL_SERVER_ERROR"]

# 내보내기 함수도 수정
@admin_dashboard_bp.route("/export", methods=["GET"])
@token_required
@admin_required  
@handle_exceptions
def export_users():
    """사용자 데이터 내보내기 (CSV) - audit_log 기반 마지막 업데이트 포함"""
    year = request.args.get("year", datetime.now().year, type=int)
    department = request.args.get("department", "")
    risk_level = request.args.get("risk_level", "")
    search = request.args.get("search", "")
    user_ids = request.args.get("user_ids", "")
    format_type = request.args.get("format", "csv")

    try:
        logging.info(f"데이터 내보내기 요청: year={year}, format={format_type}")

        # 선택된 사용자만 내보내기
        if user_ids:
            user_id_list = [int(uid.strip()) for uid in user_ids.split(",") if uid.strip()]
            users_data = _get_selected_users_for_export(user_id_list, year)
        else:
            # 전체 또는 필터링된 데이터 내보내기
            users_data, _ = _get_filtered_users_fixed(
                year, department, risk_level, search, 1, 10000, "total_penalty", "desc"
            )

        if format_type.lower() == "csv":
            return _export_as_csv(users_data, year)
        else:
            return jsonify({"error": "지원하지 않는 형식입니다."}), HTTP_STATUS["BAD_REQUEST"]

    except Exception as e:
        logging.error(f"Export error: {str(e)}")
        return jsonify({"error": "내보내기 중 오류가 발생했습니다."}), HTTP_STATUS["INTERNAL_SERVER_ERROR"]


def _get_selected_users_for_export(user_ids, year):
    """선택된 사용자들의 데이터 조회 - audit_log 기반"""
    try:
        if not user_ids:
            return []

        placeholders = ",".join(["%s"] * len(user_ids))
        
        query = f"""
            SELECT 
                u.uid,
                u.user_id,
                u.username as name,
                u.mail as email,
                u.department,
                u.ip,
                u.role,
                COALESCE(sss.total_penalty, 0.0) as total_penalty,
                COALESCE(sss.audit_penalty, 0.0) as audit_penalty,
                COALESCE(sss.education_penalty, 0.0) as education_penalty,
                COALESCE(sss.training_penalty, 0.0) as training_penalty,
                COALESCE(sss.audit_failed_count, 0) as security_audit_penalty,
                COALESCE(sss.education_incomplete_count, 0) as education_penalty_count,
                COALESCE(sss.training_failed_count, 0) as training_penalty_count,
                -- audit_log에서 가장 최근 checked_at 시간
                (SELECT MAX(al.checked_at) 
                 FROM audit_log al 
                 WHERE al.user_id = u.uid) as last_audit_time,
                CASE 
                    WHEN sss.total_penalty IS NULL THEN 'not_evaluated'
                    WHEN sss.total_penalty > 3.0 THEN 'critical'
                    WHEN sss.total_penalty > 2.0 THEN 'high'
                    WHEN sss.total_penalty > 1.0 THEN 'medium'
                    ELSE 'low'
                END as risk_level
            FROM users u
            LEFT JOIN security_score_summary sss ON u.uid = sss.user_id AND sss.evaluation_year = %s
            WHERE u.uid IN ({placeholders})
            ORDER BY u.username ASC
        """
        
        params = [year] + user_ids
        users_data = execute_query(query, params)

        # 데이터 후처리
        for user in users_data:
            user['total_penalty'] = float(user['total_penalty'])
            user['audit_penalty'] = float(user['audit_penalty'])
            user['education_penalty'] = float(user['education_penalty'])
            user['training_penalty'] = float(user['training_penalty'])
            
            # 마지막 업데이트 시간을 audit_log 기반으로 설정
            if user['last_audit_time']:
                user['updated_at'] = user['last_audit_time']
                user['last_updated'] = user['last_audit_time'].strftime('%Y-%m-%d %H:%M:%S')
            else:
                user['last_updated'] = '업데이트 없음'

        return users_data

    except Exception as e:
        logging.error(f"Selected users export error: {str(e)}")
        return []


def _export_as_csv(users_data, year):
    """CSV 형식으로 데이터 내보내기"""
    try:
        output = io.StringIO()
        writer = csv.writer(output)

        # CSV 헤더
        headers = [
            "사번", "이름", "이메일", "부서", "IP주소", "권한",
            "총감점", "감사감점", "교육감점", "훈련감점", 
            "위험도", "마지막업데이트"
        ]
        writer.writerow(headers)

        # 데이터 행
        for user in users_data:
            risk_labels = {
                'low': '우수',
                'medium': '주의', 
                'high': '위험',
                'critical': '매우위험',
                'not_evaluated': '미평가'
            }
            
            row = [
                user.get('user_id', ''),
                user.get('name', ''),
                user.get('email', ''),
                user.get('department', ''),
                user.get('ip', ''),
                '관리자' if user.get('role') == 'admin' else '일반사용자',
                f"{user.get('total_penalty', 0):.1f}점",
                f"{user.get('audit_penalty', 0):.1f}점",
                f"{user.get('education_penalty', 0):.1f}점", 
                f"{user.get('training_penalty', 0):.1f}점",
                risk_labels.get(user.get('risk_level', 'not_evaluated'), '미평가'),
                user.get('last_updated', '업데이트 없음')
            ]
            writer.writerow(row)

        # CSV 응답 생성
        csv_data = output.getvalue()
        output.close()

        response = make_response(csv_data.encode('utf-8-sig'))  # BOM 추가로 한글 깨짐 방지
        response.headers['Content-Type'] = 'text/csv; charset=utf-8-sig'
        response.headers['Content-Disposition'] = f'attachment; filename="사용자_보안현황_{year}년_{datetime.now().strftime("%Y%m%d_%H%M")}.csv"'
        
        return response

    except Exception as e:
        logging.error(f"CSV export error: {str(e)}")
        raise