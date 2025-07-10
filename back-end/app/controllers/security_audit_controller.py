# app/controllers/audit_controller.py - KPI 감점 시스템으로 수정
import os
import io
import logging
from datetime import datetime
from flask import Blueprint, json, request, jsonify, send_file, current_app
from app.services.security_audit_service import AuditService
from app.utils.decorators import token_required, validate_json, handle_exceptions
from app.utils.constants import HTTP_STATUS

audit_bp = Blueprint("audit", __name__)
audit_service = AuditService()


@audit_bp.route("/stats", methods=["GET"])
@token_required
@handle_exceptions
def get_security_stats():
    """사용자별 보안 통계 데이터 조회 (하이브리드 방식)"""
    user = request.current_user
    username = user["username"]

    # 점검 유형 파라미터 (daily, manual, 또는 전체)
    check_type = request.args.get("type", None)

    # 기존 메서드 대신 하이브리드 메서드 사용
    stats = audit_service.get_user_stats_hybrid(username, check_type)
    return jsonify(stats)


@audit_bp.route("/logs", methods=["GET"])
@token_required
@handle_exceptions
def get_audit_logs():
    """사용자별 보안 감사 로그 목록 조회 (하이브리드 방식)"""
    user = request.current_user
    username = user["username"]

    # 점검 유형 파라미터 (daily, manual, 또는 전체)
    check_type = request.args.get("type", None)

    # 기존 메서드 대신 하이브리드 메서드 사용
    logs = audit_service.get_user_logs_hybrid(username, check_type)
    return jsonify(logs)


@audit_bp.route("/checklist-items", methods=["GET"])
@handle_exceptions
def get_checklist_items():
    """체크리스트 항목 조회 (하이브리드 방식)"""
    # 점검 유형 파라미터 (daily, manual, 또는 전체)
    check_type = request.args.get("type", None)

    # 기존 메서드 대신 하이브리드 메서드 사용
    items = audit_service.get_checklist_items_hybrid(check_type)
    return jsonify(items)


@audit_bp.route("/manual-check-items", methods=["GET"])
@token_required
@handle_exceptions
def get_manual_check_items():
    """수시 점검 가능한 항목 목록 조회 (감점 가중치 포함)"""
    items = audit_service.get_manual_check_items()
    return jsonify(items)


@audit_bp.route("/manual-check", methods=["POST"])
@token_required
@validate_json
@handle_exceptions
def execute_manual_check():
    """수시 점검 실행 (감점 계산 포함)"""
    user = request.current_user
    data = request.json

    # 필수 필드 검증
    required_fields = ["item_id", "actual_value", "passed"]
    missing_fields = [field for field in required_fields if field not in data]

    if missing_fields:
        return (
            jsonify(
                {"error": f"필수 필드가 누락되었습니다: {', '.join(missing_fields)}"}
            ),
            HTTP_STATUS["BAD_REQUEST"],
        )

    try:
        # 사용자 ID 가져오기
        from app.utils.database import execute_query

        user_info = execute_query(
            "SELECT uid FROM users WHERE user_id = %s",
            (user["username"],),
            fetch_one=True,
        )

        if not user_info:
            return (
                jsonify({"error": "사용자 정보를 찾을 수 없습니다."}),
                HTTP_STATUS["BAD_REQUEST"],
            )

        user_id = user_info["uid"]

        # 수시 점검 실행
        check_result = {
            "actual_value": data["actual_value"],
            "passed": data["passed"],
            "notes": data.get("notes", ""),
        }

        result = audit_service.execute_manual_check(
            user_id, data["item_id"], check_result
        )
        return jsonify(result), HTTP_STATUS["OK"]

    except ValueError as e:
        current_app.logger.error(f"수시 점검 오류: {str(e)}")
        return jsonify({"error": str(e)}), HTTP_STATUS["BAD_REQUEST"]
    except Exception as e:
        current_app.logger.error(f"서버 오류: {str(e)}")
        return (
            jsonify(
                {
                    "status": "failed",
                    "message": "서버 오류가 발생했습니다.",
                    "details": str(e) if current_app.debug else None,
                }
            ),
            HTTP_STATUS["INTERNAL_SERVER_ERROR"],
        )


@audit_bp.route("/dashboard-stats", methods=["GET"])
@token_required
@handle_exceptions
def get_dashboard_stats():
    """대시보드용 통합 통계 데이터 조회 (감점 기준)"""
    user = request.current_user
    username = user["username"]

    try:
        # 정기 점검 통계
        daily_stats = audit_service.get_user_stats(username, "daily")

        # 수시 점검 통계
        manual_stats = audit_service.get_user_stats(username, "manual")

        # 전체 통계
        total_stats = audit_service.get_user_stats(username)

        # 수정: 감점 요약 추가
        daily_penalty_summary = audit_service.get_penalty_summary(username, "daily")
        manual_penalty_summary = audit_service.get_penalty_summary(username, "manual")
        total_penalty_summary = audit_service.get_penalty_summary(username)

        return (
            jsonify(
                {
                    "daily": daily_stats,
                    "manual": manual_stats,
                    "total": total_stats,
                    "penalty_summary": {  # 수정: 감점 요약 추가
                        "daily": daily_penalty_summary,
                        "manual": manual_penalty_summary,
                        "total": total_penalty_summary,
                    },
                }
            ),
            HTTP_STATUS["OK"],
        )

    except Exception as e:
        current_app.logger.error(f"대시보드 통계 조회 오류: {str(e)}")
        return (
            jsonify({"error": "통계 데이터를 불러오는 중 오류가 발생했습니다."}),
            HTTP_STATUS["INTERNAL_SERVER_ERROR"],
        )


# 기존 validate_check 엔드포인트 (정기 점검용, 감점 계산 포함) - 강화된 디버깅
@audit_bp.route("/validate_check", methods=["POST"])
@handle_exceptions
def validate_check():
    """항목 검증 API (정기 점검용, 감점 계산 포함) - 강화된 디버깅"""
    client_ip = request.remote_addr

    current_app.logger.info(f"[VALIDATE_CHECK_DEBUG] === /validate_check 요청 시작 ===")
    current_app.logger.info(f"[VALIDATE_CHECK_DEBUG] 클라이언트 IP: {client_ip}")
    current_app.logger.info(f"[VALIDATE_CHECK_DEBUG] 요청 메서드: {request.method}")
    current_app.logger.info(
        f"[VALIDATE_CHECK_DEBUG] Content-Type: {request.content_type}"
    )
    current_app.logger.info(
        f"[VALIDATE_CHECK_DEBUG] Content-Length: {request.content_length}"
    )
    current_app.logger.info(
        f"[VALIDATE_CHECK_DEBUG] User-Agent: {request.headers.get('User-Agent', 'N/A')}"
    )

    # 모든 헤더 로깅
    current_app.logger.info(f"[VALIDATE_CHECK_DEBUG] 모든 요청 헤더:")
    for header_name, header_value in request.headers:
        current_app.logger.info(
            f"[VALIDATE_CHECK_DEBUG]   {header_name}: {header_value}"
        )

    # Raw 데이터 확인
    try:
        raw_data = request.get_data()
        current_app.logger.info(
            f"[VALIDATE_CHECK_DEBUG] Raw 요청 데이터 길이: {len(raw_data) if raw_data else 0}"
        )
        if raw_data:
            current_app.logger.info(
                f"[VALIDATE_CHECK_DEBUG] Raw 데이터: {raw_data.decode('utf-8', errors='ignore')}"
            )
    except Exception as raw_error:
        current_app.logger.error(
            f"[VALIDATE_CHECK_DEBUG] Raw 데이터 읽기 실패: {str(raw_error)}"
        )

    # JSON 파싱
    try:
        current_app.logger.info(f"[VALIDATE_CHECK_DEBUG] JSON 파싱 시도")
        data = request.json
        current_app.logger.info(f"[VALIDATE_CHECK_DEBUG] 파싱된 JSON: {data}")
    except Exception as json_error:
        current_app.logger.error(
            f"[VALIDATE_CHECK_DEBUG] JSON 파싱 실패: {str(json_error)}"
        )
        error_response = {"error": f"JSON 파싱 실패: {str(json_error)}"}
        current_app.logger.error(
            f"[VALIDATE_CHECK_DEBUG] 에러 응답 전송: {error_response}"
        )
        return jsonify(error_response), HTTP_STATUS["BAD_REQUEST"]

    if not data:
        current_app.logger.error(
            f"[VALIDATE_CHECK_DEBUG] 요청 데이터가 None 또는 빈 값"
        )
        error_response = {"error": "요청 데이터가 필요합니다."}
        current_app.logger.error(
            f"[VALIDATE_CHECK_DEBUG] 에러 응답 전송: {error_response}"
        )
        return jsonify(error_response), HTTP_STATUS["BAD_REQUEST"]

    # 필수 필드 검증
    required_fields = ["user_id", "item_type", "actual_value"]
    missing_fields = [field for field in required_fields if field not in data]

    if missing_fields:
        current_app.logger.error(
            f"[VALIDATE_CHECK_DEBUG] 필수 필드 누락: {missing_fields}"
        )
        error_response = {
            "error": f"필수 필드가 누락되었습니다: {', '.join(missing_fields)}"
        }
        current_app.logger.error(
            f"[VALIDATE_CHECK_DEBUG] 에러 응답 전송: {error_response}"
        )
        return jsonify(error_response), HTTP_STATUS["BAD_REQUEST"]

    current_app.logger.info(f"[VALIDATE_CHECK_DEBUG] 검증할 데이터:")
    current_app.logger.info(f"[VALIDATE_CHECK_DEBUG]   user_id: {data.get('user_id')}")
    current_app.logger.info(
        f"[VALIDATE_CHECK_DEBUG]   item_type: {data.get('item_type')}"
    )
    current_app.logger.info(
        f"[VALIDATE_CHECK_DEBUG]   actual_value: {data.get('actual_value')}"
    )

    try:
        current_app.logger.info(
            f"[VALIDATE_CHECK_DEBUG] audit_service.validate_check 호출 시작"
        )
        result = audit_service.validate_check(data)
        current_app.logger.info(
            f"[VALIDATE_CHECK_DEBUG] audit_service.validate_check 완료"
        )
        current_app.logger.info(f"[VALIDATE_CHECK_DEBUG] 검증 결과: {result}")

        # 성공 응답 로깅
        response_data = jsonify(result)
        current_app.logger.info(f"[VALIDATE_CHECK_DEBUG] === 성공 응답 전송 ===")
        current_app.logger.info(f"[VALIDATE_CHECK_DEBUG] 응답 상태 코드: 200")
        current_app.logger.info(f"[VALIDATE_CHECK_DEBUG] 응답 데이터: {result}")
        current_app.logger.info(
            f"[VALIDATE_CHECK_DEBUG] === /validate_check 성공 완료 ==="
        )

        return response_data

    except ValueError as e:
        current_app.logger.error(f"[VALIDATE_CHECK_DEBUG] 검증 오류: {str(e)}")
        error_response = {"error": str(e)}
        current_app.logger.error(f"[VALIDATE_CHECK_DEBUG] === ValueError 응답 전송 ===")
        current_app.logger.error(f"[VALIDATE_CHECK_DEBUG] 응답 상태 코드: 400")
        current_app.logger.error(
            f"[VALIDATE_CHECK_DEBUG] 에러 응답 데이터: {error_response}"
        )
        current_app.logger.error(
            f"[VALIDATE_CHECK_DEBUG] === /validate_check ValueError 완료 ==="
        )
        return jsonify(error_response), HTTP_STATUS["BAD_REQUEST"]

    except Exception as e:
        current_app.logger.error(f"[VALIDATE_CHECK_DEBUG] 서버 오류: {str(e)}")
        import traceback

        current_app.logger.error(
            f"[VALIDATE_CHECK_DEBUG] 스택 트레이스: {traceback.format_exc()}"
        )

        error_response = {
            "status": "failed",
            "message": "서버 오류가 발생했습니다.",
            "details": str(e) if current_app.debug else None,
        }
        current_app.logger.error(f"[VALIDATE_CHECK_DEBUG] === Exception 응답 전송 ===")
        current_app.logger.error(f"[VALIDATE_CHECK_DEBUG] 응답 상태 코드: 500")
        current_app.logger.error(
            f"[VALIDATE_CHECK_DEBUG] 에러 응답 데이터: {error_response}"
        )
        current_app.logger.error(
            f"[VALIDATE_CHECK_DEBUG] === /validate_check Exception 완료 ==="
        )

        return jsonify(error_response), HTTP_STATUS["INTERNAL_SERVER_ERROR"]


# 로그 수신 엔드포인트 (기존 mock_app.py에서 이동)
@audit_bp.route("/log", methods=["POST"])
@handle_exceptions
def receive_log():
    """클라이언트 로그 수신"""
    try:
        data = request.get_json()
        client_ip = request.remote_addr

        # 필수 필드 검증
        required_fields = ["timestamp", "level", "message"]
        if not all(field in data for field in required_fields):
            return (
                jsonify({"error": "필수 필드가 누락되었습니다"}),
                HTTP_STATUS["BAD_REQUEST"],
            )

        # 로그 저장
        log_dir = current_app.config["LOG_DIR"]
        os.makedirs(log_dir, exist_ok=True)

        log_file = f"{log_dir}/{datetime.now().strftime('%Y-%m-%d')}.log"
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(
                f"[{data['timestamp']}] [{client_ip}] [{data['level']}] {data['message']}\n"
            )

        # 로그 레벨에 따른 처리
        if data["level"] == "FAIL":
            logging.error(data["message"])
        elif data["level"] == "PASS":
            logging.info(data["message"])
        else:
            logging.info(data["message"])

        return jsonify({"status": "연결 성공"}), HTTP_STATUS["OK"]

    except Exception as e:
        logging.error(f"로그 처리 오류: {str(e)}")
        return (
            jsonify({"error": "로그 처리 중 오류 발생"}),
            HTTP_STATUS["INTERNAL_SERVER_ERROR"],
        )


# 수시 점검 실행 결과 조회 (추가 기능)
@audit_bp.route("/manual-check-history/<int:item_id>", methods=["GET"])
@token_required
@handle_exceptions
def get_manual_check_history(item_id):
    """특정 수시 점검 항목의 실행 이력 조회 (감점 정보 포함)"""
    user = request.current_user
    username = user["username"]

    try:
        from app.utils.database import execute_query

        # 사용자 ID 가져오기
        user_info = execute_query(
            "SELECT uid FROM users WHERE user_id = %s", (username,), fetch_one=True
        )

        if not user_info:
            return (
                jsonify({"error": "사용자 정보를 찾을 수 없습니다."}),
                HTTP_STATUS["BAD_REQUEST"],
            )

        user_id = user_info["uid"]

        # 수정: 특정 항목의 수시 점검 이력 조회 (감점 정보 포함)
        history = execute_query(
            """
            SELECT al.log_id, al.actual_value, al.passed, al.notes, al.checked_at,
                   ci.item_name, ci.category, ci.penalty_weight,
                   CASE WHEN al.passed = 0 THEN COALESCE(ci.penalty_weight, 0.5) ELSE 0 END as penalty_applied
            FROM audit_log al
            LEFT JOIN checklist_items ci ON al.item_id = ci.item_id
            WHERE al.user_id = %s AND al.item_id = %s AND ci.check_type = 'manual'
            ORDER BY al.checked_at DESC
            LIMIT 10
            """,
            (user_id, item_id),
            fetch_all=True,
        )

        # 결과 포맷팅
        result = []
        for record in history:
            # JSON 파싱
            if isinstance(record["actual_value"], str):
                actual_value = json.loads(record["actual_value"])
            else:
                actual_value = record["actual_value"]

            # 날짜 포맷팅
            if isinstance(record["checked_at"], datetime):
                checked_at = record["checked_at"].strftime("%Y-%m-%d %H:%M:%S")
            else:
                checked_at = record["checked_at"]

            result.append(
                {
                    "log_id": record["log_id"],
                    "item_name": record["item_name"],
                    "category": record["category"],
                    "actual_value": actual_value,
                    "passed": record["passed"],
                    "notes": record["notes"],
                    "checked_at": checked_at,
                    "penalty_weight": float(
                        record["penalty_weight"] or 0
                    ),  # 수정: 감점 가중치 추가
                    "penalty_applied": float(
                        record["penalty_applied"] or 0
                    ),  # 수정: 적용된 감점 추가
                }
            )

        return jsonify(result), HTTP_STATUS["OK"]

    except Exception as e:
        current_app.logger.error(f"수시 점검 이력 조회 오류: {str(e)}")
        return (
            jsonify({"error": "이력 조회 중 오류가 발생했습니다."}),
            HTTP_STATUS["INTERNAL_SERVER_ERROR"],
        )


@audit_bp.route("/penalty-summary", methods=["GET"])
@token_required
@handle_exceptions
def get_penalty_summary():
    """감점 요약 정보 조회 (새로운 엔드포인트)"""
    user = request.current_user
    username = user["username"]
    check_type = request.args.get("type", None)

    try:
        penalty_summary = audit_service.get_penalty_summary(username, check_type)
        return jsonify(penalty_summary), HTTP_STATUS["OK"]
    except Exception as e:
        current_app.logger.error(f"감점 요약 조회 오류: {str(e)}")
        return (
            jsonify({"error": "감점 요약 조회 중 오류가 발생했습니다."}),
            HTTP_STATUS["INTERNAL_SERVER_ERROR"],
        )


@audit_bp.route("/penalty-breakdown", methods=["GET"])
@token_required
@handle_exceptions
def get_penalty_breakdown():
    """항목별 감점 분석 (새로운 엔드포인트)"""
    user = request.current_user
    username = user["username"]
    check_type = request.args.get("type", None)

    try:
        from app.utils.database import execute_query

        # 사용자 ID 가져오기
        user_info = execute_query(
            "SELECT uid FROM users WHERE user_id = %s", (username,), fetch_one=True
        )

        if not user_info:
            return (
                jsonify({"error": "사용자 정보를 찾을 수 없습니다."}),
                HTTP_STATUS["BAD_REQUEST"],
            )

        user_id = user_info["uid"]

        # 점검 유형별 조건 설정
        if check_type:
            type_condition = "AND ci.check_type = %s"
            params = (user_id, check_type)
        else:
            type_condition = ""
            params = (user_id,)

        # 항목별 감점 분석
        breakdown = execute_query(
            f"""
            SELECT 
                ci.item_name,
                ci.category,
                ci.check_type,
                ci.penalty_weight,
                al.passed,
                al.checked_at,
                CASE WHEN al.passed = 0 THEN ci.penalty_weight ELSE 0 END as penalty_applied,
                al.notes
            FROM audit_log al
            INNER JOIN (
                SELECT item_id, MAX(checked_at) as max_checked_at
                FROM audit_log 
                WHERE user_id = %s
                GROUP BY item_id
            ) latest ON al.item_id = latest.item_id AND al.checked_at = latest.max_checked_at
            INNER JOIN checklist_items ci ON al.item_id = ci.item_id
            WHERE al.user_id = %s {type_condition}
            ORDER BY penalty_applied DESC, ci.category, ci.item_name
            """,
            params,
            fetch_all=True,
        )

        # 총 감점 계산
        total_penalty = sum(float(item["penalty_applied"] or 0) for item in breakdown)
        failed_items = sum(1 for item in breakdown if item["passed"] == 0)

        return (
            jsonify(
                {
                    "breakdown": breakdown,
                    "summary": {
                        "total_penalty": round(total_penalty, 1),
                        "failed_items": failed_items,
                        "total_items": len(breakdown),
                        "check_type": check_type,
                    },
                }
            ),
            HTTP_STATUS["OK"],
        )

    except Exception as e:
        current_app.logger.error(f"감점 분석 조회 오류: {str(e)}")
        return (
            jsonify({"error": "감점 분석 조회 중 오류가 발생했습니다."}),
            HTTP_STATUS["INTERNAL_SERVER_ERROR"],
        )


# 수시 점검 결과 조회용 새 엔드포인트 (manual_check_results 테이블 사용)
@audit_bp.route("/manual-check-logs", methods=["GET"])
@token_required
@handle_exceptions
def get_manual_check_logs():
    """수시 점검 로그 조회 (manual_check_results 테이블에서)"""
    user = request.current_user
    username = user["username"]

    try:
        logs = audit_service.get_manual_check_logs_from_results(username)
        return jsonify(logs), HTTP_STATUS["OK"]
    except Exception as e:
        current_app.logger.error(f"수시 점검 로그 조회 오류: {str(e)}")
        return (
            jsonify({"error": "수시 점검 로그 조회 중 오류가 발생했습니다."}),
            HTTP_STATUS["INTERNAL_SERVER_ERROR"],
        )


# 수시 점검 통계 조회용 새 엔드포인트 (manual_check_results 테이블 사용)
@audit_bp.route("/manual-check-stats", methods=["GET"])
@token_required
@handle_exceptions
def get_manual_check_stats():
    """수시 점검 통계 조회 (manual_check_results 테이블에서)"""
    user = request.current_user
    username = user["username"]

    try:
        stats = audit_service.get_manual_check_stats_from_results(username)
        return jsonify(stats), HTTP_STATUS["OK"]
    except Exception as e:
        current_app.logger.error(f"수시 점검 통계 조회 오류: {str(e)}")
        return (
            jsonify({"error": "수시 점검 통계 조회 중 오류가 발생했습니다."}),
            HTTP_STATUS["INTERNAL_SERVER_ERROR"],
        )


# 수시 점검 항목 목록 조회용 새 엔드포인트 (manual_check_items 테이블 사용)
@audit_bp.route("/manual-check-items-from-table", methods=["GET"])
@handle_exceptions
def get_manual_check_items_from_table():
    """수시 점검 항목 목록 조회 (manual_check_items 테이블에서)"""
    try:
        items = audit_service.get_manual_check_items_from_table()
        return jsonify(items), HTTP_STATUS["OK"]
    except Exception as e:
        current_app.logger.error(f"수시 점검 항목 조회 오류: {str(e)}")
        return (
            jsonify({"error": "수시 점검 항목 조회 중 오류가 발생했습니다."}),
            HTTP_STATUS["INTERNAL_SERVER_ERROR"],
        )
