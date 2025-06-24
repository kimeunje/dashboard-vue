# back-end/app/services/education_period_service.py
from datetime import datetime, date
from app.utils.database import execute_query, DatabaseManager


class EducationPeriodService:
    """정보보호 교육 기간 관리 서비스"""

    def get_period_status(self, year: int = None) -> dict:
        """연도별 교육 기간 현황 조회"""
        if year is None:
            year = datetime.now().year

        # 교육 유형별 기간 목록 조회
        periods = execute_query(
            """
            SELECT 
                period_id,
                period_name,
                education_type,
                start_date,
                end_date,
                is_completed,
                completed_at,
                completed_by,
                description,
                auto_pass_setting,
                CASE 
                    WHEN CURDATE() BETWEEN start_date AND end_date THEN 'active'
                    WHEN CURDATE() < start_date THEN 'upcoming'
                    WHEN CURDATE() > end_date THEN 'ended'
                    ELSE 'unknown'
                END as status
            FROM security_education_periods
            WHERE education_year = %s AND is_active = 1
            ORDER BY education_type, start_date
            """,
            (year, ),
            fetch_all=True,
        )

        # 교육 유형별로 그룹화
        education_types = {}
        for period in periods:
            education_type = period['education_type']
            if education_type not in education_types:
                education_types[education_type] = {
                    'type_name': education_type,
                    'periods': []
                }
            education_types[education_type]['periods'].append(period)

        return {
            'year': year,
            'education_types': education_types,
            'total_periods': len(periods)
        }

    def create_period(self, period_data: dict, created_by: str) -> dict:
        """새 교육 기간 생성"""
        try:
            print(f"[DB_DEBUG] 기간 생성 요청: {period_data}")

            # 1. 중복 검사
            if self.check_period_exists(period_data['education_year'],
                                        period_data['period_name'],
                                        period_data['education_type']):
                print(f"[DB_DEBUG] 중복 기간 발견")
                return {'success': False, 'message': '동일한 연도, 기간명, 교육유형의 기간이 이미 존재합니다.'}

            # 2. 날짜 겹침 검사
            overlap_check = self.check_date_overlap(period_data['education_type'],
                                                    period_data['start_date'],
                                                    period_data['end_date'])

            if overlap_check['has_overlap']:
                overlap_details = []
                for period in overlap_check['overlapping_periods']:
                    overlap_details.append(
                        f"{period['year']}년 {period['period_name']} ({period['start_date']} ~ {period['end_date']})"
                    )

                return {
                    'success': False,
                    'message': f"날짜가 겹치는 기간이 있습니다: {', '.join(overlap_details)}",
                    'overlapping_periods': overlap_check['overlapping_periods']
                }

            # 3. 기간 생성 (return_id 제거하고 DatabaseManager 사용)
            print(f"[DB_DEBUG] 기간 생성 진행")

            with DatabaseManager.get_db_cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO security_education_periods 
                    (education_year, period_name, education_type, start_date, end_date, 
                    description, auto_pass_setting, created_by)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """, (period_data['education_year'], period_data['period_name'],
                          period_data['education_type'], period_data['start_date'],
                          period_data['end_date'], period_data.get('description', ''),
                          period_data.get('auto_pass_setting', 1), created_by))

                period_id = cursor.lastrowid

            print(f"[DB_DEBUG] 기간 생성 완료, period_id: {period_id}")

            return {
                'success': True,
                'message': f"{period_data['period_name']} 기간이 생성되었습니다.",
                'period_id': period_id
            }

        except Exception as e:
            print(f"[DB_DEBUG] 기간 생성 예외: {str(e)}")
            return {'success': False, 'message': f'기간 생성 실패: {str(e)}'}

    def complete_period(self, period_id: int, completed_by: str) -> dict:
        """교육 기간 완료 처리 (자동 통과 기능 포함)"""
        try:
            print(
                f"[DB_DEBUG] 완료 처리 시작 - period_id: {period_id}, completed_by: {completed_by}"
            )

            with DatabaseManager.get_db_cursor() as cursor:
                # 기간 정보 조회
                print(f"[DB_DEBUG] 기간 정보 조회 중...")
                cursor.execute(
                    """
                        SELECT period_name, education_type, education_year, auto_pass_setting, is_completed
                        FROM security_education_periods 
                        WHERE period_id = %s AND is_active = 1
                        """, (period_id, ))
                period_info = cursor.fetchone()

                print(f"[DB_DEBUG] 기간 정보: {period_info}")

                if not period_info:
                    print(f"[DB_DEBUG] 기간 정보 없음")
                    return {'success': False, 'message': '해당 기간을 찾을 수 없습니다.'}

                if period_info['is_completed']:
                    print(f"[DB_DEBUG] 이미 완료된 기간")
                    return {'success': False, 'message': '이미 완료된 기간입니다.'}

                # 자동 통과 처리 (설정이 활성화된 경우) - 더 안전한 방식
                auto_passed_count = 0
                if period_info['auto_pass_setting']:
                    print(f"[DB_DEBUG] 자동 통과 처리 시작")
                    try:
                        # 먼저 해당 기간에 이미 교육 기록이 없는 사용자들을 찾기
                        cursor.execute(
                            """
                            SELECT u.uid, u.username
                            FROM users u
                            WHERE u.uid NOT IN (
                                SELECT DISTINCT user_id 
                                FROM security_education 
                                WHERE period_id = %s
                            )
                            """, (period_id, ))

                        users_to_auto_pass = cursor.fetchall()
                        print(f"[DB_DEBUG] 자동 통과 대상 사용자: {len(users_to_auto_pass)}명")

                        # 각 사용자별로 개별 INSERT (IGNORE 사용으로 중복 오류 방지)
                        for user in users_to_auto_pass:
                            try:
                                print(
                                    f"[DB_DEBUG] 자동 통과 처리: {user['username']} (uid: {user['uid']})"
                                )
                                cursor.execute(
                                    """
                                    INSERT IGNORE INTO security_education 
                                    (user_id, period_id, education_type, education_year, education_period,
                                    completion_status, notes, created_at)
                                    VALUES (%s, %s, %s, %s, 'auto_complete', 1, '기간 완료로 인한 자동 통과 처리', NOW())
                                    """, (user['uid'], period_id,
                                          period_info['education_type'],
                                          period_info['education_year']))

                                if cursor.rowcount > 0:
                                    auto_passed_count += 1
                                    print(f"[DB_DEBUG] {user['username']} 자동 통과 성공")
                                else:
                                    print(
                                        f"[DB_DEBUG] {user['username']} 자동 통과 실패 - 이미 기록 존재"
                                    )

                            except Exception as user_error:
                                print(
                                    f"[DB_DEBUG] 사용자 {user['username']} 자동 통과 실패: {str(user_error)}"
                                )
                                continue

                        print(f"[DB_DEBUG] 자동 통과 처리 완료 - {auto_passed_count}명")

                        # 실제 INSERT된 데이터 확인
                        cursor.execute(
                            """
                            SELECT u.username, se.education_type, se.completion_status, se.notes, se.created_at
                            FROM security_education se
                            JOIN users u ON se.user_id = u.uid
                            WHERE se.period_id = %s AND se.notes = '기간 완료로 인한 자동 통과 처리'
                            ORDER BY se.created_at DESC
                            LIMIT 5
                            """, (period_id, ))

                        inserted_records = cursor.fetchall()
                        print(f"[DB_DEBUG] INSERT 확인 - {len(inserted_records)}건:")
                        for record in inserted_records:
                            print(
                                f"[DB_DEBUG] - {record['username']}: {record['education_type']} ({record['created_at']})"
                            )

                    except Exception as e:
                        print(f"[DB_DEBUG] 자동 통과 처리 실패: {str(e)}")
                        # 자동 통과 처리 실패해도 계속 진행

                # 기간 완료 상태 업데이트
                print(f"[DB_DEBUG] 기간 완료 상태 업데이트 중...")
                cursor.execute(
                    """
                        UPDATE security_education_periods
                        SET is_completed = 1, completed_at = NOW(), completed_by = %s, updated_at = NOW()
                        WHERE period_id = %s
                        """, (completed_by, period_id))

                print(f"[DB_DEBUG] 기간 완료 처리 성공")

                return {
                    'success': True,
                    'message': f"{period_info['period_name']} 기간이 완료되었습니다. (자동 통과: {auto_passed_count}명)"
                }

        except Exception as e:
            print(f"[DB_DEBUG] 완료 처리 예외: {str(e)}")
            import traceback
            traceback.print_exc()
            return {'success': False, 'message': f'완료 처리 실패: {str(e)}'}

    def reopen_period(self, period_id: int) -> dict:
        """교육 기간 재개"""
        try:
            with DatabaseManager.get_db_cursor() as cursor:
                # 기간 정보 조회
                cursor.execute(
                    "SELECT period_name, is_completed FROM security_education_periods WHERE period_id = %s AND is_active = 1",
                    (period_id, ))
                period_info = cursor.fetchone()

                if not period_info:
                    return {'success': False, 'message': '해당 기간을 찾을 수 없습니다.'}

                if not period_info['is_completed']:
                    return {'success': False, 'message': '완료되지 않은 기간입니다.'}

                # 자동 통과 처리된 결과 삭제
                cursor.execute(
                    """
                        DELETE FROM security_education
                        WHERE period_id = %s AND notes = '기간 완료로 인한 자동 통과 처리'
                        """, (period_id, ))

                # 기간 재개
                cursor.execute(
                    """
                        UPDATE security_education_periods
                        SET is_completed = 0, completed_at = NULL, completed_by = NULL, updated_at = NOW()
                        WHERE period_id = %s
                        """, (period_id, ))

                return {
                    'success': True,
                    'message': f"{period_info['period_name']} 기간이 재개되었습니다."
                }

        except Exception as e:
            return {'success': False, 'message': f'재개 처리 실패: {str(e)}'}

    def check_period_exists(self, year: int, period_name: str,
                            education_type: str) -> bool:
        """기간 중복 체크"""
        result = execute_query(
            """
            SELECT COUNT(*) as count
            FROM security_education_periods
            WHERE education_year = %s AND period_name = %s AND education_type = %s AND is_active = 1
            """, (year, period_name, education_type), fetch_one=True)
        return result['count'] > 0

    def check_date_overlap(self, education_type: str, start_date, end_date,
                           exclude_period_id: int = None) -> dict:
        """날짜 겹침 검사 - 더 상세한 로깅 추가"""
        try:
            from datetime import datetime

            # 날짜 타입 변환
            if isinstance(start_date, str):
                start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
            if isinstance(end_date, str):
                end_date = datetime.strptime(end_date, "%Y-%m-%d").date()

            print(
                f"[DB_DEBUG] 날짜 겹침 검사 - 교육유형: {education_type}, 기간: {start_date} ~ {end_date}"
            )

            # 같은 교육 유형의 활성 기간들 조회
            query = """
                    SELECT period_id, period_name, start_date, end_date, education_year       
                    FROM security_education_periods
                    WHERE education_type = %s AND is_active = 1
                """
            params = [education_type]

            # 수정 시 현재 기간 제외
            if exclude_period_id:
                query += " AND period_id != %s"
                params.append(exclude_period_id)

            existing_periods = execute_query(query, params, fetch_all=True)

            print(f"[DB_DEBUG] 기존 기간 조회 결과: {len(existing_periods)}건")
            for period in existing_periods:
                print(
                    f"[DB_DEBUG] 기존 기간: {period['period_name']} ({period['start_date']} ~ {period['end_date']})"
                )

            overlapping_periods = []

            for period in existing_periods:
                existing_start = period['start_date']
                existing_end = period['end_date']

                # 날짜 겹침 검사 로직
                is_overlapping = (
                    (start_date <= existing_start <= end_date) or  # 새 기간이 기존 기간 시작일을 포함
                    (start_date <= existing_end <= end_date) or  # 새 기간이 기존 기간 종료일을 포함
                    (existing_start <= start_date <= existing_end)
                    or  # 기존 기간이 새 기간 시작일을 포함
                    (existing_start <= end_date <= existing_end)  # 기존 기간이 새 기간 종료일을 포함
                )

                print(f"[DB_DEBUG] 겹침 검사 - {period['period_name']}: {is_overlapping}")

                if is_overlapping:
                    overlapping_periods.append({
                        'period_id': period['period_id'],
                        'period_name': period['period_name'],
                        'start_date': str(existing_start),
                        'end_date': str(existing_end),
                        'year': period['education_year']
                    })

            print(f"[DB_DEBUG] 겹치는 기간 수: {len(overlapping_periods)}")

            return {
                'has_overlap': len(overlapping_periods) > 0,
                'overlapping_periods': overlapping_periods,
                'message': f"{len(overlapping_periods)}개의 겹치는 기간이 발견되었습니다."
                if overlapping_periods else "겹치는 기간이 없습니다."
            }

        except Exception as e:
            print(f"[DB_DEBUG] 날짜 겹침 검사 오류: {str(e)}")
            return {
                'has_overlap': False,
                'overlapping_periods': [],
                'message': f"검사 중 오류 발생: {str(e)}"
            }
