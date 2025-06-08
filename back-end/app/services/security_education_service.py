# app/services/education_service.py
from datetime import datetime
from app.utils.database import execute_query, DatabaseManager


class EducationService:
    """정보보호 교육 관련 서비스"""

    def get_education_status(self, username: str, year: int = None) -> dict:
        """사용자의 정보보호 교육 현황 조회"""
        if year is None:
            year = datetime.now().year

        # 사용자 ID 가져오기
        user = execute_query("SELECT uid FROM users WHERE user_id = %s", (username, ),
                             fetch_one=True)

        if not user:
            raise ValueError("사용자를 찾을 수 없습니다.")

        user_id = user["uid"]

        # 교육 현황 조회
        education_records = execute_query(
            """
            SELECT 
                education_year,
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
            """, (user_id, year), fetch_all=True)

        # 상반기/하반기별 상태 정리
        period_status = []
        periods = ['first_half', 'second_half']
        period_names = {'first_half': '상반기', 'second_half': '하반기'}
        
        for period in periods:
            period_record = next(
                (r for r in education_records if r['education_period'] == period), None)

            if period_record:
                status = {
                    'period': period,
                    'period_name': period_names[period],
                    'education_type': period_record['education_type'],
                    'education_date': period_record['education_date'].strftime(
                        '%Y-%m-%d') if period_record['education_date'] else None,
                    'completion_status': period_record['completion_status'],
                    'completed': bool(period_record['completion_status']),
                    'score': period_record['score'],
                    'exclude_from_scoring': bool(period_record['exclude_from_scoring']),
                    'notes': period_record['notes']
                }
            else:
                status = {
                    'period': period,
                    'period_name': period_names[period],
                    'education_type': '기본교육',
                    'education_date': None,
                    'completion_status': 0,
                    'completed': False,
                    'score': None,
                    'exclude_from_scoring': False,
                    'notes': '교육 미실시'
                }

            period_status.append(status)

        # 통계 계산 (점수 계산에서 제외된 것은 제외)
        scoring_records = [s for s in period_status if not s['exclude_from_scoring']]
        completed_count = sum(1 for status in scoring_records if status['completed'])
        incomplete_count = len(scoring_records) - completed_count
        
        # 감점 계산
        penalty_score = incomplete_count * 0.5

        result = {
            'year': year,
            'period_status': period_status,
            'summary': {
                'total_periods': 2,
                'completed': completed_count,
                'incomplete': incomplete_count,
                'completion_rate': round((completed_count / len(scoring_records) *
                                        100) if scoring_records else 0, 1),
                'penalty_score': penalty_score,
                'excluded_count': len(period_status) - len(scoring_records)
            }
        }

        return result

    def bulk_update_education(self, records: list) -> dict:
        """교육 결과 일괄 등록/수정"""
        if not records:
            raise ValueError("등록할 교육 기록이 없습니다.")

        success_count = 0
        error_records = []

        for record in records:
            try:
                # 필수 필드 검증
                required_fields = ['user_id', 'education_year', 'education_period']
                if not all(field in record for field in required_fields):
                    error_records.append({'record': record, 'error': '필수 필드 누락'})
                    continue

                # 사용자 존재 확인
                user = execute_query("SELECT uid FROM users WHERE user_id = %s",
                                     (record['user_id'], ), fetch_one=True)

                if not user:
                    error_records.append({
                        'record': record,
                        'error': f"사용자 '{record['user_id']}'를 찾을 수 없습니다."
                    })
                    continue

                user_uid = user['uid']

                # 기간 변환
                period_map = {
                    '상반기': 'first_half',
                    '하반기': 'second_half',
                    'first_half': 'first_half',
                    'second_half': 'second_half'
                }
                
                education_period = period_map.get(record['education_period'])
                if not education_period:
                    error_records.append({
                        'record': record,
                        'error': f"교육 기간 '{record['education_period']}'이 유효하지 않습니다."
                    })
                    continue

                # 교육 기록 등록/수정
                execute_query(
                    """
                    INSERT INTO security_education 
                    (user_id, education_year, education_period, education_type, education_date,
                     completion_status, score, exclude_from_scoring, notes)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                    education_type = VALUES(education_type),
                    education_date = VALUES(education_date),
                    completion_status = VALUES(completion_status),
                    score = VALUES(score),
                    exclude_from_scoring = VALUES(exclude_from_scoring),
                    notes = VALUES(notes),
                    updated_at = NOW()
                    """,
                    (user_uid, record['education_year'], education_period,
                     record.get('education_type', '기본교육'),
                     record.get('education_date'), 
                     record.get('completion_status', 0),
                     record.get('score'), 
                     record.get('exclude_from_scoring', 0),
                     record.get('notes', '')))

                success_count += 1

            except Exception as e:
                error_records.append({'record': record, 'error': str(e)})

        return {
            'success_count': success_count,
            'total_count': len(records),
            'error_records': error_records
        }

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
                """,
                (record.get('education_type', '기본교육'),
                 record.get('education_date'),
                 record.get('completion_status', 0),
                 record.get('score'),
                 record.get('exclude_from_scoring', 0),
                 record.get('notes', ''),
                 user_uid, record['education_year'], record['education_period']))

            return True

        except Exception as e:
            raise ValueError(f"교육 기록 수정 실패: {str(e)}")

    def delete_education_record(self, user_id: str, education_year: int, education_period: str) -> bool:
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
                """,
                (user_uid, education_year, education_period))

            return result > 0

        except Exception as e:
            raise ValueError(f"교육 기록 삭제 실패: {str(e)}")

    def get_all_education_records(self, year: int = None, period: str = None, status: int = None) -> list:
        """모든 교육 기록 조회 (관리자용)"""
        if year is None:
            year = datetime.now().year

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
                base_query += " AND se.completion_status = %s"
                params.append(status)
                
            base_query += " ORDER BY u.username, se.education_period"
            
            cursor.execute(base_query, params)
            return cursor.fetchall()

    def get_education_statistics(self, year: int = None) -> dict:
        """교육 통계 조회"""
        if year is None:
            year = datetime.now().year

        with DatabaseManager.get_db_cursor(commit=False) as cursor:
            # 기간별 통계
            cursor.execute(
                """
                SELECT 
                    education_period,
                    COUNT(*) as total_count,
                    SUM(CASE WHEN completion_status = 1 THEN 1 ELSE 0 END) as completed_count,
                    SUM(CASE WHEN completion_status = 0 THEN 1 ELSE 0 END) as incomplete_count,
                    SUM(CASE WHEN exclude_from_scoring = 1 THEN 1 ELSE 0 END) as excluded_count,
                    AVG(CASE WHEN score IS NOT NULL THEN score END) as avg_score
                FROM security_education
                WHERE education_year = %s
                GROUP BY education_period
                ORDER BY education_period
                """, (year, ))
            period_stats = cursor.fetchall()

            # 부서별 통계
            cursor.execute(
                """
                SELECT 
                    u.department,
                    COUNT(*) as total_count,
                    SUM(CASE WHEN se.completion_status = 1 THEN 1 ELSE 0 END) as completed_count,
                    AVG(CASE WHEN se.score IS NOT NULL THEN se.score END) as avg_score
                FROM security_education se
                JOIN users u ON se.user_id = u.uid
                WHERE se.education_year = %s AND se.exclude_from_scoring = 0
                GROUP BY u.department
                ORDER BY u.department
                """, (year, ))
            department_stats = cursor.fetchall()

            # 교육 유형별 통계
            cursor.execute(
                """
                SELECT 
                    education_type,
                    COUNT(*) as count,
                    SUM(CASE WHEN completion_status = 1 THEN 1 ELSE 0 END) as completed_count
                FROM security_education
                WHERE education_year = %s
                GROUP BY education_type
                ORDER BY count DESC
                """, (year, ))
            type_stats = cursor.fetchall()

        return {
            'year': year,
            'period_stats': period_stats,
            'department_stats': department_stats,
            'type_stats': type_stats
        }