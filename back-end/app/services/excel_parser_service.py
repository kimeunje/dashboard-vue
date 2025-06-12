# app/services/excel_parser_service.py
import pandas as pd
import re
from datetime import datetime
from typing import Dict, List, Tuple, Any
from app.utils.database import execute_query


class ExcelParserService:
    """엑셀 파일 파싱 서비스"""

    def __init__(self):
        self.supported_types = ['malware_scan', 'seal_check', 'file_encryption']

    def detect_file_type(self, df: pd.DataFrame) -> str:
        """엑셀 파일 유형 자동 감지"""
        columns = [col.lower() for col in df.columns]

        # 악성코드 전체 검사 파일 감지
        malware_keywords = ['악성코드명', '악성코드 분류', '탐지 항목', '경로']
        if any(keyword in ' '.join(columns) for keyword in malware_keywords):
            return 'malware_scan'

        # PC 봉인씰 확인 파일 감지
        seal_keywords = ['봉인씰 확인', '이름', '부서']
        if any(keyword in ' '.join(columns) for keyword in seal_keywords):
            return 'seal_check'

        # 개인정보 파일 암호화 파일 감지
        encryption_keywords = ['회차', '주민등록번호', '로컬 ip']
        if any(keyword in ' '.join(columns) for keyword in encryption_keywords):
            return 'file_encryption'

        raise ValueError("지원되지 않는 파일 형식입니다. 올바른 점검 결과 파일을 업로드해주세요.")

    def parse_excel_file(self, file_path: str,
                         file_type: str = None) -> Tuple[str, List[Dict]]:
        """엑셀 파일 파싱"""
        try:
            # 엑셀 파일 읽기
            df = pd.read_excel(file_path)

            # 파일 유형 자동 감지 (지정되지 않은 경우)
            if not file_type:
                file_type = self.detect_file_type(df)

            # 유형별 파싱
            if file_type == 'malware_scan':
                return file_type, self._parse_malware_scan(df)
            elif file_type == 'seal_check':
                return file_type, self._parse_seal_check(df)
            elif file_type == 'file_encryption':
                return file_type, self._parse_file_encryption(df)
            else:
                raise ValueError(f"지원되지 않는 파일 유형: {file_type}")

        except Exception as e:
            raise ValueError(f"엑셀 파일 파싱 실패: {str(e)}")

    def _parse_malware_scan(self, df: pd.DataFrame) -> List[Dict]:
        """악성코드 전체 검사 파일 파싱"""
        results = []

        # 필요한 컬럼 찾기 (대소문자 무시하고 부분 매칭)
        column_mapping = self._find_columns(
            df, {
                'datetime': ['일시', 'date', 'time'],
                'ip': ['ip'],
                'malware_name': ['악성코드명', 'malware'],
                'classification': ['악성코드 분류', '분류', 'classification'],
                'path': ['경로', 'path'],
                'detection': ['탐지 항목', 'detection']
            })

        for _, row in df.iterrows():
            try:
                # 사용자 IP로 사용자 조회
                ip = str(
                    row[column_mapping['ip']]).strip() if column_mapping['ip'] else ''
                user_info = self._find_user_by_ip(ip)

                if not user_info:
                    continue  # IP로 사용자를 찾을 수 없으면 건너뛰기

                # 악성코드 탐지 여부 확인
                malware_name = str(row[column_mapping['malware_name']]).strip(
                ) if column_mapping['malware_name'] else ''
                has_malware = bool(malware_name and malware_name != 'nan'
                                   and malware_name != '')

                result_data = {
                    'user_id': user_info['uid'],
                    'check_item_code': 'malware_scan',
                    'source_ip': ip,
                    'check_date': self._parse_datetime(row[column_mapping['datetime']])
                    if column_mapping['datetime'] else datetime.now(),
                    'malware_scan_result': 'infected' if has_malware else 'clean',
                    'malware_name': malware_name if has_malware else None,
                    'malware_classification': str(
                        row[column_mapping['classification']]).strip()
                    if column_mapping['classification'] and has_malware else None,
                    'malware_path': str(row[column_mapping['path']]).strip()
                    if column_mapping['path'] and has_malware else None,
                    'detection_item': str(row[column_mapping['detection']]).strip()
                    if column_mapping['detection'] and has_malware else None,
                    'threats_found': 1 if has_malware else 0,
                    'overall_result': 'fail' if has_malware else 'pass',
                    'notes': f"악성코드 {'탐지됨' if has_malware else '없음'}"
                }

                results.append(result_data)

            except Exception as e:
                print(f"행 파싱 오류: {str(e)}")
                continue

        return results

    def _parse_seal_check(self, df: pd.DataFrame) -> List[Dict]:
        """PC 봉인씰 확인 파일 파싱"""
        results = []

        # 필요한 컬럼 찾기
        column_mapping = self._find_columns(
            df, {
                'datetime': ['일시', 'date', 'time'],
                'name': ['이름', 'name'],
                'department': ['부서', 'dept'],
                'seal_status': ['봉인씰 확인', '봉인씰', 'seal']
            })

        for _, row in df.iterrows():
            try:
                # 이름과 부서로 사용자 조회
                name = str(row[
                    column_mapping['name']]).strip() if column_mapping['name'] else ''
                dept = str(row[column_mapping['department']]).strip(
                ) if column_mapping['department'] else ''
                user_info = self._find_user_by_name_dept(name, dept)

                if not user_info:
                    continue  # 사용자를 찾을 수 없으면 건너뛰기

                # 봉인씰 상태 파싱
                seal_check_value = str(row[column_mapping['seal_status']]).strip(
                ) if column_mapping['seal_status'] else ''
                seal_status = self._parse_seal_status(seal_check_value)

                result_data = {
                    'user_id': user_info['uid'],
                    'check_item_code': 'seal_check',
                    'check_date': self._parse_datetime(row[column_mapping['datetime']])
                    if column_mapping['datetime'] else datetime.now(),
                    'seal_status': seal_status,
                    'overall_result': 'pass' if seal_status == 'normal' else 'fail',
                    'notes': f"PC 봉인씰 상태: {self._get_seal_status_korean(seal_status)}"
                }

                results.append(result_data)

            except Exception as e:
                print(f"행 파싱 오류: {str(e)}")
                continue

        return results

    def _parse_file_encryption(self, df: pd.DataFrame) -> List[Dict]:
        """개인정보 파일 암호화 파일 파싱"""
        results = []

        # 컬럼에서 최신 회차 찾기
        latest_round = self._find_latest_round(df.columns)
        if not latest_round:
            raise ValueError("회차 정보를 찾을 수 없습니다.")

        # 필요한 컬럼 찾기
        column_mapping = self._find_columns(
            df,
            {
                'ip': ['로컬 ip', 'local ip', 'ip'],
                'ssn_column': [f'{latest_round}회차']  # 최신 회차의 주민등록번호 컬럼
            })

        for _, row in df.iterrows():
            try:
                # IP로 사용자 조회
                ip = str(
                    row[column_mapping['ip']]).strip() if column_mapping['ip'] else ''
                user_info = self._find_user_by_ip(ip)

                if not user_info:
                    continue  # IP로 사용자를 찾을 수 없으면 건너뛰기

                # 주민등록번호 포함 여부 확인
                ssn_value = str(row[column_mapping['ssn_column']]).strip(
                ) if column_mapping['ssn_column'] else ''
                has_ssn = self._has_ssn_content(ssn_value)

                result_data = {
                    'user_id': user_info['uid'],
                    'check_item_code': 'file_encryption',
                    'source_ip': ip,
                    'check_date': datetime.now(),
                    'round_number': latest_round,
                    'ssn_included': 1 if has_ssn else 0,
                    'encryption_status': 'not_encrypted'
                    if has_ssn else 'fully_encrypted',
                    'overall_result': 'fail' if has_ssn else 'pass',
                    'notes': f"{latest_round}회차 개인정보 파일 암호화 {'미적용' if has_ssn else '적용됨'}"
                }

                results.append(result_data)

            except Exception as e:
                print(f"행 파싱 오류: {str(e)}")
                continue

        return results

    def _find_columns(self, df: pd.DataFrame,
                      column_specs: Dict[str, List[str]]) -> Dict[str, str]:
        """컬럼명 매칭"""
        column_mapping = {}
        df_columns = [col.lower() for col in df.columns]

        for key, keywords in column_specs.items():
            found_column = None
            for keyword in keywords:
                for i, col in enumerate(df_columns):
                    if keyword.lower() in col:
                        found_column = df.columns[i]
                        break
                if found_column:
                    break
            column_mapping[key] = found_column

        return column_mapping

    def _find_latest_round(self, columns: List[str]) -> str:
        """컬럼에서 최신 회차 찾기"""
        rounds = []
        for col in columns:
            # "161회차", "160회차" 등의 패턴 찾기
            match = re.search(r'(\d+)회차', col)
            if match:
                rounds.append(int(match.group(1)))

        return str(max(rounds)) if rounds else None

    def _find_user_by_ip(self, ip: str) -> Dict:
        """IP로 사용자 조회 (임시로 IP 매핑 테이블 필요할 수 있음)"""
        # 실제 구현시에는 IP-사용자 매핑 테이블이나 로직이 필요
        # 현재는 간단한 매핑으로 구현
        query = """
            SELECT uid, user_id, username, department 
            FROM users 
            WHERE user_id LIKE %s OR username LIKE %s
            LIMIT 1
        """
        # IP의 마지막 옥텟으로 사용자 추정 (임시 로직)
        ip_last = ip.split('.')[-1] if '.' in ip else ip
        return execute_query(query, [f"%{ip_last}%", f"%{ip_last}%"], fetch_one=True)

    def _find_user_by_name_dept(self, name: str, department: str) -> Dict:
        """이름과 부서로 사용자 조회"""
        query = """
            SELECT uid, user_id, username, department 
            FROM users 
            WHERE username = %s AND department LIKE %s
            LIMIT 1
        """
        return execute_query(query, [name, f"%{department}%"], fetch_one=True)

    def _parse_datetime(self, value) -> datetime:
        """날짜시간 파싱"""
        if pd.isna(value):
            return datetime.now()

        if isinstance(value, datetime):
            return value

        # 문자열인 경우 파싱 시도
        try:
            return pd.to_datetime(str(value))
        except:
            return datetime.now()

    def _parse_seal_status(self, value: str) -> str:
        """봉인씰 상태 파싱"""
        value = value.lower().strip()
        if any(keyword in value for keyword in ['정상', 'ok', 'normal', '양호']):
            return 'normal'
        elif any(keyword in value for keyword in ['훼손', 'damaged', '손상']):
            return 'damaged'
        elif any(keyword in value for keyword in ['없음', 'missing', '분실']):
            return 'missing'
        else:
            return 'replacement_needed'

    def _has_ssn_content(self, value: str) -> bool:
        """주민등록번호 내용 포함 여부 확인"""
        if not value or value.lower() in ['nan', '', 'none', 'null']:
            return False

        # 주민등록번호 패턴 또는 숫자가 포함되어 있으면 True
        return bool(re.search(r'\d{6}[-]?\d{7}|\d+', str(value)))

    def _get_seal_status_korean(self, status: str) -> str:
        """봉인씰 상태 한글 변환"""
        status_map = {
            'normal': '정상',
            'damaged': '훼손',
            'missing': '없음',
            'replacement_needed': '교체 필요'
        }
        return status_map.get(status, '알 수 없음')