# manual_check_service.py
# back-end/app/services/ 폴더에 생성

import pandas as pd
import io
from app.utils.database import DatabaseManager, execute_query
from datetime import datetime


class ManualCheckService:

    def get_excel_template(self):
        """엑셀 업로드용 템플릿 생성"""
        template_data = [
            "사용자ID,사용자명,부서,점검연도,점검기간,점검일시,점검자명,봉인씰상태,봉인번호,봉인씰비고,악성코드검사결과,발견위협수,치료완료여부,백신버전,악성코드비고,암호화상태,검사파일수,미암호화파일수,암호화완료여부,암호화비고,종합결과,전체비고",
            "admin,관리자,IT팀,2025,상반기,2025-06-10 14:30:00,김점검,정상,SEAL-2025-001,정상 상태 확인,정상,0,Y,V3 2025.06.10,검사 완료,완전암호화,15,0,Y,모든 파일 암호화 완료,통과,모든 항목 정상",
            "user1,홍길동,개발팀,2025,상반기,2025-06-10 15:00:00,김점검,손상,SEAL-2025-002,봉인씰 교체 필요,정상,0,Y,V3 2025.06.10,검사 완료,부분암호화,20,3,N,3개 파일 암호화 필요,부분통과,봉인씰 교체 및 암호화 조치 필요",
        ]
        return "\n".join(template_data)

    def process_bulk_upload(self, file, uploaded_by):
        """엑셀/CSV 파일 일괄 업로드 처리"""
        try:
            filename = file.filename.lower()

            # 파일 읽기
            if filename.endswith(".csv"):
                df = pd.read_csv(file, encoding="utf-8-sig")
            elif filename.endswith((".xlsx", ".xls")):
                df = pd.read_excel(file)
            else:
                raise ValueError("지원하지 않는 파일 형식입니다.")

            # 컬럼명 정규화
            df = self._normalize_columns(df)

            # 데이터 처리
            processed_data = self._process_upload_data(df)

            # 데이터베이스 저장
            results = self._save_check_results(processed_data, uploaded_by)

            return {
                "success": True,
                "total_records": len(processed_data),
                "successful_records": results["success_count"],
                "failed_records": results["error_count"],
                "errors": results["errors"],
            }

        except Exception as e:
            raise ValueError(f"파일 처리 중 오류가 발생했습니다: {str(e)}")

    def _normalize_columns(self, df):
        """컬럼명 정규화"""
        field_mapping = {
            "사용자ID": "user_id",
            "사용자명": "username",
            "부서": "department",
            "점검연도": "check_year",
            "점검기간": "check_period",
            "점검일시": "check_date",
            "점검자명": "checker_name",
            "봉인씰상태": "seal_status",
            "봉인번호": "seal_number",
            "봉인씰비고": "seal_notes",
            "악성코드검사결과": "malware_scan_result",
            "발견위협수": "threats_found",
            "치료완료여부": "threats_cleaned",
            "백신버전": "antivirus_version",
            "악성코드비고": "malware_notes",
            "암호화상태": "encryption_status",
            "검사파일수": "files_scanned",
            "미암호화파일수": "unencrypted_files",
            "암호화완료여부": "encryption_completed",
            "암호화비고": "encryption_notes",
            "종합결과": "overall_result",
            "전체비고": "notes",
        }

        df.columns = [field_mapping.get(col.strip(), col.strip()) for col in df.columns]
        return df

    def _process_upload_data(self, df):
        """업로드 데이터 처리 및 검증"""
        value_mapping = {
            "seal_status": {
                "정상": "normal",
                "손상": "damaged",
                "미부착": "missing",
                "교체필요": "replacement_needed",
            },
            "malware_scan_result": {
                "정상": "clean",
                "감염발견": "infected",
                "검사실패": "scan_failed",
                "미실시": "not_performed",
            },
            "encryption_status": {
                "완전암호화": "fully_encrypted",
                "미암호화": "not_encrypted",
                "부분암호화": "partially_encrypted",
                "해당없음": "not_applicable",
            },
            "overall_result": {"통과": "pass", "실패": "fail", "부분통과": "partial"},
            "check_period": {"상반기": "first_half", "하반기": "second_half"},
        }

        processed_data = []
        for _, row in df.iterrows():
            if pd.isna(row.get("user_id")) or pd.isna(row.get("check_date")):
                continue

            processed_row = {}
            for field, value in row.items():
                if field in value_mapping and not pd.isna(value):
                    processed_row[field] = value_mapping[field].get(str(value), value)
                else:
                    processed_row[field] = value if not pd.isna(value) else None

                # Y/N을 boolean으로 변환
                if field in ["threats_cleaned", "encryption_completed"] and not pd.isna(
                    value
                ):
                    processed_row[field] = str(value).upper() in ["Y", "1", "TRUE"]

            processed_data.append(processed_row)

        return processed_data

    def _save_check_results(self, processed_data, uploaded_by):
        """데이터베이스에 저장"""
        success_count = 0
        error_count = 0
        errors = []

        for data in processed_data:
            try:
                # 사용자 정보 조회
                user_info = execute_query(
                    "SELECT uid, username, department FROM users WHERE user_id = %s",
                    (data["user_id"],),
                    fetch_one=True,
                )

                if not user_info:
                    error_count += 1
                    errors.append(f"사용자 {data['user_id']}를 찾을 수 없습니다.")
                    continue

                # 점수 계산
                total_score = self._calculate_score(data)

                # 데이터베이스 삽입
                execute_query(
                    """
                    INSERT INTO manual_check_results (
                        user_id, check_year, check_period, check_date, checker_name,
                        seal_status, seal_number, seal_notes,
                        malware_scan_result, threats_found, threats_cleaned, antivirus_version, malware_notes,
                        encryption_status, files_scanned, unencrypted_files, encryption_completed, encryption_notes,
                        overall_result, total_score, notes
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                        seal_status = VALUES(seal_status),
                        malware_scan_result = VALUES(malware_scan_result),
                        encryption_status = VALUES(encryption_status),
                        overall_result = VALUES(overall_result),
                        total_score = VALUES(total_score),
                        updated_at = CURRENT_TIMESTAMP
                """,
                    (
                        user_info["uid"],
                        data.get("check_year", 2025),
                        data.get("check_period", "first_half"),
                        data.get("check_date"),
                        data.get("checker_name", ""),
                        data.get("seal_status"),
                        data.get("seal_number"),
                        data.get("seal_notes"),
                        data.get("malware_scan_result"),
                        data.get("threats_found", 0),
                        data.get("threats_cleaned", False),
                        data.get("antivirus_version"),
                        data.get("malware_notes"),
                        data.get("encryption_status"),
                        data.get("files_scanned", 0),
                        data.get("unencrypted_files", 0),
                        data.get("encryption_completed", False),
                        data.get("encryption_notes"),
                        data.get("overall_result"),
                        total_score,
                        data.get("notes"),
                    ),
                )

                success_count += 1

            except Exception as e:
                error_count += 1
                errors.append(f"데이터 저장 오류: {str(e)}")

        return {
            "success_count": success_count,
            "error_count": error_count,
            "errors": errors,
        }

    def _calculate_score(self, data):
        """점수 계산 로직"""
        base_score = 100.0
        penalty = 0.0

        # 각 항목별 감점 적용
        if data.get("seal_status") not in ["normal"]:
            penalty += 10.0
        if data.get("malware_scan_result") not in ["clean"]:
            penalty += 15.0
        if data.get("encryption_status") not in ["fully_encrypted"]:
            penalty += 15.0

        return max(0, base_score - penalty)

    def get_check_results(
        self,
        year=None,
        check_type=None,
        result_filter=None,
        search=None,
        page=1,
        size=20,
    ):
        """점검 결과 목록 조회 (수정된 버전)"""
        if year is None:
            year = datetime.now().year

        try:
            print(
                f"[DEBUG] 점검 결과 조회 시작: year={year}, check_type={check_type}, result_filter={result_filter}"
            )

            # 기본 쿼리 구성
            base_query = """
                SELECT 
                    mcr.check_id,
                    mcr.user_id,
                    mcr.check_item_code,
                    mcr.source_ip,
                    mcr.check_year,
                    mcr.check_period,
                    mcr.check_date,
                    mcr.checker_name,
                    mcr.overall_result,
                    mcr.total_score,
                    mcr.notes,
                    mcr.period_id,
                    mcr.created_at,
                    u.user_id as user_login_id,
                    u.username,
                    u.department,
                    u.mail as user_email
                FROM manual_check_results mcr
                JOIN users u ON mcr.user_id = u.uid
                WHERE mcr.check_year = %s
            """

            params = [year]

            # 조건 추가
            if check_type:
                base_query += " AND mcr.check_item_code = %s"
                params.append(check_type)

            if result_filter:
                base_query += " AND mcr.overall_result = %s"
                params.append(result_filter)

            if search:
                base_query += (
                    " AND (u.username LIKE %s OR u.user_id LIKE %s OR u.mail LIKE %s)"
                )
                search_pattern = f"%{search}%"
                params.extend([search_pattern, search_pattern, search_pattern])

            # 정렬 및 페이지네이션
            base_query += " ORDER BY mcr.check_date DESC"

            print(f"[DEBUG] 쿼리 파라미터: {params}")

            # 전체 개수 먼저 조회
            count_query = f"SELECT COUNT(*) as total FROM ({base_query}) as subquery"
            total_result = execute_query(count_query, params, fetch_one=True)
            total = total_result["total"] if total_result else 0

            print(f"[DEBUG] 전체 개수: {total}")

            # 페이지네이션 적용
            offset = (page - 1) * size
            base_query += f" LIMIT %s OFFSET %s"
            params.extend([size, offset])

            # 실제 데이터 조회
            results = execute_query(base_query, params, fetch_all=True)

            print(f"[DEBUG] 조회된 결과 개수: {len(results) if results else 0}")

            # 결과 가공
            processed_results = []
            for i, result in enumerate(results):
                try:
                    print(f"[DEBUG] 결과 {i} 처리 중: {result}")

                    processed_result = dict(result)

                    # 날짜 포맷팅
                    if (
                        processed_result.get("check_date")
                        and processed_result["check_date"] is not None
                    ):
                        if hasattr(processed_result["check_date"], "strftime"):
                            processed_result["check_date"] = processed_result[
                                "check_date"
                            ].strftime("%Y-%m-%d %H:%M:%S")
                        else:
                            processed_result["check_date"] = str(
                                processed_result["check_date"]
                            )

                    if (
                        processed_result.get("created_at")
                        and processed_result["created_at"] is not None
                    ):
                        if hasattr(processed_result["created_at"], "strftime"):
                            processed_result["created_at"] = processed_result[
                                "created_at"
                            ].strftime("%Y-%m-%d %H:%M:%S")
                        else:
                            processed_result["created_at"] = str(
                                processed_result["created_at"]
                            )

                    # 프론트엔드 호환성을 위한 필드 추가
                    processed_result["result_id"] = processed_result["check_id"]
                    processed_result["check_result"] = processed_result[
                        "overall_result"
                    ]
                    processed_result["check_type"] = processed_result["check_item_code"]

                    # 기간명 생성
                    period_name = f"{processed_result['check_year']}년"
                    if processed_result.get("check_period"):
                        if processed_result["check_period"] == "first_half":
                            period_name += " 상반기"
                        elif processed_result["check_period"] == "second_half":
                            period_name += " 하반기"
                        else:
                            period_name += f" {processed_result['check_period']}"

                    processed_result["period_name"] = period_name

                    # None 값들을 안전하게 처리
                    for key, value in processed_result.items():
                        if value is None:
                            processed_result[key] = ""

                    processed_results.append(processed_result)
                    print(f"[DEBUG] 결과 {i} 처리 완료")

                except Exception as e:
                    print(f"[DEBUG] 결과 {i} 처리 중 오류: {str(e)}")
                    print(f"[DEBUG] 문제가 된 결과: {result}")
                    continue

            # 페이지네이션 정보 계산
            total_pages = (total + size - 1) // size if total > 0 else 1

            result_data = {
                "results": processed_results,
                "total": total,
                "page": page,
                "size": size,
                "total_pages": total_pages,
            }

            print(f"[DEBUG] 최종 결과: {len(processed_results)}건 반환")
            return result_data

        except Exception as e:
            print(f"[ERROR] 점검 결과 조회 오류: {str(e)}")
            import traceback

            traceback.print_exc()
            return {
                "results": [],
                "total": 0,
                "page": page,
                "size": size,
                "total_pages": 1,
            }

    def update_check_result(self, check_id, update_data, updated_by):
        """점검 결과 수정"""
        try:
            # 점수 재계산
            total_score = self._calculate_score(update_data)

            execute_query(
                """
                UPDATE manual_check_results SET
                    seal_status = %s, seal_number = %s, seal_notes = %s,
                    malware_scan_result = %s, threats_found = %s, threats_cleaned = %s,
                    antivirus_version = %s, malware_notes = %s,
                    encryption_status = %s, files_scanned = %s, unencrypted_files = %s,
                    encryption_completed = %s, encryption_notes = %s,
                    overall_result = %s, total_score = %s, notes = %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE check_id = %s
            """,
                (
                    update_data.get("seal_status"),
                    update_data.get("seal_number"),
                    update_data.get("seal_notes"),
                    update_data.get("malware_scan_result"),
                    update_data.get("threats_found", 0),
                    update_data.get("threats_cleaned", False),
                    update_data.get("antivirus_version"),
                    update_data.get("malware_notes"),
                    update_data.get("encryption_status"),
                    update_data.get("files_scanned", 0),
                    update_data.get("unencrypted_files", 0),
                    update_data.get("encryption_completed", False),
                    update_data.get("encryption_notes"),
                    update_data.get("overall_result"),
                    total_score,
                    update_data.get("notes"),
                    check_id,
                ),
            )

            return {"success": True, "message": "점검 결과가 수정되었습니다."}

        except Exception as e:
            raise ValueError(f"점검 결과 수정 실패: {str(e)}")

    def delete_check_result(self, check_id):
        """점검 결과 삭제"""
        try:
            result = execute_query(
                "DELETE FROM manual_check_results WHERE check_id = %s", (check_id,)
            )

            if result > 0:
                return {"success": True, "message": "점검 결과가 삭제되었습니다."}
            else:
                return {"success": False, "message": "삭제할 결과를 찾을 수 없습니다."}

        except Exception as e:
            raise ValueError(f"점검 결과 삭제 실패: {str(e)}")

    def get_check_statistics(self, year, period=None):
        """점검 통계 조회"""
        base_query = """
            SELECT 
                COUNT(*) as total_checks,
                SUM(CASE WHEN overall_result = 'pass' THEN 1 ELSE 0 END) as pass_count,
                SUM(CASE WHEN overall_result = 'fail' THEN 1 ELSE 0 END) as fail_count,
                SUM(CASE WHEN overall_result = 'partial' THEN 1 ELSE 0 END) as partial_count,
                AVG(total_score) as avg_score
            FROM manual_check_results
            WHERE check_year = %s
        """

        params = [year]
        if period:
            base_query += " AND check_period = %s"
            params.append(period)

        basic_stats = execute_query(base_query, params, fetch_one=True)

        # 부서별 통계
        dept_query = """
            SELECT 
                u.department,
                COUNT(*) as dept_total,
                SUM(CASE WHEN mcr.overall_result = 'pass' THEN 1 ELSE 0 END) as dept_pass,
                AVG(mcr.total_score) as dept_avg_score
            FROM manual_check_results mcr
            JOIN users u ON mcr.user_id = u.uid
            WHERE mcr.check_year = %s
        """
        if period:
            dept_query += " AND mcr.check_period = %s"
        dept_query += " GROUP BY u.department ORDER BY dept_avg_score DESC"

        dept_stats = execute_query(dept_query, params)

        return {
            "basic_stats": basic_stats,
            "department_stats": dept_stats,
            "year": year,
            "period": period,
        }

    def export_results_to_csv(self, year, period=None):
        """점검 결과를 CSV로 내보내기"""
        query = """
            SELECT 
                u.user_id, u.username, u.department,
                mcr.check_year, mcr.check_period, mcr.check_date, mcr.checker_name,
                mcr.seal_status, mcr.seal_number, mcr.seal_notes,
                mcr.malware_scan_result, mcr.threats_found, mcr.threats_cleaned,
                mcr.antivirus_version, mcr.malware_notes,
                mcr.encryption_status, mcr.files_scanned, mcr.unencrypted_files,
                mcr.encryption_completed, mcr.encryption_notes,
                mcr.overall_result, mcr.total_score, mcr.notes
            FROM manual_check_results mcr
            JOIN users u ON mcr.user_id = u.uid
            WHERE mcr.check_year = %s
        """

        params = [year]
        if period:
            query += " AND mcr.check_period = %s"
            params.append(period)

        query += " ORDER BY mcr.check_date DESC"

        results = execute_query(query, params)

        # CSV 헤더
        csv_lines = [
            "\ufeff사용자ID,사용자명,부서,점검연도,점검기간,점검일시,점검자명,봉인씰상태,봉인번호,봉인씰비고,악성코드검사결과,발견위협수,치료완료여부,백신버전,악성코드비고,암호화상태,검사파일수,미암호화파일수,암호화완료여부,암호화비고,종합결과,총점,전체비고"
        ]

        # 데이터 행 추가
        for record in results:
            row = [
                str(record.get("user_id", "")),
                str(record.get("username", "")),
                str(record.get("department", "")),
                str(record.get("check_year", "")),
                "상반기" if record.get("check_period") == "first_half" else "하반기",
                str(record.get("check_date", "")),
                str(record.get("checker_name", "")),
                self._get_status_korean(record.get("seal_status"), "seal"),
                str(record.get("seal_number", "")),
                str(record.get("seal_notes", "")),
                self._get_status_korean(record.get("malware_scan_result"), "malware"),
                str(record.get("threats_found", 0)),
                "Y" if record.get("threats_cleaned") else "N",
                str(record.get("antivirus_version", "")),
                str(record.get("malware_notes", "")),
                self._get_status_korean(record.get("encryption_status"), "encryption"),
                str(record.get("files_scanned", 0)),
                str(record.get("unencrypted_files", 0)),
                "Y" if record.get("encryption_completed") else "N",
                str(record.get("encryption_notes", "")),
                self._get_status_korean(record.get("overall_result"), "result"),
                str(record.get("total_score", 0)),
                str(record.get("notes", "")),
            ]

            # CSV 형식으로 변환 (따옴표 처리)
            csv_lines.append(",".join(f'"{item.replace("", "")}"' for item in row))

        return "\n".join(csv_lines)

    def _get_status_korean(self, status, status_type):
        """영문 상태를 한글로 변환"""
        mappings = {
            "seal": {
                "normal": "정상",
                "damaged": "손상",
                "missing": "미부착",
                "replacement_needed": "교체필요",
            },
            "malware": {
                "clean": "정상",
                "infected": "감염발견",
                "scan_failed": "검사실패",
                "not_performed": "미실시",
            },
            "encryption": {
                "fully_encrypted": "완전암호화",
                "not_encrypted": "미암호화",
                "partially_encrypted": "부분암호화",
                "not_applicable": "해당없음",
            },
            "result": {"pass": "통과", "fail": "실패", "partial": "부분통과"},
        }
        return mappings.get(status_type, {}).get(status, status or "")
