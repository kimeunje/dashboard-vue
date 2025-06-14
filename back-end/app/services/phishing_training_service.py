# app/services/training_service.py - 점수 관련 로직 제거 버전
from datetime import datetime
from app.utils.database import execute_query, DatabaseManager


class TrainingService:
    """악성메일 모의훈련 관련 서비스 - 점수 관리 제거"""

    def get_training_status(self, username: str, year: int = None) -> dict:
        """사용자의 악성메일 모의훈련 현황 조회 - 연도별 제외 설정 적용"""
        if year is None:
            year = datetime.now().year

        # 사용자 ID 가져오기
        user = execute_query(
            "SELECT uid FROM users WHERE user_id = %s", (username,), fetch_one=True
        )

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
                notes
            FROM phishing_training
            WHERE user_id = %s AND training_year = %s
            ORDER BY training_period
            """,
            (user_id, year),
            fetch_all=True,
        )

        # 상반기/하반기별 상태 정리
        period_status = []
        periods = ["first_half", "second_half"]
        period_names = {"first_half": "상반기", "second_half": "하반기"}

        # ExceptionService 인스턴스 생성
        from app.services.admin_exception_service import ExceptionService

        exception_service = ExceptionService()

        for period in periods:
            period_record = next(
                (r for r in training_records if r["training_period"] == period), None
            )

            # 연도별 제외 설정 확인
            exclude_result = exception_service.is_training_excluded_for_user(
                user_id, year, period
            )
            is_excluded = exclude_result.get("is_excluded", False)
            exclude_reason = exclude_result.get("exclude_reason", "")

            if period_record:
                # 응답시간 계산 (분)
                response_time = None
                if period_record["email_sent_time"] and period_record["action_time"]:
                    time_diff = (
                        period_record["action_time"] - period_record["email_sent_time"]
                    )
                    response_time = int(time_diff.total_seconds() / 60)

                status = {
                    "period": period,
                    "period_name": period_names[period],
                    "email_sent_time": (
                        period_record["email_sent_time"].strftime("%Y-%m-%d %H:%M:%S")
                        if period_record["email_sent_time"]
                        else None
                    ),
                    "action_time": (
                        period_record["action_time"].strftime("%Y-%m-%d %H:%M:%S")
                        if period_record["action_time"]
                        else None
                    ),
                    "log_type": period_record["log_type"],
                    "mail_type": period_record["mail_type"],
                    "user_email": period_record["user_email"],
                    "ip_address": period_record["ip_address"],
                    "result": period_record["training_result"],
                    "passed": period_record["training_result"] == "pass",
                    "clicked_or_opened": period_record["log_type"] is not None,
                    "response_time_minutes": response_time
                    or period_record["response_time_minutes"],
                    "notes": period_record["notes"],
                    "exclude_from_scoring": is_excluded,  # 연도별 제외 설정 적용
                    "exclude_reason": exclude_reason,
                }
            else:
                status = {
                    "period": period,
                    "period_name": period_names[period],
                    "email_sent_time": None,
                    "action_time": None,
                    "log_type": None,
                    "mail_type": None,
                    "user_email": None,
                    "ip_address": None,
                    "result": "pending",
                    "passed": False,
                    "clicked_or_opened": None,
                    "response_time_minutes": None,
                    "notes": "훈련 미실시",
                    "exclude_from_scoring": is_excluded,  # 연도별 제외 설정 적용
                    "exclude_reason": exclude_reason,
                }

            period_status.append(status)

        # 통계 계산 (제외 설정이 적용된 것만 포함)
        conducted_count = 0
        passed_count = 0
        failed_count = 0
        excluded_count = 0

        for status in period_status:
            if status["exclude_from_scoring"]:
                excluded_count += 1
            elif status["result"] != "pending":
                conducted_count += 1
                if status["passed"]:
                    passed_count += 1
                elif status["result"] == "fail":
                    failed_count += 1

        # 총 실시 대상 (제외되지 않은 것들)
        total_target = len(period_status) - excluded_count
        not_started = total_target - conducted_count

        result = {
            "year": year,
            "period_status": period_status,
            "summary": {
                "total_periods": 2,
                "conducted": conducted_count,
                "passed": passed_count,
                "failed": failed_count,
                "not_started": not_started,
                "excluded_count": excluded_count,
                "penalty_score": failed_count * 0.5,  # 실패당 0.5점 감점
                "pass_rate": round(
                    (
                        (passed_count / conducted_count * 100)
                        if conducted_count > 0
                        else 0
                    ),
                    1,
                ),
            },
        }

        return result

    def bulk_update_training(self, records: list) -> dict:
        """모의훈련 결과 일괄 등록/수정 - 점수 관련 로직 제거"""
        if not records:
            raise ValueError("등록할 훈련 기록이 없습니다.")

        success_count = 0
        error_records = []

        for record in records:
            try:
                # 필수 필드 검증
                required_fields = ["user_email", "training_year", "training_period"]
                if not all(
                    field in record and record[field] for field in required_fields
                ):
                    error_records.append(
                        {
                            "record": record,
                            "error": "필수 필드 누락 (user_email, training_year, training_period)",
                        }
                    )
                    continue

                # 이메일로 사용자 찾기
                user = execute_query(
                    "SELECT uid FROM users WHERE mail = %s",
                    (record["user_email"],),
                    fetch_one=True,
                )

                if not user:
                    error_records.append(
                        {
                            "record": record,
                            "error": f"이메일 '{record['user_email']}'에 해당하는 사용자를 찾을 수 없습니다.",
                        }
                    )
                    continue

                user_uid = user["uid"]

                # 기간 변환
                period_map = {
                    "상반기": "first_half",
                    "하반기": "second_half",
                    "first_half": "first_half",
                    "second_half": "second_half",
                }

                training_period = period_map.get(record["training_period"])
                if not training_period:
                    error_records.append(
                        {
                            "record": record,
                            "error": f"훈련 기간 '{record['training_period']}'이 유효하지 않습니다. (상반기/하반기 또는 first_half/second_half)",
                        }
                    )
                    continue

                # 훈련 결과 결정
                training_result = "pending"
                if record.get("log_type"):
                    training_result = "fail"  # 로그유형이 있으면 실패 (클릭/열람)
                elif record.get("email_sent_time") and not record.get("action_time"):
                    training_result = "pass"  # 메일 발송했지만 액션이 없으면 통과
                elif record.get("training_result"):
                    training_result = record["training_result"]

                # 응답시간 계산
                response_time_minutes = None
                if record.get("email_sent_time") and record.get("action_time"):
                    try:
                        sent_time = datetime.fromisoformat(
                            str(record["email_sent_time"]).replace("T", " ")
                        )
                        action_time = datetime.fromisoformat(
                            str(record["action_time"]).replace("T", " ")
                        )
                        response_time_minutes = int(
                            (action_time - sent_time).total_seconds() / 60
                        )
                    except:
                        response_time_minutes = record.get("response_time_minutes")

                # 훈련 기록 등록/수정 - 점수 관련 필드 제거
                execute_query(
                    """
                    INSERT INTO phishing_training 
                    (user_id, training_year, training_period, email_sent_time, action_time,
                     log_type, mail_type, user_email, ip_address, training_result,
                     response_time_minutes, notes)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                    email_sent_time = VALUES(email_sent_time),
                    action_time = VALUES(action_time),
                    log_type = VALUES(log_type),
                    mail_type = VALUES(mail_type),
                    user_email = VALUES(user_email),
                    ip_address = VALUES(ip_address),
                    training_result = VALUES(training_result),
                    response_time_minutes = VALUES(response_time_minutes),
                    notes = VALUES(notes),
                    updated_at = NOW()
                    """,
                    (
                        user_uid,
                        record["training_year"],
                        training_period,
                        record.get("email_sent_time"),
                        record.get("action_time"),
                        record.get("log_type"),
                        record.get("mail_type"),
                        record["user_email"],
                        record.get("ip_address"),
                        training_result,
                        response_time_minutes,
                        record.get("notes", ""),
                    ),
                )

                success_count += 1

            except Exception as e:
                error_records.append({"record": record, "error": str(e)})

        return {
            "success_count": success_count,
            "total_count": len(records),
            "error_records": error_records,
        }

    def update_training_record(self, record: dict) -> bool:
        """단일 훈련 기록 수정 - 프론트엔드에서 계산된 값 사용"""
        try:
            # 사용자 확인
            user = execute_query(
                "SELECT uid FROM users WHERE user_id = %s",
                (record["user_id"],),
                fetch_one=True,
            )
            if not user:
                raise ValueError("사용자를 찾을 수 없습니다.")

            user_uid = user["uid"]

            # 프론트엔드에서 계산해서 보낸 response_time_minutes 값을 그대로 사용
            response_time_minutes = record.get("response_time_minutes")

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
                notes = %s,
                updated_at = NOW()
                WHERE user_id = %s AND training_year = %s AND training_period = %s
                """,
                (
                    record.get("email_sent_time"),
                    record.get("action_time"),
                    record.get("log_type"),
                    record.get("mail_type"),
                    record.get("user_email"),
                    record.get("ip_address"),
                    record.get("training_result", "pending"),
                    response_time_minutes,  # 프론트엔드에서 계산된 값 사용
                    record.get("notes", ""),
                    user_uid,
                    record["training_year"],
                    record["training_period"],
                ),
            )

            return True

        except Exception as e:
            raise ValueError(f"훈련 기록 수정 실패: {str(e)}")

    def delete_training_record(
        self, user_id: str, training_year: int, training_period: str
    ) -> bool:
        """훈련 기록 삭제"""
        try:
            # 사용자 확인
            user = execute_query(
                "SELECT uid FROM users WHERE user_id = %s", (user_id,), fetch_one=True
            )
            if not user:
                raise ValueError("사용자를 찾을 수 없습니다.")

            user_uid = user["uid"]

            # 기록 삭제
            result = execute_query(
                """
                DELETE FROM phishing_training
                WHERE user_id = %s AND training_year = %s AND training_period = %s
                """,
                (user_uid, training_year, training_period),
            )

            return result > 0

        except Exception as e:
            raise ValueError(f"훈련 기록 삭제 실패: {str(e)}")

    def get_training_excel_template(self) -> str:
        """엑셀 업로드용 템플릿 생성 - 점수 관련 필드 제거"""
        template_data = [
            "user_email,training_year,training_period,email_sent_time,action_time,log_type,mail_type,ip_address,notes",
            "test@example.com,2025,상반기,2025-05-15 10:44:25,2025-05-15 10:44:59,스크립트 첨부파일 열람,퇴직연금 운용상품 안내 (HTML),112.111.231.120,모의훈련 실패 - 첨부파일 열람",
            "user1@example.com,2025,상반기,2025-05-15 10:44:25,,,보안 업데이트 안내,,모의훈련 통과 - 액션 없음",
            "user2@example.com,2025,하반기,2025-11-20 14:30:00,2025-11-20 14:35:20,링크 클릭,급여명세서 확인 요청,192.168.1.100,모의훈련 실패",
        ]
        return "\n".join(template_data)

    def get_all_training_records(
        self, year: int = None, period: str = None, result: str = None
    ) -> list:
        """모든 훈련 기록 조회 (관리자용) - 제외 상태 포함"""
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
            records = cursor.fetchall()

        # ExceptionService 인스턴스 생성하여 제외 상태 확인
        from app.services.admin_exception_service import ExceptionService

        exception_service = ExceptionService()

        # 각 기록에 제외 상태 추가
        enriched_records = []
        for record in records:
            # 사용자 uid 가져오기
            user_uid_query = execute_query(
                "SELECT uid FROM users WHERE user_id = %s",
                (record["user_id"],),
                fetch_one=True,
            )

            if user_uid_query:
                user_uid = user_uid_query["uid"]

                # 제외 설정 확인
                exclude_result = exception_service.is_training_excluded_for_user(
                    user_uid, record["training_year"], record["training_period"]
                )

                # 기존 record에 제외 상태 정보 추가
                record_dict = dict(record)
                record_dict["exclude_from_scoring"] = exclude_result.get(
                    "is_excluded", False
                )
                record_dict["exclude_reason"] = exclude_result.get("exclude_reason", "")
                record_dict["exclude_type"] = exclude_result.get("exclude_type", "")

                enriched_records.append(record_dict)
            else:
                # 사용자 정보가 없는 경우 기본값 설정
                record_dict = dict(record)
                record_dict["exclude_from_scoring"] = False
                record_dict["exclude_reason"] = ""
                record_dict["exclude_type"] = ""
                enriched_records.append(record_dict)

        return enriched_records

    def get_training_statistics(self, year: int = None) -> dict:
        """모의훈련 통계 조회"""
        if year is None:
            year = datetime.now().year

        with DatabaseManager.get_db_cursor(commit=False) as cursor:
            # 기간별 통계
            cursor.execute(
                """
                SELECT 
                    training_period,
                    COUNT(*) as total_count,
                    SUM(CASE WHEN training_result = 'pass' THEN 1 ELSE 0 END) as passed_count,
                    SUM(CASE WHEN training_result = 'fail' THEN 1 ELSE 0 END) as failed_count,
                    SUM(CASE WHEN training_result = 'pending' THEN 1 ELSE 0 END) as pending_count
                FROM phishing_training
                WHERE training_year = %s
                GROUP BY training_period
                ORDER BY training_period
                """,
                (year,),
            )
            period_stats = cursor.fetchall()

            # 부서별 통계
            cursor.execute(
                """
                SELECT 
                    u.department,
                    COUNT(*) as total_count,
                    SUM(CASE WHEN pt.training_result = 'pass' THEN 1 ELSE 0 END) as passed_count,
                    SUM(CASE WHEN pt.training_result = 'fail' THEN 1 ELSE 0 END) as failed_count
                FROM phishing_training pt
                JOIN users u ON pt.user_id = u.uid
                WHERE pt.training_year = %s
                GROUP BY u.department
                ORDER BY u.department
                """,
                (year,),
            )
            department_stats = cursor.fetchall()

            # 로그 유형별 통계
            cursor.execute(
                """
                SELECT 
                    log_type,
                    COUNT(*) as count
                FROM phishing_training
                WHERE training_year = %s AND log_type IS NOT NULL
                GROUP BY log_type
                ORDER BY count DESC
                """,
                (year,),
            )
            log_type_stats = cursor.fetchall()

        return {
            "year": year,
            "period_stats": period_stats,
            "department_stats": department_stats,
            "log_type_stats": log_type_stats,
        }

    def export_training_to_csv(self, year: int = None) -> str:
        """모의훈련 데이터를 CSV 형태로 내보내기 - UTF-8 BOM 포함"""
        records = self.get_all_training_records(year)

        csv_lines = []

        # UTF-8 BOM 추가 (Excel에서 한글 인식용)
        bom = "\ufeff"

        headers = [
            "사용자ID",
            "사용자명",
            "부서",
            "연도",
            "기간",
            "발송시각",
            "수행시각",
            "로그유형",
            "메일유형",
            "이메일",
            "IP주소",
            "결과",
            "비고",
        ]

        # BOM과 함께 헤더 추가
        csv_lines.append(bom + ",".join(headers))

        for record in records:
            # 한글 데이터 안전하게 처리
            row = [
                str(record.get("user_id", "")).replace('"', '""'),
                str(record.get("username", "")).replace('"', '""'),
                str(record.get("department", "")).replace('"', '""'),
                str(record.get("training_year", "")).replace('"', '""'),
                "상반기" if record.get("training_period") == "first_half" else "하반기",
                str(record.get("email_sent_time", "")).replace('"', '""'),
                str(record.get("action_time", "")).replace('"', '""'),
                str(record.get("log_type", "")).replace('"', '""'),
                str(record.get("mail_type", "")).replace('"', '""'),
                str(record.get("user_email", "")).replace('"', '""'),
                str(record.get("ip_address", "")).replace('"', '""'),
                str(record.get("training_result", "")).replace('"', '""'),
                str(record.get("notes", "")).replace('"', '""'),
            ]
            # CSV RFC 4180 표준에 따라 필드를 따옴표로 감싸기
            csv_lines.append(",".join(f'"{item}"' for item in row))

        return "\n".join(csv_lines)
