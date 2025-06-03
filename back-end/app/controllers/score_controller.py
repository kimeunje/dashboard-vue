# app/controllers/score_controller.py - 완성된 버전
from datetime import datetime
from flask import Blueprint, request, jsonify
from app.services.score_service import ScoreService
from app.utils.decorators import token_required, handle_exceptions
from app.utils.constants import HTTP_STATUS

score_bp = Blueprint("score", __name__)
score_service = ScoreService()


@score_bp.route("/summary", methods=["GET"])
@token_required
@handle_exceptions
def get_security_score_summary():
    """사용자의 종합 보안 점수 요약 조회"""
    user = request.current_user
    username = user["username"]

    # 요청 파라미터에서 연도 가져오기 (기본값: 현재 연도)
    year = request.args.get("year", datetime.now().year, type=int)

    try:
        score_data = score_service.get_user_security_score(username, year)

        # 프론트엔드에서 기대하는 형식으로 데이터 변환
        response_data = {
            "user_id": score_data["user_id"],
            "year": score_data["year"],
            "audit_score": score_data["audit_score"],
            "audit_penalty": score_data["audit_penalty"],
            "education_penalty": score_data["education_penalty"],
            "training_penalty": score_data["training_penalty"],
            "total_score": score_data["total_score"],
            "grade": score_data["grade"],
            "education_stats": score_data["education_stats"],
            "training_stats": score_data["training_stats"],
            "audit_stats": score_data["audit_stats"],
        }

        return jsonify(response_data)
    except ValueError as e:
        return jsonify({"message": str(e)}), HTTP_STATUS["NOT_FOUND"]
    except Exception as e:
        return (
            jsonify({"error": "점수 계산 중 오류가 발생했습니다.", "details": str(e)}),
            HTTP_STATUS["INTERNAL_SERVER_ERROR"],
        )


@score_bp.route("/dashboard/overview", methods=["GET"])
@token_required
@handle_exceptions
def get_security_dashboard_overview():
    """종합 보안 대시보드 데이터 조회"""
    user = request.current_user
    username = user["username"]

    year = request.args.get("year", datetime.now().year, type=int)

    try:
        dashboard_data = score_service.get_dashboard_overview(username, year)
        return jsonify(dashboard_data)
    except ValueError as e:
        return jsonify({"message": str(e)}), HTTP_STATUS["NOT_FOUND"]
    except Exception as e:
        return (
            jsonify(
                {
                    "error": "대시보드 데이터 조회 중 오류가 발생했습니다.",
                    "details": str(e),
                }
            ),
            HTTP_STATUS["INTERNAL_SERVER_ERROR"],
        )


@score_bp.route("/calculate", methods=["POST"])
@token_required
@handle_exceptions
def calculate_security_score():
    """보안 점수 강제 재계산"""
    user = request.current_user
    username = user["username"]

    data = request.json or {}
    year = data.get("year", datetime.now().year)

    try:
        # 사용자 ID 조회
        from app.utils.database import execute_query

        user_data = execute_query(
            "SELECT uid FROM users WHERE user_id = %s", (username,), fetch_one=True
        )

        if not user_data:
            return (
                jsonify({"error": "사용자를 찾을 수 없습니다."}),
                HTTP_STATUS["NOT_FOUND"],
            )

        # 점수 재계산
        score_data = score_service.calculate_security_score(user_data["uid"], year)

        return jsonify(
            {
                "message": "보안 점수가 성공적으로 재계산되었습니다.",
                "score_data": score_data,
            }
        )
    except Exception as e:
        return (
            jsonify(
                {"error": "점수 재계산 중 오류가 발생했습니다.", "details": str(e)}
            ),
            HTTP_STATUS["INTERNAL_SERVER_ERROR"],
        )


@score_bp.route("/history", methods=["GET"])
@token_required
@handle_exceptions
def get_score_history():
    """사용자의 연도별 점수 이력 조회"""
    user = request.current_user
    username = user["username"]

    try:
        from app.utils.database import execute_query

        # 사용자 ID 조회
        user_data = execute_query(
            "SELECT uid FROM users WHERE user_id = %s", (username,), fetch_one=True
        )
        if not user_data:
            return (
                jsonify({"error": "사용자를 찾을 수 없습니다."}),
                HTTP_STATUS["NOT_FOUND"],
            )

        user_id = user_data["uid"]

        # 최근 3년간의 점수 이력 조회
        current_year = datetime.now().year
        years = [current_year - 2, current_year - 1, current_year]

        history = []
        for year in years:
            try:
                score_data = score_service.calculate_security_score(user_id, year)
                history.append(
                    {
                        "year": year,
                        "total_score": score_data["total_score"],
                        "grade": score_data["grade"],
                        "audit_score": score_data["audit_score"],
                        "audit_penalty": score_data["audit_penalty"],
                        "education_penalty": score_data["education_penalty"],
                        "training_penalty": score_data["training_penalty"],
                    }
                )
            except Exception as e:
                # 해당 연도 데이터가 없으면 건너뛰기
                continue

        return jsonify({"username": username, "history": history})
    except Exception as e:
        return (
            jsonify(
                {"error": "점수 이력 조회 중 오류가 발생했습니다.", "details": str(e)}
            ),
            HTTP_STATUS["INTERNAL_SERVER_ERROR"],
        )


@score_bp.route("/breakdown", methods=["GET"])
@token_required
@handle_exceptions
def get_score_breakdown():
    """점수 구성 요소별 상세 분석"""
    user = request.current_user
    username = user["username"]

    year = request.args.get("year", datetime.now().year, type=int)

    try:
        from app.utils.database import execute_query, DatabaseManager

        # 사용자 ID 조회
        user_data = execute_query(
            "SELECT uid FROM users WHERE user_id = %s", (username,), fetch_one=True
        )
        if not user_data:
            return (
                jsonify({"error": "사용자를 찾을 수 없습니다."}),
                HTTP_STATUS["NOT_FOUND"],
            )

        user_id = user_data["uid"]

        with DatabaseManager.get_db_cursor(commit=False) as cursor:
            # 감사 항목별 상세 정보
            cursor.execute(
                """
                SELECT 
                    ci.item_name,
                    ci.category,
                    ci.penalty_weight,
                    al.passed,
                    al.checked_at,
                    al.notes
                FROM audit_log al
                INNER JOIN (
                    SELECT item_id, MAX(checked_at) as max_checked_at
                    FROM audit_log 
                    WHERE user_id = %s AND YEAR(checked_at) = %s
                    GROUP BY item_id
                ) latest ON al.item_id = latest.item_id AND al.checked_at = latest.max_checked_at
                INNER JOIN checklist_items ci ON al.item_id = ci.item_id
                WHERE al.user_id = %s
                ORDER BY ci.category, ci.item_name
                """,
                (user_id, year, user_id),
            )
            audit_breakdown = cursor.fetchall()

            # 교육 상세 정보
            cursor.execute(
                """
                SELECT 
                    education_period,
                    education_type,
                    education_date,
                    completion_status,
                    score,
                    exclude_from_scoring,
                    notes
                FROM security_education
                WHERE user_id = %s AND education_year = %s
                ORDER BY education_period
                """,
                (user_id, year),
            )
            education_breakdown = cursor.fetchall()

            # 모의훈련 상세 정보
            cursor.execute(
                """
                SELECT 
                    training_period,
                    email_sent_time,
                    action_time,
                    log_type,
                    mail_type,
                    training_result,
                    response_time_minutes,
                    exclude_from_scoring,
                    notes
                FROM phishing_training
                WHERE user_id = %s AND training_year = %s
                ORDER BY training_period
                """,
                (user_id, year),
            )
            training_breakdown = cursor.fetchall()

        return jsonify(
            {
                "year": year,
                "audit_breakdown": audit_breakdown,
                "education_breakdown": education_breakdown,
                "training_breakdown": training_breakdown,
            }
        )
    except Exception as e:
        return (
            jsonify({"error": "점수 분석 중 오류가 발생했습니다.", "details": str(e)}),
            HTTP_STATUS["INTERNAL_SERVER_ERROR"],
        )


@score_bp.route("/recommendations", methods=["GET"])
@token_required
@handle_exceptions
def get_improvement_recommendations():
    """개선 권장사항 조회"""
    user = request.current_user
    username = user["username"]

    year = request.args.get("year", datetime.now().year, type=int)

    try:
        # 현재 점수 조회
        score_data = score_service.get_user_security_score(username, year)

        recommendations = []

        # 교육 관련 권장사항
        if score_data["education_penalty"] > 0:
            incomplete_count = score_data["education_stats"]["incomplete_count"]
            recommendations.append(
                {
                    "priority": "high",
                    "category": "education",
                    "title": "정보보호 교육 이수",
                    "description": f'미이수된 교육이 {incomplete_count}회 있습니다. 교육을 완료하여 {score_data["education_penalty"]}점 감점을 해소하세요.',
                    "impact_score": score_data["education_penalty"],
                    "action_url": "/security-education",
                }
            )

        # 모의훈련 관련 권장사항
        if score_data["training_penalty"] > 0:
            failed_count = score_data["training_stats"]["failed_count"]
            recommendations.append(
                {
                    "priority": "high",
                    "category": "training",
                    "title": "악성메일 대응 능력 향상",
                    "description": f'모의훈련에서 {failed_count}회 실패했습니다. 악성메일 식별 능력을 향상시켜 {score_data["training_penalty"]}점 감점을 해소하세요.',
                    "impact_score": score_data["training_penalty"],
                    "action_url": "/phishing-training",
                }
            )

        # 감사 관련 권장사항
        if score_data["audit_penalty"] > 0:
            failed_count = score_data["audit_stats"]["failed_count"]
            recommendations.append(
                {
                    "priority": "medium",
                    "category": "audit",
                    "title": "보안 설정 개선",
                    "description": f'{failed_count}개 보안 설정이 정책에 맞지 않습니다. 감사 결과를 확인하고 조치하여 {score_data["audit_penalty"]}점 감점을 해소하세요.',
                    "impact_score": score_data["audit_penalty"],
                    "action_url": "/security-audit/results",
                }
            )

        # 총 점수에 따른 일반적인 권장사항
        if score_data["total_score"] < 80:
            recommendations.append(
                {
                    "priority": "info",
                    "category": "general",
                    "title": "종합적인 보안 의식 개선",
                    "description": f'현재 보안 점수가 {score_data["total_score"]:.1f}점으로 낮습니다. 정기적인 보안 교육 참여와 정책 준수를 권장합니다.',
                    "impact_score": 0,
                    "action_url": "/security-audit/solutions",
                }
            )

        return jsonify(
            {
                "current_score": score_data["total_score"],
                "grade": score_data["grade"],
                "potential_improvement": score_data["education_penalty"]
                + score_data["training_penalty"]
                + score_data["audit_penalty"],
                "recommendations": recommendations,
            }
        )
    except Exception as e:
        return (
            jsonify(
                {"error": "권장사항 조회 중 오류가 발생했습니다.", "details": str(e)}
            ),
            HTTP_STATUS["INTERNAL_SERVER_ERROR"],
        )
