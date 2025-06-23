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


@education_bp.route('/status', methods=['GET'])
@handle_exceptions
def get_education_status():
    """사용자별 교육 현황 조회 (일반 사용자용)"""
    year = request.args.get('year', datetime.now().year, type=int)

    # 현재 사용자 정보 (토큰에서 추출 또는 세션에서)
    current_user = getattr(request, 'current_user', None)
    if not current_user:
        return jsonify({'error': '인증이 필요합니다.'}), HTTP_STATUS['UNAUTHORIZED']

    user_id = current_user.get('uid')

    try:
        # 사용자별 교육 현황 조회
        education_status = execute_query(
            """
            SELECT 
                se.education_type, se.completion_status, se.education_date,
                se.exclude_from_scoring, se.notes,
                sep.period_name, sep.start_date, sep.end_date, sep.is_completed
            FROM security_education se
            LEFT JOIN security_education_periods sep ON se.period_id = sep.period_id
            WHERE se.user_id = %s AND se.education_year = %s
            ORDER BY se.education_type, se.created_at
            """, (user_id, year), fetch_all=True)

        # 교육 유형별 통계 계산
        education_summary = {
            'year': year,
            'education_status': [],
            'summary': {
                'total_courses': len(education_status),
                'completed': len(
                    [e for e in education_status if e['completion_status'] == 1]),
                'incomplete': len(
                    [e for e in education_status if e['completion_status'] == 0]),
                'completion_rate': 0,
                'penalty_score': 0.0,
                'excluded_count': len(
                    [e for e in education_status if e['exclude_from_scoring'] == 1])
            }
        }

        # 완료율 계산
        if education_summary['summary']['total_courses'] > 0:
            education_summary['summary']['completion_rate'] = round(
                (education_summary['summary']['completed'] /
                 education_summary['summary']['total_courses']) * 100)

        # 교육 유형별 세부 정보
        education_types = {}
        for record in education_status:
            edu_type = record['education_type']
            if edu_type not in education_types:
                education_types[edu_type] = {
                    'type': edu_type,
                    'type_name': edu_type,
                    'total_courses': 0,
                    'completed_courses': 0,
                    'incomplete_courses': 0,
                    'status': 'not_started',
                    'education_date': None,
                    'exclude_from_scoring': False,
                    'notes': None
                }

            education_types[edu_type]['total_courses'] += 1
            if record['completion_status'] == 1:
                education_types[edu_type]['completed_courses'] += 1
                education_types[edu_type]['status'] = 'completed'
                if record['education_date']:
                    education_types[edu_type]['education_date'] = str(
                        record['education_date'])
            else:
                education_types[edu_type]['incomplete_courses'] += 1
                if education_types[edu_type]['status'] != 'completed':
                    education_types[edu_type]['status'] = 'incomplete'

            if record['exclude_from_scoring']:
                education_types[edu_type]['exclude_from_scoring'] = True

            if record['notes']:
                education_types[edu_type]['notes'] = record['notes']

        education_summary['education_status'] = list(education_types.values())

        return jsonify(education_summary)

    except Exception as e:
        print(f"[ERROR] 교육 현황 조회 실패: {str(e)}")
        return jsonify({'error': f'교육 현황 조회 실패: {str(e)}'
                        }), HTTP_STATUS['INTERNAL_SERVER_ERROR']


# 누락된 엔드포인트 1: /api/security-education/records
@education_bp.route('/records', methods=['GET'])
@admin_required
@handle_exceptions
def get_education_records():
    """교육 기록 조회 (관리자용)"""
    year = request.args.get('year', datetime.now().year, type=int)
    education_type = request.args.get('education_type', '')
    status = request.args.get('status', '')

    try:
        records = education_service.get_all_education_records(
            year, education_type, status)
        return jsonify(records)
    except Exception as e:
        return jsonify({'error': f'기록 조회 실패: {str(e)}'
                        }), HTTP_STATUS['INTERNAL_SERVER_ERROR']


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
def bulk_upload_education():
    """
    ✅ 개선된 교육 결과 일괄 업로드
    
    개선사항:
    1. 프론트엔드는 원시 데이터만 전송
    2. 백엔드에서 수료/미수료 결정 로직 처리
    3. 비즈니스 규칙 검증 강화
    4. 데이터 일관성 보장
    """
    data = request.json
    period_id = data.get('period_id')
    records = data.get('records', [])

    # 기본 검증
    if not period_id:
        return jsonify({'error': '교육 기간을 선택해주세요.'}), HTTP_STATUS['BAD_REQUEST']

    if not records:
        return jsonify({'error': '업로드할 기록이 없습니다.'}), HTTP_STATUS['BAD_REQUEST']

    try:
        # 업로더 정보 (세션에서 가져오거나 토큰에서 추출)
        uploaded_by = getattr(request, 'current_user', {}).get('user_id', 'admin')

        print(
            f"[DEBUG] 교육 업로드 시작 - period_id: {period_id}, records: {len(records)}건, 업로더: {uploaded_by}"
        )

        # ✅ 핵심 개선: 비즈니스 로직을 서비스 레이어에서 처리
        result = education_service.process_bulk_upload(period_id=period_id,
                                                       records=records,
                                                       uploaded_by=uploaded_by)

        if result['success']:
            print(f"[DEBUG] 교육 업로드 성공: {result['message']}")

            # 성공 응답
            response_data = {
                'success': True,
                'message': result['message'],
                'success_count': result['success_count'],
                'update_count': result.get('update_count', 0),
                'error_count': result.get('error_count', 0)
            }

            # 오류가 있는 경우 오류 정보도 포함
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


@education_bp.route('/template/download', methods=['GET'])
@admin_required
@handle_exceptions
def download_template():
    """교육 업로드 템플릿 다운로드"""
    try:
        csv_data = education_service.get_education_excel_template()

        # UTF-8로 인코딩된 바이트 데이터로 변환
        csv_bytes = csv_data.encode('utf-8')
        response = make_response(csv_bytes)

        # 올바른 Content-Type 설정
        response.headers['Content-Type'] = 'text/csv; charset=utf-8'
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'

        # 한글 파일명을 RFC 5987 방식으로 인코딩
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
    """개별 교육 기록 수정"""
    data = request.json
    education_id = data.get('education_id')

    try:
        # 기존 레코드 조회
        existing_record = execute_query(
            "SELECT * FROM security_education WHERE education_id = %s",
            (education_id, ), fetch_one=True)

        if not existing_record:
            return jsonify({'error': '수정할 교육 기록을 찾을 수 없습니다.'}), HTTP_STATUS['NOT_FOUND']

        # 수정할 필드들
        update_fields = []
        update_values = []

        if 'completion_status' in data:
            update_fields.append('completion_status = %s')
            update_values.append(data['completion_status'])

        if 'education_date' in data:
            update_fields.append('education_date = %s')
            update_values.append(data['education_date'])

        if 'notes' in data:
            update_fields.append('notes = %s')
            update_values.append(data['notes'])

        if 'exclude_from_scoring' in data:
            update_fields.append('exclude_from_scoring = %s')
            update_values.append(data['exclude_from_scoring'])

        if 'exclude_reason' in data:
            update_fields.append('exclude_reason = %s')
            update_values.append(data['exclude_reason'])

        if not update_fields:
            return jsonify({'error': '수정할 항목이 없습니다.'}), HTTP_STATUS['BAD_REQUEST']

        # 업데이트 실행
        update_values.append(education_id)  # WHERE 조건용
        execute_query(
            f"""
            UPDATE security_education 
            SET {', '.join(update_fields)}, updated_at = NOW()
            WHERE education_id = %s
            """, tuple(update_values))

        return jsonify({'success': True, 'message': '교육 기록이 성공적으로 수정되었습니다.'})

    except Exception as e:
        print(f"[ERROR] 교육 기록 수정 실패: {str(e)}")
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
    """교육 데이터 CSV 내보내기"""
    year = request.args.get('year', datetime.now().year, type=int)
    format_type = request.args.get('format', 'csv')

    try:
        if format_type != 'csv':
            return jsonify({'error': '현재 CSV 형식만 지원됩니다.'}), HTTP_STATUS['BAD_REQUEST']

        # 교육 데이터 조회
        education_records = execute_query(
            """
            SELECT 
                u.user_id, u.username, u.department,
                se.education_type, se.education_year, se.education_period,
                se.completion_status, se.education_date, se.notes,
                se.exclude_from_scoring, se.exclude_reason,
                sep.period_name, sep.start_date, sep.end_date
            FROM security_education se
            JOIN users u ON se.user_id = u.uid
            LEFT JOIN security_education_periods sep ON se.period_id = sep.period_id
            WHERE se.education_year = %s
            ORDER BY u.username, se.education_type, se.created_at
            """, (year, ), fetch_all=True)

        if not education_records:
            return jsonify({'error': f'{year}년 교육 데이터가 없습니다.'
                            }), HTTP_STATUS['NOT_FOUND']

        # CSV 데이터 생성
        csv_lines = []

        # UTF-8 BOM 추가 (Excel에서 한글 인식용)
        bom = "\ufeff"

        headers = [
            "사용자ID", "사용자명", "부서", "교육유형", "교육연도", "교육기간", "수료상태", "교육일", "비고", "점수제외",
            "제외사유", "기간명", "시작일", "종료일"
        ]

        # BOM과 함께 헤더 추가
        csv_lines.append(bom + ",".join(headers))

        for record in education_records:
            row = [
                str(record.get("user_id", "")).replace('"', '""'),
                str(record.get("username", "")).replace('"', '""'),
                str(record.get("department", "")).replace('"', '""'),
                str(record.get("education_type", "")).replace('"', '""'),
                str(record.get("education_year", "")).replace('"', '""'),
                "상반기" if record.get("education_period") == "first_half" else "하반기",
                "수료" if record.get("completion_status") == 1 else "미수료",
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