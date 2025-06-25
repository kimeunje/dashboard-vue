# back-end/app/controllers/security_education_controller.py
from flask import Blueprint, request, jsonify, make_response
from datetime import datetime
from urllib.parse import quote
from app.services.security_education_service import SecurityEducationService
from app.services.education_period_service import EducationPeriodService
from app.utils.decorators import token_required, admin_required, handle_exceptions, validate_json
from app.utils.constants import HTTP_STATUS
from app.utils.database import execute_query, DatabaseManager

# Blueprint 생성
education_bp = Blueprint('security_education', __name__)

# 서비스 인스턴스
education_service = SecurityEducationService()
period_service = EducationPeriodService()

# 📁 back-end/app/controllers/security_education_controller.py
# 기존 파일에서 get_education_status 함수만 수정


@education_bp.route('/status', methods=['GET'])
@token_required
@handle_exceptions
def get_education_status():
    """
    ✅ 새로운 스키마 전용 사용자별 교육 현황 조회
    데이터가 없는 경우 기본값 반환, 레거시 모드 제거
    """
    year = request.args.get('year', datetime.now().year, type=int)

    current_user = request.current_user
    user_id = current_user.get('uid')
    username = current_user.get('username')

    try:
        print(f"[DEBUG] 교육 현황 조회: username={username}, user_id={user_id}, year={year}")

        # ✅ 사용자 ID 조회 (username으로 uid 찾기)
        if not user_id:
            from app.utils.database import execute_query
            user_data = execute_query("SELECT uid FROM users WHERE user_id = %s",
                                      (username, ), fetch_one=True)
            if not user_data:
                return jsonify({'error': '사용자 정보를 찾을 수 없습니다.'
                                }), HTTP_STATUS['NOT_FOUND']
            user_id = user_data['uid']

        # ✅ 새로운 스키마 기반 교육 현황 조회
        education_status = execute_query(
            """
            SELECT 
                se.course_name,
                se.completed_count,
                se.incomplete_count,
                se.total_courses,
                se.completion_rate,
                se.education_date,
                se.education_type,
                se.exclude_from_scoring,
                se.exclude_reason,
                se.notes,
                sep.period_name,
                sep.start_date,
                sep.end_date,
                sep.is_completed
            FROM security_education se
            LEFT JOIN security_education_periods sep ON se.period_id = sep.period_id
            WHERE se.user_id = %s AND se.education_year = %s
            ORDER BY se.course_name, se.created_at
        """, (user_id, year), fetch_all=True)

        # ✅ 데이터가 없는 경우 기본값 반환
        if not education_status:
            print(f"[DEBUG] 교육 데이터 없음 - 기본값 반환: user_id={user_id}, year={year}")
            return jsonify({
                'year': year,
                'education_status': [],
                'summary': {
                    'total_courses': 0,
                    'completed': 0,
                    'incomplete': 0,
                    'not_started': 0,
                    'completion_rate': 0,
                    'penalty_score': 0.0,
                    'excluded_count': 0,
                    'unique_courses': 0,
                    'avg_completion_rate': 0.0
                }
            })

        # ✅ 새로운 스키마 기반 응답 생성
        total_completed = sum(record['completed_count'] or 0
                              for record in education_status)
        total_incomplete = sum(record['incomplete_count'] or 0
                               for record in education_status)
        total_courses = sum(record['total_courses'] or 0 for record in education_status)
        excluded_count = len(
            [e for e in education_status if e['exclude_from_scoring'] == 1])

        # 전체 수료율 계산
        overall_completion_rate = round((total_completed / total_courses *
                                         100) if total_courses > 0 else 0)

        # ✅ 감점 계산 수정 (incomplete_count > 0 기반)
        penalty_score = sum(0.5 for record in education_status if (
            record['incomplete_count'] or 0) > 0 and not record['exclude_from_scoring'])

        # ✅ 응답 데이터 구성
        education_summary = {
            'year': year,
            'education_status': [],
            'summary': {
                'total_courses': total_courses,
                'completed': total_completed,
                'incomplete': total_incomplete,
                'not_started': max(0,
                                   total_courses - total_completed - total_incomplete),
                'completion_rate': overall_completion_rate,
                'penalty_score': float(penalty_score),
                'excluded_count': excluded_count,
                'unique_courses': len(
                    set(record['course_name'] for record in education_status
                        if record['course_name'])),
                'avg_completion_rate': round(
                    sum(record['completion_rate'] or 0 for record in education_status) /
                    len(education_status), 2) if education_status else 0.0
            }
        }

        # 과정별 세부 정보 구성
        course_details = {}
        for record in education_status:
            course_name = record['course_name']
            completed_count = int(record['completed_count'] or 0)
            incomplete_count = int(record['incomplete_count'] or 0)
            total_courses_record = int(record['total_courses'] or 0)

            # 상태 계산
            completion_rate = float(record['completion_rate'] or 0)
            if record['exclude_from_scoring']:
                status = '제외'
            elif completion_rate >= 100:
                status = '완료'
            elif completion_rate >= 80:
                status = '수료'
            elif completion_rate > 0:
                status = f'부분완료({completion_rate:.0f}%)'
            else:
                status = '미실시'

            course_details[course_name] = {
                'course_name': course_name,
                'education_type': record['education_type'],
                'completed_count': completed_count,
                'incomplete_count': incomplete_count,
                'total_courses': total_courses_record,
                'completion_rate': completion_rate,
                'not_started': max(
                    0, total_courses_record - completed_count - incomplete_count),
                'status': status,
                'education_date': str(record['education_date'])
                if record['education_date'] else None,
                'exclude_from_scoring': bool(record['exclude_from_scoring']),
                'notes': record['notes'],
                # ✅ 기간 정보
                'period_name': record['period_name'],
                'start_date': str(record['start_date'])
                if record['start_date'] else None,
                'end_date': str(record['end_date']) if record['end_date'] else None,
                'is_completed': bool(record['is_completed'])
            }

        education_summary['education_status'] = list(course_details.values())

        print(f"[DEBUG] 새 스키마 기반 응답 생성 완료: {len(course_details)}개 과정")
        return jsonify(education_summary)

    except Exception as e:
        print(f"[ERROR] 교육 현황 조회 실패: {str(e)}")
        import traceback
        traceback.print_exc()

        # ✅ 오류 발생 시에도 기본값 반환 (빈 응답보다는 구조화된 기본값)
        return jsonify({
            'year': year,
            'education_status': [],
            'summary': {
                'total_courses': 0,
                'completed': 0,
                'incomplete': 0,
                'not_started': 0,
                'completion_rate': 0,
                'penalty_score': 0.0,
                'excluded_count': 0,
                'unique_courses': 0,
                'avg_completion_rate': 0.0
            },
            'error_message': '데이터 조회 중 오류가 발생했지만 기본 구조로 응답합니다.'
        }), HTTP_STATUS['OK']  # 500 대신 200으로 응답하여 프론트엔드에서 처리 가능


@education_bp.route('/records', methods=['GET'])
@admin_required
@handle_exceptions
def get_education_records():
    """
    ✅ 교육 기록 조회 (관리자용) - 새로운 스키마만 사용
    
    변경사항:
    1. 레거시 모드 제거
    2. mail 컬럼 사용
    3. 데이터가 없을 때 빈 배열 반환
    """
    year = request.args.get('year', datetime.now().year, type=int)
    education_type = request.args.get('education_type', '')
    status = request.args.get('status', '')

    try:
        print(f"[DEBUG] 교육 기록 조회: year={year}, type={education_type}, status={status}")

        # ✅ 새로운 스키마만 사용
        records = _get_education_records_new_schema(year, education_type, status)

        print(f"[DEBUG] 새 스키마 기반 응답: {len(records)}건")
        return jsonify(records)

    except Exception as e:
        print(f"[ERROR] 교육 기록 조회 실패: {str(e)}")
        return jsonify({'error': f'기록 조회 실패: {str(e)}'
                        }), HTTP_STATUS['INTERNAL_SERVER_ERROR']


def _get_education_records_new_schema(year, education_type, status):
    """
    ✅ 새로운 스키마 기반 교육 기록 조회 - 감점 로직 통일
    
    변경사항:
    1. penalty_applied 계산을 다른 페이지와 동일하게 수정
    2. exclude_from_scoring이 True인 경우 감점 없음
    3. incomplete_count > 0이고 exclude_from_scoring이 False인 경우만 0.5점 감점
    """
    try:
        # 기본 쿼리
        base_query = """
            SELECT 
                se.education_id,
                se.user_id,
                se.course_name,
                se.education_type,
                se.completed_count,
                se.incomplete_count,
                se.total_courses,
                se.completion_rate,
                se.education_date,
                se.exclude_from_scoring,
                se.exclude_reason,
                se.notes,
                se.period_id,
                u.user_id as username,
                u.username as name,
                u.department,
                u.mail as email,
                sep.period_name,
                sep.start_date,
                sep.end_date,
                sep.is_completed as period_completed
            FROM security_education se
            LEFT JOIN users u ON se.user_id = u.uid
            LEFT JOIN security_education_periods sep ON se.period_id = sep.period_id
            WHERE se.education_year = %s
        """

        query_params = [year]

        # 필터 조건 추가
        if education_type:
            base_query += " AND se.education_type = %s"
            query_params.append(education_type)

        if status == '1':  # 완료
            base_query += " AND se.completion_rate >= 100"
        elif status == '0':  # 미완료
            base_query += " AND se.completion_rate < 100"

        base_query += " ORDER BY u.department, u.username, se.course_name"

        print(f"[DEBUG] 실행할 쿼리: {base_query}")
        print(f"[DEBUG] 쿼리 파라미터: {query_params}")

        records = execute_query(base_query, tuple(query_params), fetch_all=True)

        if not records:
            print(f"[DEBUG] 조회된 교육 기록 없음")
            return []

        result_records = []
        for record in records:
            # ✅ 감점 로직 수정 - 다른 페이지와 동일하게
            penalty_applied = 0.0
            if not record['exclude_from_scoring']:  # 제외되지 않은 경우만
                if (record['incomplete_count'] or 0) > 0:  # incomplete_count > 0인 경우
                    penalty_applied = 0.5  # 고정 0.5점 감점

            result_record = {
                'education_id': record['education_id'],
                'user_id': record['user_id'],
                'username': record['username'],
                'name': record['name'],
                'department': record['department'],
                'email': record['email'],
                'course_name': record['course_name'],
                'education_type': record['education_type'],
                'completed_count': int(record['completed_count'] or 0),
                'incomplete_count': int(record['incomplete_count'] or 0),
                'total_courses': int(record['total_courses'] or 0),
                'completion_rate': float(record['completion_rate'] or 0),
                'status_text': _get_status_text_new(record),
                'education_date': str(record['education_date'])
                if record['education_date'] else None,
                'exclude_from_scoring': bool(record['exclude_from_scoring']),
                'exclude_reason': record['exclude_reason'],
                'notes': record['notes'],
                'period_id': record['period_id'],
                'period_name': record['period_name'],
                'period_start_date': str(record['start_date'])
                if record['start_date'] else None,
                'period_end_date': str(record['end_date'])
                if record['end_date'] else None,
                'period_completed': bool(record['period_completed']),
                'data_mode': 'new_schema',
                # ✅ 핵심 수정: 감점 로직을 다른 페이지와 통일
                'penalty_applied': penalty_applied
            }
            result_records.append(result_record)

        print(f"[DEBUG] 새 스키마 기반 기록 조회 완료: {len(result_records)}건")
        return result_records

    except Exception as e:
        print(f"[ERROR] 새 스키마 기록 조회 오류: {str(e)}")
        # ✅ 에러 발생 시에도 빈 배열 반환 (시스템 안정성)
        return []


def _get_status_text_new(record):
    """새로운 스키마 기반 상태 텍스트 생성"""
    if record['exclude_from_scoring']:
        return '제외'

    completion_rate = float(record['completion_rate'])
    if completion_rate >= 100:
        return '완료'
    elif completion_rate >= 80:
        return '수료'
    elif completion_rate > 0:
        return f'부분완료({completion_rate:.0f}%)'
    else:
        return '미실시'


# ✅ 레거시 함수 완전 제거
# _get_education_records_legacy 함수는 삭제됨


def _get_status_text_enhanced(record):
    """새로운 스키마 기반 상태 텍스트 생성"""
    if record['exclude_from_scoring']:
        return '제외'

    completion_rate = float(record['completion_rate'])
    if completion_rate >= 100:
        return '완료'
    elif completion_rate >= 80:
        return '수료'
    elif completion_rate > 0:
        return f'부분완료({completion_rate:.0f}%)'
    else:
        return '미실시'


@education_bp.route('/admin/records', methods=['GET'])
@admin_required
@handle_exceptions
def get_all_education_records():
    """모든 교육 기록 조회 (기존)"""
    year = request.args.get('year', datetime.now().year, type=int)
    education_type = request.args.get('education_type')

    try:
        records = education_service.get_all_education_records(year, education_type)
        return jsonify({'records': records})
    except Exception as e:
        return jsonify({'error': f'기록 조회 실패: {str(e)}'
                        }), HTTP_STATUS['INTERNAL_SERVER_ERROR']


@education_bp.route('/admin/overview', methods=['GET'])
@admin_required
@handle_exceptions
def get_education_overview():
    """교육 현황 개요 (관리자용)"""
    year = request.args.get('year', datetime.now().year, type=int)

    try:
        result = education_service.get_education_status(None, year)  # 전체 현황
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': f'현황 조회 실패: {str(e)}'
                        }), HTTP_STATUS['INTERNAL_SERVER_ERROR']


@education_bp.route('/periods/active', methods=['GET'])
@admin_required
@handle_exceptions
def get_active_periods():
    """활성 교육 기간 조회"""
    year = request.args.get('year', datetime.now().year, type=int)

    try:
        # 활성 기간 조회 (완료되지 않은 기간들)
        periods = execute_query(
            """
            SELECT 
                period_id, period_name, education_type, education_year,
                start_date, end_date, is_completed, description,
                CASE 
                    WHEN CURDATE() BETWEEN start_date AND end_date THEN 'active'
                    WHEN CURDATE() < start_date THEN 'upcoming'  
                    WHEN CURDATE() > end_date THEN 'ended'
                    ELSE 'unknown'
                END as status
            FROM security_education_periods
            WHERE education_year = %s 
            AND is_active = 1 
            AND is_completed = 0
            ORDER BY education_type, start_date
            """, (year, ), fetch_all=True)

        print(f"[DB_DEBUG] 조회된 활성 기간 수: {len(periods)}")

        # 날짜 포맷팅
        for period in periods:
            if period['start_date']:
                period['start_date'] = period['start_date'].strftime('%Y-%m-%d')
            if period['end_date']:
                period['end_date'] = period['end_date'].strftime('%Y-%m-%d')

        return jsonify({
            'success': True,
            'periods': periods,
            'year': year,
            'total_count': len(periods)
        })

    except Exception as e:
        print(f"[DB_DEBUG] 활성 기간 조회 실패: {e}")
        return jsonify({
            'success': False,
            'error': f'활성 기간 조회 실패: {str(e)}',
            'periods': [],
            'year': year,
            'total_count': 0
        }), HTTP_STATUS['INTERNAL_SERVER_ERROR']


@education_bp.route('/bulk-upload', methods=['POST'])
@admin_required
@handle_exceptions
@validate_json(['period_id', 'records'])
def bulk_upload():
    """
    ✅ 수정된 CSV 업로드 로직 - 새로운 스키마에 맞게 개선
    
    기존 구조 유지하면서 다음만 변경:
    1. CSV 형식: 이름,부서,수강과정,수료,미수료
    2. DB 매핑: course_name, completed_count, incomplete_count 사용
    3. 기존 completion_status 대신 새로운 컬럼 사용
    """
    data = request.json
    period_id = data.get('period_id')
    records = data.get('records', [])

    # 기본 검증 (기존 로직 유지)
    if not period_id:
        return jsonify({'error': '교육 기간을 선택해주세요.'}), HTTP_STATUS['BAD_REQUEST']

    if not records:
        return jsonify({'error': '업로드할 기록이 없습니다.'}), HTTP_STATUS['BAD_REQUEST']

    try:
        # 업로더 정보 (기존 로직 유지)
        uploaded_by = getattr(request, 'current_user', {}).get('user_id', 'admin')

        print(f"[DEBUG] 교육 업로드 시작 - period_id: {period_id}, records: {len(records)}건")

        # ✅ 핵심 수정: 새로운 CSV 형식 처리를 위한 서비스 호출
        result = education_service.process_csv_bulk_upload(
            period_id=period_id,
            csv_records=records,  # CSV 원본 데이터
            uploaded_by=uploaded_by)

        if result['success']:
            print(f"[DEBUG] 교육 업로드 성공: {result['message']}")

            # 기존 응답 형식 유지
            response_data = {
                'success': True,
                'message': result['message'],
                'success_count': result['success_count'],
                'update_count': result.get('update_count', 0),
                'error_count': result.get('error_count', 0)
            }

            if result.get('error_count', 0) > 0:
                response_data['errors'] = result.get('errors', [])

            return jsonify(response_data)
        else:
            print(f"[DEBUG] 교육 업로드 실패: {result.get('error')}")
            return jsonify({
                'success': False,
                'error': result.get('error', '업로드 처리 실패')
            }), HTTP_STATUS['BAD_REQUEST']

    except Exception as e:
        print(f"[ERROR] 교육 업로드 예외: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'업로드 처리 중 오류가 발생했습니다: {str(e)}'
        }), HTTP_STATUS['INTERNAL_SERVER_ERROR']


def bulk_update_education_with_period(self, period_id: int, records: list) -> dict:
    """교육 결과 일괄 업로드 (특정 기간에 대해)"""
    success_count = 0
    error_count = 0
    errors = []

    try:
        with DatabaseManager() as db:
            cursor = db.cursor()

            # 기간 정보 조회
            cursor.execute(
                """
                SELECT period_id, period_name, education_type, 
                       education_year, is_completed, is_active
                FROM security_education_periods
                WHERE period_id = %s
                """, (period_id, ))

            period_info = cursor.fetchone()
            if not period_info:
                raise ValueError("교육 기간을 찾을 수 없습니다.")

            expected_education_type = period_info['education_type']
            education_year = period_info['education_year']

            print(f"[DB_DEBUG] 기간 정보: {period_info}")

            for record in records:
                try:
                    # 사용자 조회
                    username = record.get('username', '').strip()
                    department = record.get('department', '').strip()
                    education_type = record.get('education_type', '').strip()

                    if not username or not department:
                        errors.append(f"필수 정보 누락: {username} ({department})")
                        error_count += 1
                        continue

                    # 교육 유형이 기간과 일치하는지 확인
                    if education_type != expected_education_type:
                        errors.append(
                            f"교육 유형 불일치: {username} - "
                            f"기대값({expected_education_type}) vs 실제값({education_type})")
                        error_count += 1
                        continue

                    # 사용자 조회 (기존 로직과 동일)
                    user_uid = self._find_user_by_name_and_department(
                        cursor, username, department)

                    if not user_uid:
                        errors.append(f"사용자를 찾을 수 없음: {username} ({department})")
                        error_count += 1
                        continue

                    # 기존 레코드 삭제 (동일 사용자 + 기간 + 교육유형)
                    cursor.execute(
                        """
                        DELETE FROM security_education
                        WHERE user_id = %s AND period_id = %s AND education_type = %s
                        """, (user_uid, period_id, education_type))

                    # 새 레코드들 생성
                    completed_count = int(record.get('completed_count', 0))
                    incomplete_count = int(record.get('incomplete_count', 0))

                    # 수료 레코드 생성
                    for i in range(completed_count):
                        cursor.execute(
                            """
                            INSERT INTO security_education 
                            (user_id, period_id, education_type, completion_status, 
                             education_year, notes, created_at)
                            VALUES (%s, %s, %s, 1, %s, %s, NOW())
                            """, (user_uid, period_id, education_type, education_year,
                                  f"엑셀 업로드 - 수료 {i+1}회차"))

                    # 미수료 레코드 생성
                    for i in range(incomplete_count):
                        cursor.execute(
                            """
                            INSERT INTO security_education 
                            (user_id, period_id, education_type, completion_status,
                             education_year, notes, created_at)
                            VALUES (%s, %s, %s, 0, %s, %s, NOW())
                            """, (user_uid, period_id, education_type, education_year,
                                  f"엑셀 업로드 - 미수료 {i+1}회차"))

                    success_count += 1
                    print(
                        f"[DB_DEBUG] 성공: {username} - 수료 {completed_count}건, 미수료 {incomplete_count}건"
                    )

                except Exception as record_error:
                    error_count += 1
                    errors.append(f"{username}: {str(record_error)}")
                    print(f"[DB_DEBUG] 레코드 처리 실패: {username} - {record_error}")
                    continue

            # 트랜잭션 커밋
            cursor.execute("COMMIT")

            return {
                'success': True,
                'success_count': success_count,
                'error_count': error_count,
                'errors': errors,
                'message': f'총 {len(records)}건 중 {success_count}건 성공, {error_count}건 실패',
                'period_info': {
                    'period_id': period_id,
                    'period_name': period_info['period_name'],
                    'education_type': period_info['education_type']
                }
            }

    except Exception as e:
        print(f"[DB_DEBUG] 일괄 업로드 실패: {e}")
        return {
            'success': False,
            'success_count': success_count,
            'error_count': error_count + 1,
            'errors': errors + [f"시스템 오류: {str(e)}"],
            'message': f'업로드 처리 중 오류가 발생했습니다: {str(e)}'
        }


def _find_user_by_name_and_department(self, cursor, username: str,
                                      department: str) -> int:
    """사용자명과 부서로 사용자 찾기 (기존 로직과 동일)"""
    print(f"[DB_DEBUG] 사용자 조회: {username} ({department})")

    # 1. 정확 매칭 (이름 + 부서)
    cursor.execute(
        "SELECT uid FROM users WHERE username = %s AND department = %s LIMIT 1",
        (username, department))
    result = cursor.fetchone()

    if result:
        print(f"[DB_DEBUG] 정확 매칭으로 사용자 발견: {username} ({department})")
        return result['uid']

    # 2. 이름만으로 검색
    cursor.execute("SELECT uid, department FROM users WHERE username = %s LIMIT 1",
                   (username, ))
    result = cursor.fetchone()

    if result:
        print(f"[DB_DEBUG] 이름으로만 사용자 발견: {username} -> 실제 부서: {result['department']}")
        return result['uid']

    # 3. 유사 이름 검색
    cursor.execute(
        "SELECT uid, username, department FROM users WHERE username LIKE %s LIMIT 1",
        (f"%{username}%", ))
    result = cursor.fetchone()

    if result:
        print(
            f"[DB_DEBUG] 유사 이름으로 사용자 발견: {result['username']} ({result['department']})")
        return result['uid']

    print(f"[DB_DEBUG] 사용자를 찾을 수 없음: {username} ({department})")
    return None


# ✅ 템플릿 다운로드도 새로운 형식으로 수정
@education_bp.route('/template/download', methods=['GET'])
@admin_required
@handle_exceptions
def download_template():
    """CSV 업로드 템플릿 다운로드 - 새로운 형식"""
    try:
        # ✅ 수정: 새로운 CSV 형식의 템플릿 생성
        csv_data = education_service.get_new_csv_template()

        csv_bytes = csv_data.encode('utf-8')
        response = make_response(csv_bytes)

        response.headers['Content-Type'] = 'text/csv; charset=utf-8'
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'

        # 한글 파일명 인코딩
        filename = '정보보호교육_업로드_템플릿.csv'
        encoded_filename = quote(filename.encode('utf-8'))

        response.headers['Content-Disposition'] = (
            f"attachment; "
            f"filename*=UTF-8''{encoded_filename}; "
            f'filename="education_template.csv"')

        return response
    except Exception as e:
        return jsonify({'error': f'템플릿 다운로드 실패: {str(e)}'
                        }), HTTP_STATUS['INTERNAL_SERVER_ERROR']


@education_bp.route('/update', methods=['PUT'])
@admin_required
@handle_exceptions
@validate_json(['education_id'])
def update_education_record():
    """개별 교육 기록 수정 - Generated Column 제외"""
    data = request.json
    education_id = data.get('education_id')

    try:
        # 기존 레코드 조회
        existing_record = execute_query(
            "SELECT * FROM security_education WHERE education_id = %s",
            (education_id, ), fetch_one=True)

        if not existing_record:
            return jsonify({'error': '수정할 교육 기록을 찾을 수 없습니다.'}), HTTP_STATUS['NOT_FOUND']

        # 수정할 필드들 - Generated Column 제외
        update_fields = []
        update_values = []

        # ✅ 직접 수정 가능한 필드들만 처리
        if 'course_name' in data:
            update_fields.append('course_name = %s')
            update_values.append(data['course_name'])

        if 'completed_count' in data:
            update_fields.append('completed_count = %s')
            update_values.append(
                int(data['completed_count']
                    ) if data['completed_count'] is not None else 0)

        if 'incomplete_count' in data:
            update_fields.append('incomplete_count = %s')
            update_values.append(
                int(data['incomplete_count']
                    ) if data['incomplete_count'] is not None else 0)

        # ✅ Generated Column은 제외 (total_courses, completion_rate는 자동 계산됨)

        if 'education_date' in data:
            update_fields.append('education_date = %s')
            update_values.append(data['education_date'])

        if 'notes' in data:
            update_fields.append('notes = %s')
            update_values.append(data['notes'])

        if 'exclude_from_scoring' in data:
            update_fields.append('exclude_from_scoring = %s')
            update_values.append(bool(data['exclude_from_scoring']))

        if 'exclude_reason' in data:
            update_fields.append('exclude_reason = %s')
            update_values.append(data['exclude_reason'])

        if not update_fields:
            return jsonify({'error': '수정할 항목이 없습니다.'}), HTTP_STATUS['BAD_REQUEST']

        # 업데이트 실행
        update_values.append(education_id)  # WHERE 조건용

        update_query = f"""
            UPDATE security_education 
            SET {', '.join(update_fields)}, updated_at = NOW()
            WHERE education_id = %s
        """

        print(f"[DB_DEBUG] 업데이트 쿼리: {update_query}")
        print(f"[DB_DEBUG] 파라미터: {tuple(update_values)}")

        execute_query(update_query, tuple(update_values))

        print(f"[DEBUG] 교육 기록 업데이트 완료: education_id={education_id}")
        print(f"[DEBUG] 업데이트된 필드: {update_fields}")

        return jsonify({'success': True, 'message': '교육 기록이 성공적으로 수정되었습니다.'})

    except Exception as e:
        print(f"[ERROR] 교육 기록 수정 실패: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'교육 기록 수정 실패: {str(e)}'
                        }), HTTP_STATUS['INTERNAL_SERVER_ERROR']


@education_bp.route('/toggle-exception', methods=['POST'])
@admin_required
@handle_exceptions
@validate_json(['user_id', 'period_id', 'education_type', 'exclude'])
def toggle_education_exception():
    """교육 예외 처리 토글"""
    data = request.json

    try:
        result = education_service.toggle_education_exception(
            data['user_id'], data['period_id'], data['education_type'], data['exclude'],
            data.get('exclude_reason', ''))

        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), HTTP_STATUS['BAD_REQUEST']

    except Exception as e:
        return jsonify({'error': f'예외 처리 실패: {str(e)}'
                        }), HTTP_STATUS['INTERNAL_SERVER_ERROR']


@education_bp.route('/delete', methods=['DELETE'])
@admin_required
@handle_exceptions
@validate_json(['user_id', 'period_id', 'education_type'])
def delete_education_record():
    """교육 기록 삭제"""
    data = request.json

    try:
        result = education_service.delete_education_record(data['user_id'],
                                                           data['period_id'],
                                                           data['education_type'])

        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), HTTP_STATUS['BAD_REQUEST']

    except Exception as e:
        return jsonify({'error': f'삭제 실패: {str(e)}'
                        }), HTTP_STATUS['INTERNAL_SERVER_ERROR']


@education_bp.route('/export', methods=['GET'])
@admin_required
@handle_exceptions
def export_education_data():
    """
    교육 데이터 CSV 내보내기 - 새로운 스키마 사용
    
    변경사항:
    1. 새로운 스키마 컬럼 사용 (course_name, completed_count, incomplete_count 등)
    2. mail 컬럼 사용 (u.mail as email)
    3. 레거시 스키마 제거
    """
    year = request.args.get('year', datetime.now().year, type=int)
    format_type = request.args.get('format', 'csv')

    try:
        if format_type != 'csv':
            return jsonify({'error': '현재 CSV 형식만 지원됩니다.'}), HTTP_STATUS['BAD_REQUEST']

        # ✅ 새로운 스키마 기반 교육 데이터 조회
        education_records = execute_query(
            """
            SELECT 
                u.user_id, 
                u.username, 
                u.department,
                u.mail as email,
                se.course_name,
                se.completed_count,
                se.incomplete_count,
                se.total_courses,
                se.completion_rate,
                se.education_type, 
                se.education_year, 
                se.education_period,
                se.education_date, 
                se.notes,
                se.exclude_from_scoring, 
                se.exclude_reason,
                sep.period_name, 
                sep.start_date, 
                sep.end_date,
                -- ✅ 호환성을 위한 상태 계산
                CASE 
                    WHEN se.completion_rate >= 80 THEN '수료'
                    WHEN se.completion_rate > 0 THEN '부분완료'
                    ELSE '미수료'
                END as completion_status_text
            FROM security_education se
            JOIN users u ON se.user_id = u.uid
            LEFT JOIN security_education_periods sep ON se.period_id = sep.period_id
            WHERE se.education_year = %s
            ORDER BY u.username, se.course_name, se.created_at
            """, (year, ), fetch_all=True)

        if not education_records:
            return jsonify({'error': f'{year}년 교육 데이터가 없습니다.'
                            }), HTTP_STATUS['NOT_FOUND']

        # CSV 데이터 생성
        csv_lines = []

        # UTF-8 BOM 추가 (Excel에서 한글 인식용)
        bom = "\ufeff"

        # ✅ 새로운 헤더 구성
        headers = [
            "사용자ID", "사용자명", "부서", "이메일", "과정명", "수료건수", "미수료건수", "전체과정수", "수료율(%)",
            "교육유형", "교육연도", "교육기간", "수료상태", "교육일", "비고", "점수제외", "제외사유", "기간명", "시작일",
            "종료일"
        ]

        # BOM과 함께 헤더 추가
        csv_lines.append(bom + ",".join(headers))

        # ✅ 새로운 스키마 데이터 처리
        for record in education_records:
            row = [
                str(record.get("user_id", "")).replace('"', '""'),
                str(record.get("username", "")).replace('"', '""'),
                str(record.get("department", "")).replace('"', '""'),
                str(record.get("email", "")).replace('"', '""'),
                str(record.get("course_name", "")).replace('"', '""'),
                str(record.get("completed_count", 0)),
                str(record.get("incomplete_count", 0)),
                str(record.get("total_courses", 0)),
                str(float(record.get("completion_rate", 0))),
                str(record.get("education_type", "")).replace('"', '""'),
                str(record.get("education_year", "")),
                "상반기" if record.get("education_period") == "first_half" else "하반기",
                str(record.get("completion_status_text", "")).replace('"', '""'),
                str(record.get("education_date", "")).replace('"', '""'),
                str(record.get("notes", "")).replace('"', '""'),
                "제외" if record.get("exclude_from_scoring") == 1 else "포함",
                str(record.get("exclude_reason", "")).replace('"', '""'),
                str(record.get("period_name", "")).replace('"', '""'),
                str(record.get("start_date", "")).replace('"', '""'),
                str(record.get("end_date", "")).replace('"', '""'),
            ]
            # CSV RFC 4180 표준에 따라 필드를 따옴표로 감싸기
            csv_lines.append(",".join(f'"{item}"' for item in row))

        csv_content = "\n".join(csv_lines)

        # 응답 생성
        response = make_response(csv_content.encode('utf-8'))
        response.headers['Content-Type'] = 'text/csv; charset=utf-8'
        response.headers[
            'Content-Disposition'] = f'attachment; filename="교육데이터_{year}.csv"'

        return response

    except Exception as e:
        print(f"[ERROR] 교육 데이터 내보내기 실패: {str(e)}")
        return jsonify({'error': f'데이터 내보내기 실패: {str(e)}'
                        }), HTTP_STATUS['INTERNAL_SERVER_ERROR']


# ✅ 교육 기간 상태 조회 API 추가
@education_bp.route('/periods/status', methods=['GET'])
@admin_required
@handle_exceptions
def get_periods_status():
    """업로드 가능한 교육 기간 목록 조회"""
    year = request.args.get('year', datetime.now().year, type=int)

    try:
        result = period_service.get_period_status(year)
        return jsonify(result)
    except Exception as e:
        print(f"[ERROR] 교육 기간 상태 조회 실패: {str(e)}")
        return jsonify({'error': f'교육 기간 상태 조회 실패: {str(e)}'
                        }), HTTP_STATUS['INTERNAL_SERVER_ERROR']


@education_bp.route('/periods', methods=['GET'])
@admin_required
@handle_exceptions
def get_period_status():
    """교육 기간 현황 조회 (기존 엔드포인트)"""
    year = request.args.get('year', datetime.now().year, type=int)

    try:
        result = period_service.get_period_status(year)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': f'기간 조회 실패: {str(e)}'
                        }), HTTP_STATUS['INTERNAL_SERVER_ERROR']


@education_bp.route('/periods', methods=['POST'])
@admin_required
@handle_exceptions
@validate_json(
    ['education_year', 'period_name', 'education_type', 'start_date', 'end_date'])
def create_period():
    """새 교육 기간 생성"""
    data = request.json
    created_by = request.current_user.get('user_id', 'admin')

    try:
        result = period_service.create_period(data, created_by)

        if result['success']:
            return jsonify(result), HTTP_STATUS['CREATED']
        else:
            return jsonify(result), HTTP_STATUS['BAD_REQUEST']

    except Exception as e:
        return jsonify({'error': f'기간 생성 실패: {str(e)}'
                        }), HTTP_STATUS['INTERNAL_SERVER_ERROR']


@education_bp.route('/periods/<int:period_id>/complete', methods=['POST'])
@admin_required
@handle_exceptions
def complete_period(period_id):
    """교육 기간 완료 처리"""
    completed_by = request.current_user.get('user_id', 'admin')

    try:
        result = period_service.complete_period(period_id, completed_by)

        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), HTTP_STATUS['BAD_REQUEST']

    except Exception as e:
        return jsonify({'error': f'완료 처리 실패: {str(e)}'
                        }), HTTP_STATUS['INTERNAL_SERVER_ERROR']


@education_bp.route('/periods/<int:period_id>/reopen', methods=['POST'])
@admin_required
@handle_exceptions
def reopen_period(period_id):
    """교육 기간 재개"""
    try:
        result = period_service.reopen_period(period_id)

        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), HTTP_STATUS['BAD_REQUEST']

    except Exception as e:
        return jsonify({'error': f'재개 처리 실패: {str(e)}'
                        }), HTTP_STATUS['INTERNAL_SERVER_ERROR']
