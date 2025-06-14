# app/services/manual_check_period_service.py
from datetime import datetime, date
from app.utils.database import execute_query, DatabaseManager


class ManualCheckPeriodService:
    """수시 점검 기간 관리 서비스"""

    def get_period_status(self, year: int = None) -> dict:
        """연도별 점검 기간 현황 조회"""
        if year is None:
            year = datetime.now().year

        # 기본 점검 유형 정의
        check_types = {
            "seal_check": "PC 봉인씰 확인",
            "malware_scan": "악성코드 전체 검사",
            "file_encryption": "개인정보 파일 암호화",
        }

        result = {"year": year, "check_types": {}}

        for check_type, type_name in check_types.items():
            # 해당 연도/유형의 기간 목록 조회
            periods = execute_query(
                """
                SELECT 
                    period_id,
                    period_name,
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
                FROM manual_check_periods
                WHERE check_type = %s AND period_year = %s AND is_active = 1
                ORDER BY start_date
                """,
                (check_type, year),
                fetch_all=True,
            )

            # 각 기간별 통계 조회
            for period in periods:
                stats = execute_query(
                    """
                    SELECT 
                        COUNT(DISTINCT user_id) as total_users,
                        COALESCE(SUM(CASE WHEN overall_result = 'pass' THEN 1 ELSE 0 END), 0) as pass_count,
                        COALESCE(SUM(CASE WHEN overall_result = 'fail' THEN 1 ELSE 0 END), 0) as fail_count
                    FROM manual_check_results
                    WHERE check_item_code = %s 
                    AND check_year = %s 
                    AND period_id = %s
                    """,
                    (check_type, year, period["period_id"]),
                    fetch_one=True,
                )

                if stats:
                    # None 값을 0으로 변환
                    period.update(
                        {
                            "total_users": stats.get("total_users") or 0,
                            "pass_count": stats.get("pass_count") or 0,
                            "fail_count": stats.get("fail_count") or 0,
                        }
                    )
                else:
                    period.update({"total_users": 0, "pass_count": 0, "fail_count": 0})

                # 날짜 포맷팅
                if period["start_date"]:
                    period["start_date"] = period["start_date"].strftime("%Y-%m-%d")
                if period["end_date"]:
                    period["end_date"] = period["end_date"].strftime("%Y-%m-%d")
                if period["completed_at"]:
                    period["completed_at"] = period["completed_at"].strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )

            result["check_types"][check_type] = {
                "type_name": type_name,
                "periods": periods,
                "total_users": sum(p.get("total_users", 0) or 0 for p in periods),
                "pass_count": sum(p.get("pass_count", 0) or 0 for p in periods),
                "fail_count": sum(p.get("fail_count", 0) or 0 for p in periods),
            }

        return result

    def create_period(self, data: dict, created_by: str) -> dict:
        """새로운 점검 기간 생성"""
        try:
            print(f"[DEBUG] 서비스 create_period 시작: {data}")

            # 중복 체크
            existing = execute_query(
                """
                SELECT period_id FROM manual_check_periods
                WHERE check_type = %s AND period_year = %s AND period_name = %s AND is_active = 1
                """,
                (data["check_type"], data["period_year"], data["period_name"]),
                fetch_one=True,
            )

            if existing:
                print(f"[DEBUG] 중복 기간 발견")
                return {
                    "success": False,
                    "message": f"{data['period_year']}년 {data['period_name']} 기간이 이미 존재합니다.",
                }

            # 날짜 유효성 검사
            start_date = datetime.strptime(data["start_date"], "%Y-%m-%d").date()
            end_date = datetime.strptime(data["end_date"], "%Y-%m-%d").date()
            print(f"[DEBUG] 날짜 파싱 완료: {start_date} ~ {end_date}")

            if end_date <= start_date:
                print(f"[DEBUG] 날짜 유효성 검사 실패")
                return {
                    "success": False,
                    "message": "종료일은 시작일보다 늦어야 합니다.",
                }

            # 기간 생성
            result = execute_query(
                """
                INSERT INTO manual_check_periods 
                (check_type, period_year, period_name, start_date, end_date, 
                 description, auto_pass_setting, created_by)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    data["check_type"],
                    data["period_year"],
                    data["period_name"],
                    start_date,
                    end_date,
                    data.get("description", ""),
                    data.get("auto_pass_setting", True),
                    created_by,
                ),
            )

            print(f"[DEBUG] INSERT 결과: {result}")

            # INSERT 성공 여부 확인
            if result <= 0:
                print(f"[DEBUG] INSERT 실패")
                return {"success": False, "message": "기간 생성에 실패했습니다."}

            print(f"[DEBUG] 기간 생성 성공")
            return {
                "success": True,
                "message": "점검 기간이 성공적으로 생성되었습니다.",
                "affected_rows": result,
            }

        except ValueError as e:
            print(f"[DEBUG] ValueError: {str(e)}")
            return {
                "success": False,
                "message": f"날짜 형식이 올바르지 않습니다: {str(e)}",
            }
        except Exception as e:
            print(f"[DEBUG] Exception: {str(e)}")
            import traceback

            traceback.print_exc()
            return {"success": False, "message": f"기간 생성 실패: {str(e)}"}

    def update_period(self, period_id: int, data: dict) -> dict:
        """점검 기간 수정"""
        try:
            # 기간 존재 확인
            existing = execute_query(
                "SELECT period_id, is_completed FROM manual_check_periods WHERE period_id = %s AND is_active = 1",
                (period_id,),
                fetch_one=True,
            )

            if not existing:
                return {"success": False, "message": "해당 기간을 찾을 수 없습니다."}

            if existing["is_completed"]:
                return {
                    "success": False,
                    "message": "완료된 기간은 수정할 수 없습니다.",
                }

            # 날짜 유효성 검사
            start_date = datetime.strptime(data["start_date"], "%Y-%m-%d").date()
            end_date = datetime.strptime(data["end_date"], "%Y-%m-%d").date()

            if end_date <= start_date:
                return {
                    "success": False,
                    "message": "종료일은 시작일보다 늦어야 합니다.",
                }

            # 기간 수정
            execute_query(
                """
                UPDATE manual_check_periods 
                SET start_date = %s, end_date = %s, description = %s, 
                    auto_pass_setting = %s, updated_at = NOW()
                WHERE period_id = %s
                """,
                (
                    start_date,
                    end_date,
                    data.get("description", ""),
                    data.get("auto_pass_setting", True),
                    period_id,
                ),
            )

            return {
                "success": True,
                "message": "점검 기간이 성공적으로 수정되었습니다.",
            }

        except ValueError as e:
            return {
                "success": False,
                "message": f"날짜 형식이 올바르지 않습니다: {str(e)}",
            }
        except Exception as e:
            return {"success": False, "message": f"기간 수정 실패: {str(e)}"}

    def delete_period(self, period_id: int) -> dict:
        """점검 기간 삭제"""
        try:
            with DatabaseManager.get_db_cursor() as cursor:
                # 기간 존재 확인
                cursor.execute(
                    "SELECT period_id, is_completed FROM manual_check_periods WHERE period_id = %s AND is_active = 1",
                    (period_id,),
                )
                existing = cursor.fetchone()

                if not existing:
                    return {
                        "success": False,
                        "message": "해당 기간을 찾을 수 없습니다.",
                    }

                if existing["is_completed"]:
                    return {
                        "success": False,
                        "message": "완료된 기간은 삭제할 수 없습니다.",
                    }

                # 연결된 점검 결과 확인
                cursor.execute(
                    "SELECT COUNT(*) as count FROM manual_check_results WHERE period_id = %s",
                    (period_id,),
                )
                result_count = cursor.fetchone()["count"]

                if result_count > 0:
                    return {
                        "success": False,
                        "message": f"해당 기간에 {result_count}개의 점검 결과가 있어 삭제할 수 없습니다.",
                    }

                # 기간 삭제 (소프트 삭제)
                cursor.execute(
                    "UPDATE manual_check_periods SET is_active = 0, updated_at = NOW() WHERE period_id = %s",
                    (period_id,),
                )

                return {
                    "success": True,
                    "message": "점검 기간이 성공적으로 삭제되었습니다.",
                }

        except Exception as e:
            return {"success": False, "message": f"기간 삭제 실패: {str(e)}"}

    def complete_period(self, period_id: int, completed_by: str) -> dict:
        """점검 기간 완료 처리 - 중복 점수 반영 방지"""
        try:
            with DatabaseManager.get_db_cursor() as cursor:
                # 기간 정보 조회
                cursor.execute(
                    """
                    SELECT check_type, period_year, period_name, is_completed, auto_pass_setting
                    FROM manual_check_periods
                    WHERE period_id = %s AND is_active = 1
                    """,
                    (period_id,),
                )
                period_info = cursor.fetchone()

                if not period_info:
                    return {
                        "success": False,
                        "message": "해당 기간을 찾을 수 없습니다.",
                    }

                if period_info["is_completed"]:
                    return {"success": False, "message": "이미 완료된 기간입니다."}

                # 기간 완료 처리
                cursor.execute(
                    """
                    UPDATE manual_check_periods
                    SET is_completed = 1, completed_at = NOW(), completed_by = %s, updated_at = NOW()
                    WHERE period_id = %s
                    """,
                    (completed_by, period_id),
                )

                # 자동 통과 처리가 활성화된 경우
                if period_info["auto_pass_setting"]:
                    print(
                        f"[DEBUG] 자동 통과 처리 시작 - 점검 유형: {period_info['check_type']}"
                    )

                    # 🔥 핵심 수정: 해당 기간과 점검 유형에 대해 이미 결과가 있는 사용자 제외
                    # period_id가 있는 경우와 없는 경우를 모두 고려
                    cursor.execute(
                        """
                        INSERT INTO manual_check_results
                        (user_id, check_item_code, check_year, check_period, check_date, 
                        checker_name, overall_result, total_score, notes, period_id)
                        SELECT 
                            u.uid,
                            %s,
                            %s,
                            'auto_complete',
                            NOW(),
                            '자동완료',
                            'pass',
                            100.0,
                            '기간 완료로 인한 자동 통과 처리',
                            %s
                        FROM users u
                        WHERE u.uid NOT IN (
                            -- 해당 기간(period_id)에 이미 결과가 있는 사용자 제외
                            SELECT DISTINCT mcr1.user_id 
                            FROM manual_check_results mcr1 
                            WHERE mcr1.period_id = %s
                        )
                        AND u.uid NOT IN (
                            -- 같은 점검 유형, 연도, 기간에 이미 결과가 있는 사용자도 제외 (period_id가 없는 경우 대비)
                            SELECT DISTINCT mcr2.user_id 
                            FROM manual_check_results mcr2 
                            WHERE mcr2.check_item_code = %s 
                            AND mcr2.check_year = %s
                            AND (mcr2.period_id = %s OR (
                                mcr2.period_id IS NULL 
                                AND DATE(mcr2.check_date) BETWEEN (
                                    SELECT start_date FROM manual_check_periods WHERE period_id = %s
                                ) AND (
                                    SELECT end_date FROM manual_check_periods WHERE period_id = %s
                                )
                            ))
                        )
                        AND u.uid NOT IN (
                            -- 예외 설정된 사용자 제외
                            SELECT uee.user_id 
                            FROM user_extended_exceptions uee 
                            WHERE uee.item_id = CONCAT('manual_', %s, '_', %s, '_', %s)
                            AND uee.is_active = 1
                        )
                        """,
                        (
                            period_info["check_type"],  # check_item_code
                            period_info["period_year"],  # check_year
                            period_id,  # period_id (INSERT용)
                            period_id,  # period_id 조건 1
                            period_info["check_type"],  # check_item_code 조건
                            period_info["period_year"],  # check_year 조건
                            period_id,  # period_id 조건 2
                            period_id,  # start_date 조회용
                            period_id,  # end_date 조회용
                            period_info["check_type"],  # 예외 설정 확인용
                            period_info["period_year"],  # 예외 설정 확인용
                            period_info["period_name"],  # 예외 설정 확인용
                        ),
                    )

                    # 영향받은 행 수 확인
                    affected_rows = cursor.rowcount
                    print(f"[DEBUG] 자동 통과 처리 완료 - {affected_rows}명 처리")

                    return {
                        "success": True,
                        "message": f"{period_info['period_name']} 기간이 완료 처리되었습니다. ({affected_rows}명 자동 통과)",
                    }
                else:
                    return {
                        "success": True,
                        "message": f"{period_info['period_name']} 기간이 완료 처리되었습니다.",
                    }

        except Exception as e:
            print(f"[ERROR] 기간 완료 처리 오류: {str(e)}")
            import traceback

            traceback.print_exc()
            return {"success": False, "message": f"완료 처리 실패: {str(e)}"}

    def reopen_period(self, period_id: int) -> dict:
        """점검 기간 재개"""
        try:
            with DatabaseManager.get_db_cursor() as cursor:
                # 기간 정보 조회
                cursor.execute(
                    "SELECT period_name, is_completed FROM manual_check_periods WHERE period_id = %s AND is_active = 1",
                    (period_id,),
                )
                period_info = cursor.fetchone()

                if not period_info:
                    return {
                        "success": False,
                        "message": "해당 기간을 찾을 수 없습니다.",
                    }

                if not period_info["is_completed"]:
                    return {"success": False, "message": "완료되지 않은 기간입니다."}

                # 자동 통과 처리된 결과 삭제
                cursor.execute(
                    """
                    DELETE FROM manual_check_results
                    WHERE period_id = %s AND notes = '기간 완료로 인한 자동 통과 처리'
                    """,
                    (period_id,),
                )

                # 기간 재개
                cursor.execute(
                    """
                    UPDATE manual_check_periods
                    SET is_completed = 0, completed_at = NULL, completed_by = NULL, updated_at = NOW()
                    WHERE period_id = %s
                    """,
                    (period_id,),
                )

                return {
                    "success": True,
                    "message": f"{period_info['period_name']} 기간이 재개되었습니다.",
                }

        except Exception as e:
            return {"success": False, "message": f"재개 처리 실패: {str(e)}"}

    def get_check_types(self) -> dict:
        """지원되는 점검 유형 목록 반환"""
        return {
            "seal_check": "PC 봉인씰 확인",
            "malware_scan": "악성코드 전체 검사",
            "file_encryption": "개인정보 파일 암호화",
        }

    def _map_check_type_to_db(self, check_type: str) -> str:
        """프론트엔드 점검 유형을 데이터베이스 ENUM 값으로 매핑"""
        # 임시 매핑 (기존 ENUM 값 활용)
        mapping = {
            "seal_check": "screen_saver",  # 임시로 기존 값 사용
            "malware_scan": "antivirus",  # 임시로 기존 값 사용
            "file_encryption": "patch_update",  # 임시로 기존 값 사용
        }
        return mapping.get(check_type, check_type)
