# app/services/training_service.py
from datetime import datetime
from app.utils.database import execute_query


class TrainingService:
    """악성메일 모의훈련 관련 서비스"""

    def get_training_status(self, username: str, year: int = None) -> dict:
        """사용자의 악성메일 모의훈련 현황 조회"""
        if year is None:
            year = datetime.now().year

        # 사용자 ID 가져오기
        user = execute_query("SELECT uid FROM users WHERE user_id = %s", (username, ),
                             fetch_one=True)

        if not user:
            raise ValueError("사용자를 찾을 수 없습니다.")

        user_id = user["uid"]

        # 모의훈련 현황 조회
        training_records = execute_query(
            """
            SELECT 
                training_year,
                quarter,
                training_date,
                training_result,
                clicked_phishing,
                response_time,
                training_score,
                notes
            FROM phishing_training
            WHERE user_id = %s AND training_year = %s
            ORDER BY quarter
            """, (user_id, year), fetch_all=True)

        # 분기별 상태 정리
        quarterly_status = []
        for quarter in [1, 2, 3, 4]:
            quarter_record = next(
                (r for r in training_records if r['quarter'] == quarter), None)

            if quarter_record:
                status = {
                    'quarter': quarter,
                    'training_date': quarter_record['training_date'].strftime(
                        '%Y-%m-%d') if quarter_record['training_date'] else None,
                    'result': quarter_record['training_result'],
                    'passed': quarter_record['training_result'] == 'pass',
                    'clicked_phishing': bool(quarter_record['clicked_phishing']),
                    'response_time': quarter_record['response_time'],
                    'score': quarter_record['training_score'],
                    'notes': quarter_record['notes']
                }
            else:
                status = {
                    'quarter': quarter,
                    'training_date': None,
                    'result': 'pending',
                    'passed': False,
                    'clicked_phishing': None,
                    'response_time': None,
                    'score': None,
                    'notes': '훈련 미실시'
                }

            quarterly_status.append(status)

        # 통계 계산
        conducted_count = sum(1 for status in quarterly_status
                              if status['result'] != 'pending')
        passed_count = sum(1 for status in quarterly_status if status['passed'])
        failed_count = sum(1 for status in quarterly_status
                           if status['result'] == 'fail')
        clicked_count = sum(1 for status in quarterly_status
                            if status['clicked_phishing'])

        result = {
            'year': year,
            'quarterly_status': quarterly_status,
            'summary': {
                'total_quarters': 4,
                'conducted': conducted_count,
                'passed': passed_count,
                'failed': failed_count,
                'clicked_phishing_count': clicked_count,
                'pass_rate': round((passed_count / conducted_count *
                                    100) if conducted_count > 0 else 0, 1),
                'penalty_score': failed_count * 0.5
            }
        }

        return result

    def bulk_update_training(self, records: list) -> dict:
        """모의훈련 결과 일괄 등록/수정"""
        if not records:
            raise ValueError("등록할 훈련 기록이 없습니다.")

        success_count = 0
        error_records = []

        for record in records:
            try:
                # 필수 필드 검증
                required_fields = [
                    'user_id', 'training_year', 'quarter', 'training_result'
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

                # 훈련 기록 등록/수정
                execute_query(
                    """
                    INSERT INTO phishing_training 
                    (user_id, training_year, quarter, training_date, training_result,
                     clicked_phishing, response_time, training_score, notes)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                    training_date = VALUES(training_date),
                    training_result = VALUES(training_result),
                    clicked_phishing = VALUES(clicked_phishing),
                    response_time = VALUES(response_time),
                    training_score = VALUES(training_score),
                    notes = VALUES(notes),
                    updated_at = NOW()
                    """,
                    (user_uid, record['training_year'], record['quarter'],
                     record.get('training_date'), record['training_result'],
                     record.get('clicked_phishing', 0), record.get('response_time'),
                     record.get('training_score'), record.get('notes', '')))

                success_count += 1

            except Exception as e:
                error_records.append({'record': record, 'error': str(e)})

        return {
            'success_count': success_count,
            'total_count': len(records),
            'error_records': error_records
        }