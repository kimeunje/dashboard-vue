# app/services/score_service.py
from datetime import datetime
from app.utils.database import DatabaseManager, execute_query
from app.utils.constants import SCORE_WEIGHTS, GRADE_CRITERIA


class ScoreService:
    """점수 계산 관련 서비스"""

    def calculate_security_score(self, user_id: int, year: int = None) -> dict:
        """
        사용자의 종합 보안 점수를 계산하는 함수
        - 상시감사: 기본 점수 (통과율 기반)
        - 정보보호 교육 미이수: 연 2회 x -0.5점
        - 악성메일 모의훈련 미흡: 연 2회 x -0.5점
        """
        if year is None:
            year = datetime.now().year

        with DatabaseManager.get_db_cursor() as cursor:
            # 1. 상시감사 점수 계산 (통과율 기반)
            cursor.execute(
                """
                SELECT 
                    COUNT(DISTINCT item_id) as total_items,
                    COUNT(DISTINCT CASE WHEN passed = 1 THEN item_id END) as passed_items
                FROM audit_log 
                WHERE user_id = %s 
                AND YEAR(checked_at) = %s
                """, (user_id, year))

            audit_result = cursor.fetchone()
            total_items = audit_result['total_items'] or 0
            passed_items = audit_result['passed_items'] or 0

            # 기본 점수 100점에서 시작, 통과율에 따라 조정
            if total_items > 0:
                audit_score = (passed_items / total_items) * 100
            else:
                audit_score = 100.0

            # 2. 정보보호 교육 미이수 감점 계산
            cursor.execute(
                """
                SELECT COUNT(*) as incomplete_count
                FROM security_education
                WHERE user_id = %s 
                AND education_year = %s 
                AND completion_status = 0
                """, (user_id, year))

            education_incomplete = cursor.fetchone()['incomplete_count'] or 0
            education_penalty = education_incomplete * SCORE_WEIGHTS['EDUCATION_PENALTY']

            # 3. 악성메일 모의훈련 미흡 감점 계산
            cursor.execute(
                """
                SELECT COUNT(*) as failed_count
                FROM phishing_training
                WHERE user_id = %s 
                AND training_year = %s 
                AND training_result = 'fail'
                """, (user_id, year))

            training_failed = cursor.fetchone()['failed_count'] or 0
            training_penalty = training_failed * SCORE_WEIGHTS['TRAINING_PENALTY']

            # 4. 총 점수 계산
            total_score = audit_score - education_penalty - training_penalty
            total_score = max(0, total_score)  # 최소 0점

            # 5. 등급 계산
            grade = self._calculate_grade(total_score)

            # 6. 결과 저장 또는 업데이트
            cursor.execute(
                """
                INSERT INTO security_score_summary 
                (user_id, evaluation_year, audit_score, education_penalty, training_penalty, total_score, grade)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                audit_score = VALUES(audit_score),
                education_penalty = VALUES(education_penalty),
                training_penalty = VALUES(training_penalty),
                total_score = VALUES(total_score),
                grade = VALUES(grade),
                last_calculated = NOW()
                """, (user_id, year, audit_score, education_penalty, training_penalty,
                      total_score, grade))

            return {
                'user_id': user_id,
                'year': year,
                'audit_score': round(audit_score, 1),
                'education_incomplete': education_incomplete,
                'education_penalty': education_penalty,
                'training_failed': training_failed,
                'training_penalty': training_penalty,
                'total_score': round(total_score, 1),
                'grade': grade,
                'details': {
                    'total_audit_items': total_items,
                    'passed_audit_items': passed_items,
                    'audit_pass_rate': round(
                        (passed_items / total_items * 100) if total_items > 0 else 0, 1)
                }
            }

    def _calculate_grade(self, score: float) -> str:
        """점수에 따른 등급 계산"""
        for threshold, grade in GRADE_CRITERIA:
            if score >= threshold:
                return grade
        return 'F'  # 기본값

    def generate_recommendations(self, score_data: dict) -> list:
        """점수 데이터를 바탕으로 개선 권장사항 생성"""
        recommendations = []

        # 상시감사 관련 권장사항
        if score_data['audit_score'] < 80:
            recommendations.append({
                'category': 'audit',
                'priority': 'high',
                'title': '상시보안감사 개선 필요',
                'description': '보안 정책 미준수 항목이 있습니다. 조치방법을 확인하여 개선해주세요.',
                'action_link': '/security-audit/results'
            })

        # 교육 관련 권장사항
        if score_data['education_incomplete'] > 0:
            recommendations.append({
                'category': 'education',
                'priority': 'medium',
                'title': '정보보호교육 이수 필요',
                'description': f'{score_data["education_incomplete"]}회의 교육을 미이수하였습니다. 조속히 이수해주세요.',
                'action_link': '/security-education'
            })

        # 모의훈련 관련 권장사항
        if score_data['training_failed'] > 0:
            recommendations.append({
                'category': 'training',
                'priority': 'medium',
                'title': '모의훈련 결과 개선 필요',
                'description': f'{score_data["training_failed"]}회의 모의훈련에서 미흡한 결과를 보였습니다. 추가 교육을 받아주세요.',
                'action_link': '/phishing-training'
            })

        # 전반적인 점수가 낮은 경우
        if score_data['total_score'] < 70:
            recommendations.append({
                'category': 'overall',
                'priority': 'high',
                'title': '종합적인 보안 역량 강화 필요',
                'description': '전반적인 보안 점수가 낮습니다. IT 보안팀에 문의하여 개별 상담을 받아보세요.',
                'action_link': '/security-audit/contact'
            })

        # 우수한 경우 격려 메시지
        if score_data['total_score'] >= 90:
            recommendations.append({
                'category': 'excellent',
                'priority': 'info',
                'title': '우수한 보안 의식',
                'description': '훌륭한 보안 관리 상태입니다. 현재 수준을 지속적으로 유지해주세요.',
                'action_link': None
            })

        return recommendations

    def get_user_security_score(self, username: str, year: int = None) -> dict:
        """사용자의 보안 점수 조회"""
        if year is None:
            year = datetime.now().year

        # 사용자 ID 가져오기
        user = execute_query("SELECT uid FROM users WHERE user_id = %s", (username, ),
                             fetch_one=True)

        if not user:
            raise ValueError("사용자를 찾을 수 없습니다.")

        user_id = user["uid"]

        # 점수 계산
        return self.calculate_security_score(user_id, year)

    def get_dashboard_overview(self, username: str, year: int = None) -> dict:
        """종합 보안 대시보드 데이터 조회"""
        if year is None:
            year = datetime.now().year

        # 사용자 정보 조회
        user = execute_query("SELECT uid, username FROM users WHERE user_id = %s",
                             (username, ), fetch_one=True)

        if not user:
            raise ValueError("사용자를 찾을 수 없습니다.")

        user_id = user["uid"]
        user_display_name = user["username"]

        # 점수 계산
        score_summary = self.calculate_security_score(user_id, year)

        # 대시보드 데이터 구성
        dashboard_data = {
            'user_info': {
                'name': user_display_name,
                'user_id': username
            },
            'evaluation_year': year,
            'overall_score': {
                'total_score': score_summary['total_score'],
                'grade': score_summary['grade'],
                'max_score': 100.0
            },
            'score_breakdown': {
                'audit': {
                    'name': '상시보안감사',
                    'score': score_summary['audit_score'],
                    'status': 'good' if score_summary['audit_score'] >= 80 else
                    'warning' if score_summary['audit_score'] >= 60 else 'critical'
                },
                'education': {
                    'name': '정보보호교육',
                    'incomplete_count': score_summary['education_incomplete'],
                    'penalty': score_summary['education_penalty'],
                    'status': 'good'
                    if score_summary['education_incomplete'] == 0 else 'warning'
                    if score_summary['education_incomplete'] <= 1 else 'critical'
                },
                'training': {
                    'name': '모의훈련',
                    'failed_count': score_summary['training_failed'],
                    'penalty': score_summary['training_penalty'],
                    'status': 'good' if score_summary['training_failed'] == 0 else
                    'warning' if score_summary['training_failed'] <= 1 else 'critical'
                }
            },
            'quick_stats': {
                'audit_pass_rate': score_summary['details']['audit_pass_rate'],
                'education_completion_rate': round(
                    (4 - score_summary['education_incomplete']) / 4 * 100, 1),
                'training_pass_rate': round(
                    (4 - score_summary['training_failed']) / 4 * 100, 1)
            },
            'recommendations': self.generate_recommendations(score_summary)
        }

        return dashboard_data