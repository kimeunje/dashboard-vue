# app/services/score_service.py
from datetime import datetime
from app.utils.database import execute_query, DatabaseManager
from app.utils.constants import SCORE_WEIGHTS, GRADE_CRITERIA, EXCEPTION_ITEM_NAMES


class ScoreService:
    """보안 점수 계산 관련 서비스"""

    def calculate_security_score(self, user_id: int, year: int = None) -> dict:
        """사용자의 종합 보안 점수 계산"""
        if year is None:
            year = datetime.now().year

        with DatabaseManager.get_db_cursor() as cursor:
            # 1. 상시감사 점수 계산 (기본 100점에서 감점)
            audit_score = self._calculate_audit_score(cursor, user_id, year)

            # 2. 교육 점수 계산 (미이수 시 감점)
            education_penalty, education_stats = self._calculate_education_penalty(cursor, user_id, year)

            # 3. 모의훈련 점수 계산 (실패 시 감점)
            training_penalty, training_stats = self._calculate_training_penalty(cursor, user_id, year)

            # 4. 총 점수 계산
            total_score = audit_score - education_penalty - training_penalty
            total_score = max(0, total_score)  # 최소 0점

            # 5. 등급 계산
            grade = self._calculate_grade(total_score)

            # 6. 점수 요약 저장
            self._save_score_summary(cursor, user_id, year, audit_score, 
                                   education_penalty, training_penalty, 
                                   total_score, grade, education_stats, training_stats)

            return {
                'user_id': user_id,
                'year': year,
                'audit_score': audit_score,
                'education_penalty': education_penalty,
                'training_penalty': training_penalty,
                'total_score': total_score,
                'grade': grade,
                'education_stats': education_stats,
                'training_stats': training_stats
            }

    def _calculate_audit_score(self, cursor, user_id: int, year: int) -> float:
        """상시감사 점수 계산"""
        # 해당 연도의 감사 로그 조회
        cursor.execute(
            """
            SELECT COUNT(*) as total_checks,
                   SUM(CASE WHEN is_compliant = 1 THEN 1 ELSE 0 END) as compliant_checks
            FROM audit_log 
            WHERE user_id = %s 
              AND YEAR(timestamp) = %s
              AND item_name NOT IN %s
            """, (user_id, year, EXCEPTION_ITEM_NAMES))
        
        result = cursor.fetchone()
        
        if not result or result['total_checks'] == 0:
            return 100.0  # 감사 기록이 없으면 기본 100점
        
        # 통과율 계산
        compliance_rate = result['compliant_checks'] / result['total_checks']
        
        # 통과율에 따른 점수 계산 (100점 기준)
        audit_score = compliance_rate * 100
        return round(audit_score, 1)

    def _calculate_education_penalty(self, cursor, user_id: int, year: int) -> tuple:
        """정보보호 교육 감점 계산"""
        cursor.execute(
            """
            SELECT 
                COUNT(*) as total_count,
                SUM(CASE WHEN completion_status = 1 THEN 1 ELSE 0 END) as completed_count,
                SUM(CASE WHEN exclude_from_scoring = 0 AND completion_status = 0 THEN 1 ELSE 0 END) as penalty_count,
                SUM(CASE WHEN exclude_from_scoring = 1 THEN 1 ELSE 0 END) as excluded_count
            FROM security_education
            WHERE user_id = %s AND education_year = %s
            """, (user_id, year))
        
        result = cursor.fetchone()
        
        penalty_count = result['penalty_count'] if result else 0
        penalty = penalty_count * SCORE_WEIGHTS['EDUCATION_PENALTY']
        
        stats = {
            'total_count': result['total_count'] if result else 0,
            'completed_count': result['completed_count'] if result else 0,
            'penalty_count': penalty_count,
            'excluded_count': result['excluded_count'] if result else 0
        }
        
        return penalty, stats

    def _calculate_training_penalty(self, cursor, user_id: int, year: int) -> tuple:
        """모의훈련 감점 계산"""
        cursor.execute(
            """
            SELECT 
                COUNT(*) as total_count,
                SUM(CASE WHEN training_result = 'pass' THEN 1 ELSE 0 END) as passed_count,
                SUM(CASE WHEN exclude_from_scoring = 0 AND training_result = 'fail' THEN 1 ELSE 0 END) as penalty_count,
                SUM(CASE WHEN exclude_from_scoring = 1 THEN 1 ELSE 0 END) as excluded_count
            FROM phishing_training
            WHERE user_id = %s AND training_year = %s
            """, (user_id, year))
        
        result = cursor.fetchone()
        
        penalty_count = result['penalty_count'] if result else 0
        penalty = penalty_count * SCORE_WEIGHTS['TRAINING_PENALTY']
        
        stats = {
            'total_count': result['total_count'] if result else 0,
            'passed_count': result['passed_count'] if result else 0,
            'penalty_count': penalty_count,
            'excluded_count': result['excluded_count'] if result else 0
        }
        
        return penalty, stats

    def _calculate_grade(self, score: float) -> str:
        """점수에 따른 등급 계산"""
        for min_score, grade in GRADE_CRITERIA:
            if score >= min_score:
                return grade
        return 'F'

    def _save_score_summary(self, cursor, user_id: int, year: int, audit_score: float,
                           education_penalty: float, training_penalty: float,
                           total_score: float, grade: str, education_stats: dict, training_stats: dict):
        """점수 요약 저장"""
        cursor.execute(
            """
            INSERT INTO security_score_summary 
            (user_id, evaluation_year, audit_score, education_penalty, training_penalty,
             total_score, grade, education_completed_count, education_total_count,
             training_passed_count, training_total_count)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
            audit_score = VALUES(audit_score),
            education_penalty = VALUES(education_penalty),
            training_penalty = VALUES(training_penalty),
            total_score = VALUES(total_score),
            grade = VALUES(grade),
            education_completed_count = VALUES(education_completed_count),
            education_total_count = VALUES(education_total_count),
            training_passed_count = VALUES(training_passed_count),
            training_total_count = VALUES(training_total_count),
            last_calculated = NOW()
            """,
            (user_id, year, audit_score, education_penalty, training_penalty,
             total_score, grade, education_stats['completed_count'], 
             education_stats['total_count'], training_stats['passed_count'],
             training_stats['total_count']))

    def get_user_score_summary(self, user_id: int, year: int = None) -> dict:
        """사용자 점수 요약 조회"""
        if year is None:
            year = datetime.now().year

        # 점수 계산 (최신 상태로)
        score_data = self.calculate_security_score(user_id, year)

        # 상세 정보 조회
        with DatabaseManager.get_db_cursor(commit=False) as cursor:
            # 교육 상세 정보
            cursor.execute(
                """
                SELECT education_period, completion_status, education_date, 
                       exclude_from_scoring, notes
                FROM security_education
                WHERE user_id = %s AND education_year = %s
                ORDER BY education_period
                """, (user_id, year))
            education_details = cursor.fetchall()

            # 모의훈련 상세 정보
            cursor.execute(
                """
                SELECT training_period, training_result, email_sent_time, action_time,
                       log_type, exclude_from_scoring, notes
                FROM phishing_training
                WHERE user_id = %s AND training_year = %s
                ORDER BY training_period
                """, (user_id, year))
            training_details = cursor.fetchall()

            # 감사 로그 요약
            cursor.execute(
                """
                SELECT COUNT(*) as total_checks,
                       SUM(CASE WHEN is_compliant = 1 THEN 1 ELSE 0 END) as compliant_checks,
                       SUM(CASE WHEN is_compliant = 0 THEN 1 ELSE 0 END) as non_compliant_checks
                FROM audit_log 
                WHERE user_id = %s 
                  AND YEAR(timestamp) = %s
                  AND item_name NOT IN %s
                """, (user_id, year, EXCEPTION_ITEM_NAMES))
            audit_summary = cursor.fetchone()

        return {
            **score_data,
            'education_details': education_details,
            'training_details': training_details,
            'audit_summary': audit_summary
        }

    def get_dashboard_overview(self, user_id: int, year: int = None) -> dict:
        """대시보드용 개요 정보 조회"""
        if year is None:
            year = datetime.now().year

        # 사용자 점수 정보 가져오기
        score_summary = self.get_user_score_summary(user_id, year)

        with DatabaseManager.get_db_cursor(commit=False) as cursor:
            # 최근 감사 활동
            cursor.execute(
                """
                SELECT item_name, is_compliant, timestamp
                FROM audit_log
                WHERE user_id = %s AND YEAR(timestamp) = %s
                ORDER BY timestamp DESC
                LIMIT 5
                """, (user_id, year))
            recent_audits = cursor.fetchall()

            # 월별 감사 통계
            cursor.execute(
                """
                SELECT 
                    MONTH(timestamp) as month,
                    COUNT(*) as total_checks,
                    SUM(CASE WHEN is_compliant = 1 THEN 1 ELSE 0 END) as compliant_checks
                FROM audit_log
                WHERE user_id = %s AND YEAR(timestamp) = %s
                  AND item_name NOT IN %s
                GROUP BY MONTH(timestamp)
                ORDER BY month
                """, (user_id, year, EXCEPTION_ITEM_NAMES))
            monthly_stats = cursor.fetchall()

        return {
            'score_summary': {
                'total_score': score_summary['total_score'],
                'grade': score_summary['grade'],
                'audit_score': score_summary['audit_score'],
                'education_penalty': score_summary['education_penalty'],
                'training_penalty': score_summary['training_penalty']
            },
            'recent_audits': recent_audits,
            'monthly_stats': monthly_stats,
            'year': year
        }