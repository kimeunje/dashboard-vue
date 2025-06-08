# app/services/score_service.py - KPI 감점 시스템으로 수정
from datetime import datetime
from app.utils.database import execute_query, DatabaseManager


class ScoreService:
    """KPI 보안 감점 계산 관련 서비스 (100점 기준 제거, 감점만 계산)"""

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
        """사용자의 KPI 보안 감점 계산 (감점만 계산, 100점 기준 제거)"""
        if year is None:
            year = datetime.now().year

        with DatabaseManager.get_db_cursor() as cursor:
            # 1. 상시감사 감점 계산 (실패 항목당 0.5점 감점)
            audit_penalty, audit_stats = self._calculate_audit_penalty(
                cursor, user_id, year
            )

            # 2. 교육 감점 계산 (미이수 시 0.5점 감점)
            education_penalty, education_stats = self._calculate_education_penalty(
                cursor, user_id, year
            )

            # 3. 모의훈련 감점 계산 (실패 시 0.5점 감점)
            training_penalty, training_stats = self._calculate_training_penalty(
                cursor, user_id, year
            )

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

            return {
                "user_id": user_id,
                "year": year,
                "audit_penalty": float(audit_penalty),  # 수정: audit_score 제거
                "education_penalty": float(education_penalty),
                "training_penalty": float(training_penalty),
                "total_penalty": float(total_penalty),  # 수정: total_score -> total_penalty
                "education_stats": education_stats,
                "training_stats": training_stats,
                "audit_stats": audit_stats,
            }

    def _calculate_audit_penalty(self, cursor, user_id: int, year: int) -> tuple:
        """상시감사 감점 계산 (100점 기준 제거, 실패 항목당 0.5점 감점)"""

        # 해당 연도의 최신 감사 로그 조회 (각 항목별 최신 기록만)
        cursor.execute(
            """
            SELECT 
                al.item_id,
                al.passed,
                ci.penalty_weight,
                ci.item_name,
                ci.check_type
            FROM audit_log al
            INNER JOIN (
                SELECT item_id, MAX(checked_at) as max_checked_at
                FROM audit_log 
                WHERE user_id = %s AND YEAR(checked_at) = %s
                GROUP BY item_id
            ) latest ON al.item_id = latest.item_id AND al.checked_at = latest.max_checked_at
            INNER JOIN checklist_items ci ON al.item_id = ci.item_id
            WHERE al.user_id = %s
            """,
            (user_id, year, user_id),
        )

        audit_logs = cursor.fetchall()

        # 통계 계산
        total_items = len(audit_logs)
        passed_items = sum(1 for log in audit_logs if log["passed"] == 1)
        failed_items = sum(1 for log in audit_logs if log["passed"] == 0)
        pending_items = sum(1 for log in audit_logs if log["passed"] is None)

        # 감점 계산 (실패한 항목만, 항목별 가중치 적용)
        total_penalty = 0.0
        for log in audit_logs:
            if log["passed"] == 0:  # 실패한 경우만 감점
                penalty_weight = (
                    float(log["penalty_weight"]) if log["penalty_weight"] else 0.5
                )
                total_penalty += penalty_weight

        audit_stats = {
            "total_count": total_items,
            "passed_count": passed_items,
            "failed_count": failed_items,
            "pending_count": pending_items,
            "penalty_count": failed_items,
            "total_penalty": round(total_penalty, 2),
            # 수정: pass_rate 제거 (KPI에서 불필요)
        }

        return total_penalty, audit_stats

    def _calculate_education_penalty(self, cursor, user_id: int, year: int) -> tuple:
        """정보보호 교육 감점 계산 (미이수당 0.5점 감점)"""
        cursor.execute(
            """
            SELECT 
                education_period,
                completion_status,
                exclude_from_scoring,
                CASE 
                    WHEN exclude_from_scoring = 1 THEN 0.0
                    WHEN completion_status = 0 THEN 0.5
                    ELSE 0.0
                END as penalty_score
            FROM security_education
            WHERE user_id = %s AND education_year = %s
            """,
            (user_id, year),
        )

        education_records = cursor.fetchall()

        # 전체 교육 대상 (상반기, 하반기)
        expected_periods = ["first_half", "second_half"]

        total_penalty = 0.0
        completed_count = 0
        excluded_count = 0

        # 기록된 교육 처리
        recorded_periods = set()
        for record in education_records:
            recorded_periods.add(record["education_period"])
            if record["exclude_from_scoring"]:
                excluded_count += 1
            elif record["completion_status"]:
                completed_count += 1
            else:
                total_penalty += float(record["penalty_score"])

        # 기록되지 않은 교육 (미실시로 간주하여 감점)
        for period in expected_periods:
            if period not in recorded_periods:
                total_penalty += 0.5  # 미실시 감점

        total_count = len(expected_periods)
        incomplete_count = total_count - completed_count - excluded_count

        education_stats = {
            "total_count": total_count,
            "completed_count": completed_count,
            "incomplete_count": incomplete_count,
            "penalty_count": incomplete_count,
            "excluded_count": excluded_count,
            "total_penalty": round(total_penalty, 2),
            # 수정: completion_rate 제거 (KPI에서 불필요)
        }

        return total_penalty, education_stats

    def _calculate_training_penalty(self, cursor, user_id: int, year: int) -> tuple:
        """모의훈련 감점 계산 (실패당 0.5점 감점)"""
        cursor.execute(
            """
                SELECT 
                    training_period,
                    training_result,
                    exclude_from_scoring,
                    CASE 
                        WHEN exclude_from_scoring = 1 THEN 0.0
                        WHEN training_result = 'fail' THEN 0.5
                        ELSE 0.0
                    END as penalty_score
                FROM phishing_training
                WHERE user_id = %s AND training_year = %s
                """,
            (user_id, year),
        )

        training_records = cursor.fetchall()

        # 전체 훈련 대상 (상반기, 하반기)
        expected_periods = ["first_half", "second_half"]

        total_penalty = 0.0
        passed_count = 0
        excluded_count = 0

        # 기록된 훈련 처리
        recorded_periods = set()
        for record in training_records:
            recorded_periods.add(record["training_period"])
            if record["exclude_from_scoring"]:
                excluded_count += 1
            elif record["training_result"] == "pass":
                passed_count += 1
            elif record["training_result"] == "fail":
                total_penalty += float(record["penalty_score"])

        # 기록되지 않은 훈련은 미실시로 간주 (감점 없음, 단 통계에는 반영)
        total_count = len(expected_periods)
        failed_count = len(
            [
                r
                for r in training_records
                if r["training_result"] == "fail" and not r["exclude_from_scoring"]
            ]
        )
        pending_count = total_count - passed_count - failed_count - excluded_count

        training_stats = {
            "total_count": total_count,
            "passed_count": passed_count,
            "failed_count": failed_count,
            "pending_count": pending_count,
            "penalty_count": failed_count,
            "excluded_count": excluded_count,
            "total_penalty": round(total_penalty, 2),
            # 수정: pass_rate 제거 (KPI에서 불필요)
        }

        return total_penalty, training_stats

    # 수정: _calculate_grade 메서드 제거 (등급 불필요)

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
        """KPI 감점 요약 저장 (100점 기준 제거)"""
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
        """대시보드용 KPI 감점 정보 조회 (100점 기준 제거)"""
        if year is None:
            year = datetime.now().year

        # 사용자 감점 정보 가져오기
        score_data = self.get_user_security_score(username, year)

        # 사용자 ID 가져오기
        user = execute_query(
            "SELECT uid FROM users WHERE user_id = %s", (username,), fetch_one=True
        )
        if not user:
            raise ValueError("사용자를 찾을 수 없습니다.")

        user_id = user["uid"]

        with DatabaseManager.get_db_cursor(commit=False) as cursor:
            # 최근 감사 활동
            cursor.execute(
                """
                SELECT 
                    ci.item_name, 
                    al.passed, 
                    al.checked_at,
                    ci.category,
                    ci.penalty_weight
                FROM audit_log al
                JOIN checklist_items ci ON al.item_id = ci.item_id
                WHERE al.user_id = %s AND YEAR(al.checked_at) = %s
                ORDER BY al.checked_at DESC
                LIMIT 5
                """,
                (user_id, year),
            )
            recent_audits = cursor.fetchall()

            # 월별 감점 통계
            cursor.execute(
                """
                SELECT 
                    MONTH(al.checked_at) as month,
                    COUNT(*) as total_checks,
                    SUM(CASE WHEN al.passed = 1 THEN 1 ELSE 0 END) as passed_checks,
                    SUM(CASE WHEN al.passed = 0 THEN 1 ELSE 0 END) as failed_checks,
                    SUM(CASE WHEN al.passed = 0 THEN ci.penalty_weight ELSE 0 END) as monthly_penalty
                FROM audit_log al
                JOIN checklist_items ci ON al.item_id = ci.item_id
                WHERE al.user_id = %s AND YEAR(al.checked_at) = %s
                GROUP BY MONTH(al.checked_at)
                ORDER BY month
                """,
                (user_id, year),
            )
            monthly_stats = cursor.fetchall()

        return {
            "penalty_summary": {  # 수정: score_summary -> penalty_summary
                "total_penalty": score_data["total_penalty"],
                "audit_penalty": score_data["audit_penalty"],
                "education_penalty": score_data["education_penalty"],
                "training_penalty": score_data["training_penalty"],
            },
            "recent_audits": recent_audits,
            "monthly_stats": monthly_stats,
            "year": year,
            "education_stats": score_data["education_stats"],
            "training_stats": score_data["training_stats"],
            "audit_stats": score_data["audit_stats"],
        }