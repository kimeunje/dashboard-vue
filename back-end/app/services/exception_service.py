# app/services/exception_service.py
from datetime import datetime, date
from typing import List, Dict, Optional
from app.utils.database import execute_query, DatabaseManager


class ExceptionService:
    """사용자별/부서별 감사 항목 제외 설정 관리 서비스"""

    def get_user_exceptions(self, user_id: int = None, item_id: int = None) -> List[Dict]:
        """사용자별 제외 설정 조회"""
        conditions = ["uie.is_active = 1"]
        params = []

        if user_id:
            conditions.append("uie.user_id = %s")
            params.append(user_id)

        if item_id:
            conditions.append("uie.item_id = %s")
            params.append(item_id)

        where_clause = " AND ".join(conditions)

        return execute_query(
            f"""
            SELECT 
                uie.exception_id,
                uie.user_id,
                u.user_id as user_login_id,
                u.username,
                u.department,
                uie.item_id,
                ci.item_name,
                ci.category,
                uie.exclude_reason,
                uie.exclude_type,
                uie.start_date,
                uie.end_date,
                uie.created_by,
                uie.created_at,
                uie.updated_at
            FROM user_item_exceptions uie
            JOIN users u ON uie.user_id = u.uid
            JOIN checklist_items ci ON uie.item_id = ci.item_id
            WHERE {where_clause}
            ORDER BY u.username, ci.item_name
            """, params, fetch_all=True)

    def get_department_exceptions(self, department: str = None, item_id: int = None) -> List[Dict]:
        """부서별 제외 설정 조회"""
        conditions = ["die.is_active = 1"]
        params = []

        if department:
            conditions.append("die.department = %s")
            params.append(department)

        if item_id:
            conditions.append("die.item_id = %s")
            params.append(item_id)

        where_clause = " AND ".join(conditions)

        return execute_query(
            f"""
            SELECT 
                die.dept_exception_id,
                die.department,
                die.item_id,
                ci.item_name,
                ci.category,
                die.exclude_reason,
                die.exclude_type,
                die.start_date,
                die.end_date,
                die.created_by,
                die.created_at,
                die.updated_at,
                COUNT(u.uid) as affected_users
            FROM department_item_exceptions die
            JOIN checklist_items ci ON die.item_id = ci.item_id
            LEFT JOIN users u ON die.department = u.department
            WHERE {where_clause}
            GROUP BY die.dept_exception_id, die.department, die.item_id, ci.item_name, ci.category,
                     die.exclude_reason, die.exclude_type, die.start_date, die.end_date,
                     die.created_by, die.created_at, die.updated_at
            ORDER BY die.department, ci.item_name
            """, params, fetch_all=True)

    def get_active_exceptions_for_user(self, user_id: int) -> List[Dict]:
        """특정 사용자에게 적용되는 모든 유효한 제외 설정 조회"""
        return execute_query(
            """
            SELECT 
                exception_type,
                user_id,
                item_id,
                item_name,
                category,
                exclude_reason,
                exclude_type
            FROM v_active_exceptions
            WHERE user_id = %s
            ORDER BY item_name
            """, (user_id,), fetch_all=True)

    def is_item_excluded_for_user(self, user_id: int, item_id: int) -> Dict:
        """특정 사용자-항목이 제외 대상인지 확인"""
        result = execute_query(
            """
            SELECT 
                exception_type,
                exclude_reason,
                exclude_type,
                start_date,
                end_date
            FROM v_active_exceptions
            WHERE user_id = %s AND item_id = %s
            LIMIT 1
            """, (user_id, item_id), fetch_one=True)

        if result:
            return {
                "is_excluded": True,
                "exception_type": result["exception_type"],
                "exclude_reason": result["exclude_reason"],
                "exclude_type": result["exclude_type"],
                "start_date": result["start_date"],
                "end_date": result["end_date"]
            }
        
        return {"is_excluded": False}

    def add_user_exception(self, user_id: int, item_id: int, exclude_reason: str, 
                          exclude_type: str = "permanent", start_date: date = None, 
                          end_date: date = None, created_by: str = "admin") -> Dict:
        """사용자별 제외 설정 추가"""
        try:
            # 기존 설정 확인
            existing = execute_query(
                "SELECT exception_id FROM user_item_exceptions WHERE user_id = %s AND item_id = %s",
                (user_id, item_id), fetch_one=True)

            if existing:
                # 기존 설정 업데이트
                execute_query(
                    """
                    UPDATE user_item_exceptions 
                    SET exclude_reason = %s, exclude_type = %s, start_date = %s, 
                        end_date = %s, created_by = %s, is_active = 1, updated_at = NOW()
                    WHERE user_id = %s AND item_id = %s
                    """, (exclude_reason, exclude_type, start_date, end_date, created_by, user_id, item_id))
                
                return {
                    "success": True,
                    "message": "기존 제외 설정이 업데이트되었습니다.",
                    "action": "updated"
                }
            else:
                # 새 설정 추가
                execute_query(
                    """
                    INSERT INTO user_item_exceptions 
                    (user_id, item_id, exclude_reason, exclude_type, start_date, end_date, created_by)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, (user_id, item_id, exclude_reason, exclude_type, start_date, end_date, created_by))
                
                return {
                    "success": True,
                    "message": "새로운 제외 설정이 추가되었습니다.",
                    "action": "created"
                }

        except Exception as e:
            return {
                "success": False,
                "message": f"제외 설정 추가 실패: {str(e)}"
            }

    def add_department_exception(self, department: str, item_id: int, exclude_reason: str,
                               exclude_type: str = "permanent", start_date: date = None,
                               end_date: date = None, created_by: str = "admin") -> Dict:
        """부서별 제외 설정 추가"""
        try:
            # 기존 설정 확인
            existing = execute_query(
                "SELECT dept_exception_id FROM department_item_exceptions WHERE department = %s AND item_id = %s",
                (department, item_id), fetch_one=True)

            if existing:
                # 기존 설정 업데이트
                execute_query(
                    """
                    UPDATE department_item_exceptions 
                    SET exclude_reason = %s, exclude_type = %s, start_date = %s, 
                        end_date = %s, created_by = %s, is_active = 1, updated_at = NOW()
                    WHERE department = %s AND item_id = %s
                    """, (exclude_reason, exclude_type, start_date, end_date, created_by, department, item_id))
                
                return {
                    "success": True,
                    "message": "기존 부서별 제외 설정이 업데이트되었습니다.",
                    "action": "updated"
                }
            else:
                # 새 설정 추가
                execute_query(
                    """
                    INSERT INTO department_item_exceptions 
                    (department, item_id, exclude_reason, exclude_type, start_date, end_date, created_by)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, (department, item_id, exclude_reason, exclude_type, start_date, end_date, created_by))
                
                return {
                    "success": True,
                    "message": "새로운 부서별 제외 설정이 추가되었습니다.",
                    "action": "created"
                }

        except Exception as e:
            return {
                "success": False,
                "message": f"부서별 제외 설정 추가 실패: {str(e)}"
            }

    def remove_user_exception(self, user_id: int, item_id: int) -> Dict:
        """사용자별 제외 설정 제거"""
        try:
            result = execute_query(
                "UPDATE user_item_exceptions SET is_active = 0 WHERE user_id = %s AND item_id = %s",
                (user_id, item_id))

            if result > 0:
                return {
                    "success": True,
                    "message": "제외 설정이 비활성화되었습니다."
                }
            else:
                return {
                    "success": False,
                    "message": "해당 제외 설정을 찾을 수 없습니다."
                }

        except Exception as e:
            return {
                "success": False,
                "message": f"제외 설정 제거 실패: {str(e)}"
            }

    def remove_department_exception(self, department: str, item_id: int) -> Dict:
        """부서별 제외 설정 제거"""
        try:
            result = execute_query(
                "UPDATE department_item_exceptions SET is_active = 0 WHERE department = %s AND item_id = %s",
                (department, item_id))

            if result > 0:
                return {
                    "success": True,
                    "message": "부서별 제외 설정이 비활성화되었습니다."
                }
            else:
                return {
                    "success": False,
                    "message": "해당 부서별 제외 설정을 찾을 수 없습니다."
                }

        except Exception as e:
            return {
                "success": False,
                "message": f"부서별 제외 설정 제거 실패: {str(e)}"
            }

    def get_all_departments(self) -> List[str]:
        """시스템에 등록된 모든 부서 목록 조회"""
        departments = execute_query(
            "SELECT DISTINCT department FROM users WHERE department IS NOT NULL ORDER BY department",
            fetch_all=True)
        
        return [dept["department"] for dept in departments]

    def get_exception_summary(self) -> Dict:
        """제외 설정 요약 통계"""
        with DatabaseManager.get_db_cursor(commit=False) as cursor:
            # 사용자별 제외 설정 통계
            cursor.execute(
                """
                SELECT 
                    COUNT(*) as total_user_exceptions,
                    COUNT(CASE WHEN exclude_type = 'permanent' THEN 1 END) as permanent_user_exceptions,
                    COUNT(CASE WHEN exclude_type = 'temporary' THEN 1 END) as temporary_user_exceptions
                FROM user_item_exceptions 
                WHERE is_active = 1
                """)
            user_stats = cursor.fetchone()

            # 부서별 제외 설정 통계
            cursor.execute(
                """
                SELECT 
                    COUNT(*) as total_dept_exceptions,
                    COUNT(CASE WHEN exclude_type = 'permanent' THEN 1 END) as permanent_dept_exceptions,
                    COUNT(CASE WHEN exclude_type = 'temporary' THEN 1 END) as temporary_dept_exceptions,
                    COUNT(DISTINCT department) as affected_departments
                FROM department_item_exceptions 
                WHERE is_active = 1
                """)
            dept_stats = cursor.fetchone()

            # 가장 많이 제외된 항목들
            cursor.execute(
                """
                SELECT 
                    ci.item_name,
                    ci.category,
                    COUNT(*) as exception_count
                FROM (
                    SELECT item_id FROM user_item_exceptions WHERE is_active = 1
                    UNION ALL
                    SELECT die.item_id 
                    FROM department_item_exceptions die
                    JOIN users u ON die.department = u.department
                    WHERE die.is_active = 1
                ) exceptions
                JOIN checklist_items ci ON exceptions.item_id = ci.item_id
                GROUP BY ci.item_id, ci.item_name, ci.category
                ORDER BY exception_count DESC
                LIMIT 5
                """)
            top_excluded_items = cursor.fetchall()

        return {
            "user_exceptions": user_stats,
            "department_exceptions": dept_stats,
            "top_excluded_items": top_excluded_items
        }