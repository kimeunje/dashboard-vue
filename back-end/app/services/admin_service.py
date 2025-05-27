# app/services/admin_service.py
from datetime import datetime
from app.utils.database import DatabaseManager, execute_query
from app.services.score_service import ScoreService
from app.services.education_service import EducationService
from app.services.training_service import TrainingService


class AdminService:
    """관리자 관련 서비스"""

    def __init__(self):
        self.score_service = ScoreService()
        self.education_service = EducationService()
        self.training_service = TrainingService()

    def get_admin_dashboard(self) -> dict:
        """관리자 대시보드 전체 현황 조회"""
        current_year = datetime.now().year

        with DatabaseManager.get_db_cursor(commit=False) as cursor:
            # 전체 사용자 수
            cursor.execute("SELECT COUNT(*) as total_users FROM users")
            total_users = cursor.fetchone()['total_users']

            # 올해 교육 현황
            cursor.execute(
                """
                SELECT 
                    COUNT(DISTINCT user_id) as total_participants,
                    SUM(CASE WHEN completion_status = 1 THEN 1 ELSE 0 END) as completed_count,
                    SUM(CASE WHEN completion_status = 0 THEN 1 ELSE 0 END) as incomplete_count
                FROM security_education 
                WHERE education_year = %s
                """, (current_year, ))
            education_stats = cursor.fetchone()

            # 올해 모의훈련 현황
            cursor.execute(
                """
                SELECT 
                    COUNT(DISTINCT user_id) as total_participants,
                    SUM(CASE WHEN training_result = 'pass' THEN 1 ELSE 0 END) as passed_count,
                    SUM(CASE WHEN training_result = 'fail' THEN 1 ELSE 0 END) as failed_count
                FROM phishing_training 
                WHERE training_year = %s
                """, (current_year, ))
            training_stats = cursor.fetchone()

            # 평균 보안 점수
            cursor.execute(
                """
                SELECT AVG(total_score) as avg_score
                FROM security_score_summary 
                WHERE evaluation_year = %s
                """, (current_year, ))
            avg_score_result = cursor.fetchone()
            avg_score = avg_score_result['avg_score'] or 0

        dashboard_data = {
            'overview': {
                'total_users': total_users,
                'avg_score': round(float(avg_score), 1),
                'evaluation_year': current_year
            },
            'education': {
                'total_participants': education_stats['total_participants'] or 0,
                'completed': education_stats['completed_count'] or 0,
                'incomplete': education_stats['incomplete_count'] or 0,
                'completion_rate': round(
                    (education_stats['completed_count'] /
                     max(1, education_stats['total_participants'] * 4)) *
                    100, 1) if education_stats['total_participants'] else 0
            },
            'training': {
                'total_participants': training_stats['total_participants'] or 0,
                'passed': training_stats['passed_count'] or 0,
                'failed': training_stats['failed_count'] or 0,
                'pass_rate': round(
                    (training_stats['passed_count'] /
                     max(1, training_stats['total_participants'])) *
                    100, 1) if training_stats['total_participants'] else 0
            }
        }

        return dashboard_data

    def get_all_users(self) -> list:
        """전체 사용자 목록 조회"""
        users = execute_query(
            """
            SELECT uid, user_id, username, mail, department, last_updated
            FROM users
            ORDER BY username
            """, fetch_all=True)

        # 각 사용자의 최신 점수 정보도 함께 조회
        for user in users:
            score_info = execute_query(
                """
                SELECT total_score, grade, last_calculated
                FROM security_score_summary
                WHERE user_id = %s AND evaluation_year = %s
                ORDER BY last_calculated DESC
                LIMIT 1
                """, (user['uid'], datetime.now().year), fetch_one=True)

            user['latest_score'] = score_info['total_score'] if score_info else None
            user['latest_grade'] = score_info['grade'] if score_info else None
            user['last_score_update'] = score_info[
                'last_calculated'] if score_info else None

        return users

    def bulk_update_education(self, records: list) -> dict:
        """교육 결과 일괄 등록/수정"""
        return self.education_service.bulk_update_education(records)

    def bulk_update_training(self, records: list) -> dict:
        """모의훈련 결과 일괄 등록/수정"""
        return self.training_service.bulk_update_training(records)

    def recalculate_all_scores(self, year: int = None) -> dict:
        """전체 사용자 점수 재계산"""
        if year is None:
            year = datetime.now().year

        # 모든 사용자 조회
        users = execute_query("SELECT uid FROM users", fetch_all=True)

        success_count = 0
        error_users = []

        for user in users:
            try:
                # 각 사용자의 점수 재계산
                self.score_service.calculate_security_score(user['uid'], year)
                success_count += 1
            except Exception as e:
                error_users.append({'user_id': user['uid'], 'error': str(e)})

        return {
            'success_count': success_count,
            'total_count': len(users),
            'error_users': error_users,
            'year': year
        }

    def get_user_details(self, user_id: int, year: int = None) -> dict:
        """특정 사용자의 상세 정보 조회"""
        if year is None:
            year = datetime.now().year

        with DatabaseManager.get_db_cursor(commit=False) as cursor:
            # 사용자 기본 정보
            cursor.execute(
                """
                SELECT uid, user_id, username, mail, department, last_updated
                FROM users WHERE uid = %s
                """, (user_id, ))
            user_info = cursor.fetchone()

            if not user_info:
                raise ValueError("사용자를 찾을 수 없습니다.")

            # 교육 현황
            cursor.execute(
                """
                SELECT * FROM security_education
                WHERE user_id = %s AND education_year = %s
                ORDER BY quarter
                """, (user_id, year))
            education_records = cursor.fetchall()

            # 모의훈련 현황
            cursor.execute(
                """
                SELECT * FROM phishing_training
                WHERE user_id = %s AND training_year = %s
                ORDER BY quarter
                """, (user_id, year))
            training_records = cursor.fetchall()

            # 점수 정보
            cursor.execute(
                """
                SELECT * FROM security_score_summary
                WHERE user_id = %s AND evaluation_year = %s
                """, (user_id, year))
            score_info = cursor.fetchone()

        return {
            'user_info': user_info,
            'education_records': education_records,
            'training_records': training_records,
            'score_info': score_info,
            'year': year
        }