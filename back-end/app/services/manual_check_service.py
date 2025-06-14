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
            "file_encryption": {
                "required_columns": ["로컬 IP", "회차.*주민등록번호.*수정"],
                "keywords": ["개인정보", "암호화", "주민등록번호", "회차"],
            },
            "seal_check": {
                "required_columns": ["일시", "이름", "부서", "훼손여부"],
                "keywords": ["봉인씰", "확인", "훼손"],
            },
            "malware_scan": {
                "required_columns": [
                    "IP",
                    "악성코드명",
                    "악성코드 분류",
                    "경로",
                    "탐지 항목",
                ],
                "keywords": ["악성코드", "검사", "탐지"],
            },
        }

    def detect_file_type(self, df, filename):
        """파일 내용을 기반으로 점검 유형 자동 감지 - 개선된 버전"""
        columns = [col.strip() for col in df.columns]
        filename_lower = filename.lower()

        # 파일명 기반 1차 판별
        if "개인정보" in filename or "암호화" in filename:
            return "file_encryption"
        elif "봉인씰" in filename:
            return "seal_check"
        elif "악성코드" in filename:
            return "malware_scan"

        # 컬럼 기반 2차 판별 - 개인정보 암호화 특별 처리
        if self._has_encryption_columns(columns):
            return "file_encryption"

        # 기존 로직으로 다른 유형 확인
        for check_type, config in self.check_type_patterns.items():
            if check_type == "file_encryption":
                continue  # 이미 위에서 처리함

            required_cols = config["required_columns"]
            matched_cols = sum(
                1 for col in required_cols if any(req in col for req in columns)
            )

            if matched_cols >= len(required_cols) * 0.8:  # 80% 이상 일치
                return check_type

        return None

    def _has_encryption_columns(self, columns):
        """개인정보 암호화 파일 여부 확인"""
        import re

        has_ip = False
        has_round_ssn = False

        # 로컬 IP 컬럼 확인
        ip_keywords = ["로컬 IP", "로컬IP", "IP", "로컬 ip"]
        for col in columns:
            if any(keyword in str(col) for keyword in ip_keywords):
                has_ip = True
                break

        # 회차별 주민등록번호 컬럼 확인
        round_pattern = r"\d+회차.*주민등록번호.*수정"
        for col in columns:
            if re.search(round_pattern, str(col)):
                has_round_ssn = True
                break

        return has_ip and has_round_ssn

    def validate_file_structure(self, df, check_type):
        """파일 구조 검증 - 개인정보 암호화 특별 처리"""
        if check_type == "file_encryption":
            return self._validate_encryption_structure(df)

        # 기존 검증 로직
        if check_type not in self.check_type_patterns:
            return False, f"알 수 없는 점검 유형: {check_type}"

        required_cols = self.check_type_patterns[check_type]["required_columns"]
        columns = [col.strip() for col in df.columns]

        missing_cols = []
        for req_col in required_cols:
            if not any(req_col in col for col in columns):
                missing_cols.append(req_col)

        if missing_cols:
            return False, f"필수 컬럼이 없습니다: {', '.join(missing_cols)}"

        return True, "구조 검증 완료"

    def _validate_encryption_structure(self, df):
        """개인정보 암호화 파일 구조 검증"""
        columns = [col.strip() for col in df.columns]

        # 로컬 IP 컬럼 확인
        if not self._find_local_ip_column(columns):
            return False, "로컬 IP 컬럼을 찾을 수 없습니다. (예: '로컬 IP', 'IP' 등)"

        # 회차별 주민등록번호 컬럼 확인
        round_columns = self._detect_round_columns(columns)
        if not round_columns:
            return (
                False,
                "회차별 주민등록번호 컬럼을 찾을 수 없습니다. (예: '161회차에서 주민등록번호(수정)' 등)",
            )

        return (
            True,
            f"개인정보 암호화 파일 구조 확인 완료 - {len(round_columns)}개 회차 감지",
        )

    def get_excel_template(self):
        """엑셀 업로드용 템플릿 생성"""
        template_data = [
            "사용자ID,사용자명,부서,점검연도,점검기간,점검일시,점검자명,봉인씰상태,봉인번호,봉인씰비고,악성코드검사결과,발견위협수,치료완료여부,백신버전,악성코드비고,암호화상태,검사파일수,미암호화파일수,암호화완료여부,암호화비고,종합결과,전체비고",
            "admin,관리자,IT팀,2025,상반기,2025-06-10 14:30:00,김점검,정상,SEAL-2025-001,정상 상태 확인,정상,0,Y,V3 2025.06.10,검사 완료,완전암호화,15,0,Y,모든 파일 암호화 완료,통과,모든 항목 정상",
            "user1,홍길동,개발팀,2025,상반기,2025-06-10 15:00:00,김점검,손상,SEAL-2025-002,봉인씰 교체 필요,정상,0,Y,V3 2025.06.10,검사 완료,부분암호화,20,3,N,3개 파일 암호화 필요,부분통과,봉인씰 교체 및 암호화 조치 필요",
        ]
        return "\n".join(template_data)

    def process_bulk_upload(self, file, uploaded_by):
        """엑셀/CSV 파일 일괄 업로드 처리 - 멀티 헤더 지원"""
        try:
            filename = file.filename

            # 파일 읽기 - 멀티 헤더 처리
            if filename.lower().endswith(".csv"):
                df = pd.read_csv(file, encoding="utf-8-sig")
            elif filename.lower().endswith((".xlsx", ".xls")):
                # 엑셀 파일의 경우 멀티 헤더 처리
                df = self._read_excel_with_multi_header(file)
            else:
                raise ValueError("지원하지 않는 파일 형식입니다. (Excel, CSV만 지원)")

            # 빈 데이터프레임 체크
            if df.empty:
                raise ValueError("파일에 데이터가 없습니다.")

            print(f"[DEBUG] 처리된 컬럼명: {list(df.columns)}")

            # 점검 유형 자동 감지
            check_type = self.detect_file_type(df, filename)
            if not check_type:
                raise ValueError(
                    "점검 유형을 자동으로 감지할 수 없습니다. 파일명이나 컬럼을 확인해주세요."
                )

            # 파일 구조 검증
            is_valid, message = self.validate_file_structure(df, check_type)
            if not is_valid:
                raise ValueError(message)

            # 데이터 처리
            processed_data = self._process_check_data(df, check_type, uploaded_by)

            # 데이터베이스 저장
            save_result = self._save_to_existing_table(
                processed_data, check_type, uploaded_by
            )

            return {
                "success": True,
                "message": f"{self.get_check_type_name(check_type)} 업로드 완료",
                "file_type": self.get_check_type_name(check_type),
                "total_records": len(processed_data),
                "success_count": save_result["success_count"],
                "error_count": save_result["error_count"],
                "errors": save_result["errors"],
            }

        except Exception as e:
            print(f"파일 업로드 처리 오류: {str(e)}")
            raise ValueError(f"파일 처리 중 오류가 발생했습니다: {str(e)}")

    def _read_excel_with_multi_header(self, file):
        """멀티 헤더 엑셀 파일 읽기 및 컬럼명 합성"""
        try:
            # 첫 번째 시도: 1-2행을 헤더로 읽기
            df_headers = pd.read_excel(file, header=[0, 1], nrows=0)

            # 멀티 헤더 컬럼명 합성
            new_columns = []
            for col in df_headers.columns:
                if isinstance(col, tuple):
                    # 튜플인 경우 합성
                    col1, col2 = col
                    if pd.isna(col2) or str(col2).startswith("Unnamed"):
                        # 2행이 비어있으면 1행만 사용
                        new_columns.append(str(col1).strip())
                    else:
                        # 둘 다 있으면 합성
                        new_columns.append(
                            f"{str(col1).strip()}에서 {str(col2).strip()}"
                        )
                else:
                    new_columns.append(str(col).strip())

            print(f"[DEBUG] 합성된 컬럼명: {new_columns}")

            # 실제 데이터 읽기 (3행부터)
            file.seek(0)  # 파일 포인터 리셋
            df_data = pd.read_excel(file, header=None, skiprows=2)

            # 컬럼명 설정
            df_data.columns = new_columns[: len(df_data.columns)]

            return df_data

        except Exception as e:
            print(f"[DEBUG] 멀티 헤더 읽기 실패, 일반 방식으로 시도: {str(e)}")
            # 실패 시 일반적인 방식으로 읽기
            file.seek(0)
            return pd.read_excel(file)

    def _process_check_data(self, df, check_type, uploaded_by):
        """점검 유형별 데이터 처리 (기존 테이블 구조에 맞게)"""
        processed_data = []

        if check_type == "file_encryption":
            processed_data = self._process_file_encryption_data(df, uploaded_by)
        elif check_type == "seal_check":
            processed_data = self._process_seal_check_data(df, uploaded_by)
        elif check_type == "malware_scan":
            processed_data = self._process_malware_scan_data(df, uploaded_by)

        return processed_data

    def _process_file_encryption_data(self, df, uploaded_by):
        """개인정보 파일 암호화 데이터 처리 - 회차별 검증 로직"""
        processed_data = []

        # 회차별 주민등록번호 컬럼 자동 감지
        round_columns = self._detect_round_columns(df.columns)

        if not round_columns:
            print("회차별 주민등록번호 컬럼을 찾을 수 없습니다.")
            return processed_data

        # 로컬 IP 컬럼 찾기
        local_ip_column = self._find_local_ip_column(df.columns)

        if not local_ip_column:
            print("로컬 IP 컬럼을 찾을 수 없습니다.")
            return processed_data

        for idx, row in df.iterrows():
            try:
                # 로컬 IP로 사용자 찾기
                local_ip = (
                    str(row[local_ip_column]) if pd.notna(row[local_ip_column]) else ""
                )

                # 회차별 데이터 분석
                analysis_result = self._analyze_round_data(row, round_columns)

                processed_row = {
                    "check_item_code": "file_encryption",
                    "source_ip": local_ip,
                    "check_year": datetime.now().year,
                    "check_period": "first_half",
                    "check_date": datetime.now(),
                    "checker_name": uploaded_by,
                    "encryption_status": analysis_result["encryption_status"],
                    "unencrypted_files": analysis_result["total_violations"],
                    "encryption_completed": (
                        1 if analysis_result["overall_result"] == "pass" else 0
                    ),
                    "encryption_notes": analysis_result["notes"],
                    "ssn_included": 1 if analysis_result["total_violations"] > 0 else 0,
                    "overall_result": analysis_result["overall_result"],
                    "notes": analysis_result["detailed_notes"],
                    "row_index": idx + 2,
                }

                processed_data.append(processed_row)

            except Exception as e:
                print(f"개인정보 파일 암호화 데이터 처리 오류 (행 {idx + 2}): {str(e)}")
                continue

        return processed_data

    def _detect_round_columns(self, columns):
        """회차별 주민등록번호 컬럼 자동 감지 및 정렬 - 개선된 정규표현식"""
        import re

        # 다양한 패턴 시도
        patterns = [
            r"(\d+)회차.*주민등록번호.*수정",  # 기본 패턴
            r"(\d+)회차에서\s*주민등록번호\s*\(수정\)",  # 정확한 패턴
            r"(\d+)회차.*주민등록번호",  # 단순 패턴
            r"(\d+)\s*회차.*주민",  # 더 단순한 패턴
        ]

        round_columns = {}

        for col in columns:
            col_str = str(col).strip()
            print(f"[DEBUG] 컬럼 확인: '{col_str}'")

            for pattern in patterns:
                match = re.search(pattern, col_str)
                if match:
                    round_number = int(match.group(1))
                    round_columns[round_number] = col
                    print(f"[DEBUG] 회차 매칭 성공: {round_number}회차 -> '{col_str}'")
                    break

        # 최신 회차부터 정렬 (내림차순)
        sorted_rounds = sorted(round_columns.items(), key=lambda x: x[0], reverse=True)

        print(f"감지된 회차 컬럼: {dict(sorted_rounds)}")
        return sorted_rounds

    def _find_local_ip_column(self, columns):
        """로컬 IP 컬럼 찾기"""
        ip_keywords = ["로컬 IP", "로컬IP", "IP", "로컬 ip", "local ip", "local_ip"]

        for col in columns:
            col_str = str(col).strip()
            for keyword in ip_keywords:
                if keyword in col_str:
                    return col

        return None

    def _analyze_round_data(self, row, round_columns):
        """회차별 주민등록번호 데이터 분석 및 판정"""

        if not round_columns:
            return {
                "overall_result": "fail",
                "encryption_status": "not_encrypted",
                "total_violations": 0,
                "notes": "회차 데이터 없음",
                "detailed_notes": "회차별 주민등록번호 컬럼을 찾을 수 없습니다.",
            }

        latest_round = round_columns[0][0]  # 최신 회차 번호
        round_details = []
        total_violations = 0

        print(f"[DEBUG] 분석 시작 - 최신 회차: {latest_round}")
        print(f"[DEBUG] 회차 컬럼들: {[(num, col) for num, col in round_columns]}")

        # 최신 회차부터 역순으로 확인
        for round_number, column_name in round_columns:
            raw_value = row[column_name] if column_name in row.index else None
            value = raw_value if pd.notna(raw_value) else None

            print(
                f"[DEBUG] {round_number}회차 - 컬럼: '{column_name}', 원본값: '{raw_value}', 처리값: '{value}'"
            )

            if value is None:
                round_details.append(f"{round_number}회차: 데이터 없음")
                print(f"[DEBUG] {round_number}회차: 데이터 없음으로 스킵")
                continue

            value_str = str(value).strip()
            print(f"[DEBUG] {round_number}회차 - 문자열 변환: '{value_str}'")

            # "-" 값 처리 - 최신 회차 여부를 먼저 확인
            if value_str == "-" or value_str == "" or value_str.lower() == "nan":
                print(f"[DEBUG] {round_number}회차에서 '-' 또는 빈값 감지")
                round_details.append(f"{round_number}회차: 미확인(-)")

                if round_number == latest_round:
                    # 최신 회차에서 "-"이면 실패
                    print(
                        f"[DEBUG] 최신 회차({latest_round})에서 '-' 감지 -> 실패 처리"
                    )
                    return {
                        "overall_result": "fail",
                        "encryption_status": "not_encrypted",
                        "total_violations": 1,
                        "notes": f"{latest_round}회차에서 미확인(-) 상태로 실패",
                        "detailed_notes": f"검증 결과: {', '.join(round_details)} - 최신 회차({latest_round}회차)에서 주민등록번호 확인 불가로 실패",
                    }
                else:
                    # 과거 회차에서 "-"이면 통과 (모든 조건 무시)
                    print(
                        f"[DEBUG] 과거 회차({round_number})에서 '-' 감지 -> 통과 처리"
                    )
                    return {
                        "overall_result": "pass",
                        "encryption_status": "fully_encrypted",
                        "total_violations": 0,
                        "notes": f"{round_number}회차 미확인으로 통과",
                        "detailed_notes": f"검증 결과: {', '.join(round_details)} - {round_number}회차에서 미확인(-) 상태이므로 자동 통과",
                    }

            # 숫자 값 처리
            try:
                if isinstance(value, (int, float)):
                    count = int(value)
                else:
                    # 문자열에서 숫자 추출
                    numbers = re.findall(r"\d+", value_str)
                    count = int(numbers[0]) if numbers else 0

                print(f"[DEBUG] {round_number}회차 - 숫자 처리 결과: {count}건")
                round_details.append(f"{round_number}회차: {count}건")

                if count > 0:
                    total_violations += count
                    print(
                        f"[DEBUG] {round_number}회차에서 {count}건 발견, 다음 회차 확인 계속"
                    )
                    # 1건 이상이면 다음 회차 확인을 위해 계속 진행
                    continue
                else:
                    # 0건이면 통과
                    print(f"[DEBUG] {round_number}회차에서 0건 -> 통과 처리")
                    return {
                        "overall_result": "pass",
                        "encryption_status": "fully_encrypted",
                        "total_violations": 0,
                        "notes": f"{round_number}회차에서 0건으로 통과",
                        "detailed_notes": f"검증 결과: {', '.join(round_details)} - {round_number}회차 0건으로 최종 통과",
                    }

            except (ValueError, IndexError) as e:
                round_details.append(f"{round_number}회차: 형식 오류")
                print(f"[DEBUG] 회차 데이터 파싱 오류: {value_str}, 오류: {str(e)}")
                continue

        # 모든 회차를 확인했는데 모두 1건 이상이면 실패
        print(f"[DEBUG] 모든 회차 확인 완료 - 총 위반 건수: {total_violations}")
        return {
            "overall_result": "fail",
            "encryption_status": "not_encrypted",
            "total_violations": total_violations,
            "notes": f"모든 회차에서 위반 건수 발견 (총 {total_violations}건)",
            "detailed_notes": f"검증 결과: {', '.join(round_details)} - 모든 회차에서 주민등록번호 발견으로 실패",
        }

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

    def get_check_types(self):
        """지원되는 점검 유형 목록 반환 (period_service와 일관성 유지)"""
        return {
            "seal_check": "PC 봉인씰 확인",
            "malware_scan": "악성코드 전체 검사",
            "file_encryption": "개인정보 파일 암호화",
        }

    def _process_seal_check_data(self, df, uploaded_by):
        """PC 봉인씰 확인 데이터 처리"""
        processed_data = []

        # 컬럼 매핑
        col_mapping = self._find_column_mapping(
            df.columns,
            {
                "datetime": ["일시", "점검일시", "날짜"],
                "name": ["이름", "사용자명", "성명"],
                "department": ["부서", "부서명", "소속"],
                "damage_status": ["훼손여부", "봉인씰 확인", "상태"],
            },
        )

        for idx, row in df.iterrows():
            try:
                # 사용자 정보
                username = (
                    str(row[col_mapping["name"]])
                    if col_mapping["name"] and pd.notna(row[col_mapping["name"]])
                    else ""
                )
                department = (
                    str(row[col_mapping["department"]])
                    if col_mapping["department"]
                    and pd.notna(row[col_mapping["department"]])
                    else ""
                )

                # 훼손여부 확인
                damage_status = ""
                if col_mapping["damage_status"]:
                    damage_value = row[col_mapping["damage_status"]]
                    if pd.notna(damage_value):
                        damage_status = str(damage_value).strip()

                # 봉인씰 상태 매핑
                seal_status_map = {
                    "훼손": "damaged",
                    "정상": "normal",
                    "미부착": "missing",
                }
                seal_status = seal_status_map.get(damage_status, "normal")

                # 결과 판정: 훼손이면 불합격
                overall_result = "fail" if "훼손" in damage_status else "pass"

                processed_row = {
                    "check_item_code": "seal_check",
                    "check_year": datetime.now().year,
                    "check_period": "first_half",
                    "check_date": (
                        self._parse_datetime(row[col_mapping["datetime"]])
                        if col_mapping["datetime"]
                        else datetime.now()
                    ),
                    "checker_name": uploaded_by,
                    "seal_status": seal_status,
                    "seal_notes": f"봉인씰 상태: {damage_status}",
                    "overall_result": overall_result,
                    "notes": f"PC 봉인씰 확인: {damage_status}",
                    "username": username,
                    "department": department,
                    "row_index": idx + 2,
                }

                processed_data.append(processed_row)

            except Exception as e:
                print(f"PC 봉인씰 확인 데이터 처리 오류 (행 {idx + 2}): {str(e)}")
                continue

        return processed_data

    def _process_malware_scan_data(self, df, uploaded_by):
        """악성코드 전체 검사 데이터 처리 - 엑셀 파일의 일시 컬럼 사용"""
        processed_data = []

        # 컬럼 매핑 - 일시 컬럼 추가
        col_mapping = self._find_column_mapping(
            df.columns,
            {
                "datetime": ["일시", "점검일시", "날짜", "검사일시"],  # 일시 컬럼 추가
                "ip": ["IP", "로컬 IP", "IP주소"],
                "username": ["사용자명", "사용자", "이름"],
                "malware_name": ["악성코드명", "악성코드", "위협명"],
                "malware_type": ["악성코드 분류", "분류", "유형"],
                "path": ["경로", "파일경로", "위치"],
                "detection_item": ["탐지 항목", "탐지항목", "탐지"],
            },
        )

        for idx, row in df.iterrows():
            try:
                # 일시 정보 추출 - 엑셀 파일의 실제 일시 사용
                check_date = datetime.now()  # 기본값
                if col_mapping["datetime"] and pd.notna(row[col_mapping["datetime"]]):
                    check_date = self._parse_datetime(row[col_mapping["datetime"]])

                # 사용자명 추출
                username = ""
                if col_mapping["username"] and pd.notna(row[col_mapping["username"]]):
                    username = str(row[col_mapping["username"]]).strip()

                # IP 주소
                ip_address = (
                    str(row[col_mapping["ip"]])
                    if col_mapping["ip"] and pd.notna(row[col_mapping["ip"]])
                    else ""
                )

                # 악성코드 정보
                malware_name = (
                    str(row[col_mapping["malware_name"]])
                    if col_mapping["malware_name"]
                    and pd.notna(row[col_mapping["malware_name"]])
                    else ""
                )
                malware_type = (
                    str(row[col_mapping["malware_type"]])
                    if col_mapping["malware_type"]
                    and pd.notna(row[col_mapping["malware_type"]])
                    else ""
                )
                file_path = (
                    str(row[col_mapping["path"]])
                    if col_mapping["path"] and pd.notna(row[col_mapping["path"]])
                    else ""
                )

                # 탐지 항목 확인
                detection_item = ""
                if col_mapping["detection_item"]:
                    detection_value = row[col_mapping["detection_item"]]
                    if pd.notna(detection_value):
                        detection_item = str(detection_value).strip()

                # 결과 판정: 탐지 항목이 있으면 불합격
                overall_result = "fail" if detection_item else "pass"
                malware_scan_result = "infected" if detection_item else "clean"
                threats_found = 1 if detection_item else 0

                processed_row = {
                    "check_item_code": "malware_scan",
                    "source_ip": ip_address,
                    "check_year": check_date.year,  # 엑셀 파일의 일시에서 연도 추출
                    "check_period": "first_half",
                    "check_date": check_date,  # 엑셀 파일의 실제 일시 사용
                    "checker_name": uploaded_by,
                    "malware_scan_result": malware_scan_result,
                    "threats_found": threats_found,
                    "threats_cleaned": 0 if threats_found > 0 else 1,
                    "malware_name": malware_name,
                    "malware_classification": malware_type,
                    "malware_path": file_path,
                    "detection_item": detection_item,
                    "malware_notes": (
                        f"탐지 항목: {detection_item}" if detection_item else "정상"
                    ),
                    "overall_result": overall_result,
                    "notes": (
                        f"악성코드 검사: {detection_item}"
                        if detection_item
                        else "악성코드 미발견"
                    ),
                    "username": username,  # 사용자명도 추가
                    "row_index": idx + 2,
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

    # _parse_datetime 함수도 한국어 날짜 형식을 더 잘 처리하도록 개선
    def _parse_datetime(self, value):
        """날짜시간 파싱 - 한국어 형식 지원 강화"""
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
            # 한국어 오전/오후 형식 처리
            str_value = str(value).strip()

            # "2025-05-31 오후 1:02:53" 형식 처리
            if "오후" in str_value or "오전" in str_value:
                # 오후/오전을 AM/PM으로 변경
                str_value = str_value.replace("오전", "AM").replace("오후", "PM")

                # 시간 형식을 표준화 (1:02:53 -> 01:02:53)
                import re

                time_pattern = (
                    r"(\d{4}-\d{2}-\d{2})\s+(AM|PM)\s+(\d{1,2}):(\d{2}):(\d{2})"
                )
                match = re.match(time_pattern, str_value)

                if match:
                    date_part = match.group(1)
                    am_pm = match.group(2)
                    hour = int(match.group(3))
                    minute = match.group(4)
                    second = match.group(5)

                    # 12시간 형식을 24시간 형식으로 변환
                    if am_pm == "PM" and hour != 12:
                        hour += 12
                    elif am_pm == "AM" and hour == 12:
                        hour = 0

                    formatted_time = f"{date_part} {hour:02d}:{minute}:{second}"
                    return pd.to_datetime(formatted_time)

            # 일반적인 날짜 형식 시도
            return pd.to_datetime(str_value)

        except Exception as e:
            print(f"날짜 파싱 오류: {str_value}, 오류: {str(e)}")
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
                    errors.append(
                        f"행 {data.get('row_index', '?')}: 사용자를 찾을 수 없습니다."
                    )
                    continue

                # 기존 데이터 확인 (동일 사용자/날짜/점검유형 업데이트)
                existing_query = """
                    SELECT check_id FROM manual_check_results 
                    WHERE user_id = %s AND check_item_code = %s 
                    AND DATE(check_date) = DATE(%s)
                """

                existing_result = execute_query(
                    existing_query,
                    (user_id, data["check_item_code"], data["check_date"]),
                    fetch_one=True,
                )

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
                        (
                            data.get("seal_status"),
                            data.get("malware_scan_result"),
                            data.get("encryption_status"),
                            data.get("threats_found", 0),
                            data.get("threats_cleaned", 0),
                            data.get("unencrypted_files", 0),
                            data.get("encryption_completed", 0),
                            data.get("malware_name"),
                            data.get("malware_classification"),
                            data.get("malware_path"),
                            data.get("detection_item"),
                            data.get("ssn_included", 0),
                            data["overall_result"],
                            data["notes"],
                            existing_result["check_id"],
                        ),
                    )
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
                        (
                            user_id,
                            data["check_item_code"],
                            data.get("source_ip"),
                            data["check_year"],
                            data["check_period"],
                            data["check_date"],
                            data["checker_name"],
                            data.get("seal_status"),
                            data.get("seal_notes"),
                            data.get("malware_scan_result"),
                            data.get("threats_found", 0),
                            data.get("threats_cleaned", 0),
                            data.get("malware_notes"),
                            data.get("malware_name"),
                            data.get("malware_classification"),
                            data.get("malware_path"),
                            data.get("detection_item"),
                            data.get("encryption_status"),
                            data.get("unencrypted_files", 0),
                            data.get("encryption_completed", 0),
                            data.get("encryption_notes"),
                            data.get("ssn_included", 0),
                            data["overall_result"],
                            data["notes"],
                        ),
                    )

                success_count += 1

            except Exception as e:
                error_count += 1
                error_msg = f"행 {data.get('row_index', '?')}: {str(e)}"
                errors.append(error_msg)
                print(f"데이터 저장 오류: {error_msg}")

        return {
            "success_count": success_count,
            "error_count": error_count,
            "errors": errors,
        }

    def _find_user_id(self, data, check_type):
        """점검 유형에 따라 사용자 ID 찾기"""
        try:
            if check_type == "file_encryption":
                # IP로 사용자 찾기 (올바른 컬럼 사용)
                source_ip = data.get("source_ip")
                if source_ip:
                    user = execute_query(
                        "SELECT uid FROM users WHERE ip LIKE %s LIMIT 1",
                        (f"%{source_ip}%",),
                        fetch_one=True,
                    )
                    if user:
                        return user["uid"]

            elif check_type == "seal_check":
                # 이름으로 사용자 찾기
                username = data.get("username")
                if username:
                    user = execute_query(
                        "SELECT uid FROM users WHERE username = %s OR user_id = %s LIMIT 1",
                        (username, username),
                        fetch_one=True,
                    )
                    if user:
                        return user["uid"]

            elif check_type == "malware_scan":
                # 1. 사용자명으로 먼저 검색 (악성코드 파일에 사용자명이 있음)
                username = data.get("username")  # 사용자명 컬럼
                if username:
                    user = execute_query(
                        "SELECT uid FROM users WHERE username = %s OR user_id = %s LIMIT 1",
                        (username, username),
                        fetch_one=True,
                    )
                    if user:
                        return user["uid"]

                # 2. IP로 사용자 찾기 (올바른 컬럼 사용)
                source_ip = data.get("source_ip")
                if source_ip:
                    user = execute_query(
                        "SELECT uid FROM users WHERE ip LIKE %s LIMIT 1",
                        (f"%{source_ip}%",),
                        fetch_one=True,
                    )
                    if user:
                        return user["uid"]

            # 3. 사용자를 찾지 못한 경우 None 반환 (admin 반환하지 않음)
            return None

        except Exception as e:
            print(f"사용자 ID 찾기 오류: {str(e)}")
            return None  # 오류 시에도 admin 반환하지 않음

    def get_check_type_name(self, check_type):
        """점검 유형명 반환 - 개인정보 암호화 설명 업데이트"""
        type_names = {
            "file_encryption": "개인정보 파일 암호화 (회차별 검증)",
            "seal_check": "PC 봉인씰 확인",
            "malware_scan": "악성코드 전체 검사",
        }
        return type_names.get(check_type, check_type)

    def get_check_type_mapping(self):
        """점검 유형 매핑 정보 반환 - 개인정보 암호화 설명 업데이트"""
        return {
            "file_encryption": "개인정보 파일 암호화 (회차별)",
            "seal_check": "PC 봉인씰 확인",
            "malware_scan": "악성코드 전체 검사",
        }

    def _analyze_expected_results(self, df, check_type):
        """업로드 파일의 예상 결과 분석 - 개선된 버전"""
        try:
            total_records = len(df)
            expected_pass = 0
            expected_fail = 0
            analysis_details = []

            if check_type == "file_encryption":
                # 개인정보 파일 암호화 분석 - 회차별 로직
                round_columns = self._detect_round_columns(df.columns)

                if not round_columns:
                    analysis_details.append(
                        "회차별 주민등록번호 컬럼을 찾을 수 없어 정확한 분석이 어렵습니다."
                    )
                    return self._create_analysis_result(
                        total_records, 0, 0, analysis_details
                    )

                latest_round = round_columns[0][0]  # 최신 회차

                for idx, row in df.iterrows():
                    try:
                        analysis_result = self._analyze_round_data(row, round_columns)

                        if analysis_result["overall_result"] == "pass":
                            expected_pass += 1
                            if len(analysis_details) < 10:  # 최대 10개까지만 표시
                                analysis_details.append(
                                    f"행 {idx + 2}: {analysis_result['notes']} → 통과"
                                )
                        else:
                            expected_fail += 1
                            if len(analysis_details) < 10:
                                analysis_details.append(
                                    f"행 {idx + 2}: {analysis_result['notes']} → 실패"
                                )

                    except Exception as e:
                        expected_fail += 1
                        if len(analysis_details) < 10:
                            analysis_details.append(f"행 {idx + 2}: 분석 오류 → 실패")

            elif check_type == "seal_check":
                # PC 봉인씰 확인 분석 (기존 로직 유지)
                col_mapping = self._find_column_mapping(
                    df.columns, {"damage_status": ["훼손여부", "봉인씰 확인", "상태"]}
                )

                if col_mapping["damage_status"]:
                    for idx, row in df.iterrows():
                        damage_value = row[col_mapping["damage_status"]]
                        if pd.notna(damage_value):
                            damage_status = str(damage_value).strip()
                            if "훼손" in damage_status:
                                expected_fail += 1
                                if len(analysis_details) < 10:
                                    analysis_details.append(
                                        f"행 {idx + 2}: {damage_status} → 실패"
                                    )
                            else:
                                expected_pass += 1
                                if len(analysis_details) < 10:
                                    analysis_details.append(
                                        f"행 {idx + 2}: {damage_status} → 통과"
                                    )
                        else:
                            expected_pass += 1
                else:
                    analysis_details.append(
                        "훼손여부 컬럼을 찾을 수 없어 정확한 분석이 어렵습니다."
                    )

            elif check_type == "malware_scan":
                # 악성코드 검사 분석 (기존 로직 유지)
                col_mapping = self._find_column_mapping(
                    df.columns, {"detection_item": ["탐지 항목", "탐지항목", "탐지"]}
                )

                if col_mapping["detection_item"]:
                    for idx, row in df.iterrows():
                        detection_value = row[col_mapping["detection_item"]]
                        if pd.notna(detection_value):
                            detection_item = str(detection_value).strip()
                            if detection_item and detection_item != "":
                                expected_fail += 1
                                if len(analysis_details) < 10:
                                    analysis_details.append(
                                        f"행 {idx + 2}: {detection_item} 탐지 → 실패"
                                    )
                            else:
                                expected_pass += 1
                        else:
                            expected_pass += 1
                else:
                    analysis_details.append(
                        "탐지 항목 컬럼을 찾을 수 없어 정확한 분석이 어렵습니다."
                    )

            return self._create_analysis_result(
                total_records, expected_pass, expected_fail, analysis_details
            )

        except Exception as e:
            print(f"예상 결과 분석 오류: {str(e)}")
            return self._create_analysis_result(
                len(df), 0, 0, ["분석 중 오류가 발생했습니다."]
            )

    def _create_analysis_result(
        self, total_records, expected_pass, expected_fail, analysis_details
    ):
        """분석 결과 객체 생성"""
        return {
            "total_records": total_records,
            "expected_pass": expected_pass,
            "expected_fail": expected_fail,
            "pass_rate": (
                round((expected_pass / total_records) * 100, 1)
                if total_records > 0
                else 0
            ),
            "analysis_details": analysis_details,
            "summary": f"총 {total_records}건 중 통과 예상 {expected_pass}건, 실패 예상 {expected_fail}건",
        }

    def generate_file_encryption_template(self):
        """개인정보 파일 암호화 템플릿 생성 - 회차별 컬럼 포함"""
        template_data = [
            "로컬 IP,161회차에서 주민등록번호(수정),160회차에서 주민등록번호(수정),159회차에서 주민등록번호(수정)",
            "192.168.1.100,0,2,1",
            "192.168.1.101,1,0,3",
            "192.168.1.102,0,0,0",
            "192.168.1.103,-,1,2",
            "192.168.1.104,2,-,1",
        ]
        return "\n".join(template_data)

    def generate_upload_template(self):
        """업로드 템플릿 생성 - 점검 유형별 안내 포함"""
        template_content = """# 수시 점검 업로드 템플릿 안내

    ## 1. 개인정보 파일 암호화
    필수 컬럼: 로컬 IP, XXX회차에서 주민등록번호(수정)
    - 로컬 IP: 검사 대상 PC의 IP 주소
    - 회차별 주민등록번호: 각 회차에서 발견된 주민등록번호 건수 또는 "-"
    - 판정 기준: 
      * 최신 회차부터 역순으로 확인
      * 값이 "-"인 경우: 최신 회차면 실패, 과거 회차면 통과
      * 숫자인 경우: 0건이면 통과, 1건 이상이면 다음 회차 확인
      * 모든 회차가 1건 이상이면 실패

    ## 2. PC 봉인씰 확인  
    필수 컬럼: 일시, 이름, 부서, 훼손여부
    판정 기준: 훼손여부가 "훼손"이면 불합격

    ## 3. 악성코드 전체 검사
    필수 컬럼: IP, 악성코드명, 악성코드 분류, 경로, 탐지 항목
    판정 기준: 탐지 항목이 있으면 불합격

    각 점검 유형별로 개별 템플릿을 다운로드하려면 
    ?type=file_encryption, ?type=seal_check, ?type=malware_scan 
    파라미터를 사용하세요.

    예시 데이터:
    개인정보 암호화 - 161회차: 2건, 160회차: 0건 → 실패 (161회차에서 발견)
    개인정보 암호화 - 161회차: 0건, 160회차: 3건 → 통과 (161회차가 0건)
    개인정보 암호화 - 161회차: "-", 160회차: 1건 → 실패 (최신 회차가 "-")
    개인정보 암호화 - 161회차: 2건, 160회차: "-" → 통과 (160회차가 "-")
    """
        return template_content

    def generate_seal_check_template(self):
        """PC 봉인씰 확인 템플릿 생성"""
        template_data = [
            "일시,이름,부서,훼손여부",
            "2025-06-13 09:00:00,홍길동,개발팀,정상",
            "2025-06-13 09:15:00,김철수,운영팀,훼손",
            "2025-06-13 09:30:00,이영희,기획팀,정상",
        ]
        return "\n".join(template_data)

    # 악성코드 템플릿도 일시 컬럼을 포함하도록 수정
    def generate_malware_scan_template(self):
        """악성코드 전체 검사 템플릿 생성 - 일시 컬럼 포함"""
        template_data = [
            "일시,IP,사용자명,악성코드명,악성코드 분류,경로,탐지 항목",
            "2025-06-13 14:30:00,192.168.1.100,홍길동,,,C:\\Users\\user1,",
            "2025-06-13 14:35:00,192.168.1.101,김철수,Trojan.Generic,트로이목마,C:\\Users\\user2,virus.exe",
            "2025-06-13 14:40:00,192.168.1.102,이영희,,,C:\\Users\\user3,",
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
