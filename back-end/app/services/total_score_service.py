# app/services/total_score_service.py - DB 스키마에 맞게 수정

from datetime import datetime
from app.utils.database import execute_query, DatabaseManager
import logging


class ScoreService:
    """KPI 보안 감점 계산 관련 서비스 - 실제 DB 스키마에 맞춘 버전"""

    def get_user_security_score(self, username: str, year: int = None) -> dict:
        """사용자명으로 보안 감점 조회"""
        if year is None:
            year = datetime.now().year

        # 사용자 ID 가져오기
        user = execute_query(
            "SELECT uid FROM users WHERE user_id = %s", (username,), fetch_one=True
        )

        if not user:
            raise ValueError("사용자를 찾을 수 없습니다.")

        return self.calculate_security_score(user["uid"], year)

    def calculate_security_score(self, user_id: int, year: int = None) -> dict:
        """사용자의 KPI 보안 감점 계산 - 실제 DB 스키마 기반"""
        if year is None:
            year = datetime.now().year

        logging.info(f"점수 계산 시작: user_id={user_id}, year={year}")

        with DatabaseManager.get_db_cursor() as cursor:
            # 1. 상시감사 감점 계산 (audit_log + manual_check_results)
            audit_penalty, audit_stats = self._calculate_audit_penalty_from_real_data(
                cursor, user_id, year
            )
            logging.info(f"감사 감점 계산 완료: {audit_penalty}")

            # 2. 교육 감점 계산 (security_education 테이블)
            education_penalty, education_stats = (
                self._calculate_education_penalty_from_real_data(cursor, user_id, year)
            )
            logging.info(f"교육 감점 계산 완료: {education_penalty}")

            # 3. 모의훈련 감점 계산 (phishing_training 테이블)
            training_penalty, training_stats = (
                self._calculate_training_penalty_from_real_data(cursor, user_id, year)
            )
            logging.info(f"훈련 감점 계산 완료: {training_penalty}")

            # 4. 총 감점 계산 (최대 -5.0점)
            total_penalty = audit_penalty + education_penalty + training_penalty
            total_penalty = min(5.0, total_penalty)  # 최대 5점 감점

            # 5. 감점 요약 저장
            self._save_score_summary(
                cursor,
                user_id,
                year,
                audit_penalty,
                education_penalty,
                training_penalty,
                total_penalty,
                education_stats,
                training_stats,
                audit_stats,
            )
            logging.info(f"점수 저장 완료: total_penalty={total_penalty}")

            return {
                "user_id": user_id,
                "year": year,
                "audit_penalty": float(audit_penalty),
                "education_penalty": float(education_penalty),
                "training_penalty": float(training_penalty),
                "total_penalty": float(total_penalty),
                "education_stats": education_stats,
                "training_stats": training_stats,
                "audit_stats": audit_stats,
            }

    def _calculate_audit_penalty_from_real_data(
        self, cursor, user_id: int, year: int
    ) -> tuple:
        """실제 DB 스키마를 바탕으로 감사 감점 계산"""

        # 1. audit_log에서 상시감사 로그 조회 (daily 타입만)
        cursor.execute(
            """
            SELECT 
                al.log_id,
                al.item_id,
                al.passed,
                al.checked_at,
                ci.item_name,
                ci.penalty_weight
            FROM audit_log al
            INNER JOIN checklist_items ci ON al.item_id = ci.item_id
            WHERE al.user_id = %s 
            AND YEAR(al.checked_at) = %s 
            AND ci.check_type = 'daily'
            ORDER BY al.checked_at DESC
            """,
            (user_id, year),
        )

        audit_logs = cursor.fetchall()

        # 2. manual_check_results에서 수시감사 로그 조회
        cursor.execute(
            """
            SELECT 
                mcr.check_id,
                mcr.check_item_code,
                mcr.overall_result,
                mcr.check_date,
                mcr.exclude_from_scoring,
                0.5 as penalty_weight
            FROM manual_check_results mcr
            WHERE mcr.user_id = %s 
            AND mcr.check_year = %s
            ORDER BY mcr.check_date DESC
            """,
            (user_id, year),
        )

        manual_checks = cursor.fetchall()

        # 3. 감점 계산
        total_penalty = 0.0
        failed_items = []

        # audit_log 감점 계산
        audit_failed_count = 0
        for log in audit_logs:
            if log["passed"] == 0:  # 실패한 경우
                penalty = float(log["penalty_weight"]) if log["penalty_weight"] else 0.5
                total_penalty += penalty
                audit_failed_count += 1
                failed_items.append(
                    {
                        "item_name": log["item_name"],
                        "checked_at": log["checked_at"],
                        "penalty": penalty,
                        "source": "audit_log",
                    }
                )

        # manual_check_results 감점 계산
        manual_failed_count = 0
        for check in manual_checks:
            if check["overall_result"] == "fail" and check["exclude_from_scoring"] == 0:
                penalty = float(check["penalty_weight"])
                total_penalty += penalty
                manual_failed_count += 1
                failed_items.append(
                    {
                        "item_name": f"수시감사 - {check['check_item_code']}",
                        "checked_at": check["check_date"],
                        "penalty": penalty,
                        "source": "manual_check_results",
                    }
                )

        audit_stats = {
            "total_count": len(audit_logs) + len(manual_checks),
            "passed_count": len(audit_logs)
            - audit_failed_count
            + len([c for c in manual_checks if c["overall_result"] == "pass"]),
            "failed_count": audit_failed_count + manual_failed_count,
            "pending_count": len([log for log in audit_logs if log["passed"] is None]),
            "total_penalty": round(total_penalty, 2),
            "failed_items": failed_items,
            "audit_log_count": len(audit_logs),
            "manual_check_count": len(manual_checks),
        }

        return total_penalty, audit_stats

    def _calculate_education_penalty_from_real_data(
        self, cursor, user_id: int, year: int
    ) -> tuple:
        """실제 DB 스키마를 바탕으로 교육 감점 계산"""

        cursor.execute(
            """
            SELECT 
                education_id,
                education_period,
                completion_status
            FROM security_education 
            WHERE user_id = %s 
            AND education_year = %s
            """,
            (user_id, year),
        )

        education_records = cursor.fetchall()

        # 교육 데이터가 없는 경우 기본 감점 적용
        if not education_records:
            # 연도별 필수 교육 회차 (상반기, 하반기)
            required_sessions = 2
            education_penalty = required_sessions * 0.5

            education_stats = {
                "total_required": required_sessions,
                "completed_count": 0,
                "incomplete_count": required_sessions,
                "total_penalty": education_penalty,
                "incomplete_sessions": [f"{year}년 상반기", f"{year}년 하반기"],
            }

            return education_penalty, education_stats

        # 실제 교육 기록이 있는 경우
        completed_count = sum(
            1 for record in education_records if record["completion_status"] == 1
        )
        incomplete_count = sum(
            1 for record in education_records if record["completion_status"] == 0
        )

        education_penalty = incomplete_count * 0.5

        incomplete_sessions = []
        for record in education_records:
            if record["completion_status"] == 0:
                incomplete_sessions.append(f"{year}년 {record['education_period']}")

        education_stats = {
            "total_required": len(education_records),
            "completed_count": completed_count,
            "incomplete_count": incomplete_count,
            "total_penalty": round(education_penalty, 2),
            "incomplete_sessions": incomplete_sessions,
        }

        return education_penalty, education_stats

    def _calculate_training_penalty_from_real_data(
        self, cursor, user_id: int, year: int
    ) -> tuple:
        """실제 DB 스키마를 바탕으로 모의훈련 감점 계산"""

        cursor.execute(
            """
            SELECT 
                training_id,
                training_period,
                training_result
            FROM phishing_training 
            WHERE user_id = %s 
            AND training_year = %s
            """,
            (user_id, year),
        )

        training_records = cursor.fetchall()

        # 훈련 데이터가 없는 경우 기본 감점 적용
        if not training_records:
            # 연도별 필수 훈련 회차 (상반기, 하반기)
            required_sessions = 2
            training_penalty = required_sessions * 0.5

            training_stats = {
                "total_required": required_sessions,
                "passed_count": 0,
                "failed_count": required_sessions,
                "total_penalty": training_penalty,
                "failed_sessions": [f"{year}년 상반기", f"{year}년 하반기"],
            }

            return training_penalty, training_stats

        # 실제 훈련 기록이 있는 경우
        passed_count = sum(
            1 for record in training_records if record["training_result"] == "pass"
        )
        failed_count = sum(
            1 for record in training_records if record["training_result"] == "fail"
        )

        training_penalty = failed_count * 0.5

        failed_sessions = []
        for record in training_records:
            if record["training_result"] == "fail":
                failed_sessions.append(f"{year}년 {record['training_period']}")

        training_stats = {
            "total_required": len(training_records),
            "passed_count": passed_count,
            "failed_count": failed_count,
            "total_penalty": round(training_penalty, 2),
            "failed_sessions": failed_sessions,
        }

        return training_penalty, training_stats

    def _save_score_summary(
        self,
        cursor,
        user_id: int,
        year: int,
        audit_penalty: float,
        education_penalty: float,
        training_penalty: float,
        total_penalty: float,
        education_stats: dict,
        training_stats: dict,
        audit_stats: dict,
    ):
        """KPI 감점 요약 저장"""
        cursor.execute(
            """
            INSERT INTO security_score_summary 
            (user_id, evaluation_year, audit_penalty, education_penalty, 
            training_penalty, total_penalty, audit_failed_count, education_incomplete_count,
            training_failed_count)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
            audit_penalty = VALUES(audit_penalty),
            education_penalty = VALUES(education_penalty),
            training_penalty = VALUES(training_penalty),
            total_penalty = VALUES(total_penalty),
            audit_failed_count = VALUES(audit_failed_count),
            education_incomplete_count = VALUES(education_incomplete_count),
            training_failed_count = VALUES(training_failed_count),
            last_calculated = NOW()
            """,
            (
                user_id,
                year,
                audit_penalty,
                education_penalty,
                training_penalty,
                total_penalty,
                audit_stats["failed_count"],
                education_stats["incomplete_count"],
                training_stats["failed_count"],
            ),
        )

    def get_dashboard_overview(self, username: str, year: int = None) -> dict:
        """대시보드용 KPI 감점 정보 조회"""
        if year is None:
            year = datetime.now().year

        # 사용자 감점 정보 가져오기
        score_data = self.get_user_security_score(username, year)

        # 추가 대시보드 정보 생성
        dashboard_data = {
            "user_score": score_data,
            "risk_level": self._calculate_risk_level(score_data["total_penalty"]),
            "last_updated": datetime.now().isoformat(),
        }

        return dashboard_data

    def _calculate_risk_level(self, total_penalty: float) -> str:
        """위험도 계산"""
        if total_penalty >= 3.0:
            return "critical"
        elif total_penalty >= 2.0:
            return "high"
        elif total_penalty >= 1.0:
            return "medium"
        elif total_penalty > 0:
            return "low"
        else:
            return "excellent"
