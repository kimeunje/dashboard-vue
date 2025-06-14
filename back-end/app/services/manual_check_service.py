# manual_check_service.py
# back-end/app/services/ 폴더에 생성

import pandas as pd
import io
import re
from app.utils.database import DatabaseManager, execute_query
from datetime import datetime


class ManualCheckService:

    def __init__(self):
        self.check_type_patterns = {
            'file_encryption': {
                'required_columns': ['일시', '로컬 IP', '주민등록번호'],
                'keywords': ['개인정보', '암호화', '주민등록번호']
            },
            'seal_check': {
                'required_columns': ['일시', '이름', '부서', '훼손여부'],
                'keywords': ['봉인씰', '확인', '훼손']
            },
            'malware_scan': {
                'required_columns': ['IP', '악성코드명', '악성코드 분류', '경로', '탐지 항목'],
                'keywords': ['악성코드', '검사', '탐지']
            }
        }

    def detect_file_type(self, df, filename):
        """파일 내용을 기반으로 점검 유형 자동 감지"""
        columns = [col.strip() for col in df.columns]
        filename_lower = filename.lower()

        # 파일명 기반 1차 판별
        if '개인정보' in filename or '암호화' in filename:
            return 'file_encryption'
        elif '봉인씰' in filename:
            return 'seal_check'
        elif '악성코드' in filename:
            return 'malware_scan'

        # 컬럼 기반 2차 판별
        for check_type, config in self.check_type_patterns.items():
            required_cols = config['required_columns']
            matched_cols = sum(1 for col in required_cols
                               if any(req in col for req in columns))

            if matched_cols >= len(required_cols) * 0.8:  # 80% 이상 일치
                return check_type

        return None

    def validate_file_structure(self, df, check_type):
        """파일 구조 검증"""
        if check_type not in self.check_type_patterns:
            return False, f"알 수 없는 점검 유형: {check_type}"

        required_cols = self.check_type_patterns[check_type]['required_columns']
        columns = [col.strip() for col in df.columns]

        missing_cols = []
        for req_col in required_cols:
            if not any(req_col in col for col in columns):
                missing_cols.append(req_col)

        if missing_cols:
            return False, f"필수 컬럼이 없습니다: {', '.join(missing_cols)}"

        return True, "구조 검증 완료"

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
            filename = file.filename

            # 파일 읽기
            if filename.lower().endswith('.csv'):
                df = pd.read_csv(file, encoding='utf-8-sig')
            elif filename.lower().endswith(('.xlsx', '.xls')):
                df = pd.read_excel(file)
            else:
                raise ValueError("지원하지 않는 파일 형식입니다. (Excel, CSV만 지원)")

            # 빈 데이터프레임 체크
            if df.empty:
                raise ValueError("파일에 데이터가 없습니다.")

            # 점검 유형 자동 감지
            check_type = self.detect_file_type(df, filename)
            if not check_type:
                raise ValueError("점검 유형을 자동으로 감지할 수 없습니다. 파일명이나 컬럼을 확인해주세요.")

            # 파일 구조 검증
            is_valid, message = self.validate_file_structure(df, check_type)
            if not is_valid:
                raise ValueError(message)

            # 데이터 처리
            processed_data = self._process_check_data(df, check_type, uploaded_by)

            # 데이터베이스 저장 (기존 테이블 구조 사용)
            save_result = self._save_to_existing_table(processed_data, check_type,
                                                       uploaded_by)

            return {
                "success": True,
                "message": f"{self.get_check_type_name(check_type)} 업로드 완료",
                "file_type": self.get_check_type_name(check_type),
                "total_records": len(processed_data),
                "success_count": save_result["success_count"],
                "error_count": save_result["error_count"],
                "errors": save_result["errors"]
            }

        except Exception as e:
            print(f"파일 업로드 처리 오류: {str(e)}")
            raise ValueError(f"파일 처리 중 오류가 발생했습니다: {str(e)}")

    def _process_check_data(self, df, check_type, uploaded_by):
        """점검 유형별 데이터 처리 (기존 테이블 구조에 맞게)"""
        processed_data = []

        if check_type == 'file_encryption':
            processed_data = self._process_file_encryption_data(df, uploaded_by)
        elif check_type == 'seal_check':
            processed_data = self._process_seal_check_data(df, uploaded_by)
        elif check_type == 'malware_scan':
            processed_data = self._process_malware_scan_data(df, uploaded_by)

        return processed_data

    def _process_file_encryption_data(self, df, uploaded_by):
        """개인정보 파일 암호화 데이터 처리"""
        processed_data = []

        # 컬럼 매핑
        col_mapping = self._find_column_mapping(
            df.columns, {
                'datetime': ['일시', '점검일시', '날짜'],
                'local_ip': ['로컬 IP', 'IP', '로컬IP'],
                'ssn_count': ['주민등록번호', '주민번호', '00회차에서 주민등록번호']
            })

        for idx, row in df.iterrows():
            try:
                # 로컬 IP로 사용자 찾기
                local_ip = str(row[
                    col_mapping['local_ip']]) if col_mapping['local_ip'] and pd.notna(
                        row[col_mapping['local_ip']]) else ''

                # 주민등록번호 건수 확인
                ssn_count = 0
                if col_mapping['ssn_count']:
                    ssn_value = row[col_mapping['ssn_count']]
                    if pd.notna(ssn_value):
                        if isinstance(ssn_value, (int, float)):
                            ssn_count = int(ssn_value)
                        else:
                            numbers = re.findall(r'\d+', str(ssn_value))
                            ssn_count = int(numbers[0]) if numbers else 0

                # 결과 판정: 주민등록번호가 0건 이상이면 불합격
                overall_result = 'fail' if ssn_count > 0 else 'pass'
                encryption_status = 'not_encrypted' if ssn_count > 0 else 'fully_encrypted'

                processed_row = {
                    'check_item_code': 'file_encryption',
                    'source_ip': local_ip,
                    'check_year': datetime.now().year,
                    'check_period': 'first_half',  # 기본값, 나중에 기간 설정으로 수정 가능
                    'check_date': self._parse_datetime(row[col_mapping['datetime']])
                    if col_mapping['datetime'] else datetime.now(),
                    'checker_name': uploaded_by,
                    'encryption_status': encryption_status,
                    'unencrypted_files': ssn_count,
                    'encryption_completed': 1 if ssn_count == 0 else 0,
                    'encryption_notes': f"주민등록번호 {ssn_count}건 발견"
                    if ssn_count > 0 else "정상",
                    'ssn_included': 1 if ssn_count > 0 else 0,
                    'overall_result': overall_result,
                    'notes': f"개인정보 파일 암호화 점검: {ssn_count}건 미암호화"
                    if ssn_count > 0 else "모든 개인정보 파일 암호화 완료",
                    'row_index': idx + 2
                }

                processed_data.append(processed_row)

            except Exception as e:
                print(f"개인정보 파일 암호화 데이터 처리 오류 (행 {idx + 2}): {str(e)}")
                continue

        return processed_data

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
            "overall_result": {
                "통과": "pass",
                "실패": "fail",
                "부분통과": "partial"
            },
            "check_period": {
                "상반기": "first_half",
                "하반기": "second_half"
            },
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
                if field in ["threats_cleaned", "encryption_completed"
                             ] and not pd.isna(value):
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
                    (data["user_id"], ),
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
                    " AND (u.username LIKE %s OR u.user_id LIKE %s OR u.mail LIKE %s)")
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
                    if (processed_result.get("check_date")
                            and processed_result["check_date"] is not None):
                        if hasattr(processed_result["check_date"], "strftime"):
                            processed_result["check_date"] = processed_result[
                                "check_date"].strftime("%Y-%m-%d %H:%M:%S")
                        else:
                            processed_result["check_date"] = str(
                                processed_result["check_date"])

                    if (processed_result.get("created_at")
                            and processed_result["created_at"] is not None):
                        if hasattr(processed_result["created_at"], "strftime"):
                            processed_result["created_at"] = processed_result[
                                "created_at"].strftime("%Y-%m-%d %H:%M:%S")
                        else:
                            processed_result["created_at"] = str(
                                processed_result["created_at"])

                    # 프론트엔드 호환성을 위한 필드 추가
                    processed_result["result_id"] = processed_result["check_id"]
                    processed_result["check_result"] = processed_result[
                        "overall_result"]
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
                "DELETE FROM manual_check_results WHERE check_id = %s", (check_id, ))

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
            "result": {
                "pass": "통과",
                "fail": "실패",
                "partial": "부분통과"
            },
        }
        return mappings.get(status_type, {}).get(status, status or "")

    def get_check_type_mapping(self):
        """점검 유형 코드와 이름 매핑 반환"""
        return {
            "seal_check": "PC 봉인씰 확인",
            "malware_scan": "악성코드 전체 검사",
            "file_encryption": "개인정보 파일 암호화",
            # 기존 호환성을 위한 매핑도 포함
            "screen_saver": "화면보호기",
            "antivirus": "백신",
            "patch_update": "패치",
        }

    def get_check_types(self):
        """지원되는 점검 유형 목록 반환 (period_service와 일관성 유지)"""
        return {
            "seal_check": "PC 봉인씰 확인",
            "malware_scan": "악성코드 전체 검사",
            "file_encryption": "개인정보 파일 암호화",
        }

    def _process_check_data(self, df, check_type, uploaded_by):
        """점검 유형별 데이터 처리 (기존 테이블 구조에 맞게)"""
        processed_data = []

        if check_type == 'file_encryption':
            processed_data = self._process_file_encryption_data(df, uploaded_by)
        elif check_type == 'seal_check':
            processed_data = self._process_seal_check_data(df, uploaded_by)
        elif check_type == 'malware_scan':
            processed_data = self._process_malware_scan_data(df, uploaded_by)

        return processed_data

    def _process_file_encryption_data(self, df, uploaded_by):
        """개인정보 파일 암호화 데이터 처리"""
        processed_data = []

        # 컬럼 매핑
        col_mapping = self._find_column_mapping(
            df.columns, {
                'datetime': ['일시', '점검일시', '날짜'],
                'local_ip': ['로컬 IP', 'IP', '로컬IP'],
                'ssn_count': ['주민등록번호', '주민번호', '00회차에서 주민등록번호']
            })

        for idx, row in df.iterrows():
            try:
                # 로컬 IP로 사용자 찾기
                local_ip = str(row[
                    col_mapping['local_ip']]) if col_mapping['local_ip'] and pd.notna(
                        row[col_mapping['local_ip']]) else ''

                # 주민등록번호 건수 확인
                ssn_count = 0
                if col_mapping['ssn_count']:
                    ssn_value = row[col_mapping['ssn_count']]
                    if pd.notna(ssn_value):
                        if isinstance(ssn_value, (int, float)):
                            ssn_count = int(ssn_value)
                        else:
                            numbers = re.findall(r'\d+', str(ssn_value))
                            ssn_count = int(numbers[0]) if numbers else 0

                # 결과 판정: 주민등록번호가 0건 이상이면 불합격
                overall_result = 'fail' if ssn_count > 0 else 'pass'
                encryption_status = 'not_encrypted' if ssn_count > 0 else 'fully_encrypted'

                processed_row = {
                    'check_item_code': 'file_encryption',
                    'source_ip': local_ip,
                    'check_year': datetime.now().year,
                    'check_period': 'first_half',  # 기본값, 나중에 기간 설정으로 수정 가능
                    'check_date': self._parse_datetime(row[col_mapping['datetime']])
                    if col_mapping['datetime'] else datetime.now(),
                    'checker_name': uploaded_by,
                    'encryption_status': encryption_status,
                    'unencrypted_files': ssn_count,
                    'encryption_completed': 1 if ssn_count == 0 else 0,
                    'encryption_notes': f"주민등록번호 {ssn_count}건 발견"
                    if ssn_count > 0 else "정상",
                    'ssn_included': 1 if ssn_count > 0 else 0,
                    'overall_result': overall_result,
                    'notes': f"개인정보 파일 암호화 점검: {ssn_count}건 미암호화"
                    if ssn_count > 0 else "모든 개인정보 파일 암호화 완료",
                    'row_index': idx + 2
                }

                processed_data.append(processed_row)

            except Exception as e:
                print(f"개인정보 파일 암호화 데이터 처리 오류 (행 {idx + 2}): {str(e)}")
                continue

        return processed_data

    def _process_seal_check_data(self, df, uploaded_by):
        """PC 봉인씰 확인 데이터 처리"""
        processed_data = []

        # 컬럼 매핑
        col_mapping = self._find_column_mapping(
            df.columns, {
                'datetime': ['일시', '점검일시', '날짜'],
                'name': ['이름', '사용자명', '성명'],
                'department': ['부서', '부서명', '소속'],
                'damage_status': ['훼손여부', '봉인씰 확인', '상태']
            })

        for idx, row in df.iterrows():
            try:
                # 사용자 정보
                username = str(
                    row[col_mapping['name']]) if col_mapping['name'] and pd.notna(
                        row[col_mapping['name']]) else ''
                department = str(row[col_mapping['department']]
                                 ) if col_mapping['department'] and pd.notna(
                                     row[col_mapping['department']]) else ''

                # 훼손여부 확인
                damage_status = ''
                if col_mapping['damage_status']:
                    damage_value = row[col_mapping['damage_status']]
                    if pd.notna(damage_value):
                        damage_status = str(damage_value).strip()

                # 봉인씰 상태 매핑
                seal_status_map = {'훼손': 'damaged', '정상': 'normal', '미부착': 'missing'}
                seal_status = seal_status_map.get(damage_status, 'normal')

                # 결과 판정: 훼손이면 불합격
                overall_result = 'fail' if '훼손' in damage_status else 'pass'

                processed_row = {
                    'check_item_code': 'seal_check',
                    'check_year': datetime.now().year,
                    'check_period': 'first_half',
                    'check_date': self._parse_datetime(row[col_mapping['datetime']])
                    if col_mapping['datetime'] else datetime.now(),
                    'checker_name': uploaded_by,
                    'seal_status': seal_status,
                    'seal_notes': f"봉인씰 상태: {damage_status}",
                    'overall_result': overall_result,
                    'notes': f"PC 봉인씰 확인: {damage_status}",
                    'username': username,
                    'department': department,
                    'row_index': idx + 2
                }

                processed_data.append(processed_row)

            except Exception as e:
                print(f"PC 봉인씰 확인 데이터 처리 오류 (행 {idx + 2}): {str(e)}")
                continue

        return processed_data

    def _process_malware_scan_data(self, df, uploaded_by):
        """악성코드 전체 검사 데이터 처리"""
        processed_data = []

        # 컬럼 매핑
        col_mapping = self._find_column_mapping(
            df.columns, {
                'ip': ['IP', '로컬 IP', 'IP주소'],
                'malware_name': ['악성코드명', '악성코드', '위협명'],
                'malware_type': ['악성코드 분류', '분류', '유형'],
                'path': ['경로', '파일경로', '위치'],
                'detection_item': ['탐지 항목', '탐지항목', '탐지']
            })

        for idx, row in df.iterrows():
            try:
                # IP 주소
                ip_address = str(
                    row[col_mapping['ip']]) if col_mapping['ip'] and pd.notna(
                        row[col_mapping['ip']]) else ''

                # 악성코드 정보
                malware_name = str(row[col_mapping['malware_name']]
                                   ) if col_mapping['malware_name'] and pd.notna(
                                       row[col_mapping['malware_name']]) else ''
                malware_type = str(row[col_mapping['malware_type']]
                                   ) if col_mapping['malware_type'] and pd.notna(
                                       row[col_mapping['malware_type']]) else ''
                file_path = str(
                    row[col_mapping['path']]) if col_mapping['path'] and pd.notna(
                        row[col_mapping['path']]) else ''

                # 탐지 항목 확인
                detection_item = ''
                if col_mapping['detection_item']:
                    detection_value = row[col_mapping['detection_item']]
                    if pd.notna(detection_value):
                        detection_item = str(detection_value).strip()

                # 결과 판정: 탐지 항목이 있으면 불합격
                overall_result = 'fail' if detection_item else 'pass'
                malware_scan_result = 'infected' if detection_item else 'clean'
                threats_found = 1 if detection_item else 0

                processed_row = {
                    'check_item_code': 'malware_scan',
                    'source_ip': ip_address,
                    'check_year': datetime.now().year,
                    'check_period': 'first_half',
                    'check_date': datetime.now(),
                    'checker_name': uploaded_by,
                    'malware_scan_result': malware_scan_result,
                    'threats_found': threats_found,
                    'threats_cleaned': 0 if threats_found > 0 else 1,
                    'malware_name': malware_name,
                    'malware_classification': malware_type,
                    'malware_path': file_path,
                    'detection_item': detection_item,
                    'malware_notes': f"탐지 항목: {detection_item}"
                    if detection_item else "정상",
                    'overall_result': overall_result,
                    'notes': f"악성코드 검사: {detection_item}"
                    if detection_item else "악성코드 미발견",
                    'row_index': idx + 2
                }

                processed_data.append(processed_row)

            except Exception as e:
                print(f"악성코드 전체 검사 데이터 처리 오류 (행 {idx + 2}): {str(e)}")
                continue

        return processed_data

    def _find_column_mapping(self, columns, mapping_dict):
        """컬럼명 매핑 찾기"""
        result = {}

        for key, candidates in mapping_dict.items():
            result[key] = None
            for candidate in candidates:
                for col in columns:
                    if candidate in str(col):
                        result[key] = col
                        break
                if result[key]:
                    break

        return result

    def _parse_datetime(self, value):
        """날짜시간 파싱"""
        if pd.isna(value):
            return datetime.now()

        if isinstance(value, datetime):
            return value

        # 엑셀 시리얼 번호인 경우
        if isinstance(value, (int, float)):
            try:
                # 엑셀 시리얼 날짜 변환 (1900-01-01 기준)
                excel_date = datetime(1900, 1, 1) + pd.Timedelta(days=value - 2)
                return excel_date
            except:
                return datetime.now()

        # 문자열인 경우
        try:
            return pd.to_datetime(str(value))
        except:
            return datetime.now()

    def _save_to_existing_table(self, processed_data, check_type, uploaded_by):
        """기존 manual_check_results 테이블에 저장"""
        success_count = 0
        error_count = 0
        errors = []

        for data in processed_data:
            try:
                # 사용자 정보 조회 (IP나 이름으로)
                user_id = self._find_user_id(data, check_type)
                if not user_id:
                    # 사용자를 찾을 수 없는 경우 기본 사용자 생성 또는 건너뛰기
                    error_count += 1
                    errors.append(f"행 {data.get('row_index', '?')}: 사용자를 찾을 수 없습니다.")
                    continue

                # 기존 데이터 확인 (동일 사용자/날짜/점검유형 업데이트)
                existing_query = """
                    SELECT check_id FROM manual_check_results 
                    WHERE user_id = %s AND check_item_code = %s 
                    AND DATE(check_date) = DATE(%s)
                """

                existing_result = execute_query(
                    existing_query,
                    (user_id, data['check_item_code'], data['check_date']),
                    fetch_one=True)

                if existing_result:
                    # 업데이트
                    update_query = """
                        UPDATE manual_check_results 
                        SET seal_status = %s, malware_scan_result = %s, encryption_status = %s,
                            threats_found = %s, threats_cleaned = %s, unencrypted_files = %s,
                            encryption_completed = %s, malware_name = %s, malware_classification = %s,
                            malware_path = %s, detection_item = %s, ssn_included = %s,
                            overall_result = %s, notes = %s, updated_at = NOW()
                        WHERE check_id = %s
                    """

                    execute_query(
                        update_query,
                        (data.get('seal_status'), data.get('malware_scan_result'),
                         data.get('encryption_status'), data.get('threats_found', 0),
                         data.get('threats_cleaned', 0), data.get(
                             'unencrypted_files', 0), data.get(
                                 'encryption_completed', 0), data.get('malware_name'),
                         data.get('malware_classification'), data.get('malware_path'),
                         data.get('detection_item'), data.get(
                             'ssn_included', 0), data['overall_result'], data['notes'],
                         existing_result['check_id']))
                else:
                    # 신규 삽입
                    insert_query = """
                        INSERT INTO manual_check_results (
                            user_id, check_item_code, source_ip, check_year, check_period,
                            check_date, checker_name, seal_status, seal_notes,
                            malware_scan_result, threats_found, threats_cleaned, malware_notes,
                            malware_name, malware_classification, malware_path, detection_item,
                            encryption_status, unencrypted_files, encryption_completed, encryption_notes,
                            ssn_included, overall_result, notes, created_at
                        ) VALUES (
                            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s, %s, %s, NOW()
                        )
                    """

                    execute_query(
                        insert_query,
                        (user_id, data['check_item_code'], data.get('source_ip'),
                         data['check_year'], data['check_period'], data['check_date'],
                         data['checker_name'], data.get('seal_status'),
                         data.get('seal_notes'), data.get('malware_scan_result'),
                         data.get('threats_found', 0), data.get('threats_cleaned', 0),
                         data.get('malware_notes'), data.get('malware_name'),
                         data.get('malware_classification'), data.get('malware_path'),
                         data.get('detection_item'), data.get('encryption_status'),
                         data.get('unencrypted_files',
                                  0), data.get('encryption_completed', 0),
                         data.get('encryption_notes'), data.get(
                             'ssn_included', 0), data['overall_result'], data['notes']))

                success_count += 1

            except Exception as e:
                error_count += 1
                error_msg = f"행 {data.get('row_index', '?')}: {str(e)}"
                errors.append(error_msg)
                print(f"데이터 저장 오류: {error_msg}")

        return {
            "success_count": success_count,
            "error_count": error_count,
            "errors": errors
        }

    def _find_user_id(self, data, check_type):
        """점검 유형에 따라 사용자 ID 찾기"""
        try:
            if check_type == 'file_encryption':
                # IP로 사용자 찾기
                source_ip = data.get('source_ip')
                if source_ip:
                    user = execute_query(
                        "SELECT uid FROM users WHERE user_id LIKE %s OR username LIKE %s LIMIT 1",
                        (f"%{source_ip}%", f"%{source_ip}%"), fetch_one=True)
                    if user:
                        return user['uid']

            elif check_type == 'seal_check':
                # 이름으로 사용자 찾기
                username = data.get('username')
                if username:
                    user = execute_query(
                        "SELECT uid FROM users WHERE username = %s OR user_id = %s LIMIT 1",
                        (username, username), fetch_one=True)
                    if user:
                        return user['uid']

            elif check_type == 'malware_scan':
                # IP로 사용자 찾기
                source_ip = data.get('source_ip')
                if source_ip:
                    user = execute_query(
                        "SELECT uid FROM users WHERE user_id LIKE %s OR username LIKE %s LIMIT 1",
                        (f"%{source_ip}%", f"%{source_ip}%"), fetch_one=True)
                    if user:
                        return user['uid']

            # 기본적으로 admin 사용자 반환 (테스트용)
            admin_user = execute_query(
                "SELECT uid FROM users WHERE user_id = 'admin' OR username = 'admin' LIMIT 1",
                fetch_one=True)
            return admin_user['uid'] if admin_user else 1

        except Exception as e:
            print(f"사용자 ID 찾기 오류: {str(e)}")
            return 1  # 기본값

    def get_check_type_name(self, check_type):
        """점검 유형명 반환"""
        type_names = {
            'file_encryption': '개인정보 파일 암호화',
            'seal_check': 'PC 봉인씰 확인',
            'malware_scan': '악성코드 전체 검사'
        }
        return type_names.get(check_type, check_type)

    def get_check_type_mapping(self):
        """점검 유형 매핑 정보 반환"""
        return {
            'file_encryption': '개인정보 파일 암호화',
            'seal_check': 'PC 봉인씰 확인',
            'malware_scan': '악성코드 전체 검사',
            'screen_saver': '화면보호기',
            'antivirus': '백신',
            'patch_update': '패치'
        }

    def _analyze_expected_results(self, df, check_type):
        """업로드 파일의 예상 결과 분석"""
        try:
            total_records = len(df)
            expected_pass = 0
            expected_fail = 0
            analysis_details = []

            if check_type == 'file_encryption':
                # 개인정보 파일 암호화 분석
                col_mapping = self._find_column_mapping(
                    df.columns, {'ssn_count': ['주민등록번호', '주민번호', '00회차에서 주민등록번호']})

                if col_mapping['ssn_count']:
                    for idx, row in df.iterrows():
                        ssn_value = row[col_mapping['ssn_count']]
                        if pd.notna(ssn_value):
                            if isinstance(ssn_value, (int, float)):
                                ssn_count = int(ssn_value)
                            else:
                                numbers = re.findall(r'\d+', str(ssn_value))
                                ssn_count = int(numbers[0]) if numbers else 0

                            if ssn_count > 0:
                                expected_fail += 1
                                analysis_details.append(
                                    f"행 {idx + 2}: 주민등록번호 {ssn_count}건 → 실패")
                            else:
                                expected_pass += 1
                        else:
                            expected_pass += 1
                else:
                    analysis_details.append("주민등록번호 컬럼을 찾을 수 없어 정확한 분석이 어렵습니다.")

            elif check_type == 'seal_check':
                # PC 봉인씰 확인 분석
                col_mapping = self._find_column_mapping(
                    df.columns, {'damage_status': ['훼손여부', '봉인씰 확인', '상태']})

                if col_mapping['damage_status']:
                    for idx, row in df.iterrows():
                        damage_value = row[col_mapping['damage_status']]
                        if pd.notna(damage_value):
                            damage_status = str(damage_value).strip()
                            if '훼손' in damage_status:
                                expected_fail += 1
                                analysis_details.append(
                                    f"행 {idx + 2}: {damage_status} → 실패")
                            else:
                                expected_pass += 1
                                analysis_details.append(
                                    f"행 {idx + 2}: {damage_status} → 통과")
                        else:
                            expected_pass += 1
                else:
                    analysis_details.append("훼손여부 컬럼을 찾을 수 없어 정확한 분석이 어렵습니다.")

            elif check_type == 'malware_scan':
                # 악성코드 검사 분석
                col_mapping = self._find_column_mapping(
                    df.columns, {'detection_item': ['탐지 항목', '탐지항목', '탐지']})

                if col_mapping['detection_item']:
                    for idx, row in df.iterrows():
                        detection_value = row[col_mapping['detection_item']]
                        if pd.notna(detection_value):
                            detection_item = str(detection_value).strip()
                            if detection_item and detection_item != '':
                                expected_fail += 1
                                analysis_details.append(
                                    f"행 {idx + 2}: {detection_item} 탐지 → 실패")
                            else:
                                expected_pass += 1
                        else:
                            expected_pass += 1
                else:
                    analysis_details.append("탐지 항목 컬럼을 찾을 수 없어 정확한 분석이 어렵습니다.")

            return {
                "total_records": total_records,
                "expected_pass": expected_pass,
                "expected_fail": expected_fail,
                "pass_rate": round((expected_pass / total_records) *
                                   100, 1) if total_records > 0 else 0,
                "analysis_details": analysis_details[:10],  # 최대 10개까지만
                "summary": f"총 {total_records}건 중 통과 예상 {expected_pass}건, 실패 예상 {expected_fail}건"
            }

        except Exception as e:
            print(f"예상 결과 분석 오류: {str(e)}")
            return {
                "total_records": len(df),
                "expected_pass": 0,
                "expected_fail": 0,
                "pass_rate": 0,
                "analysis_details": ["분석 중 오류가 발생했습니다."],
                "summary": "분석 실패"
            }

    def generate_file_encryption_template(self):
        """개인정보 파일 암호화 템플릿 생성"""
        template_data = [
            "일시,로컬 IP,주민등록번호", "2025-06-13 14:30:00,192.168.1.100,0",
            "2025-06-13 14:35:00,192.168.1.101,2", "2025-06-13 14:40:00,192.168.1.102,0"
        ]
        return "\n".join(template_data)

    def generate_seal_check_template(self):
        """PC 봉인씰 확인 템플릿 생성"""
        template_data = [
            "일시,이름,부서,훼손여부", "2025-06-13 09:00:00,홍길동,개발팀,정상",
            "2025-06-13 09:15:00,김철수,운영팀,훼손", "2025-06-13 09:30:00,이영희,기획팀,정상"
        ]
        return "\n".join(template_data)

    def generate_malware_scan_template(self):
        """악성코드 전체 검사 템플릿 생성"""
        template_data = [
            "IP,악성코드명,악성코드 분류,경로,탐지 항목", "192.168.1.100,,,C:\\Users\\user1,",
            "192.168.1.101,Trojan.Generic,트로이목마,C:\\Users\\user2,virus.exe",
            "192.168.1.102,,,C:\\Users\\user3,"
        ]
        return "\n".join(template_data)

    def generate_all_templates(self):
        """전체 점검 유형 템플릿 안내"""
        template_content = """# 수시 점검 템플릿 안내

    ## 1. 개인정보 파일 암호화generate_all_templates
    필수 컬럼: 일시, 로컬 IP, 주민등록번호
    판정 기준: 주민등록번호가 0건 이상이면 불합격

    ## 2. PC 봉인씰 확인  
    필수 컬럼: 일시, 이름, 부서, 훼손여부
    판정 기준: 훼손여부가 "훼손"이면 불합격

    ## 3. 악성코드 전체 검사
    필수 컬럼: IP, 악성코드명, 악성코드 분류, 경로, 탐지 항목
    판정 기준: 탐지 항목이 있으면 불합격

    각 점검 유형별로 개별 템플릿을 다운로드하려면 
    ?type=file_encryption, ?type=seal_check, ?type=malware_scan 
    파라미터를 사용하세요.
    """
        return template_content