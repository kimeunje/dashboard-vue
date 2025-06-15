# app/controllers/personal_dashboard_controller.py
"""
개인 보안 점수 현황판 컨트롤러
4개 테이블(audit_log, manual_check_results, security_education, phishing_training)에서 
개인 사용자의 보안 점수 데이터를 통합하여 제공
"""

from flask import Blueprint, request, jsonify
from datetime import datetime
from app.utils.decorators import token_required, handle_exceptions
from app.utils.constants import HTTP_STATUS
from app.utils.database import DatabaseManager, execute_query
import logging

# 블루프린트 생성 (URL 접두사 포함)
personal_dashboard_bp = Blueprint("personal_dashboard", __name__, url_prefix="/api/personal-dashboard")

@personal_dashboard_bp.route("/summary", methods=["GET"])
@token_required
@handle_exceptions
def get_personal_dashboard_summary():
    """개인 보안 점수 현황 조회 - 4개 테이블 통합"""
    user = request.current_user
    username = user["username"]  # uid가 아닌 username 사용
    year = request.args.get("year", datetime.now().year, type=int)
    
    try:
        logging.info(f"개인 현황판 조회: username={username}, year={year}")
        
        # 사용자 ID 조회 (username으로 uid 찾기)
        user_data = execute_query(
            "SELECT uid FROM users WHERE user_id = %s", (username,), fetch_one=True
        )
        
        if not user_data:
            return jsonify({"error": "사용자 정보를 찾을 수 없습니다."}), HTTP_STATUS["NOT_FOUND"]
        
        user_id = user_data["uid"]
        
        # 1. 기본 사용자 정보
        user_info = _get_user_info(user_id)
        if not user_info:
            return jsonify({"error": "사용자 상세 정보를 찾을 수 없습니다."}), HTTP_STATUS["NOT_FOUND"]
        
        # 2. 상시감사 감점 및 통계
        audit_penalty, audit_stats = _calculate_audit_penalty(user_id, year)
        
        # 3. 수시감사 감점 및 통계
        manual_penalty, manual_stats = _calculate_manual_check_penalty(user_id, year)
        
        # 4. 교육 감점 및 통계
        education_penalty, education_stats = _calculate_education_penalty(user_id, year)
        
        # 5. 모의훈련 감점 및 통계
        training_penalty, training_stats = _calculate_training_penalty(user_id, year)
        
        # 6. 총 감점 계산
        total_penalty = audit_penalty + manual_penalty + education_penalty + training_penalty
        total_penalty = min(5.0, total_penalty)  # 최대 5점 감점
        
        # 7. 감점 요약 저장/업데이트
        _save_score_summary(user_id, year, audit_penalty, manual_penalty, 
                          education_penalty, training_penalty, total_penalty)
        
        response_data = {
            "user_info": user_info,
            "year": year,
            "audit_penalty": float(audit_penalty),
            "manual_check_penalty": float(manual_penalty),
            "education_penalty": float(education_penalty),
            "training_penalty": float(training_penalty),
            "total_penalty": float(total_penalty),
            "audit_stats": audit_stats,
            "manual_check_stats": manual_stats,
            "education_stats": education_stats,
            "training_stats": training_stats,
            "last_updated": datetime.now().isoformat()
        }
        
        logging.info(f"개인 현황판 응답: total_penalty={total_penalty}")
        return jsonify(response_data)
            
    except Exception as e:
        logging.error(f"Personal dashboard error: {str(e)}")
        return jsonify({
            "error": "개인 현황 조회 중 오류가 발생했습니다.",
            "details": str(e)
        }), HTTP_STATUS["INTERNAL_SERVER_ERROR"]


@personal_dashboard_bp.route("/recommendations", methods=["GET"])
@token_required
@handle_exceptions 
def get_personal_recommendations():
    """개인 보안 개선 권장사항 조회"""
    user = request.current_user
    username = user["username"]  # uid가 아닌 username 사용
    year = request.args.get("year", datetime.now().year, type=int)
    
    try:
        logging.info(f"개인 권장사항 조회: username={username}, year={year}")
        
        # 사용자 ID 조회 (username으로 uid 찾기)
        user_data = execute_query(
            "SELECT uid FROM users WHERE user_id = %s", (username,), fetch_one=True
        )
        
        if not user_data:
            return jsonify({"error": "사용자 정보를 찾을 수 없습니다."}), HTTP_STATUS["NOT_FOUND"]
        
        user_id = user_data["uid"]
        
        # 현재 감점 정보 조회
        score_summary = execute_query("""
            SELECT audit_penalty, education_penalty, training_penalty, total_penalty,
                   audit_failed_count, education_incomplete_count, training_failed_count
            FROM security_score_summary 
            WHERE user_id = %s AND evaluation_year = %s
        """, (user_id, year), fetch_one=True)
        
        if not score_summary:
            return jsonify({
                "recommendations": [], 
                "message": "점수 데이터가 없습니다."
            })
        
        recommendations = []
        
        # 교육 관련 권장사항
        if score_summary["education_penalty"] > 0:
            recommendations.append({
                "priority": "high",
                "category": "education",
                "title": "📚 정보보호 교육 이수",
                "description": f"미이수된 교육이 {score_summary['education_incomplete_count']}회 있습니다. 교육을 완료하여 -{score_summary['education_penalty']}점 감점을 해소하세요.",
                "penalty_score": float(score_summary["education_penalty"]),
                "action_url": "/security-education"
            })
        
        # 모의훈련 관련 권장사항
        if score_summary["training_penalty"] > 0:
            recommendations.append({
                "priority": "high", 
                "category": "training",
                "title": "🎯 악성메일 대응 능력 향상",
                "description": f"모의훈련에서 {score_summary['training_failed_count']}회 실패했습니다. 악성메일 식별 능력을 향상시켜 -{score_summary['training_penalty']}점 감점을 해소하세요.",
                "penalty_score": float(score_summary["training_penalty"]),
                "action_url": "/phishing-training"
            })
        
        # 감사 관련 권장사항  
        if score_summary["audit_penalty"] > 0:
            recommendations.append({
                "priority": "medium",
                "category": "audit", 
                "title": "🛡️ 보안 설정 개선",
                "description": f"{score_summary['audit_failed_count']}개 보안 설정이 정책에 맞지 않습니다. 감사 결과를 확인하고 조치하여 -{score_summary['audit_penalty']}점 감점을 해소하세요.",
                "penalty_score": float(score_summary["audit_penalty"]),
                "action_url": "/security-audit/results"
            })
        
        # 종합 권장사항
        if score_summary["total_penalty"] >= 2.0:
            recommendations.append({
                "priority": "info",
                "category": "general",
                "title": "💡 종합적인 보안 의식 개선", 
                "description": f"현재 총 -{score_summary['total_penalty']}점 감점되었습니다. 정기적인 보안 교육 참여와 정책 준수를 권장합니다.",
                "penalty_score": 0,
                "action_url": "/security-audit/solutions"
            })
        
        response_data = {
            "current_penalty": float(score_summary["total_penalty"]),
            "potential_improvement": float(score_summary["education_penalty"] + 
                                         score_summary["training_penalty"] + 
                                         score_summary["audit_penalty"]),
            "recommendations": recommendations
        }
        
        logging.info(f"개인 권장사항 응답: {len(recommendations)}개")
        return jsonify(response_data)
            
    except Exception as e:
        logging.error(f"Personal recommendations error: {str(e)}")
        return jsonify({
            "error": "권장사항 조회 중 오류가 발생했습니다.",
            "details": str(e)
        }), HTTP_STATUS["INTERNAL_SERVER_ERROR"]


def _get_user_info(user_id):
    """사용자 기본 정보 조회"""
    return execute_query("""
        SELECT uid, user_id, username, mail as email, department
        FROM users 
        WHERE uid = %s
    """, (user_id,), fetch_one=True)


def _calculate_audit_penalty(user_id, year):
    """상시감사 감점 계산 (audit_log 테이블)"""
    try:
        # 해당 연도의 최신 감사 로그 조회
        audit_logs = execute_query("""
            SELECT 
                al.item_id,
                al.passed,
                al.exclude_reason,
                ci.penalty_weight,
                ci.item_name,
                ci.category
            FROM audit_log al
            INNER JOIN (
                SELECT item_id, MAX(checked_at) as max_checked_at
                FROM audit_log 
                WHERE user_id = %s AND YEAR(checked_at) = %s
                GROUP BY item_id
            ) latest ON al.item_id = latest.item_id AND al.checked_at = latest.max_checked_at
            INNER JOIN checklist_items ci ON al.item_id = ci.item_id
            WHERE al.user_id = %s
        """, (user_id, year, user_id), fetch_all=True)

        # 통계 계산
        total_items = len(audit_logs)
        passed_items = sum(1 for log in audit_logs if log["passed"] == 1)
        failed_items = sum(1 for log in audit_logs if log["passed"] == 0)
        pending_items = sum(1 for log in audit_logs if log["passed"] is None)

        # 감점 계산 (실패한 항목만, 제외 사유가 없는 경우)
        total_penalty = 0.0
        failed_item_details = []
        
        for log in audit_logs:
            if log["passed"] == 0 and not log["exclude_reason"]:
                penalty_weight = float(log["penalty_weight"]) if log["penalty_weight"] else 0.5
                total_penalty += penalty_weight
                failed_item_details.append({
                    "item_name": log["item_name"],
                    "category": log["category"],
                    "penalty": penalty_weight
                })

        audit_stats = {
            "total_count": total_items,
            "passed_count": passed_items,
            "failed_count": failed_items,
            "pending_count": pending_items,
            "total_penalty": round(total_penalty, 2),
            "failed_items": failed_item_details
        }

        return total_penalty, audit_stats
        
    except Exception as e:
        logging.error(f"Audit penalty calculation error: {str(e)}")
        return 0.0, {"total_count": 0, "passed_count": 0, "failed_count": 0, "pending_count": 0, "total_penalty": 0.0, "failed_items": []}


def _calculate_manual_check_penalty(user_id, year):
    """수시감사 감점 계산 (manual_check_results 테이블)"""
    try:
        manual_checks = execute_query("""
            SELECT 
                check_item_code,
                overall_result,
                penalty_points,
                exclude_from_scoring
            FROM manual_check_results
            WHERE user_id = %s AND check_year = %s
        """, (user_id, year), fetch_all=True)

        if not manual_checks:
            return 0.0, {"total_count": 0, "passed_count": 0, "failed_count": 0, "total_penalty": 0.0, "items": []}

        # 통계 계산
        total_count = len(manual_checks)
        passed_count = sum(1 for check in manual_checks if check["overall_result"] == "pass")
        failed_count = sum(1 for check in manual_checks if check["overall_result"] == "fail")
        
        # 감점 계산
        total_penalty = 0.0
        check_details = []
        
        check_type_names = {
            "seal_check": "봉인씰 점검",
            "malware_scan": "악성코드 검사", 
            "file_encryption": "파일 암호화 점검"
        }
        
        for check in manual_checks:
            penalty = 0.0
            if not check["exclude_from_scoring"] and check["overall_result"] == "fail":
                penalty = float(check["penalty_points"]) if check["penalty_points"] else 0.5
                total_penalty += penalty
            
            check_details.append({
                "check_type": check_type_names.get(check["check_item_code"], check["check_item_code"]),
                "result": check["overall_result"],
                "penalty": penalty
            })

        manual_stats = {
            "total_count": total_count,
            "passed_count": passed_count,
            "failed_count": failed_count,
            "total_penalty": round(total_penalty, 2),
            "items": check_details
        }

        return total_penalty, manual_stats
        
    except Exception as e:
        logging.error(f"Manual check penalty calculation error: {str(e)}")
        return 0.0, {"total_count": 0, "passed_count": 0, "failed_count": 0, "total_penalty": 0.0, "items": []}


def _calculate_education_penalty(user_id, year):
    """정보보호 교육 감점 계산 (security_education 테이블)"""
    try:
        education_records = execute_query("""
            SELECT 
                education_period,
                completion_status,
                exclude_from_scoring
            FROM security_education
            WHERE user_id = %s AND education_year = %s
        """, (user_id, year), fetch_all=True)

        # 전체 교육 대상 (상반기, 하반기)
        expected_periods = ["first_half", "second_half"]
        
        total_penalty = 0.0
        incomplete_periods = []
        completed_count = 0
        incomplete_count = 0
        
        # 각 기간별 확인
        for period in expected_periods:
            period_record = next((r for r in education_records if r["education_period"] == period), None)
            
            if period_record:
                if not period_record["exclude_from_scoring"] and period_record["completion_status"] == 0:
                    total_penalty += 0.5
                    incomplete_count += 1
                    period_name = "상반기" if period == "first_half" else "하반기"
                    incomplete_periods.append(period_name)
                elif period_record["completion_status"] == 1:
                    completed_count += 1
            else:
                # 교육 기록이 없는 경우도 미이수로 간주
                total_penalty += 0.5
                incomplete_count += 1
                period_name = "상반기" if period == "first_half" else "하반기"
                incomplete_periods.append(period_name)

        education_stats = {
            "total_count": len(expected_periods),
            "completed_count": completed_count,
            "incomplete_count": incomplete_count,
            "total_penalty": round(total_penalty, 2),
            "incomplete_periods": incomplete_periods
        }

        return total_penalty, education_stats
        
    except Exception as e:
        logging.error(f"Education penalty calculation error: {str(e)}")
        return 0.0, {"total_count": 2, "completed_count": 0, "incomplete_count": 2, "total_penalty": 1.0, "incomplete_periods": ["상반기", "하반기"]}


def _calculate_training_penalty(user_id, year):
    """악성메일 모의훈련 감점 계산 (phishing_training 테이블)"""
    try:
        training_records = execute_query("""
            SELECT 
                training_period,
                training_result,
                exclude_from_scoring
            FROM phishing_training
            WHERE user_id = %s AND training_year = %s
        """, (user_id, year), fetch_all=True)

        # 전체 훈련 대상 (상반기, 하반기)  
        expected_periods = ["first_half", "second_half"]
        
        total_penalty = 0.0
        failed_periods = []
        passed_count = 0
        failed_count = 0
        
        # 각 기간별 확인
        for period in expected_periods:
            period_record = next((r for r in training_records if r["training_period"] == period), None)
            
            if period_record:
                if not period_record["exclude_from_scoring"] and period_record["training_result"] == "fail":
                    total_penalty += 0.5
                    failed_count += 1
                    period_name = "상반기" if period == "first_half" else "하반기"
                    failed_periods.append(period_name)
                elif period_record["training_result"] == "pass":
                    passed_count += 1
            else:
                # 훈련 기록이 없는 경우도 실패로 간주
                total_penalty += 0.5
                failed_count += 1
                period_name = "상반기" if period == "first_half" else "하반기"
                failed_periods.append(period_name)

        training_stats = {
            "total_count": len(expected_periods),
            "passed_count": passed_count,
            "failed_count": failed_count,
            "total_penalty": round(total_penalty, 2),
            "failed_periods": failed_periods
        }

        return total_penalty, training_stats
        
    except Exception as e:
        logging.error(f"Training penalty calculation error: {str(e)}")
        return 0.0, {"total_count": 2, "passed_count": 0, "failed_count": 2, "total_penalty": 1.0, "failed_periods": ["상반기", "하반기"]}


def _save_score_summary(user_id, year, audit_penalty, manual_penalty, 
                       education_penalty, training_penalty, total_penalty):
    """감점 요약 저장/업데이트 (security_score_summary 테이블)"""
    try:
        # 기존 레코드 확인
        existing = execute_query("""
            SELECT summary_id FROM security_score_summary 
            WHERE user_id = %s AND evaluation_year = %s
        """, (user_id, year), fetch_one=True)
        
        total_audit_penalty = audit_penalty + manual_penalty
        
        if existing:
            # 업데이트
            execute_query("""
                UPDATE security_score_summary 
                SET audit_penalty = %s,
                    education_penalty = %s,
                    training_penalty = %s,
                    total_penalty = %s,
                    last_calculated = NOW()
                WHERE user_id = %s AND evaluation_year = %s
            """, (total_audit_penalty, education_penalty, training_penalty, total_penalty, user_id, year))
        else:
            # 새로 삽입
            execute_query("""
                INSERT INTO security_score_summary 
                (user_id, evaluation_year, audit_penalty, education_penalty, training_penalty, total_penalty)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (user_id, year, total_audit_penalty, education_penalty, training_penalty, total_penalty))
            
        logging.info(f"Score summary saved: user_id={user_id}, year={year}, total_penalty={total_penalty}")
        
    except Exception as e:
        logging.error(f"Score summary save error: {str(e)}")
        # 저장 실패는 치명적이지 않으므로 에러를 발생시키지 않음