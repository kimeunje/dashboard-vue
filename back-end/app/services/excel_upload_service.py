# back-end/app/services/excel_upload_service.py

import pandas as pd
import uuid
import re
from datetime import datetime
from typing import Dict, List, Any, Tuple
from app.utils.database import execute_query, DatabaseManager
import logging

logger = logging.getLogger(__name__)

class ExcelUploadService:
    
    def __init__(self):
        self.supported_types = ['seal_check', 'malware_scan', 'file_encryption']
    
    def process_excel_upload(self, file, check_type: str, uploaded_by: str) -> Dict[str, Any]:
        """엑셀 파일 업로드 및 처리 메인 함수"""
        
        if check_type not in self.supported_types:
            raise ValueError(f"지원하지 않는 점검 유형입니다: {check_type}")
        
        # 배치 ID 생성
        batch_id = str(uuid.uuid4())
        filename = file.filename
        
        try:
            # 1. 배치 레코드 생성
            self._create_batch_record(batch_id, check_type, filename, uploaded_by)
            
            # 2. 엑셀 파일 읽기
            df = self._read_excel_file(file)
            
            # 3. 파싱 설정 가져오기
            parsing_config = self._get_parsing_config(check_type)
            
            # 4. 데이터 파싱 및 검증
            parsed_data = self._parse_excel_data(df, check_type, parsing_config)
            
            # 5. 데이터베이스 저장
            result = self._save_parsed_data(batch_id, check_type, parsed_data)
            
            # 6. 배치 상태 업데이트
            self._update_batch_status(batch_id, 'completed', 
                                    len(parsed_data), result['success_count'], result['error_count'])
            
            return {
                'success': True,
                'batch_id': batch_id,
                'total_records': len(parsed_data),
                'success_records': result['success_count'],
                'failed_records': result['error_count'],
                'errors': result['errors']
            }
            
        except Exception as e:
            logger.error(f"엑셀 업로드 처리 실패: {str(e)}")
            self._update_batch_status(batch_id, 'failed', 0, 0, 0, str(e))
            raise ValueError(f"엑셀 처리 중 오류가 발생했습니다: {str(e)}")
    
    def _read_excel_file(self, file) -> pd.DataFrame:
        """엑셀 파일 읽기"""
        filename = file.filename.lower()
        
        try:
            if filename.endswith('.csv'):
                df = pd.read_csv(file, encoding='utf-8-sig')
            elif filename.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(file)
            else:
                raise ValueError('지원하지 않는 파일 형식입니다. (.xlsx, .xls, .csv만 지원)')
            
            return df
            
        except Exception as e:
            raise ValueError(f"파일 읽기 실패: {str(e)}")
    
    def _get_parsing_config(self, check_type: str) -> Dict[str, Any]:
        """파싱 설정 조회"""
        config = execute_query(
            """
            SELECT required_columns, optional_columns, parsing_rules 
            FROM excel_parsing_config 
            WHERE check_type = %s AND config_name = 'default' AND is_active = 1
            """, 
            (check_type,), 
            fetch_one=True
        )
        
        if not config:
            raise ValueError(f"파싱 설정을 찾을 수 없습니다: {check_type}")
        
        return {
            'required_columns': config['required_columns'],
            'optional_columns': config['optional_columns'],
            'parsing_rules': config['parsing_rules']
        }
    
    def _parse_excel_data(self, df: pd.DataFrame, check_type: str, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """엑셀 데이터 파싱"""
        
        if check_type == 'malware_scan':
            return self._parse_malware_data(df, config)
        elif check_type == 'seal_check':
            return self._parse_seal_data(df, config)
        elif check_type == 'file_encryption':
            return self._parse_encryption_data(df, config)
        else:
            raise ValueError(f"알 수 없는 점검 유형: {check_type}")
    
    def _parse_malware_data(self, df: pd.DataFrame, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """악성코드 검사 데이터 파싱"""
        required_cols = config['required_columns']
        parsed_data = []
        
        # 헤더 매핑
        column_mapping = {}
        for field, header in required_cols.items():
            matching_cols = [col for col in df.columns if header in str(col)]
            if matching_cols:
                column_mapping[field] = matching_cols[0]
            else:
                raise ValueError(f"필수 컬럼을 찾을 수 없습니다: {header}")
        
        # 데이터 파싱
        for idx, row in df.iterrows():
            if idx == 0:  # 헤더 행 스킵
                continue
                
            try:
                scan_date = self._parse_datetime(row[column_mapping['scan_date']])
                
                parsed_record = {
                    'scan_date': scan_date,
                    'ip_address': str(row[column_mapping['ip_address']]),
                    'malware_name': str(row[column_mapping['malware_name']]),
                    'malware_category': str(row[column_mapping['malware_category']]),
                    'file_path': str(row[column_mapping['file_path']]),
                    'detection_item': str(row[column_mapping['detection_item']])
                }
                
                parsed_data.append(parsed_record)
                
            except Exception as e:
                logger.warning(f"행 {idx} 파싱 실패: {str(e)}")
                continue
        
        return parsed_data
    
    def _parse_seal_data(self, df: pd.DataFrame, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """PC 봉인씰 확인 데이터 파싱"""
        required_cols = config['required_columns']
        parsed_data = []
        
        # 헤더 매핑
        column_mapping = {}
        for field, header in required_cols.items():
            matching_cols = [col for col in df.columns if header in str(col)]
            if matching_cols:
                column_mapping[field] = matching_cols[0]
            else:
                raise ValueError(f"필수 컬럼을 찾을 수 없습니다: {header}")
        
        # 데이터 파싱
        for idx, row in df.iterrows():
            if idx == 0:  # 헤더 행 스킵
                continue
                
            try:
                check_date = self._parse_datetime(row[column_mapping['check_date']])
                seal_status = self._normalize_seal_status(str(row[column_mapping['seal_status']]))
                
                parsed_record = {
                    'check_date': check_date,
                    'user_name': str(row[column_mapping['user_name']]),
                    'department': str(row[column_mapping['department']]),
                    'seal_status': seal_status
                }
                
                parsed_data.append(parsed_record)
                
            except Exception as e:
                logger.warning(f"행 {idx} 파싱 실패: {str(e)}")
                continue
        
        return parsed_data
    
    def _parse_encryption_data(self, df: pd.DataFrame, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """개인정보 파일 암호화 데이터 파싱"""
        required_cols = config['required_columns']
        parsed_data = []
        
        # 최신 회차 찾기
        latest_round = self._find_latest_round(df.columns)
        if not latest_round:
            raise ValueError("회차 정보를 찾을 수 없습니다")
        
        # 로컬 IP 컬럼 찾기
        local_ip_col = None
        for col in df.columns:
            if '로컬 IP' in str(col):
                local_ip_col = col
                break
        
        if local_ip_col is None:
            raise ValueError("로컬 IP 컬럼을 찾을 수 없습니다")
        
        # 최신 회차의 주민등록번호 컬럼 찾기
        ssn_col = self._find_ssn_column(df.columns, latest_round)
        if not ssn_col:
            raise ValueError(f"{latest_round}회차의 주민등록번호 컬럼을 찾을 수 없습니다")
        
        # 데이터 파싱 (헤더 행 제외하고 시작)
        data_start_row = 2  # 복합 헤더이므로 3번째 행부터 데이터
        for idx, row in df.iterrows():
            if idx < data_start_row:
                continue
                
            try:
                local_ip = str(row[local_ip_col])
                ssn_count = self._parse_ssn_count(row[ssn_col])
                
                # 검사 상태 결정
                scan_status = '정상' if ssn_count == 0 else '탐지'
                if pd.isna(row[ssn_col]) or str(row[ssn_col]).strip() in ['미검사', '-', '']:
                    scan_status = '미검사'
                
                parsed_record = {
                    'local_ip': local_ip,
                    'latest_round': latest_round,
                    'ssn_detected_count': ssn_count,
                    'scan_status': scan_status
                }
                
                parsed_data.append(parsed_record)
                
            except Exception as e:
                logger.warning(f"행 {idx} 파싱 실패: {str(e)}")
                continue
        
        return parsed_data
    
    def _find_latest_round(self, columns) -> int:
        """컬럼에서 최신 회차 찾기"""
        rounds = []
        for col in columns:
            if '회차' in str(col):
                match = re.search(r'(\d+)회차', str(col))
                if match:
                    rounds.append(int(match.group(1)))
        
        return max(rounds) if rounds else None
    
    def _find_ssn_column(self, columns, target_round: int) -> str:
        """특정 회차의 주민등록번호 컬럼 찾기"""
        round_start_idx = None
        
        # 회차 컬럼의 시작 인덱스 찾기
        for idx, col in enumerate(columns):
            if f'{target_round}회차' in str(col):
                round_start_idx = idx
                break
        
        if round_start_idx is None:
            return None
        
        # 해당 회차 영역에서 주민등록번호 컬럼 찾기 (보통 5개 컬럼 범위 내)
        for i in range(round_start_idx, min(round_start_idx + 6, len(columns))):
            if '주민등록번호' in str(columns[i]):
                return columns[i]
        
        return None
    
    def _parse_datetime(self, value) -> datetime:
        """날짜/시간 파싱"""
        if pd.isna(value):
            raise ValueError("날짜 값이 비어있습니다")
        
        if isinstance(value, datetime):
            return value
        
        # 문자열 파싱 시도
        date_str = str(value).strip()
        
        # 일반적인 날짜 형식들 시도
        formats = [
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%d %p %I:%M:%S',
            '%Y-%m-%d',
            '%Y/%m/%d %H:%M:%S',
            '%Y/%m/%d'
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        
        raise ValueError(f"날짜 형식을 인식할 수 없습니다: {date_str}")
    
    def _normalize_seal_status(self, status: str) -> str:
        """봉인씰 상태 정규화"""
        status = status.strip()
        
        mapping = {
            '정상': '정상',
            '훼손': '훼손', 
            '손상': '훼손',
            '파손': '훼손',
            '미부착': '미부착',
            '없음': '미부착',
            '교체필요': '교체필요',
            '교체': '교체필요'
        }
        
        return mapping.get(status, '훼손')  # 기본값은 훼손으로
    
    def _parse_ssn_count(self, value) -> int:
        """주민등록번호 탐지 건수 파싱"""
        if pd.isna(value):
            return 0
        
        # 숫자로 변환 시도
        try:
            count = int(float(str(value)))
            return max(0, count)  # 음수 방지
        except (ValueError, TypeError):
            # 문자열인 경우 0으로 처리
            if str(value).strip() in ['-', '미검사', '']:
                return 0
            return 0
    
    def _save_parsed_data(self, batch_id: str, check_type: str, parsed_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """파싱된 데이터 저장"""
        
        if check_type == 'malware_scan':
            return self._save_malware_data(batch_id, parsed_data)
        elif check_type == 'seal_check':
            return self._save_seal_data(batch_id, parsed_data)
        elif check_type == 'file_encryption':
            return self._save_encryption_data(batch_id, parsed_data)
        else:
            raise ValueError(f"알 수 없는 점검 유형: {check_type}")
    
    def _save_malware_data(self, batch_id: str, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """악성코드 검사 데이터 저장"""
        success_count = 0
        error_count = 0
        errors = []
        
        for record in data:
            try:
                execute_query(
                    """
                    INSERT INTO malware_scan_details 
                    (batch_id, scan_date, ip_address, malware_name, malware_category, file_path, detection_item)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """,
                    (batch_id, record['scan_date'], record['ip_address'], 
                     record['malware_name'], record['malware_category'],
                     record['file_path'], record['detection_item'])
                )
                success_count += 1
                
            except Exception as e:
                error_count += 1
                errors.append(f"데이터 저장 실패: {str(e)}")
        
        return {
            'success_count': success_count,
            'error_count': error_count,
            'errors': errors
        }
    
    def _save_seal_data(self, batch_id: str, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """PC 봉인씰 확인 데이터 저장"""
        success_count = 0
        error_count = 0
        errors = []
        
        for record in data:
            try:
                execute_query(
                    """
                    INSERT INTO seal_check_details 
                    (batch_id, check_date, user_name, department, seal_status)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (batch_id, record['check_date'], record['user_name'],
                     record['department'], record['seal_status'])
                )
                success_count += 1
                
            except Exception as e:
                error_count += 1
                errors.append(f"데이터 저장 실패: {str(e)}")
        
        return {
            'success_count': success_count,
            'error_count': error_count,
            'errors': errors
        }
    
    def _save_encryption_data(self, batch_id: str, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """개인정보 파일 암호화 데이터 저장"""
        success_count = 0
        error_count = 0
        errors = []
        
        for record in data:
            try:
                execute_query(
                    """
                    INSERT INTO encryption_scan_details 
                    (batch_id, local_ip, latest_round, ssn_detected_count, scan_status)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (batch_id, record['local_ip'], record['latest_round'],
                     record['ssn_detected_count'], record['scan_status'])
                )
                success_count += 1
                
            except Exception as e:
                error_count += 1
                errors.append(f"데이터 저장 실패: {str(e)}")
        
        return {
            'success_count': success_count,
            'error_count': error_count,
            'errors': errors
        }
    
    def _create_batch_record(self, batch_id: str, check_type: str, filename: str, uploaded_by: str):
        """배치 레코드 생성"""
        execute_query(
            """
            INSERT INTO excel_upload_batches 
            (batch_id, check_type, filename, uploaded_by, status)
            VALUES (%s, %s, %s, %s, 'processing')
            """,
            (batch_id, check_type, filename, uploaded_by)
        )
    
    def _update_batch_status(self, batch_id: str, status: str, total: int, success: int, failed: int, error_log: str = None):
        """배치 상태 업데이트"""
        execute_query(
            """
            UPDATE excel_upload_batches 
            SET status = %s, total_records = %s, success_records = %s, 
                failed_records = %s, error_log = %s
            WHERE batch_id = %s
            """,
            (status, total, success, failed, error_log, batch_id)
        )
    
    def get_upload_history(self, check_type: str = None, limit: int = 50) -> List[Dict[str, Any]]:
        """업로드 이력 조회"""
        query = """
            SELECT batch_id, check_type, filename, upload_date, uploaded_by,
                   total_records, success_records, failed_records, status
            FROM excel_upload_batches
        """
        params = []
        
        if check_type:
            query += " WHERE check_type = %s"
            params.append(check_type)
        
        query += " ORDER BY upload_date DESC LIMIT %s"
        params.append(limit)
        
        return execute_query(query, params)
    
    def get_batch_details(self, batch_id: str) -> Dict[str, Any]:
        """배치 상세 정보 조회"""
        batch_info = execute_query(
            "SELECT * FROM excel_upload_batches WHERE batch_id = %s",
            (batch_id,),
            fetch_one=True
        )
        
        if not batch_info:
            raise ValueError("배치 정보를 찾을 수 없습니다")
        
        # 상세 데이터 조회
        check_type = batch_info['check_type']
        
        if check_type == 'malware_scan':
            details = execute_query(
                "SELECT * FROM malware_scan_details WHERE batch_id = %s ORDER BY scan_date DESC",
                (batch_id,)
            )
        elif check_type == 'seal_check':
            details = execute_query(
                "SELECT * FROM seal_check_details WHERE batch_id = %s ORDER BY check_date DESC",
                (batch_id,)
            )
        elif check_type == 'file_encryption':
            details = execute_query(
                "SELECT * FROM encryption_scan_details WHERE batch_id = %s ORDER BY local_ip",
                (batch_id,)
            )
        else:
            details = []
        
        return {
            'batch_info': batch_info,
            'details': details
        }