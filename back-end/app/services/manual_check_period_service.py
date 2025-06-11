# back-end/app/services/manual_check_period_service.py
from datetime import datetime, date
from typing import List, Dict, Optional
from app.utils.database import execute_query


class ManualCheckPeriodService:
    """수시 점검 기간 관리 서비스"""

    CHECK_TYPES = {
        'screen_saver': '화면보호기',
        'antivirus': '백신',
        'patch_update': '패치'
    }

    def get_periods(self, year: int = None, check_type: str = None) -> List[Dict]:
        """기간 목록 조회"""
        if year is None:
            year = datetime.now().year

        query = """
            SELECT 
                period_id,
                check_type,
                period_year,
                period_name,
                start_date,
                end_date,
                is_completed,
                completed_at,
                completed_by,
                description,
                auto_pass_setting,
                created_by,
                created_at,
                updated_at,
                CASE 
                    WHEN %s BETWEEN start_date AND end_date THEN 'active'
                    WHEN %s < start_date THEN 'upcoming'
                    WHEN %s > end_date THEN 'ended'
                    ELSE 'unknown'
                END as status
            FROM manual_check_periods
            WHERE period_year = %s AND is_active = 1
        """
        params = [date.today(), date.today(), date.today(), year]

        if check_type:
            query += " AND check_type = %s"
            params.append(check_type)

        query += " ORDER BY check_type, start_date"

        return execute_query(query, params, fetch_all=True)

    def create_period(self, period_data: Dict) -> bool:
        """기간 생성"""
        try:
            # 중복 체크
            if self.check_period_exists(
                period_data['check_type'], 
                period_data['period_year'], 
                period_data['period_name']
            ):
                raise ValueError("동일한 점검 유형, 연도, 기간명이 이미 존재합니다.")

            # 날짜 검증
            start_date = datetime.strptime(period_data['start_date'], '%Y-%m-%d').date()
            end_date = datetime.strptime(period_data['end_date'], '%Y-%m-%d').date()
            
            if start_date >= end_date:
                raise ValueError("종료일은 시작일보다 늦어야 합니다.")

            query = """
                INSERT INTO manual_check_periods
                (check_type, period_year, period_name, start_date, end_date, 
                 description, auto_pass_setting, created_by)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            execute_query(query, (
                period_data['check_type'],
                period_data['period_year'],
                period_data['period_name'],
                start_date,
                end_date,
                period_data.get('description', ''),
                period_data.get('auto_pass_setting', 1),
                period_data['created_by']
            ))
            
            return True
        except Exception as e:
            raise ValueError(f"기간 생성 실패: {str(e)}")

    def update_period(self, period_id: int, period_data: Dict) -> bool:
        """기간 수정"""
        try:
            # 날짜 검증
            start_date = datetime.strptime(period_data['start_date'], '%Y-%m-%d').date()
            end_date = datetime.strptime(period_data['end_date'], '%Y-%m-%d').date()
            
            if start_date >= end_date:
                raise ValueError("종료일은 시작일보다 늦어야 합니다.")

            query = """
                UPDATE manual_check_periods
                SET period_name = %s, start_date = %s, end_date = %s,
                    description = %s, auto_pass_setting = %s, updated_at = NOW()
                WHERE period_id = %s AND is_active = 1
            """
            
            execute_query(query, (
                period_data['period_name'],
                start_date,
                end_date,
                period_data.get('description', ''),
                period_data.get('auto_pass_setting', 1),
                period_id
            ))
            
            return True
        except Exception as e:
            raise ValueError(f"기간 수정 실패: {str(e)}")

    def delete_period(self, period_id: int) -> bool:
        """기간 삭제 (소프트 삭제)"""
        try:
            # 연결된 결과가 있는지 확인
            result_count = execute_query(
                "SELECT COUNT(*) as count FROM manual_check_results WHERE period_id = %s",
                (period_id,),
                fetch_one=True
            )
            
            if result_count['count'] > 0:
                raise ValueError("해당 기간에 연결된 점검 결과가 있어 삭제할 수 없습니다.")

            execute_query(
                "UPDATE manual_check_periods SET is_active = 0, updated_at = NOW() WHERE period_id = %s",
                (period_id,)
            )
            
            return True
        except Exception as e:
            raise ValueError(f"기간 삭제 실패: {str(e)}")

    def complete_period(self, period_id: int, completed_by: str) -> bool:
        """기간 완료 처리 및 자동 통과"""
        try:
            with execute_query("START TRANSACTION"):
                # 기간 정보 조회
                period_info = execute_query(
                    """
                    SELECT check_type, period_year, period_name, auto_pass_setting
                    FROM manual_check_periods
                    WHERE period_id = %s AND is_active = 1
                    """,
                    (period_id,),
                    fetch_one=True
                )
                
                if not period_info:
                    raise ValueError("기간 정보를 찾을 수 없습니다.")

                # 자동 통과 처리가 설정된 경우
                if period_info['auto_pass_setting']:
                    # 해당 기간에 결과가 없는 사용자들을 자동 통과 처리
                    execute_query(
                        """
                        INSERT INTO manual_check_results 
                        (user_id, check_type, check_year, period_name, period_id, 
                         check_result, notes, created_at, updated_at)
                        SELECT 
                            u.user_id,
                            %s,
                            %s,
                            %s,
                            %s,
                            'pass',
                            '기간 완료로 인한 자동 통과 처리',
                            NOW(),
                            NOW()
                        FROM users u
                        WHERE u.is_active = 1
                        AND NOT EXISTS (
                            SELECT 1 FROM manual_check_results mcr
                            WHERE mcr.user_id = u.user_id
                            AND mcr.period_id = %s
                        )
                        """,
                        (
                            period_info['check_type'],
                            period_info['period_year'],
                            period_info['period_name'],
                            period_id,
                            period_id
                        )
                    )

                # 기간 완료 상태 업데이트
                execute_query(
                    """
                    UPDATE manual_check_periods
                    SET is_completed = 1, completed_at = NOW(), completed_by = %s, updated_at = NOW()
                    WHERE period_id = %s
                    """,
                    (completed_by, period_id)
                )

                return True
        except Exception as e:
            raise ValueError(f"완료 처리 실패: {str(e)}")

    def reopen_period(self, period_id: int) -> bool:
        """기간 재개 (자동 통과 처리된 결과 삭제)"""
        try:
            with execute_query("START TRANSACTION"):
                # 자동 통과 처리된 레코드들만 삭제
                execute_query(
                    """
                    DELETE FROM manual_check_results
                    WHERE period_id = %s 
                    AND notes = '기간 완료로 인한 자동 통과 처리'
                    """,
                    (period_id,)
                )

                # 기간 상태 되돌리기
                execute_query(
                    """
                    UPDATE manual_check_periods
                    SET is_completed = 0, completed_at = NULL, completed_by = NULL, updated_at = NOW()
                    WHERE period_id = %s
                    """,
                    (period_id,)
                )

                return True
        except Exception as e:
            raise ValueError(f"재개 처리 실패: {str(e)}")

    def check_period_exists(self, check_type: str, year: int, period_name: str) -> bool:
        """기간 중복 체크"""
        result = execute_query(
            """
            SELECT COUNT(*) as count
            FROM manual_check_periods
            WHERE check_type = %s AND period_year = %s AND period_name = %s AND is_active = 1
            """,
            (check_type, year, period_name),
            fetch_one=True
        )
        return result['count'] > 0

    def get_current_status(self, year: int = None) -> Dict:
        """현재 기간 상태 요약"""
        if year is None:
            year = datetime.now().year

        today = date.today()

        # 각 점검 유형별 기간 현황
        periods_by_type = {}
        
        for check_type, type_name in self.CHECK_TYPES.items():
            periods = execute_query(
                """
                SELECT 
                    period_id,
                    period_name,
                    start_date,
                    end_date,
                    is_completed,
                    completed_at,
                    CASE 
                        WHEN %s BETWEEN start_date AND end_date THEN 'active'
                        WHEN %s < start_date THEN 'upcoming'
                        WHEN %s > end_date THEN 'ended'
                        ELSE 'unknown'
                    END as status
                FROM manual_check_periods
                WHERE check_type = %s AND period_year = %s AND is_active = 1
                ORDER BY start_date
                """,
                (today, today, today, check_type, year),
                fetch_all=True
            )

            # 각 기간별 통계
            for period in periods:
                stats = execute_query(
                    """
                    SELECT 
                        COUNT(*) as total_users,
                        SUM(CASE WHEN check_result = 'pass' THEN 1 ELSE 0 END) as pass_count,
                        SUM(CASE WHEN check_result = 'fail' THEN 1 ELSE 0 END) as fail_count
                    FROM manual_check_results
                    WHERE period_id = %s
                    """,
                    (period['period_id'],),
                    fetch_one=True
                )
                period.update(stats)

            periods_by_type[check_type] = {
                'type_name': type_name,
                'periods': periods
            }

        return {
            'year': year,
            'check_types': periods_by_type,
            'summary': self._get_year_summary(year)
        }

    def _get_year_summary(self, year: int) -> Dict:
        """연간 요약 통계"""
        summary = {}
        
        for check_type, type_name in self.CHECK_TYPES.items():
            stats = execute_query(
                """
                SELECT 
                    COUNT(DISTINCT mcp.period_id) as total_periods,
                    SUM(CASE WHEN mcp.is_completed = 1 THEN 1 ELSE 0 END) as completed_periods,
                    COUNT(mcr.result_id) as total_results,
                    SUM(CASE WHEN mcr.check_result = 'pass' THEN 1 ELSE 0 END) as total_pass,
                    SUM(CASE WHEN mcr.check_result = 'fail' THEN 1 ELSE 0 END) as total_fail
                FROM manual_check_periods mcp
                LEFT JOIN manual_check_results mcr ON mcp.period_id = mcr.period_id
                WHERE mcp.check_type = %s AND mcp.period_year = %s AND mcp.is_active = 1
                """,
                (check_type, year),
                fetch_one=True
            )
            
            summary[check_type] = {
                'type_name': type_name,
                **stats
            }

        return summary

    def get_expired_periods(self) -> List[Dict]:
        """만료된 기간 중 미완료 상태인 것들 조회"""
        today = date.today()
        
        return execute_query(
            """
            SELECT 
                period_id,
                check_type,
                period_year,
                period_name,
                start_date,
                end_date,
                auto_pass_setting
            FROM manual_check_periods
            WHERE end_date < %s 
            AND is_completed = 0 
            AND is_active = 1
            AND auto_pass_setting = 1
            ORDER BY end_date
            """,
            (today,),
            fetch_all=True
        )