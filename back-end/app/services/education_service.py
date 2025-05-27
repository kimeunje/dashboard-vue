# app/services/education_service.py
from datetime import datetime
from app.utils.database import execute_query


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
                quarter,
                education_type,
                education_date,
                completion_status,
                score,
                notes
            FROM security_education
            WHERE user_id = %s AND education_year = %s
            ORDER BY quarter
            """, (user_id, year), fetch_all=True)

        # 분기별 상태 정리
        quarterly_status = []
        for quarter in [1, 2, 3, 4]:
            quarter_record = next(
                (r for r in education_records if r['quarter'] == quarter), None)

            if quarter_record:
                status = {
                    'quarter': quarter,
                    'completed': bool(quarter_record['completion_status']),
                    'education_date': quarter_record['education_date'].strftime(
                        '%Y-%m-%d') if quarter_record['education_date'] else None,
                    'score': quarter_record['score'],
                    'notes': quarter_record['notes']
                }
            else:
                status = {
                    'quarter': quarter,
                    'completed': False,
                    'education_date': None,
                    'score': None,
                    'notes': '교육 미참여'
                }

            quarterly_status.append(status)

        # 통계 계산
        completed_count = sum(1 for status in quarterly_status if status['completed'])
        incomplete_count = 4 - completed_count
        completion_rate = (completed_count / 4) * 100

        result = {
            'year': year,
            'quarterly_status': quarterly_status,
            'summary': {
                'total_quarters': 4,
                'completed': completed_count,
                'incomplete': incomplete_count,
                'completion_rate': round(completion_rate, 1),
                'penalty_score': incomplete_count * 0.5
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
                required_fields = [
                    'user_id', 'education_year', 'quarter', 'completion_status'
                ]
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

                # 교육 기록 등록/수정
                execute_query(
                    """
                    INSERT INTO security_education 
                    (user_id, education_year, quarter, education_type, education_date, 
                     completion_status, score, notes)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                    education_type = VALUES(education_type),
                    education_date = VALUES(education_date),
                    completion_status = VALUES(completion_status),
                    score = VALUES(score),
                    notes = VALUES(notes),
                    updated_at = NOW()
                    """, (user_uid, record['education_year'], record['quarter'],
                          record.get('education_type', '기본교육'),
                          record.get('education_date'), record['completion_status'],
                          record.get('score'), record.get('notes', '')))

                success_count += 1

            except Exception as e:
                error_records.append({'record': record, 'error': str(e)})

        return {
            'success_count': success_count,
            'total_count': len(records),
            'error_records': error_records
        }