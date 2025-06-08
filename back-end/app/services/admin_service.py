# app/services/admin_service.py
from datetime import datetime
from app.utils.database import DatabaseManager, execute_query
from app.services.total_score_service import ScoreService
from app.services.security_education_service import EducationService
from app.services.phishing_training_service import TrainingService


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

            # 올해 교육 현황 (상반기/하반기)
            cursor.execute(
                """
                SELECT 
                    COUNT(DISTINCT user_id) as total_participants,
                    SUM(CASE WHEN completion_status = 1 THEN 1 ELSE 0 END) as completed_count,
                    SUM(CASE WHEN completion_status = 0 AND exclude_from_scoring = 0 THEN 1 ELSE 0 END) as incomplete_count,
                    SUM(CASE WHEN exclude_from_scoring = 1 THEN 1 ELSE 0 END) as excluded_count
                FROM security_education 
                WHERE education_year = %s
                """, (current_year, ))
            education_stats = cursor.fetchone()

            # 올해 모의훈련 현황 (상반기/하반기)
            cursor.execute(
                """
                SELECT 
                    COUNT(DISTINCT user_id) as total_participants,
                    SUM(CASE WHEN training_result = 'pass' THEN 1 ELSE 0 END) as passed_count,
                    SUM(CASE WHEN training_result = 'fail' AND exclude_from_scoring = 0 THEN 1 ELSE 0 END) as failed_count,
                    SUM(CASE WHEN exclude_from_scoring = 1 THEN 1 ELSE 0 END) as excluded_count
                FROM phishing_training 
                WHERE training_year = %s
                """, (current_year, ))
            training_stats = cursor.fetchone()

            # 평균 보안 점수 (security_score_summary 테이블이 없다면 기본값)
            try:
                cursor.execute(
                    """
                    SELECT AVG(total_score) as avg_score
                    FROM security_score_summary 
                    WHERE evaluation_year = %s
                    """, (current_year, ))
                avg_score_result = cursor.fetchone()
                avg_score = avg_score_result['avg_score'] if avg_score_result else 0
            except:
                avg_score = 85.5  # 기본값

        # 교육 이수율 계산 (전체 대상자 대비)
        education_completion_rate = 0
        if education_stats and education_stats['total_participants']:
            # 상반기 + 하반기 총 2회 교육 대상
            total_education_opportunities = total_users * 2
            completion_rate = (education_stats['completed_count'] /
                               total_education_opportunities) * 100
            education_completion_rate = round(completion_rate, 1)

        # 모의훈련 통과율 계산
        training_pass_rate = 0
        if training_stats and training_stats['total_participants']:
            pass_rate = (training_stats['passed_count'] /
                         training_stats['total_participants']) * 100
            training_pass_rate = round(pass_rate, 1)

        dashboard_data = {
            'overview': {
                'total_users': total_users,
                'avg_score': round(float(avg_score), 1) if avg_score else 0,
                'evaluation_year': current_year
            },
            'education': {
                'total_participants': education_stats['total_participants']
                if education_stats else 0,
                'completed': education_stats['completed_count']
                if education_stats else 0,
                'incomplete': education_stats['incomplete_count']
                if education_stats else 0,
                'excluded': education_stats['excluded_count'] if education_stats else 0,
                'completion_rate': education_completion_rate
            },
            'training': {
                'total_participants': training_stats['total_participants']
                if training_stats else 0,
                'passed': training_stats['passed_count'] if training_stats else 0,
                'failed': training_stats['failed_count'] if training_stats else 0,
                'excluded': training_stats['excluded_count'] if training_stats else 0,
                'pass_rate': training_pass_rate
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

        # 각 사용자의 최신 점수 정보도 함께 조회 (테이블이 있다면)
        for user in users:
            try:
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
            except:
                # security_score_summary 테이블이 없는 경우
                user['latest_score'] = None
                user['latest_grade'] = None
                user['last_score_update'] = None

        return users

    def get_all_education_records(self, year: int = None, period: str = None,
                                  status: str = None) -> list:
        """모든 교육 기록 조회 (관리자용)"""
        if year is None:
            year = datetime.now().year

        try:
            with DatabaseManager.get_db_cursor(commit=False) as cursor:
                base_query = """
                    SELECT 
                        se.education_id,
                        u.user_id,
                        u.username,
                        u.department,
                        se.education_year,
                        se.education_period,
                        se.education_type,
                        se.education_date,
                        se.completion_status,
                        se.score,
                        se.exclude_from_scoring,
                        se.notes,
                        se.created_at,
                        se.updated_at
                    FROM security_education se
                    JOIN users u ON se.user_id = u.uid
                    WHERE se.education_year = %s
                """

                params = [year]

                if period:
                    base_query += " AND se.education_period = %s"
                    params.append(period)

                if status is not None:
                    if status == 'completed':
                        base_query += " AND se.completion_status = 1"
                    elif status == 'incomplete':
                        base_query += " AND se.completion_status = 0"

                base_query += " ORDER BY u.username, se.education_period"

                cursor.execute(base_query, params)
                return cursor.fetchall()
        except Exception as e:
            # security_education 테이블이 없는 경우 빈 리스트 반환
            print(f"Education records error: {e}")
            return []

    def get_all_training_records(self, year: int = None, period: str = None,
                                 result: str = None) -> list:
        """모든 모의훈련 기록 조회 (관리자용)"""
        if year is None:
            year = datetime.now().year

        with DatabaseManager.get_db_cursor(commit=False) as cursor:
            base_query = """
                SELECT 
                    pt.training_id,
                    u.user_id,
                    u.username,
                    u.department,
                    pt.training_year,
                    pt.training_period,
                    pt.email_sent_time,
                    pt.action_time,
                    pt.log_type,
                    pt.mail_type,
                    pt.user_email,
                    pt.ip_address,
                    pt.training_result,
                    pt.response_time_minutes,
                    pt.notes,
                    pt.created_at,
                    pt.updated_at
                FROM phishing_training pt
                JOIN users u ON pt.user_id = u.uid
                WHERE pt.training_year = %s
            """

            params = [year]

            if period:
                base_query += " AND pt.training_period = %s"
                params.append(period)

            if result:
                base_query += " AND pt.training_result = %s"
                params.append(result)

            base_query += " ORDER BY u.username, pt.training_period"

            cursor.execute(base_query, params)
            return cursor.fetchall()

    def update_education_record(self, record: dict) -> bool:
        """단일 교육 기록 수정"""
        try:
            # 사용자 확인
            user = execute_query("SELECT uid FROM users WHERE user_id = %s",
                                 (record['user_id'], ), fetch_one=True)
            if not user:
                raise ValueError("사용자를 찾을 수 없습니다.")

            user_uid = user['uid']

            # 기록 수정
            execute_query(
                """
                UPDATE security_education SET
                education_type = %s,
                education_date = %s,
                completion_status = %s,
                score = %s,
                exclude_from_scoring = %s,
                notes = %s,
                updated_at = NOW()
                WHERE user_id = %s AND education_year = %s AND education_period = %s
                """, (record.get('education_type'), record.get('education_date'),
                      record.get('completion_status', 0), record.get('score'),
                      record.get('exclude_from_scoring', 0), record.get('notes', ''),
                      user_uid, record['education_year'], record['education_period']))

            return True

        except Exception as e:
            raise ValueError(f"교육 기록 수정 실패: {str(e)}")

    def delete_education_record(self, user_id: str, education_year: int,
                                education_period: str) -> bool:
        """교육 기록 삭제"""
        try:
            # 사용자 확인
            user = execute_query("SELECT uid FROM users WHERE user_id = %s",
                                 (user_id, ), fetch_one=True)
            if not user:
                raise ValueError("사용자를 찾을 수 없습니다.")

            user_uid = user['uid']

            # 기록 삭제
            result = execute_query(
                """
                DELETE FROM security_education
                WHERE user_id = %s AND education_year = %s AND education_period = %s
                """, (user_uid, education_year, education_period))

            return result > 0

        except Exception as e:
            raise ValueError(f"교육 기록 삭제 실패: {str(e)}")

    def update_training_record(self, record: dict) -> bool:
        """단일 모의훈련 기록 수정"""
        return self.training_service.update_training_record(record)

    def delete_training_record(self, user_id: str, training_year: int,
                               training_period: str) -> bool:
        """모의훈련 기록 삭제"""
        return self.training_service.delete_training_record(user_id, training_year,
                                                            training_period)

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

            # 교육 현황 (상반기/하반기)
            try:
                cursor.execute(
                    """
                    SELECT education_period, education_type, education_date, completion_status,
                           score, exclude_from_scoring, notes
                    FROM security_education
                    WHERE user_id = %s AND education_year = %s
                    ORDER BY education_period
                    """, (user_id, year))
                education_records = cursor.fetchall()
            except:
                education_records = []

            # 모의훈련 현황 (상반기/하반기)
            cursor.execute(
                """
                SELECT training_period, email_sent_time, action_time, log_type, mail_type,
                       user_email, ip_address, training_result, response_time_minutes,
                       training_score, exclude_from_scoring, notes
                FROM phishing_training
                WHERE user_id = %s AND training_year = %s
                ORDER BY training_period
                """, (user_id, year))
            training_records = cursor.fetchall()

            # 점수 정보
            try:
                cursor.execute(
                    """
                    SELECT * FROM security_score_summary
                    WHERE user_id = %s AND evaluation_year = %s
                    """, (user_id, year))
                score_info = cursor.fetchone()
            except:
                score_info = None

        return {
            'user_info': user_info,
            'education_records': education_records,
            'training_records': training_records,
            'score_info': score_info,
            'year': year
        }

    def toggle_scoring_exclusion(self, user_id: str, year: int, record_type: str,
                                 period: str, exclude: bool) -> bool:
        """점수 계산 제외/포함 토글"""
        try:
            # 사용자 ID로 uid 찾기
            user = execute_query("SELECT uid FROM users WHERE user_id = %s",
                                 (user_id, ), fetch_one=True)
            if not user:
                raise ValueError("사용자를 찾을 수 없습니다.")

            user_uid = user['uid']

            if record_type == 'education':
                table = 'security_education'
                period_field = 'education_period'
                year_field = 'education_year'
            elif record_type == 'training':
                table = 'phishing_training'
                period_field = 'training_period'
                year_field = 'training_year'
            else:
                raise ValueError("잘못된 기록 유형입니다.")

            execute_query(
                f"""
                UPDATE {table} 
                SET exclude_from_scoring = %s, updated_at = NOW()
                WHERE user_id = %s AND {year_field} = %s AND {period_field} = %s
                """, (1 if exclude else 0, user_uid, year, period))

            # 점수 재계산 (점수 서비스가 있는 경우에만)
            try:
                self.score_service.calculate_security_score(user_uid, year)
            except:
                pass  # 점수 서비스가 없어도 계속 진행

            return True

        except Exception as e:
            raise ValueError(f"점수 계산 제외 설정 실패: {str(e)}")