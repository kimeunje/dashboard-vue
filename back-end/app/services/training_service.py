# app/services/training_service.py
from datetime import datetime
from app.utils.database import execute_query, DatabaseManager


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
                training_period,
                email_sent_time,
                action_time,
                log_type,
                mail_type,
                user_email,
                ip_address,
                training_result,
                response_time_minutes,
                training_score,
                exclude_from_scoring,
                notes
            FROM phishing_training
            WHERE user_id = %s AND training_year = %s
            ORDER BY training_period
            """, (user_id, year), fetch_all=True)

        # 상반기/하반기별 상태 정리
        period_status = []
        periods = ['first_half', 'second_half']
        period_names = {'first_half': '상반기', 'second_half': '하반기'}
        
        for period in periods:
            period_record = next(
                (r for r in training_records if r['training_period'] == period), None)

            if period_record:
                # 응답시간 계산 (분)
                response_time = None
                if period_record['email_sent_time'] and period_record['action_time']:
                    time_diff = period_record['action_time'] - period_record['email_sent_time']
                    response_time = int(time_diff.total_seconds() / 60)
                    
                status = {
                    'period': period,
                    'period_name': period_names[period],
                    'email_sent_time': period_record['email_sent_time'].strftime(
                        '%Y-%m-%d %H:%M:%S') if period_record['email_sent_time'] else None,
                    'action_time': period_record['action_time'].strftime(
                        '%Y-%m-%d %H:%M:%S') if period_record['action_time'] else None,
                    'log_type': period_record['log_type'],
                    'mail_type': period_record['mail_type'],
                    'user_email': period_record['user_email'],
                    'ip_address': period_record['ip_address'],
                    'result': period_record['training_result'],
                    'passed': period_record['training_result'] == 'pass',
                    'clicked_or_opened': period_record['log_type'] is not None,
                    'response_time_minutes': response_time or period_record['response_time_minutes'],
                    'score': period_record['training_score'],
                    'exclude_from_scoring': bool(period_record['exclude_from_scoring']),
                    'notes': period_record['notes']
                }
            else:
                status = {
                    'period': period,
                    'period_name': period_names[period],
                    'email_sent_time': None,
                    'action_time': None,
                    'log_type': None,
                    'mail_type': None,
                    'user_email': None,
                    'ip_address': None,
                    'result': 'pending',
                    'passed': False,
                    'clicked_or_opened': None,
                    'response_time_minutes': None,
                    'score': None,
                    'exclude_from_scoring': False,
                    'notes': '훈련 미실시'
                }

            period_status.append(status)

        # 통계 계산 (점수 계산에서 제외된 것은 제외)
        scoring_records = [s for s in period_status if not s['exclude_from_scoring']]
        conducted_count = sum(1 for status in scoring_records
                              if status['result'] != 'pending')
        passed_count = sum(1 for status in scoring_records if status['passed'])
        failed_count = sum(1 for status in scoring_records
                           if status['result'] == 'fail')
        clicked_count = sum(1 for status in scoring_records
                            if status['clicked_or_opened'])

        # 감점 계산 (실패한 것만)
        penalty_score = failed_count * 0.5

        result = {
            'year': year,
            'period_status': period_status,
            'summary': {
                'total_periods': 2,
                'conducted': conducted_count,
                'passed': passed_count,
                'failed': failed_count,
                'clicked_or_opened_count': clicked_count,
                'pass_rate': round((passed_count / conducted_count *
                                    100) if conducted_count > 0 else 0, 1),
                'penalty_score': penalty_score,
                'excluded_count': len(period_status) - len(scoring_records)
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
                required_fields = ['user_email', 'training_year', 'training_period']
                if not all(field in record and record[field] for field in required_fields):
                    error_records.append({'record': record, 'error': '필수 필드 누락 (user_email, training_year, training_period)'})
                    continue

                # 이메일로 사용자 찾기
                user = execute_query("SELECT uid FROM users WHERE mail = %s",
                                     (record['user_email'], ), fetch_one=True)

                if not user:
                    error_records.append({
                        'record': record,
                        'error': f"이메일 '{record['user_email']}'에 해당하는 사용자를 찾을 수 없습니다."
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
                
                training_period = period_map.get(record['training_period'])
                if not training_period:
                    error_records.append({
                        'record': record,
                        'error': f"훈련 기간 '{record['training_period']}'이 유효하지 않습니다. (상반기/하반기 또는 first_half/second_half)"
                    })
                    continue

                # 훈련 결과 결정
                training_result = 'pending'
                if record.get('log_type'):
                    training_result = 'fail'  # 로그유형이 있으면 실패 (클릭/열람)
                elif record.get('email_sent_time') and not record.get('action_time'):
                    training_result = 'pass'  # 메일 발송했지만 액션이 없으면 통과

                # 응답시간 계산
                response_time_minutes = None
                if record.get('email_sent_time') and record.get('action_time'):
                    try:
                        sent_time = datetime.fromisoformat(str(record['email_sent_time']).replace('T', ' '))
                        action_time = datetime.fromisoformat(str(record['action_time']).replace('T', ' '))
                        response_time_minutes = int((action_time - sent_time).total_seconds() / 60)
                    except:
                        response_time_minutes = record.get('response_time_minutes')

                # 점수 계산
                training_score = None
                if training_result == 'pass':
                    training_score = 95.0
                elif training_result == 'fail':
                    training_score = 40.0

                # 훈련 기록 등록/수정
                execute_query(
                    """
                    INSERT INTO phishing_training 
                    (user_id, training_year, training_period, email_sent_time, action_time,
                     log_type, mail_type, user_email, ip_address, training_result,
                     response_time_minutes, training_score, exclude_from_scoring, notes)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                    email_sent_time = VALUES(email_sent_time),
                    action_time = VALUES(action_time),
                    log_type = VALUES(log_type),
                    mail_type = VALUES(mail_type),
                    user_email = VALUES(user_email),
                    ip_address = VALUES(ip_address),
                    training_result = VALUES(training_result),
                    response_time_minutes = VALUES(response_time_minutes),
                    training_score = VALUES(training_score),
                    exclude_from_scoring = VALUES(exclude_from_scoring),
                    notes = VALUES(notes),
                    updated_at = NOW()
                    """,
                    (user_uid, record['training_year'], training_period,
                     record.get('email_sent_time'), record.get('action_time'),
                     record.get('log_type'), record.get('mail_type'),
                     record['user_email'], record.get('ip_address'),
                     training_result, response_time_minutes, training_score,
                     record.get('exclude_from_scoring', 0), record.get('notes', '')))

                success_count += 1

            except Exception as e:
                error_records.append({'record': record, 'error': str(e)})

        return {
            'success_count': success_count,
            'total_count': len(records),
            'error_records': error_records
        }

    def update_training_record(self, record: dict) -> bool:
        """단일 훈련 기록 수정"""
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
                UPDATE phishing_training SET
                email_sent_time = %s,
                action_time = %s,
                log_type = %s,
                mail_type = %s,
                user_email = %s,
                ip_address = %s,
                training_result = %s,
                response_time_minutes = %s,
                training_score = %s,
                exclude_from_scoring = %s,
                notes = %s,
                updated_at = NOW()
                WHERE user_id = %s AND training_year = %s AND training_period = %s
                """,
                (record.get('email_sent_time'), record.get('action_time'),
                 record.get('log_type'), record.get('mail_type'),
                 record.get('user_email'), record.get('ip_address'),
                 record.get('training_result', 'pending'),
                 record.get('response_time_minutes'),
                 record.get('training_score'),
                 record.get('exclude_from_scoring', 0),
                 record.get('notes', ''),
                 user_uid, record['training_year'], record['training_period']))

            return True

        except Exception as e:
            raise ValueError(f"훈련 기록 수정 실패: {str(e)}")

    def delete_training_record(self, user_id: str, training_year: int, training_period: str) -> bool:
        """훈련 기록 삭제"""
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
                DELETE FROM phishing_training
                WHERE user_id = %s AND training_year = %s AND training_period = %s
                """,
                (user_uid, training_year, training_period))

            return result > 0

        except Exception as e:
            raise ValueError(f"훈련 기록 삭제 실패: {str(e)}")

    def get_training_excel_template(self) -> str:
        """엑셀 업로드용 템플릿 생성"""
        template_data = [
            "user_email,training_year,training_period,email_sent_time,action_time,log_type,mail_type,ip_address,exclude_from_scoring,notes",
            "test@example.com,2025,상반기,2025-05-15 10:44:25,2025-05-15 10:44:59,스크립트 첨부파일 열람,퇴직연금 운용상품 안내 (HTML),112.111.231.120,0,모의훈련 실패 - 첨부파일 열람",
            "user1@example.com,2025,상반기,2025-05-15 10:44:25,,,보안 업데이트 안내,,0,모의훈련 통과 - 액션 없음",
            "user2@example.com,2025,하반기,2025-11-20 14:30:00,2025-11-20 14:35:20,링크 클릭,급여명세서 확인 요청,192.168.1.100,1,모의훈련 실패 - 점수 계산 제외"
        ]
        return "\n".join(template_data)

    def get_all_training_records(self, year: int = None, period: str = None, result: str = None) -> list:
        """모든 훈련 기록 조회 (관리자용)"""
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
                    pt.training_score,
                    pt.exclude_from_scoring,
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
            
# app/controllers/training_controller.py
from datetime import datetime
from flask import Blueprint, request, jsonify, make_response
from app.services.training_service import TrainingService
from app.utils.decorators import token_required, admin_required, handle_exceptions
from app.utils.constants import HTTP_STATUS

training_bp = Blueprint('training', __name__)
training_service = TrainingService()


@training_bp.route('/status', methods=['GET'])
@token_required
@handle_exceptions
def get_phishing_training_status():
    """사용자의 악성메일 모의훈련 현황 조회"""
    user = request.current_user
    username = user["username"]

    year = request.args.get('year', datetime.now().year, type=int)

    try:
        result = training_service.get_training_status(username, year)
        return jsonify(result)
    except ValueError as e:
        return jsonify({"message": str(e)}), HTTP_STATUS['NOT_FOUND']


@training_bp.route('/template/download', methods=['GET'])
@admin_required
@handle_exceptions
def download_training_template():
    """모의훈련 업로드 템플릿 다운로드"""
    template_csv = training_service.get_training_excel_template()
    
    response = make_response(template_csv)
    response.headers['Content-Type'] = 'text/csv; charset=utf-8'
    response.headers['Content-Disposition'] = 'attachment; filename=모의훈련_업로드_템플릿.csv'
    
    return response


@training_bp.route('/records', methods=['GET'])
@admin_required
@handle_exceptions
def get_all_training_records():
    """모든 모의훈련 기록 조회 (관리자용)"""
    year = request.args.get('year', datetime.now().year, type=int)
    period = request.args.get('period', None)
    result = request.args.get('result', None)
    
    records = training_service.get_all_training_records(year, period, result)
    return jsonify(records)


@training_bp.route('/update', methods=['POST'])
@admin_required
@handle_exceptions
def update_training_record():
    """단일 모의훈련 기록 수정"""
    data = request.json
    
    try:
        success = training_service.update_training_record(data)
        if success:
            return jsonify({"message": "모의훈련 기록이 수정되었습니다."})
        else:
            return jsonify({"error": "수정에 실패했습니다."}), HTTP_STATUS['BAD_REQUEST']
    except ValueError as e:
        return jsonify({"error": str(e)}), HTTP_STATUS['BAD_REQUEST']


@training_bp.route('/delete', methods=['DELETE'])
@admin_required
@handle_exceptions
def delete_training_record():
    """모의훈련 기록 삭제"""
    data = request.json
    
    try:
        success = training_service.delete_training_record(
            data['user_id'], 
            data['training_year'], 
            data['training_period']
        )
        if success:
            return jsonify({"message": "모의훈련 기록이 삭제되었습니다."})
        else:
            return jsonify({"error": "삭제할 기록을 찾을 수 없습니다."}), HTTP_STATUS['NOT_FOUND']
    except ValueError as e:
        return jsonify({"error": str(e)}), HTTP_STATUS['BAD_REQUEST']