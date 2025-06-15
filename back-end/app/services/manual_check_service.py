# manual_check_service.py
# back-end/app/services/ 폴더에 생성

import pandas as pd
import io
import re
from app.utils.database import DatabaseManager, execute_query
from datetime import datetime, timedelta


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

    # ✅ 1단계: 날짜 기반 기간 매칭 함수 추가
    def _find_appropriate_period(self, check_date, check_type):
        """날짜를 기반으로 적절한 기간을 찾기"""
        try:
            year = check_date.year

            # 해당 연도와 점검 유형의 모든 활성 기간 조회
            periods = execute_query(
                """
                SELECT period_id, period_name, start_date, end_date, is_completed
                FROM manual_check_periods
                WHERE period_year = %s AND check_type = %s AND is_active = 1
                ORDER BY start_date
                """,
                (year, check_type),
                fetch_all=True,
            )

            if not periods:
                print(f"[DEBUG] {year}년 {check_type}에 대한 기간 설정이 없습니다.")
                return None, "first_half"  # 기본값 반환

            # 날짜가 포함되는 기간 찾기
            check_date_only = check_date.date()

            for period in periods:
                if period["start_date"] <= check_date_only <= period["end_date"]:
                    print(
                        f"[DEBUG] 날짜 {check_date_only}가 기간 '{period['period_name']}'에 포함됨"
                    )
                    return period["period_id"], period["period_name"]

            # 해당하는 기간이 없으면 가장 가까운 기간 찾기
            closest_period = None
            min_distance = float("inf")

            for period in periods:
                # 시작일과의 거리 계산
                distance_to_start = abs((check_date_only - period["start_date"]).days)
                # 종료일과의 거리 계산
                distance_to_end = abs((check_date_only - period["end_date"]).days)
                # 최소 거리
                distance = min(distance_to_start, distance_to_end)

                if distance < min_distance:
                    min_distance = distance
                    closest_period = period

            if closest_period:
                print(f"[DEBUG] 가장 가까운 기간: '{closest_period['period_name']}'")
                return closest_period["period_id"], closest_period["period_name"]

            # 모든 경우에 실패하면 첫 번째 기간 사용
            first_period = periods[0]
            print(
                f"[DEBUG] 기본적으로 첫 번째 기간 사용: '{first_period['period_name']}'"
            )
            return first_period["period_id"], first_period["period_name"]

        except Exception as e:
            print(f"[DEBUG] 기간 찾기 오류: {str(e)}")
            return None, "first_half"

    # ✅ 4단계: 회차별 날짜 계산 함수 추가
    def _calculate_round_date(self, upload_date, round_number, latest_round_number):
        """회차별 날짜 계산 - 최신 회차는 저번주, 이전 회차는 순차적으로 이전 주"""
        try:
            # 업로드 날짜에서 주의 시작일(월요일) 계산
            upload_weekday = upload_date.weekday()  # 0=월요일, 6=일요일

            # 이번주 월요일 계산
            this_week_monday = upload_date - timedelta(days=upload_weekday)

            # 최신 회차와 현재 회차의 차이 계산
            weeks_back = latest_round_number - round_number + 1

            # 해당 회차의 주 계산 (저번주부터 시작)
            round_week_monday = this_week_monday - timedelta(weeks=weeks_back)

            # 해당 주의 중간 날짜 반환 (수요일)
            round_date = round_week_monday + timedelta(days=2)

            print(
                f"[DEBUG] 회차 {round_number}: {round_date.strftime('%Y-%m-%d')} (업로드: {upload_date.strftime('%Y-%m-%d')})"
            )

            return round_date

        except Exception as e:
            print(f"[DEBUG] 회차 날짜 계산 오류: {str(e)}")
            return upload_date - timedelta(weeks=1)  # 기본값: 저번주

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

    def _find_local_ip_column(self, columns):
        """로컬 IP 컬럼 찾기"""
        ip_keywords = ["로컬 IP", "로컬IP", "IP", "로컬 ip", "접근 IP"]
        for col in columns:
            if any(keyword in str(col) for keyword in ip_keywords):
                return col
        return None

    def _detect_round_columns(self, columns):
        """회차별 주민등록번호 컬럼 감지"""
        round_columns = []
        round_pattern = r"(\d+)회차.*주민등록번호.*수정"

        for col in columns:
            match = re.search(round_pattern, str(col))
            if match:
                round_number = int(match.group(1))
                round_columns.append({"column": col, "round": round_number})

        return round_columns

    def _find_username_column(self, columns):
        """사용자명 컬럼 찾기"""
        username_keywords = ["사용자명", "사용자", "이름", "호스트명"]
        for col in columns:
            if any(keyword in str(col) for keyword in username_keywords):
                return col
        return None

    def _find_department_column(self, columns):
        """부서/소속 컬럼 찾기"""
        dept_keywords = ["소속", "부서", "부서명", "조직"]
        for col in columns:
            if any(keyword in str(col) for keyword in dept_keywords):
                return col
        return None

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

    def _read_excel_with_multi_header(self, file):
        """멀티 헤더 엑셀 파일 읽기 및 컬럼명 합성 - 파일 구조 자동 감지"""
        try:
            filename = getattr(file, "filename", "")

            # 1단계: 파일명 기반 구분
            if "개인정보" in filename or "암호화" in filename:
                # 개인정보 암호화 파일 - 멀티헤더 처리
                return self._read_multi_header_file(file)
            else:
                # 봉인씰, 악성코드 등 - 단일헤더 처리
                return self._read_single_header_file(file)

        except Exception as e:
            print(f"[DEBUG] 파일 읽기 실패, 기본 방식으로 시도: {str(e)}")
            file.seek(0)
            return pd.read_excel(file)

    def _read_multi_header_file(self, file):
        """멀티헤더 파일 처리 (3행부터 데이터)"""
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

    def _read_single_header_file(self, file):
        """단일헤더 파일 처리 (2행부터 데이터)"""
        file.seek(0)
        return pd.read_excel(file, header=0)  # 1행을

    # ✅ 개선된 사용자 찾기 함수
    # ✅ 수정된 사용자 찾기 함수
    def _find_user_id(self, data, check_type):
        """사용자 ID 찾기 - 수정된 버전"""
        try:
            print(
                f"[DEBUG] 사용자 찾기 시작: {data.get('username')}, IP: {data.get('source_ip')}"
            )

            # 1. 사용자명으로 찾기 (우선순위)
            username = data.get("username")
            if username:
                # 정확한 매칭
                user = execute_query(
                    "SELECT uid FROM users WHERE username = %s OR user_id = %s LIMIT 1",
                    (username, username),
                    fetch_one=True,
                )
                if user:
                    print(f"[DEBUG] 사용자명 {username}으로 사용자 {user['uid']} 찾음")
                    return user["uid"]

                # 부분 매칭 시도
                user = execute_query(
                    "SELECT uid FROM users WHERE username LIKE %s OR user_id LIKE %s LIMIT 1",
                    (f"%{username}%", f"%{username}%"),
                    fetch_one=True,
                )
                if user:
                    print(f"[DEBUG] 사용자명 부분매칭으로 사용자 {user['uid']} 찾음")
                    return user["uid"]

            # 2. IP 주소로 사용자 찾기 (✅ ip 컬럼으로 수정)
            source_ip = data.get("source_ip")
            if source_ip:
                # ip 컬럼으로 검색 (last_ip 대신)
                user = execute_query(
                    "SELECT uid FROM users WHERE ip LIKE %s LIMIT 1",
                    (f"%{source_ip}%",),
                    fetch_one=True,
                )
                if user:
                    print(f"[DEBUG] IP {source_ip}로 사용자 {user['uid']} 찾음")
                    return user["uid"]

            # 3. 부서와 사용자명 조합으로 찾기
            department = data.get("department")
            if department and username:
                user = execute_query(
                    "SELECT uid FROM users WHERE username LIKE %s AND department LIKE %s LIMIT 1",
                    (f"%{username}%", f"%{department}%"),
                    fetch_one=True,
                )
                if user:
                    print(f"[DEBUG] 사용자명+부서로 사용자 {user['uid']} 찾음")
                    return user["uid"]

            # ✅ 4. 사용자를 찾지 못한 경우 - 기본 사용자 생성 또는 사용
            if username or source_ip:
                print(f"[WARNING] 사용자를 찾을 수 없어서 기본 사용자 생성 시도")

                # 4-1. 먼저 기본 관리자 사용자가 있는지 확인
                admin_user = execute_query(
                    "SELECT uid FROM users WHERE user_id = 'admin' OR username = 'admin' LIMIT 1",
                    fetch_one=True,
                )
                if admin_user:
                    print(f"[DEBUG] 기본 관리자 사용자 {admin_user['uid']} 사용")
                    return admin_user["uid"]

                # 4-2. 첫 번째 사용자 사용
                first_user = execute_query(
                    "SELECT uid FROM users ORDER BY uid LIMIT 1", fetch_one=True
                )
                if first_user:
                    print(f"[DEBUG] 첫 번째 사용자 {first_user['uid']} 사용")
                    return first_user["uid"]

                # 4-3. 마지막 수단: 사용자 생성 (옵션)
                # return self._create_default_user(username, source_ip)

            print(
                f"[ERROR] 사용자를 찾을 수 없음 - 사용자명: {username}, IP: {source_ip}"
            )
            return None

        except Exception as e:
            print(f"[ERROR] 사용자 검색 오류: {str(e)}")
            return None

    def _process_seal_check_data(self, df, uploaded_by):
        """PC 봉인씰 확인 데이터 처리 - 기간 매칭 로직 추가"""
        processed_data = []

        # 컬럼 매핑
        col_mapping = self._find_column_mapping(
            df.columns,
            {
                "datetime": ["일시", "점검일시", "날짜"],
                "username": ["이름", "사용자명", "담당자"],
                "department": ["부서", "부서명"],
                "damage_status": ["훼손여부", "상태", "봉인상태"],
            },
        )

        for idx, row in df.iterrows():
            try:
                # ✅ 일시 정보 파싱 (엑셀 파일의 실제 날짜 사용)
                check_date = datetime.now()  # 기본값
                if col_mapping["datetime"] and pd.notna(row[col_mapping["datetime"]]):
                    check_date = self._parse_datetime(row[col_mapping["datetime"]])
                    print(f"[DEBUG] 봉인씰 - 행 {idx+2}: 파싱된 날짜 = {check_date}")

                # ✅ 날짜 기반으로 적절한 기간 찾기
                period_id, period_name = self._find_appropriate_period(
                    check_date, "seal_check"
                )
                print(
                    f"[DEBUG] 봉인씰 - 행 {idx+2}: 매칭된 기간 = {period_name} (ID: {period_id})"
                )

                # 사용자명과 부서 정보
                username = ""
                if col_mapping["username"] and pd.notna(row[col_mapping["username"]]):
                    username = str(row[col_mapping["username"]]).strip()

                department = ""
                if col_mapping["department"] and pd.notna(
                    row[col_mapping["department"]]
                ):
                    department = str(row[col_mapping["department"]]).strip()

                # 훼손여부 확인
                damage_status = "정상"  # 기본값
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
                    "check_year": check_date.year,  # ✅ 실제 연도 사용
                    "check_period": period_name,  # ✅ 동적 기간명 사용 (하드코딩 제거)
                    "period_id": period_id,  # ✅ 기간 ID 설정 (중요!)
                    "check_date": check_date,  # ✅ 실제 날짜 사용
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

    # ✅ 3단계: 악성코드 데이터 처리 로직 수정
    def _process_malware_scan_data(self, df, uploaded_by):
        """악성코드 전체 검사 데이터 처리 - 기간 매칭 로직 추가"""
        processed_data = []

        # 컬럼 매핑 - 일시 컬럼 추가
        col_mapping = self._find_column_mapping(
            df.columns,
            {
                "datetime": ["일시", "점검일시", "날짜", "검사일시"],
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
                # ✅ 일시 정보 추출 - 엑셀 파일의 실제 일시 사용
                check_date = datetime.now()  # 기본값
                if col_mapping["datetime"] and pd.notna(row[col_mapping["datetime"]]):
                    check_date = self._parse_datetime(row[col_mapping["datetime"]])
                    print(f"[DEBUG] 악성코드 - 행 {idx+2}: 파싱된 날짜 = {check_date}")

                # ✅ 날짜 기반으로 적절한 기간 찾기
                period_id, period_name = self._find_appropriate_period(
                    check_date, "malware_scan"
                )
                print(
                    f"[DEBUG] 악성코드 - 행 {idx+2}: 매칭된 기간 = {period_name} (ID: {period_id})"
                )

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
                    "check_year": check_date.year,  # ✅ 실제 연도 사용
                    "check_period": period_name,  # ✅ 동적 기간명 사용 (하드코딩 제거)
                    "period_id": period_id,  # ✅ 기간 ID 설정 (중요!)
                    "check_date": check_date,  # ✅ 엑셀 파일의 실제 일시 사용
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
                    "username": username,
                    "row_index": idx + 2,
                }

                processed_data.append(processed_row)

            except Exception as e:
                print(f"악성코드 전체 검사 데이터 처리 오류 (행 {idx + 2}): {str(e)}")
                continue

        return processed_data

    # ✅ 유연한 컬럼 매핑 함수 (멀티헤더 지원)
    def _find_column_mapping_flexible(self, columns, mapping_dict):
        """컬럼명 매핑 찾기 - 멀티헤더 및 부분 매칭 지원"""
        result = {}

        for key, candidates in mapping_dict.items():
            result[key] = None

            # 정확한 매칭 우선
            for candidate in candidates:
                for col in columns:
                    if candidate in str(col):
                        result[key] = col
                        break
                if result[key]:
                    break

            # 정확한 매칭이 없으면 부분 매칭 시도
            if not result[key]:
                for col in columns:
                    col_str = str(col).lower()
                    for candidate in candidates:
                        candidate_lower = candidate.lower()
                        if candidate_lower in col_str or any(
                            word in col_str for word in candidate_lower.split()
                        ):
                            result[key] = col
                            break
                    if result[key]:
                        break

        return result

    # ✅ 안전한 날짜 파싱 함수
    def _parse_datetime_safe(self, value):
        """안전한 날짜시간 파싱"""
        try:
            if pd.isna(value):
                return datetime.now()

            if isinstance(value, datetime):
                return value

            # 엑셀 시리얼 번호인 경우
            if isinstance(value, (int, float)):
                try:
                    excel_date = datetime(1900, 1, 1) + pd.Timedelta(days=value - 2)
                    return excel_date
                except:
                    return datetime.now()

            # 문자열인 경우
            str_value = str(value).strip()

            # 빈 문자열 체크
            if not str_value or str_value == "nan":
                return datetime.now()

            # 한국어 오전/오후 형식 처리
            if "오후" in str_value or "오전" in str_value:
                try:
                    # 오후/오전을 AM/PM으로 변경
                    str_value = str_value.replace("오전", "AM").replace("오후", "PM")

                    # 정규식으로 날짜 시간 추출
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
                except Exception as e:
                    print(f"[DEBUG] 한국어 날짜 파싱 실패: {str_value}, 오류: {str(e)}")

            # 일반적인 날짜 형식 시도
            try:
                return pd.to_datetime(str_value)
            except:
                # 마지막 시도: 날짜 부분만 추출
                import re

                date_match = re.search(r"(\d{4}-\d{2}-\d{2})", str_value)
                if date_match:
                    return pd.to_datetime(date_match.group(1))

                return datetime.now()

        except Exception as e:
            print(f"[ERROR] 날짜 파싱 오류: {value}, 오류: {str(e)}")
            return datetime.now()

    # ✅ 4단계: 개인정보 암호화 데이터 처리 로직 수정 (회차별 날짜 계산 포함)
    def _process_file_encryption_data(self, df, uploaded_by):
        """개인정보 파일 암호화 데이터 처리 - 회차별 날짜 계산 포함 (수정된 버전)"""
        processed_data = []

        # 업로드 날짜 (현재 시점)
        upload_date = datetime.now()

        print(f"[DEBUG] === 개인정보 암호화 처리 시작 ===")
        print(f"[DEBUG] 총 데이터프레임 행 수: {len(df)}")
        print(f"[DEBUG] 컬럼명: {list(df.columns)}")

        # 로컬 IP 컬럼 찾기
        local_ip_col = self._find_local_ip_column(df.columns)
        if not local_ip_col:
            raise ValueError("로컬 IP 컬럼을 찾을 수 없습니다.")
        print(f"[DEBUG] 로컬 IP 컬럼: {local_ip_col}")

        # 회차별 주민등록번호 컬럼 감지
        round_columns = self._detect_round_columns(df.columns)
        if not round_columns:
            raise ValueError("회차별 주민등록번호 컬럼을 찾을 수 없습니다.")
        print(f"[DEBUG] 감지된 회차 컬럼: {round_columns}")

        # ✅ 최신 회차 번호 찾기 (가장 큰 회차 번호)
        latest_round_number = max(round_info["round"] for round_info in round_columns)
        print(f"[DEBUG] 감지된 최신 회차: {latest_round_number}")

        # 사용자명, 소속 컬럼 찾기
        username_col = self._find_username_column(df.columns)
        department_col = self._find_department_column(df.columns)
        print(f"[DEBUG] 사용자명 컬럼: {username_col}")
        print(f"[DEBUG] 부서 컬럼: {department_col}")

        # ✅ 개선된 데이터 행 판단 로직
        valid_data_rows = 0
        for idx, row in df.iterrows():
            print(f"[DEBUG] === 행 {idx+1} 처리 시작 ===")

            # IP 주소가 있는지 확인하여 실제 데이터 행인지 판단
            ip_address = ""
            if local_ip_col and pd.notna(row[local_ip_col]):
                ip_address = str(row[local_ip_col]).strip()

            print(f"[DEBUG] 행 {idx+1} IP 주소: '{ip_address}'")

            # IP 주소가 없거나 유효하지 않으면 헤더 행으로 간주
            if not ip_address or ip_address in ["", "nan", "None"]:
                print(f"[DEBUG] 행 {idx+1}: IP 주소가 없어 헤더 행으로 건너뜀")
                continue

            # 유효한 IP 형식인지 간단 체크 (숫자와 점으로 구성)
            import re

            if not re.match(r"^[\d\.]+$", ip_address):
                print(f"[DEBUG] 행 {idx+1}: 유효하지 않은 IP 형식으로 건너뜀")
                continue

            valid_data_rows += 1
            print(f"[DEBUG] 유효한 데이터 행 #{valid_data_rows}")

            try:
                # 사용자명 추출
                username = ""
                if username_col and pd.notna(row[username_col]):
                    username = str(row[username_col]).strip()

                # 소속/부서 추출
                department = ""
                if department_col and pd.notna(row[department_col]):
                    department = str(row[department_col]).strip()

                print(
                    f"[DEBUG] 행 {idx+1} 사용자 정보: 이름='{username}', 부서='{department}'"
                )

                # ✅ 회차별 주민등록번호 확인 및 최신 회차 기준 날짜 계산
                ssn_found = False
                latest_round_with_ssn = None
                latest_round_ssn_count = 0

                print(f"[DEBUG] 행 {idx+1} 회차별 SSN 검사 시작")

                # 최신 회차부터 역순으로 검사
                sorted_rounds = sorted(
                    round_columns, key=lambda x: x["round"], reverse=True
                )

                for round_info in sorted_rounds:
                    round_col = round_info["column"]
                    round_num = round_info["round"]

                    if pd.notna(row[round_col]):
                        ssn_value = row[round_col]
                        print(
                            f"[DEBUG] 행 {idx+1} {round_num}회차 값: '{ssn_value}' (타입: {type(ssn_value)})"
                        )

                        # 숫자 형태의 SSN 개수
                        if isinstance(ssn_value, (int, float)) and ssn_value > 0:
                            if (
                                latest_round_with_ssn is None
                            ):  # 첫 번째로 발견된 것이 최신
                                ssn_found = True
                                latest_round_with_ssn = round_num
                                latest_round_ssn_count = int(ssn_value)
                                print(
                                    f"[DEBUG] 행 {idx+1} {round_num}회차에서 SSN 발견: {latest_round_ssn_count}건"
                                )

                        # 문자열 형태의 SSN (-, 0 제외)
                        elif isinstance(ssn_value, str) and ssn_value.strip() not in [
                            "-",
                            "",
                            "0",
                        ]:
                            if latest_round_with_ssn is None:
                                ssn_found = True
                                latest_round_with_ssn = round_num
                                try:
                                    latest_round_ssn_count = int(float(ssn_value))
                                except:
                                    latest_round_ssn_count = 1
                                print(
                                    f"[DEBUG] 행 {idx+1} {round_num}회차에서 SSN 발견: {latest_round_ssn_count}건"
                                )

                # ✅ 최신 회차 정보를 기반으로 대표 날짜 계산
                if latest_round_with_ssn:
                    representative_date = self._calculate_round_date(
                        upload_date, latest_round_with_ssn, latest_round_number
                    )
                else:
                    # SSN이 없으면 최신 회차 날짜 사용
                    representative_date = self._calculate_round_date(
                        upload_date, latest_round_number, latest_round_number
                    )

                print(f"[DEBUG] 행 {idx+1} 대표 날짜: {representative_date}")

                # ✅ 계산된 날짜를 기반으로 적절한 기간 찾기
                period_id, period_name = self._find_appropriate_period(
                    representative_date, "file_encryption"
                )
                print(
                    f"[DEBUG] 행 {idx+1} 매칭된 기간: {period_name} (ID: {period_id})"
                )

                # 암호화 상태 결정
                if ssn_found and latest_round_with_ssn:
                    encryption_status = "not_encrypted"
                    overall_result = "fail"
                    notes = f"검증 결과: {latest_round_with_ssn}회차: {latest_round_ssn_count}건 - 최신 회차에서 주민등록번호 발견으로 실패"
                else:
                    encryption_status = "fully_encrypted"
                    overall_result = "pass"
                    notes = f"검증 결과: 모든 회차에서 주민등록번호 미발견으로 통과"

                print(f"[DEBUG] 행 {idx+1} 처리 완료 - 결과: {overall_result}")

                processed_row = {
                    "check_item_code": "file_encryption",
                    "source_ip": ip_address,
                    "check_year": representative_date.year,
                    "check_period": period_name,
                    "period_id": period_id,
                    "check_date": representative_date,
                    "checker_name": uploaded_by,
                    "encryption_status": encryption_status,
                    "unencrypted_files": latest_round_ssn_count,
                    "encryption_completed": 0 if ssn_found else 1,
                    "round_number": latest_round_with_ssn or latest_round_number,
                    "ssn_included": 1 if ssn_found else 0,
                    "overall_result": overall_result,
                    "notes": notes,
                    "username": username,
                    "department": department,
                    "row_index": idx + 1,
                }

                processed_data.append(processed_row)
                print(f"[DEBUG] === 행 {idx+1} 처리 완료 ===")

            except Exception as e:
                print(f"개인정보 파일 암호화 데이터 처리 오류 (행 {idx + 1}): {str(e)}")
                continue

        print(f"[DEBUG] === 개인정보 암호화 처리 완료 ===")
        print(f"[DEBUG] 총 처리된 데이터 행: {valid_data_rows}")
        print(f"[DEBUG] 생성된 processed_data: {len(processed_data)}개")

        return processed_data

    # 데이터 처리 통합 함수
    def _process_check_data(self, df, check_type, uploaded_by):
        """점검 유형에 따른 데이터 처리 분기"""
        if check_type == "seal_check":
            return self._process_seal_check_data(df, uploaded_by)
        elif check_type == "malware_scan":
            return self._process_malware_scan_data(df, uploaded_by)
        elif check_type == "file_encryption":
            return self._process_file_encryption_data(df, uploaded_by)
        else:
            raise ValueError(f"지원하지 않는 점검 유형: {check_type}")

    # 기존 함수들 - 개인정보 암호화 관련 분석 (기존 로직 유지)
    def _analyze_encryption_file(self, df):
        """개인정보 암호화 파일 분석 - 회차별 검증 로직"""
        analysis_result = {
            "total_violations": 0,
            "round_violations": {},
            "latest_round_analysis": None,
            "overall_result": "pass",
            "detailed_notes": "",
        }

        try:
            # 로컬 IP 컬럼 찾기
            local_ip_col = self._find_local_ip_column(df.columns)
            if not local_ip_col:
                raise ValueError("로컬 IP 컬럼을 찾을 수 없습니다.")

            # 회차별 주민등록번호 컬럼 감지
            round_columns = self._detect_round_columns(df.columns)
            if not round_columns:
                raise ValueError("회차별 주민등록번호 컬럼을 찾을 수 없습니다.")

            # 각 사용자별로 분석
            for idx, row in df.iterrows():
                if idx < 2:  # 헤더 행 건너뛰기
                    continue

                ip_address = (
                    str(row[local_ip_col]) if pd.notna(row[local_ip_col]) else ""
                )
                if not ip_address:
                    continue

                # 회차별 주민등록번호 확인
                for round_info in round_columns:
                    round_col = round_info["column"]
                    round_num = round_info["round"]

                    if pd.notna(row[round_col]):
                        ssn_value = row[round_col]

                        # 값 분석
                        if isinstance(ssn_value, (int, float)) and ssn_value > 0:
                            # 숫자형 SSN 개수
                            ssn_count = int(ssn_value)
                            if round_num not in analysis_result["round_violations"]:
                                analysis_result["round_violations"][round_num] = 0
                            analysis_result["round_violations"][round_num] += ssn_count
                            analysis_result["total_violations"] += ssn_count

                        elif isinstance(ssn_value, str) and ssn_value.strip() not in [
                            "-",
                            "",
                            "0",
                        ]:
                            # 문자열형 SSN (숫자 변환 시도)
                            try:
                                ssn_count = int(float(ssn_value))
                                if round_num not in analysis_result["round_violations"]:
                                    analysis_result["round_violations"][round_num] = 0
                                analysis_result["round_violations"][
                                    round_num
                                ] += ssn_count
                                analysis_result["total_violations"] += ssn_count
                            except:
                                # 변환 실패 시 1건으로 처리
                                if round_num not in analysis_result["round_violations"]:
                                    analysis_result["round_violations"][round_num] = 0
                                analysis_result["round_violations"][round_num] += 1
                                analysis_result["total_violations"] += 1

            # 최신 회차 분석 (가장 큰 회차 번호)
            if round_columns:
                latest_round = max(round_info["round"] for round_info in round_columns)
                latest_violations = analysis_result["round_violations"].get(
                    latest_round, 0
                )

                analysis_result["latest_round_analysis"] = {
                    "round": latest_round,
                    "violations": latest_violations,
                }

                # 전체 결과 판정
                if latest_violations > 0:
                    analysis_result["overall_result"] = "fail"
                    analysis_result["detailed_notes"] = (
                        f"최신 회차({latest_round}회차)에서 {latest_violations}건의 주민등록번호 발견"
                    )
                else:
                    analysis_result["overall_result"] = "pass"
                    analysis_result["detailed_notes"] = (
                        f"최신 회차({latest_round}회차)에서 주민등록번호 미발견"
                    )

            return analysis_result

        except Exception as e:
            print(f"개인정보 암호화 파일 분석 오류: {str(e)}")
            return {
                "error": str(e),
                "overall_result": "error",
                "total_violations": 0,
                "round_violations": {},
            }

    def _save_to_existing_table(self, processed_data, check_type, uploaded_by):
        """기존 manual_check_results 테이블에 저장 - 상세 디버그 추가"""
        success_count = 0
        error_count = 0
        update_count = 0
        errors = []

        print(f"[DEBUG] 저장 시작 - 총 {len(processed_data)}개 데이터 처리 예정")

        for i, data in enumerate(processed_data):
            try:
                print(f"[DEBUG] === 데이터 {i+1}/{len(processed_data)} 처리 시작 ===")
                print(
                    f"[DEBUG] 데이터 내용: 사용자명={data.get('username')}, IP={data.get('source_ip')}, 기간={data.get('check_period')}"
                )

                # 사용자 정보 조회 (IP나 이름으로)
                user_id = self._find_user_id(data, check_type)
                if not user_id:
                    error_count += 1
                    error_msg = f"행 {data.get('row_index', '?')}: 사용자를 찾을 수 없습니다 (사용자명: {data.get('username')}, IP: {data.get('source_ip')})"
                    errors.append(error_msg)
                    print(f"[DEBUG] {error_msg}")
                    continue

                print(f"[DEBUG] 사용자 ID 찾음: {user_id}")

                # ✅ 중복 체크: 동일한 사용자, 점검유형, 연도, 기간의 결과가 있는지 확인
                existing_check = execute_query(
                    """
                    SELECT check_id FROM manual_check_results 
                    WHERE user_id = %s AND check_item_code = %s AND check_year = %s AND check_period = %s
                    ORDER BY created_at DESC LIMIT 1
                    """,
                    (
                        user_id,
                        data.get("check_item_code"),
                        data.get("check_year"),
                        data.get("check_period"),
                    ),
                    fetch_one=True,
                )

                if existing_check:
                    print(
                        f"[DEBUG] 기존 데이터 발견 - check_id: {existing_check['check_id']}, 업데이트 진행"
                    )

                    # ✅ 기존 결과가 있으면 업데이트
                    update_query = """
                        UPDATE manual_check_results SET
                            source_ip = %s,
                            check_date = %s,
                            checker_name = %s,
                            period_id = %s,
                            seal_status = %s,
                            seal_notes = %s,
                            malware_scan_result = %s,
                            threats_found = %s,
                            threats_cleaned = %s,
                            malware_name = %s,
                            malware_classification = %s,
                            malware_path = %s,
                            detection_item = %s,
                            malware_notes = %s,
                            encryption_status = %s,
                            unencrypted_files = %s,
                            encryption_completed = %s,
                            round_number = %s,
                            ssn_included = %s,
                            overall_result = %s,
                            notes = %s,
                            updated_at = NOW()
                        WHERE check_id = %s
                    """

                    update_data = (
                        data.get("source_ip"),
                        data.get("check_date"),
                        data.get("checker_name"),
                        data.get("period_id"),
                        # 봉인씰 관련
                        data.get("seal_status"),
                        data.get("seal_notes"),
                        # 악성코드 관련
                        data.get("malware_scan_result"),
                        data.get("threats_found", 0),
                        data.get("threats_cleaned", 0),
                        data.get("malware_name"),
                        data.get("malware_classification"),
                        data.get("malware_path"),
                        data.get("detection_item"),
                        data.get("malware_notes"),
                        # 암호화 관련
                        data.get("encryption_status"),
                        data.get("unencrypted_files", 0),
                        data.get("encryption_completed", 0),
                        data.get("round_number", 0),
                        data.get("ssn_included", 0),
                        # 공통
                        data.get("overall_result"),
                        data.get("notes"),
                        # WHERE 조건
                        existing_check["check_id"],
                    )

                    result = execute_query(update_query, update_data)
                    update_count += 1
                    print(
                        f"[DEBUG] 업데이트 완료 - 행 {data.get('row_index')}: "
                        f"사용자 {user_id}, 기간 {data.get('check_period')}({data.get('period_id')})"
                    )

                else:
                    print(f"[DEBUG] 기존 데이터 없음 - 신규 삽입 진행")

                    # ✅ 기존 결과가 없으면 새로 삽입
                    insert_query = """
                        INSERT INTO manual_check_results (
                            user_id, check_item_code, source_ip, check_year, check_period, 
                            check_date, checker_name, period_id, 
                            seal_status, seal_notes, 
                            malware_scan_result, threats_found, threats_cleaned, 
                            malware_name, malware_classification, malware_path, 
                            detection_item, malware_notes,
                            encryption_status, unencrypted_files, encryption_completed, 
                            round_number, ssn_included,
                            overall_result, notes, created_at, updated_at
                        ) VALUES (
                            %s, %s, %s, %s, %s, %s, %s, %s, 
                            %s, %s, 
                            %s, %s, %s, 
                            %s, %s, %s, 
                            %s, %s,
                            %s, %s, %s, 
                            %s, %s,
                            %s, %s, NOW(), NOW()
                        )
                    """

                    insert_data = (
                        user_id,
                        data.get("check_item_code"),
                        data.get("source_ip"),
                        data.get("check_year"),
                        data.get("check_period"),
                        data.get("check_date"),
                        data.get("checker_name"),
                        data.get("period_id"),
                        # 봉인씰 관련
                        data.get("seal_status"),
                        data.get("seal_notes"),
                        # 악성코드 관련
                        data.get("malware_scan_result"),
                        data.get("threats_found", 0),
                        data.get("threats_cleaned", 0),
                        data.get("malware_name"),
                        data.get("malware_classification"),
                        data.get("malware_path"),
                        data.get("detection_item"),
                        data.get("malware_notes"),
                        # 암호화 관련
                        data.get("encryption_status"),
                        data.get("unencrypted_files", 0),
                        data.get("encryption_completed", 0),
                        data.get("round_number", 0),
                        data.get("ssn_included", 0),
                        # 공통
                        data.get("overall_result"),
                        data.get("notes"),
                    )

                    print(f"[DEBUG] INSERT 데이터: {insert_data}")
                    result = execute_query(insert_query, insert_data)
                    success_count += 1
                    print(
                        f"[DEBUG] 신규 저장 완료 - 행 {data.get('row_index')}: "
                        f"사용자 {user_id}, 기간 {data.get('check_period')}({data.get('period_id')})"
                    )

                print(f"[DEBUG] === 데이터 {i+1} 처리 완료 ===")

            except Exception as e:
                error_count += 1
                error_msg = f"행 {data.get('row_index', '?')}: {str(e)}"
                errors.append(error_msg)
                print(f"[ERROR] 저장 실패 - {error_msg}")
                import traceback

                traceback.print_exc()

        print(
            f"[DEBUG] 저장 완료 - 성공: {success_count}, 업데이트: {update_count}, 오류: {error_count}"
        )

        return {
            "success_count": success_count,
            "update_count": update_count,
            "error_count": error_count,
            "errors": errors[:10],  # 최대 10개 오류만 반환
        }

    # 업로드 결과 메시지도 수정

    # ✅ 메인 업로드 처리 함수에도 디버그 추가
    def process_bulk_upload(self, file, uploaded_by):
        """엑셀/CSV 파일 일괄 업로드 처리 - 디버그 강화"""
        try:
            filename = file.filename
            print(f"[DEBUG] 업로드 시작 - 파일명: {filename}, 업로더: {uploaded_by}")

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

            print(f"[DEBUG] 파일 읽기 완료 - 총 {len(df)}행, 컬럼: {list(df.columns)}")

            # 점검 유형 자동 감지
            check_type = self.detect_file_type(df, filename)
            if not check_type:
                raise ValueError(
                    "점검 유형을 자동으로 감지할 수 없습니다. 파일명이나 컬럼을 확인해주세요."
                )

            print(f"[DEBUG] 점검 유형 감지 완료: {check_type}")

            # 파일 구조 검증
            is_valid, message = self.validate_file_structure(df, check_type)
            if not is_valid:
                raise ValueError(message)

            print(f"[DEBUG] 파일 구조 검증 완료: {message}")

            # 데이터 처리
            processed_data = self._process_check_data(df, check_type, uploaded_by)
            print(f"[DEBUG] 데이터 처리 완료 - {len(processed_data)}개 데이터 생성")

            # 처리된 데이터 중 일부 샘플 출력
            for i, data in enumerate(processed_data[:2]):  # 처음 2개만
                print(
                    f"[DEBUG] 샘플 데이터 {i+1}: 사용자={data.get('username')}, IP={data.get('source_ip')}, 기간={data.get('check_period')}"
                )

            # 데이터베이스 저장 (중복 체크 및 업데이트)
            save_result = self._save_to_existing_table(
                processed_data, check_type, uploaded_by
            )

            # ✅ 결과 메시지 개선
            total_processed = save_result["success_count"] + save_result["update_count"]

            if save_result["update_count"] > 0:
                message = f"{self.get_check_type_name(check_type)} 업로드 완료 (신규: {save_result['success_count']}건, 업데이트: {save_result['update_count']}건)"
            else:
                message = f"{self.get_check_type_name(check_type)} 업로드 완료"

            print(f"[DEBUG] 최종 결과: {message}")

            return {
                "success": True,
                "message": message,
                "file_type": self.get_check_type_name(check_type),
                "total_records": len(processed_data),
                "success_count": save_result["success_count"],
                "update_count": save_result["update_count"],
                "error_count": save_result["error_count"],
                "errors": save_result["errors"],
            }

        except Exception as e:
            print(f"파일 업로드 처리 오류: {str(e)}")
            import traceback

            traceback.print_exc()
            raise ValueError(f"파일 처리 중 오류가 발생했습니다: {str(e)}")

    # 기타 유틸리티 함수들
    def get_check_type_name(self, check_type):
        """점검 유형명 반환"""
        type_names = {
            "file_encryption": "개인정보 파일 암호화 (회차별 검증)",
            "seal_check": "PC 봉인씰 확인",
            "malware_scan": "악성코드 전체 검사",
        }
        return type_names.get(check_type, check_type)

    def get_check_types(self):
        """지원되는 점검 유형 목록 반환 (period_service와 일관성 유지)"""
        return {
            "seal_check": "PC 봉인씰 확인",
            "malware_scan": "악성코드 전체 검사",
            "file_encryption": "개인정보 파일 암호화",
        }

    def get_check_type_mapping(self):
        """점검 유형 매핑 정보 반환 - 개인정보 암호화 설명 업데이트"""
        return {
            "file_encryption": "개인정보 파일 암호화 (회차별)",
            "seal_check": "PC 봉인씰 확인",
            "malware_scan": "악성코드 전체 검사",
        }

    # 템플릿 생성 함수들
    def get_excel_template(self):
        """엑셀 업로드용 템플릿 생성"""
        template_data = [
            "사용자ID,사용자명,부서,점검연도,점검기간,점검일시,점검자명,봉인씰상태,봉인번호,봉인씰비고,악성코드검사결과,발견위협수,치료완료여부,백신버전,악성코드비고,암호화상태,검사파일수,미암호화파일수,암호화완료여부,암호화비고,종합결과,전체비고",
            "admin,관리자,IT팀,2025,상반기,2025-06-10 14:30:00,김점검,정상,SEAL-2025-001,정상 상태 확인,정상,0,Y,V3 2025.06.10,검사 완료,완전암호화,15,0,Y,모든 파일 암호화 완료,통과,모든 항목 정상",
            "user1,홍길동,개발팀,2025,상반기,2025-06-10 15:00:00,김점검,손상,SEAL-2025-002,봉인씰 교체 필요,정상,0,Y,V3 2025.06.10,검사 완료,부분암호화,20,3,N,3개 파일 암호화 필요,부분통과,봉인씰 교체 및 암호화 조치 필요",
        ]
        return "\n".join(template_data)

    def generate_file_encryption_template(self):
        """개인정보 파일 암호화 템플릿 생성 - 회차별 설명 포함"""
        template_content = """# 개인정보 파일 암호화 점검 템플릿

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

    def generate_malware_scan_template(self):
        """악성코드 전체 검사 템플릿 생성 - 일시 컬럼 포함"""
        template_data = [
            "일시,IP,사용자명,악성코드명,악성코드 분류,경로,탐지 항목",
            "2025-06-13 14:30:00,192.168.1.100,홍길동,,,C:\\Users\\user1,",
            "2025-06-13 14:35:00,192.168.1.101,김철수,Trojan.Generic,트로이목마,C:\\Users\\user2,virus.exe",
            "2025-06-13 14:40:00,192.168.1.102,이영희,,,C:\\Users\\user3,",
        ]
        return "\n".join(template_data)

    # 기존 호출 방식과 호환되는 get_check_results 함수
    def get_check_results(
        self,
        year=None,
        check_type=None,
        result_filter=None,
        search=None,
        page=1,
        size=20,
    ):
        """점검 결과 목록 조회 - 기존 호출 방식 호환"""
        if year is None:
            year = datetime.now().year

        try:
            print(f"[DEBUG] 점검 결과 조회 시작: year={year}, check_type={check_type}")

            # 기본 쿼리 구성 - period 정보도 JOIN해서 가져오기
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
                    u.mail as email,
                    mcp.period_name as actual_period_name,
                    mcp.period_year as actual_period_year
                FROM manual_check_results mcr
                LEFT JOIN users u ON mcr.user_id = u.uid
                LEFT JOIN manual_check_periods mcp ON mcr.period_id = mcp.period_id
                WHERE mcr.check_year = %s
            """

            params = [year]

            # 검색 조건 추가
            if check_type:
                base_query += " AND mcr.check_item_code = %s"
                params.append(check_type)

            if result_filter:
                base_query += " AND mcr.overall_result = %s"
                params.append(result_filter)

            if search:
                base_query += " AND (u.username LIKE %s OR u.department LIKE %s OR mcr.notes LIKE %s)"
                search_param = f"%{search}%"
                params.extend([search_param, search_param, search_param])

            # 전체 개수 조회
            count_query = base_query.replace(
                "SELECT mcr.check_id, mcr.user_id, mcr.check_item_code, mcr.source_ip, mcr.check_year, mcr.check_period, mcr.check_date, mcr.checker_name, mcr.overall_result, mcr.total_score, mcr.notes, mcr.period_id, mcr.created_at, u.user_id as user_login_id, u.username, u.department, u.mail as email, mcp.period_name as actual_period_name, mcp.period_year as actual_period_year",
                "SELECT COUNT(*)",
            )

            total = execute_query(count_query, params, fetch_one=True)
            total_count = (
                total[0] if isinstance(total, tuple) else total.get("COUNT(*)", 0)
            )

            # 실제 데이터 조회 (페이지네이션 적용)
            base_query += " ORDER BY mcr.created_at DESC LIMIT %s OFFSET %s"
            params.extend([size, (page - 1) * size])

            results = execute_query(base_query, params)

            print(f"[DEBUG] 조회된 결과 수: {len(results)}")

            processed_results = []
            for i, result in enumerate(results):
                try:
                    processed_result = dict(result)

                    # 날짜 처리
                    if processed_result.get("check_date"):
                        if hasattr(processed_result["check_date"], "strftime"):
                            processed_result["check_date"] = processed_result[
                                "check_date"
                            ].strftime("%Y-%m-%d")
                        else:
                            processed_result["check_date"] = str(
                                processed_result["check_date"]
                            )

                    if processed_result.get("created_at"):
                        if hasattr(processed_result["created_at"], "strftime"):
                            processed_result["created_at"] = processed_result[
                                "created_at"
                            ].strftime("%Y-%m-%d %H:%M:%S")
                        else:
                            processed_result["created_at"] = str(
                                processed_result["created_at"]
                            )

                    # ✅ 수정된 기간명 생성 로직
                    if processed_result.get("actual_period_name"):
                        # manual_check_periods 테이블의 실제 데이터 사용
                        processed_result["period_name"] = processed_result[
                            "actual_period_name"
                        ]
                    else:
                        # period_id가 없거나 매칭되지 않는 경우 기본 로직
                        check_period = processed_result.get("check_period", "")
                        if check_period == "auto_complete":
                            period_name = "자동완료"
                        elif check_period == "first_half":
                            period_name = "상반기"
                        elif check_period == "second_half":
                            period_name = "하반기"
                        elif check_period and check_period not in ["auto_complete"]:
                            period_name = check_period
                        else:
                            period_name = "미설정"
                        processed_result["period_name"] = period_name

                    # None 값들을 안전하게 처리
                    for key, value in processed_result.items():
                        if value is None:
                            processed_result[key] = ""

                    processed_results.append(processed_result)
                    print(
                        f"[DEBUG] 결과 {i} 처리 완료 - 기간명: {processed_result['period_name']}"
                    )

                except Exception as e:
                    print(f"[DEBUG] 결과 {i} 처리 중 오류: {str(e)}")
                    continue

            # 페이지네이션 정보 계산
            total_pages = (total_count + size - 1) // size if total_count > 0 else 1

            result_data = {
                "results": processed_results,
                "total": total_count,
                "page": page,
                "size": size,
                "total_pages": total_pages,
            }

            print(
                f"[DEBUG] 최종 결과 반환: {len(processed_results)}개 결과, 총 {total_count}개"
            )
            return result_data

        except Exception as e:
            print(f"[DEBUG] 점검 결과 조회 실패: {str(e)}")
            import traceback

            traceback.print_exc()
            raise ValueError(f"점검 결과 조회 실패: {str(e)}")

    # 새로운 함수는 기존 함수를 래핑하는 방식으로 구현
    def get_results(
        self, year=None, check_type=None, period=None, user_id=None, page=1, size=20
    ):
        """수시 점검 결과 조회 - 새로운 방식 (기존 함수 래핑)"""
        return self.get_check_results(
            year=year,
            check_type=check_type,
            result_filter=period,
            search=None,
            page=page,
            size=size,
        )

    # CSV 내보내기 함수
    def export_results_to_csv(self, year=None, check_type=None, period=None):
        """결과를 CSV로 내보내기"""
        try:
            # 모든 결과 조회 (페이지네이션 없이)
            results_data = self.get_results(
                year=year, check_type=check_type, period=period, page=1, size=10000
            )

            if not results_data["success"]:
                raise ValueError("결과 조회 실패")

            results = results_data["data"]
            if not results:
                return ""

            # CSV 헤더
            headers = [
                "점검ID",
                "사용자ID",
                "사용자명",
                "부서",
                "점검유형",
                "점검연도",
                "점검기간",
                "점검일시",
                "점검자",
                "결과",
                "비고",
                "생성일시",
            ]

            # CSV 데이터 생성
            csv_lines = [",".join(headers)]

            for result in results:
                # 점검 유형 한글명 변환
                check_type_korean = {
                    "seal_check": "PC 봉인씰 확인",
                    "malware_scan": "악성코드 전체 검사",
                    "file_encryption": "개인정보 파일 암호화",
                }.get(result.get("check_type", ""), result.get("check_type", ""))

                # 결과 한글명 변환
                result_korean = {
                    "pass": "통과",
                    "fail": "실패",
                    "partial": "부분통과",
                }.get(result.get("check_result", ""), result.get("check_result", ""))

                row = [
                    str(result.get("result_id", "")),
                    str(result.get("user_login_id", "")),
                    str(result.get("username", "")),
                    str(result.get("department", "")),
                    check_type_korean,
                    str(result.get("check_year", "")),
                    str(result.get("period_name", "")),  # ✅ 실제 기간명 사용
                    str(result.get("check_date", "")),
                    str(result.get("checker_name", "")),
                    result_korean,
                    str(result.get("notes", "")),
                    str(result.get("created_at", "")),
                ]

                escaped_row = []
                for item in row:
                    escaped_item = '"' + str(item).replace('"', '""') + '"'
                    escaped_row.append(escaped_item)

                csv_lines.append(",".join(escaped_row))

            return "\n".join(csv_lines)

        except Exception as e:
            print(f"CSV 내보내기 오류: {str(e)}")
            raise ValueError(f"CSV 내보내기 실패: {str(e)}")

    # 기타 분석 함수들
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
                    return {
                        "total_records": total_records,
                        "expected_pass": 0,
                        "expected_fail": 0,
                        "analysis_details": analysis_details,
                    }

                local_ip_col = self._find_local_ip_column(df.columns)
                if not local_ip_col:
                    return {
                        "total_records": total_records,
                        "expected_pass": 0,
                        "expected_fail": 0,
                        "analysis_details": ["로컬 IP 컬럼을 찾을 수 없습니다."],
                    }

                # 데이터 행별 분석
                data_rows = 0
                for idx, row in df.iterrows():
                    if idx < 2:  # 헤더 행 건너뛰기
                        continue

                    ip_address = (
                        str(row[local_ip_col]) if pd.notna(row[local_ip_col]) else ""
                    )
                    if not ip_address:
                        continue

                    data_rows += 1

                    # 회차별 주민등록번호 확인
                    has_violations = False
                    latest_round = max(
                        round_info["round"] for round_info in round_columns
                    )

                    for round_info in round_columns:
                        round_col = round_info["column"]
                        round_num = round_info["round"]

                        if pd.notna(row[round_col]):
                            ssn_value = row[round_col]

                            # 최신 회차에서 위반 사항 확인
                            if round_num == latest_round:
                                if (
                                    isinstance(ssn_value, (int, float))
                                    and ssn_value > 0
                                ):
                                    has_violations = True
                                elif isinstance(
                                    ssn_value, str
                                ) and ssn_value.strip() not in ["-", "", "0"]:
                                    has_violations = True
                                break

                    if has_violations:
                        expected_fail += 1
                    else:
                        expected_pass += 1

                analysis_details.append(f"총 {data_rows}개 IP 주소 분석 완료")
                analysis_details.append(f"최신 회차({latest_round}회차) 기준으로 판정")

            elif check_type == "seal_check":
                # 봉인씰 분석
                col_mapping = self._find_column_mapping(
                    df.columns, {"damage_status": ["훼손여부", "상태", "봉인상태"]}
                )

                if not col_mapping["damage_status"]:
                    return {
                        "total_records": total_records,
                        "expected_pass": 0,
                        "expected_fail": 0,
                        "analysis_details": ["훼손여부 컬럼을 찾을 수 없습니다."],
                    }

                for idx, row in df.iterrows():
                    damage_value = row[col_mapping["damage_status"]]
                    if pd.notna(damage_value):
                        damage_status = str(damage_value).strip()
                        if "훼손" in damage_status:
                            expected_fail += 1
                        else:
                            expected_pass += 1

                analysis_details.append("훼손여부 컬럼 기준으로 분석")

            elif check_type == "malware_scan":
                # 악성코드 분석
                col_mapping = self._find_column_mapping(
                    df.columns, {"detection_item": ["탐지 항목", "탐지항목", "탐지"]}
                )

                if not col_mapping["detection_item"]:
                    return {
                        "total_records": total_records,
                        "expected_pass": 0,
                        "expected_fail": 0,
                        "analysis_details": ["탐지 항목 컬럼을 찾을 수 없습니다."],
                    }

                for idx, row in df.iterrows():
                    detection_value = row[col_mapping["detection_item"]]
                    if pd.notna(detection_value):
                        detection_item = str(detection_value).strip()
                        if detection_item:
                            expected_fail += 1
                        else:
                            expected_pass += 1

                analysis_details.append("탐지 항목 컬럼 기준으로 분석")

            return {
                "total_records": total_records,
                "expected_pass": expected_pass,
                "expected_fail": expected_fail,
                "analysis_details": analysis_details,
            }

        except Exception as e:
            return {
                "total_records": 0,
                "expected_pass": 0,
                "expected_fail": 0,
                "analysis_details": [f"분석 중 오류 발생: {str(e)}"],
            }

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
