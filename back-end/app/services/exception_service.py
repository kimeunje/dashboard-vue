# app/services/exception_service.py - 뷰 테이블 제거 버전
from datetime import datetime, date
from typing import List, Dict, Optional
from app.utils.database import execute_query, DatabaseManager


class ExceptionService:
    """사용자별/부서별 감사 항목 제외 설정 관리 서비스 - 뷰 테이블 제거 버전"""

    def get_active_exceptions_for_user(self, user_id: int) -> List[Dict]:
        """특정 사용자에게 적용되는 모든 유효한 제외 설정 조회 (뷰 테이블 제거)"""

        # 1. 사용자별 감사 항목 제외 설정
        user_audit_exceptions = execute_query(
            """
            SELECT 
                'user' as exception_type,
                uie.user_id,
                CAST(uie.item_id AS CHAR) as item_id,
                uie.item_name,
                uie.item_category as category,
                uie.exclude_reason,
                uie.exclude_type
            FROM user_item_exceptions uie
            WHERE uie.user_id = %s 
            AND uie.is_active = 1
            AND (uie.exclude_type = 'permanent' OR 
                 (uie.exclude_type = 'temporary' AND CURDATE() BETWEEN uie.start_date AND uie.end_date))
            """,
            (user_id, ),
            fetch_all=True,
        )

        # 2. 사용자별 확장 제외 설정 (교육/훈련)
        user_extended_exceptions = execute_query(
            """
            SELECT 
                'user_extended' as exception_type,
                uee.user_id,
                uee.item_id,
                uee.item_name,
                uee.item_category as category,
                uee.exclude_reason,
                uee.exclude_type
            FROM user_extended_exceptions uee
            WHERE uee.user_id = %s 
            AND uee.is_active = 1
            AND (uee.exclude_type = 'permanent' OR 
                 (uee.exclude_type = 'temporary' AND CURDATE() BETWEEN uee.start_date AND uee.end_date))
            """,
            (user_id, ),
            fetch_all=True,
        )

        # 3. 사용자 부서 정보 조회
        user_dept = execute_query("SELECT department FROM users WHERE uid = %s",
                                  (user_id, ), fetch_one=True)

        if not user_dept:
            return user_audit_exceptions + user_extended_exceptions

        department = user_dept["department"]

        # 4. 부서별 감사 항목 제외 설정
        dept_audit_exceptions = execute_query(
            """
            SELECT 
                'department' as exception_type,
                %s as user_id,
                CAST(die.item_id AS CHAR) as item_id,
                die.item_name,
                die.item_category as category,
                die.exclude_reason,
                die.exclude_type
            FROM department_item_exceptions die
            WHERE die.department = %s 
            AND die.is_active = 1
            AND (die.exclude_type = 'permanent' OR 
                 (die.exclude_type = 'temporary' AND CURDATE() BETWEEN die.start_date AND die.end_date))
            """,
            (user_id, department),
            fetch_all=True,
        )

        # 5. 부서별 확장 제외 설정 (교육/훈련)
        dept_extended_exceptions = execute_query(
            """
            SELECT 
                'department_extended' as exception_type,
                %s as user_id,
                dee.item_id,
                dee.item_name,
                dee.item_category as category,
                dee.exclude_reason,
                dee.exclude_type
            FROM department_extended_exceptions dee
            WHERE dee.department = %s 
            AND dee.is_active = 1
            AND (dee.exclude_type = 'permanent' OR 
                 (dee.exclude_type = 'temporary' AND CURDATE() BETWEEN dee.start_date AND dee.end_date))
            """,
            (user_id, department),
            fetch_all=True,
        )

        # 모든 예외 설정 합치기
        all_exceptions = (user_audit_exceptions + user_extended_exceptions +
                          dept_audit_exceptions + dept_extended_exceptions)

        # 중복 제거 (같은 item_id에 대해 사용자별 설정이 부서별 설정보다 우선)
        unique_exceptions = {}
        for exc in all_exceptions:
            item_key = exc["item_id"]
            if item_key not in unique_exceptions:
                unique_exceptions[item_key] = exc
            elif exc["exception_type"] in ["user", "user_extended"]:
                # 사용자별 설정이 부서별 설정보다 우선
                unique_exceptions[item_key] = exc

        result = list(unique_exceptions.values())
        result.sort(key=lambda x: x["item_name"])

        return result

    def is_item_excluded_for_user(self, user_id: int, item_id: int) -> Dict:
        """특정 사용자-항목이 제외 대상인지 확인 (뷰 테이블 제거)"""
        # 1. 사용자별 감사 항목 제외 설정 확인
        user_audit_exception = execute_query(
            """
            SELECT 
                'user' as exception_type,
                exclude_reason,
                exclude_type,
                start_date,
                end_date
            FROM user_item_exceptions
            WHERE user_id = %s 
            AND item_id = %s 
            AND is_active = 1
            AND (exclude_type = 'permanent' OR 
                 (exclude_type = 'temporary' AND CURDATE() BETWEEN start_date AND end_date))
            LIMIT 1
            """,
            (user_id, item_id),
            fetch_one=True,
        )

        if user_audit_exception:
            return {
                "is_excluded": True,
                "exception_type": user_audit_exception["exception_type"],
                "exclude_reason": user_audit_exception["exclude_reason"],
                "exclude_type": user_audit_exception["exclude_type"],
                "start_date": user_audit_exception["start_date"],
                "end_date": user_audit_exception["end_date"],
            }

        # 2. 사용자별 확장 제외 설정 확인 (교육/훈련)
        user_extended_exception = execute_query(
            """
            SELECT 
                'user_extended' as exception_type,
                exclude_reason,
                exclude_type,
                start_date,
                end_date
            FROM user_extended_exceptions
            WHERE user_id = %s 
            AND item_id = CAST(%s AS CHAR)
            AND item_type = 'audit_item'
            AND is_active = 1
            AND (exclude_type = 'permanent' OR 
                 (exclude_type = 'temporary' AND CURDATE() BETWEEN start_date AND end_date))
            LIMIT 1
            """,
            (user_id, item_id),
            fetch_one=True,
        )

        if user_extended_exception:
            return {
                "is_excluded": True,
                "exception_type": user_extended_exception["exception_type"],
                "exclude_reason": user_extended_exception["exclude_reason"],
                "exclude_type": user_extended_exception["exclude_type"],
                "start_date": user_extended_exception["start_date"],
                "end_date": user_extended_exception["end_date"],
            }

        # 3. 사용자 부서 정보 조회
        user_dept = execute_query("SELECT department FROM users WHERE uid = %s",
                                  (user_id, ), fetch_one=True)

        if not user_dept:
            return {"is_excluded": False}

        department = user_dept["department"]

        # 4. 부서별 감사 항목 제외 설정 확인
        dept_audit_exception = execute_query(
            """
            SELECT 
                'department' as exception_type,
                exclude_reason,
                exclude_type,
                start_date,
                end_date
            FROM department_item_exceptions
            WHERE department = %s 
            AND item_id = %s 
            AND is_active = 1
            AND (exclude_type = 'permanent' OR 
                 (exclude_type = 'temporary' AND CURDATE() BETWEEN start_date AND end_date))
            LIMIT 1
            """,
            (department, item_id),
            fetch_one=True,
        )

        if dept_audit_exception:
            return {
                "is_excluded": True,
                "exception_type": dept_audit_exception["exception_type"],
                "exclude_reason": dept_audit_exception["exclude_reason"],
                "exclude_type": dept_audit_exception["exclude_type"],
                "start_date": dept_audit_exception["start_date"],
                "end_date": dept_audit_exception["end_date"],
            }

        # 5. 부서별 확장 제외 설정 확인 (교육/훈련)
        dept_extended_exception = execute_query(
            """
            SELECT 
                'department_extended' as exception_type,
                exclude_reason,
                exclude_type,
                start_date,
                end_date
            FROM department_extended_exceptions
            WHERE department = %s 
            AND item_id = CAST(%s AS CHAR)
            AND item_type = 'audit_item'
            AND is_active = 1
            AND (exclude_type = 'permanent' OR 
                 (exclude_type = 'temporary' AND CURDATE() BETWEEN start_date AND end_date))
            LIMIT 1
            """,
            (department, item_id),
            fetch_one=True,
        )

        if dept_extended_exception:
            return {
                "is_excluded": True,
                "exception_type": dept_extended_exception["exception_type"],
                "exclude_reason": dept_extended_exception["exclude_reason"],
                "exclude_type": dept_extended_exception["exclude_type"],
                "start_date": dept_extended_exception["start_date"],
                "end_date": dept_extended_exception["end_date"],
            }

        return {"is_excluded": False}

    # 나머지 메서드들은 기존과 동일하게 유지
    def get_user_exceptions(self, user_id: int = None,
                            item_id: int = None) -> List[Dict]:
        """사용자별 제외 설정 조회 (확장된 테이블 포함)"""
        # 기존 감사 항목 제외 설정
        audit_conditions = ["uie.is_active = 1"]
        audit_params = []

        if user_id:
            audit_conditions.append("uie.user_id = %s")
            audit_params.append(user_id)

        if item_id:
            audit_conditions.append("uie.item_id = %s")
            audit_params.append(item_id)

        audit_where_clause = " AND ".join(audit_conditions)

        audit_exceptions = execute_query(
            f"""
            SELECT 
                uie.exception_id,
                uie.user_id,
                u.user_id as user_login_id,
                u.username,
                u.department,
                CAST(uie.item_id AS CHAR) as item_id,
                'audit_item' as item_type,
                uie.item_name,
                uie.item_category,
                uie.exclude_reason,
                uie.exclude_type,
                uie.start_date,
                uie.end_date,
                uie.created_by,
                uie.created_at,
                uie.updated_at
            FROM user_item_exceptions uie
            JOIN users u ON uie.user_id = u.uid
            WHERE {audit_where_clause}
            """,
            audit_params,
            fetch_all=True,
        )

        # 확장된 제외 설정 (교육/훈련)
        extended_conditions = ["uee.is_active = 1"]
        extended_params = []

        if user_id:
            extended_conditions.append("uee.user_id = %s")
            extended_params.append(user_id)

        extended_where_clause = " AND ".join(extended_conditions)

        extended_exceptions = execute_query(
            f"""
            SELECT 
                uee.exception_id,
                uee.user_id,
                u.user_id as user_login_id,
                u.username,
                u.department,
                uee.item_id,
                uee.item_type,
                uee.item_name,
                uee.item_category,
                uee.exclude_reason,
                uee.exclude_type,
                uee.start_date,
                uee.end_date,
                uee.created_by,
                uee.created_at,
                uee.updated_at
            FROM user_extended_exceptions uee
            JOIN users u ON uee.user_id = u.uid
            WHERE {extended_where_clause}
            """,
            extended_params,
            fetch_all=True,
        )

        # 결과 합치기
        all_exceptions = audit_exceptions + extended_exceptions
        all_exceptions.sort(
            key=lambda x: (x["username"], x["item_type"], x["item_name"]))

        return all_exceptions

    def get_department_exceptions(self, department: str = None,
                                  item_id: int = None) -> List[Dict]:
        """부서별 제외 설정 조회 (확장된 테이블 포함)"""
        # 기존 감사 항목 제외 설정
        audit_conditions = ["die.is_active = 1"]
        audit_params = []

        if department:
            audit_conditions.append("die.department = %s")
            audit_params.append(department)

        if item_id:
            audit_conditions.append("die.item_id = %s")
            audit_params.append(item_id)

        audit_where_clause = " AND ".join(audit_conditions)

        audit_exceptions = execute_query(
            f"""
            SELECT 
                die.dept_exception_id,
                die.department,
                CAST(die.item_id AS CHAR) as item_id,
                'audit_item' as item_type,
                die.item_name,
                die.item_category,
                die.exclude_reason,
                die.exclude_type,
                die.start_date,
                die.end_date,
                die.created_by,
                die.created_at,
                die.updated_at,
                COUNT(u.uid) as affected_users
            FROM department_item_exceptions die
            LEFT JOIN users u ON die.department = u.department
            WHERE {audit_where_clause}
            GROUP BY die.dept_exception_id, die.department, die.item_id,
                     die.item_name, die.item_category, die.exclude_reason, die.exclude_type,
                     die.start_date, die.end_date, die.created_by, die.created_at, die.updated_at
            """,
            audit_params,
            fetch_all=True,
        )

        # 확장된 제외 설정 (교육/훈련)
        extended_conditions = ["dee.is_active = 1"]
        extended_params = []

        if department:
            extended_conditions.append("dee.department = %s")
            extended_params.append(department)

        extended_where_clause = " AND ".join(extended_conditions)

        extended_exceptions = execute_query(
            f"""
            SELECT 
                dee.dept_exception_id,
                dee.department,
                dee.item_id,
                dee.item_type,
                dee.item_name,
                dee.item_category,
                dee.exclude_reason,
                dee.exclude_type,
                dee.start_date,
                dee.end_date,
                dee.created_by,
                dee.created_at,
                dee.updated_at,
                COUNT(u.uid) as affected_users
            FROM department_extended_exceptions dee
            LEFT JOIN users u ON dee.department = u.department
            WHERE {extended_where_clause}
            GROUP BY dee.dept_exception_id, dee.department, dee.item_id, dee.item_type,
                     dee.item_name, dee.item_category, dee.exclude_reason, dee.exclude_type,
                     dee.start_date, dee.end_date, dee.created_by, dee.created_at, dee.updated_at
            """,
            extended_params,
            fetch_all=True,
        )

        # 결과 합치기
        all_exceptions = audit_exceptions + extended_exceptions
        all_exceptions.sort(
            key=lambda x: (x["department"], x["item_type"], x["item_name"]))

        return all_exceptions

    # 나머지 메서드들은 기존과 동일 (add_user_exception, remove_user_exception 등)
    def search_users(self, search_query: str = "", department: str = "",
                     limit: int = 50) -> List[Dict]:
        """사용자 검색"""
        conditions = []
        params = []

        if search_query:
            conditions.append(
                "(u.username LIKE %s OR u.user_id LIKE %s OR u.mail LIKE %s)")
            search_pattern = f"%{search_query}%"
            params.extend([search_pattern, search_pattern, search_pattern])

        if department:
            conditions.append("u.department = %s")
            params.append(department)

        where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""

        return execute_query(
            f"""
            SELECT uid, user_id, username, department, mail
            FROM users u
            {where_clause}
            ORDER BY u.username
            LIMIT %s
            """,
            params + [limit],
            fetch_all=True,
        )

    def get_available_items(self) -> Dict[str, List[Dict]]:
        """제외 설정 가능한 항목들 조회 (카테고리별 분류)"""
        # 정보보안 감사 항목들
        audit_items = execute_query(
            """
            SELECT item_id, item_name, category, description, check_type, penalty_weight
            FROM checklist_items
            ORDER BY category, item_name
            """,
            fetch_all=True,
        )

        # 정보보호 교육 항목들 (동적 생성)
        education_items = [
            {
                "item_type": "education_first_half",
                "item_name": "상반기 정보보호 교육",
                "category": "정보보호 교육",
                "description": "상반기 정보보호 교육 이수",
                "penalty_weight": 0.5,
            },
            {
                "item_type": "education_second_half",
                "item_name": "하반기 정보보호 교육",
                "category": "정보보호 교육",
                "description": "하반기 정보보호 교육 이수",
                "penalty_weight": 0.5,
            },
        ]

        # 악성메일 모의훈련 항목들 (동적 생성)
        training_items = [
            {
                "item_type": "training_first_half",
                "item_name": "상반기 악성메일 모의훈련",
                "category": "악성메일 모의훈련",
                "description": "상반기 악성메일 모의훈련 참여",
                "penalty_weight": 0.5,
            },
            {
                "item_type": "training_second_half",
                "item_name": "하반기 악성메일 모의훈련",
                "category": "악성메일 모의훈련",
                "description": "하반기 악성메일 모의훈련 참여",
                "penalty_weight": 0.5,
            },
        ]

        return {
            "정보보안 감사": audit_items,
            "정보보호 교육": education_items,
            "악성메일 모의훈련": training_items,
        }

    def add_user_exception(
        self,
        user_id: int,
        item_type: str,
        item_name: str,
        exclude_reason: str,
        exclude_type: str = "permanent",
        start_date: date = None,
        end_date: date = None,
        created_by: str = "admin",
    ) -> Dict:
        """사용자별 제외 설정 추가 (확장된 버전)"""
        try:
            # item_type에 따라 적절한 테이블과 item_id 결정
            if item_type.startswith("audit_"):
                # 감사 항목 처리
                item_id = int(item_type.replace("audit_", ""))
                return self._add_user_audit_exception(
                    user_id,
                    item_id,
                    item_name,
                    exclude_reason,
                    exclude_type,
                    start_date,
                    end_date,
                    created_by,
                )
            else:
                # 교육/훈련 항목 처리
                return self._add_user_extended_exception(
                    user_id,
                    item_type,
                    item_name,
                    exclude_reason,
                    exclude_type,
                    start_date,
                    end_date,
                    created_by,
                )

        except Exception as e:
            return {"success": False, "message": f"제외 설정 추가 실패: {str(e)}"}

    def _add_user_audit_exception(
        self,
        user_id: int,
        item_id: int,
        item_name: str,
        exclude_reason: str,
        exclude_type: str,
        start_date: date,
        end_date: date,
        created_by: str,
    ) -> Dict:
        """감사 항목 사용자별 제외 설정 추가"""
        # 항목 정보 조회
        item_info = execute_query(
            "SELECT item_name, category FROM checklist_items WHERE item_id = %s",
            (item_id, ),
            fetch_one=True,
        )

        if not item_info:
            return {"success": False, "message": "존재하지 않는 감사 항목입니다."}

        # 기존 설정 확인
        existing = execute_query(
            "SELECT exception_id FROM user_item_exceptions WHERE user_id = %s AND item_id = %s",
            (user_id, item_id),
            fetch_one=True,
        )

        if existing:
            # 기존 설정 업데이트
            execute_query(
                """
                UPDATE user_item_exceptions 
                SET exclude_reason = %s, exclude_type = %s, start_date = %s, 
                    end_date = %s, created_by = %s, is_active = 1, updated_at = NOW(),
                    item_name = %s, item_category = %s
                WHERE user_id = %s AND item_id = %s
                """,
                (
                    exclude_reason,
                    exclude_type,
                    start_date,
                    end_date,
                    created_by,
                    item_info["item_name"],
                    item_info["category"],
                    user_id,
                    item_id,
                ),
            )
            return {
                "success": True,
                "message": "기존 제외 설정이 업데이트되었습니다.",
                "action": "updated",
            }
        else:
            # 새 설정 추가
            execute_query(
                """
                INSERT INTO user_item_exceptions 
                (user_id, item_id, exclude_reason, exclude_type, start_date, end_date, 
                 created_by, item_name, item_category, item_type)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'audit')
                """,
                (
                    user_id,
                    item_id,
                    exclude_reason,
                    exclude_type,
                    start_date,
                    end_date,
                    created_by,
                    item_info["item_name"],
                    item_info["category"],
                ),
            )
            return {
                "success": True,
                "message": "새로운 제외 설정이 추가되었습니다.",
                "action": "created",
            }

    def _add_user_extended_exception(
        self,
        user_id: int,
        item_type: str,
        item_name: str,
        exclude_reason: str,
        exclude_type: str,
        start_date: date,
        end_date: date,
        created_by: str,
    ) -> Dict:
        """교육/훈련 항목 사용자별 제외 설정 추가"""
        # item_type에 따른 카테고리 결정
        if item_type.startswith("education_"):
            category = "정보보호 교육"
        elif item_type.startswith("training_"):
            category = "악성메일 모의훈련"
        else:
            return {"success": False, "message": "알 수 없는 항목 유형입니다."}

        # 기존 설정 확인
        existing = execute_query(
            "SELECT exception_id FROM user_extended_exceptions WHERE user_id = %s AND item_id = %s",
            (user_id, item_type),
            fetch_one=True,
        )

        if existing:
            # 기존 설정 업데이트
            execute_query(
                """
                UPDATE user_extended_exceptions 
                SET exclude_reason = %s, exclude_type = %s, start_date = %s, 
                    end_date = %s, created_by = %s, is_active = 1, updated_at = NOW(),
                    item_name = %s, item_category = %s
                WHERE user_id = %s AND item_id = %s
                """,
                (
                    exclude_reason,
                    exclude_type,
                    start_date,
                    end_date,
                    created_by,
                    item_name,
                    category,
                    user_id,
                    item_type,
                ),
            )
            return {
                "success": True,
                "message": "기존 제외 설정이 업데이트되었습니다.",
                "action": "updated",
            }
        else:
            # 새 설정 추가
            if item_type.startswith("education_"):
                db_item_type = "education_period"
            elif item_type.startswith("training_"):
                db_item_type = "training_period"
            else:
                db_item_type = "audit_item"

            execute_query(
                """
                INSERT INTO user_extended_exceptions 
                (user_id, item_id, item_type, item_name, item_category, exclude_reason, 
                 exclude_type, start_date, end_date, created_by)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    user_id,
                    item_type,
                    db_item_type,
                    item_name,
                    category,
                    exclude_reason,
                    exclude_type,
                    start_date,
                    end_date,
                    created_by,
                ),
            )
            return {
                "success": True,
                "message": "새로운 제외 설정이 추가되었습니다.",
                "action": "created",
            }

    def add_department_exception(
        self,
        department: str,
        item_type: str,
        item_name: str,
        exclude_reason: str,
        exclude_type: str = "permanent",
        start_date: date = None,
        end_date: date = None,
        created_by: str = "admin",
    ) -> Dict:
        """부서별 제외 설정 추가 (확장된 버전)"""
        try:
            # item_type에 따라 적절한 테이블과 item_id 결정
            if item_type.startswith("audit_"):
                # 감사 항목 처리
                item_id = int(item_type.replace("audit_", ""))
                return self._add_department_audit_exception(
                    department,
                    item_id,
                    item_name,
                    exclude_reason,
                    exclude_type,
                    start_date,
                    end_date,
                    created_by,
                )
            else:
                # 교육/훈련 항목 처리
                return self._add_department_extended_exception(
                    department,
                    item_type,
                    item_name,
                    exclude_reason,
                    exclude_type,
                    start_date,
                    end_date,
                    created_by,
                )

        except Exception as e:
            return {
                "success": False,
                "message": f"부서별 제외 설정 추가 실패: {str(e)}",
            }

    def _add_department_audit_exception(
        self,
        department: str,
        item_id: int,
        item_name: str,
        exclude_reason: str,
        exclude_type: str,
        start_date: date,
        end_date: date,
        created_by: str,
    ) -> Dict:
        """감사 항목 부서별 제외 설정 추가"""
        # 항목 정보 조회
        item_info = execute_query(
            "SELECT item_name, category FROM checklist_items WHERE item_id = %s",
            (item_id, ),
            fetch_one=True,
        )

        if not item_info:
            return {"success": False, "message": "존재하지 않는 감사 항목입니다."}

        # 기존 설정 확인
        existing = execute_query(
            "SELECT dept_exception_id FROM department_item_exceptions WHERE department = %s AND item_id = %s",
            (department, item_id),
            fetch_one=True,
        )

        if existing:
            # 기존 설정 업데이트
            execute_query(
                """
                UPDATE department_item_exceptions 
                SET exclude_reason = %s, exclude_type = %s, start_date = %s, 
                    end_date = %s, created_by = %s, is_active = 1, updated_at = NOW(),
                    item_name = %s, item_category = %s
                WHERE department = %s AND item_id = %s
                """,
                (
                    exclude_reason,
                    exclude_type,
                    start_date,
                    end_date,
                    created_by,
                    item_info["item_name"],
                    item_info["category"],
                    department,
                    item_id,
                ),
            )
            return {
                "success": True,
                "message": "기존 부서별 제외 설정이 업데이트되었습니다.",
                "action": "updated",
            }
        else:
            # 새 설정 추가
            execute_query(
                """
                INSERT INTO department_item_exceptions 
                (department, item_id, exclude_reason, exclude_type, start_date, end_date, 
                 created_by, item_name, item_category, item_type)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'audit')
                """,
                (
                    department,
                    item_id,
                    exclude_reason,
                    exclude_type,
                    start_date,
                    end_date,
                    created_by,
                    item_info["item_name"],
                    item_info["category"],
                ),
            )
            return {
                "success": True,
                "message": "새로운 부서별 제외 설정이 추가되었습니다.",
                "action": "created",
            }

    def _add_department_extended_exception(
        self,
        department: str,
        item_type: str,
        item_name: str,
        exclude_reason: str,
        exclude_type: str,
        start_date: date,
        end_date: date,
        created_by: str,
    ) -> Dict:
        """교육/훈련 항목 부서별 제외 설정 추가"""
        # item_type에 따른 카테고리 결정
        if item_type.startswith("education_"):
            category = "정보보호 교육"
        elif item_type.startswith("training_"):
            category = "악성메일 모의훈련"
        else:
            return {"success": False, "message": "알 수 없는 항목 유형입니다."}

        # 기존 설정 확인
        existing = execute_query(
            "SELECT dept_exception_id FROM department_extended_exceptions WHERE department = %s AND item_id = %s",
            (department, item_type),
            fetch_one=True,
        )

        if existing:
            # 기존 설정 업데이트
            execute_query(
                """
                UPDATE department_extended_exceptions 
                SET exclude_reason = %s, exclude_type = %s, start_date = %s, 
                    end_date = %s, created_by = %s, is_active = 1, updated_at = NOW(),
                    item_name = %s, item_category = %s
                WHERE department = %s AND item_id = %s
                """,
                (
                    exclude_reason,
                    exclude_type,
                    start_date,
                    end_date,
                    created_by,
                    item_name,
                    category,
                    department,
                    item_type,
                ),
            )
            return {
                "success": True,
                "message": "기존 부서별 제외 설정이 업데이트되었습니다.",
                "action": "updated",
            }
        else:
            # 새 설정 추가
            if item_type.startswith("education_"):
                db_item_type = "education_period"
            elif item_type.startswith("training_"):
                db_item_type = "training_period"
            else:
                db_item_type = "audit_item"

            execute_query(
                """
                INSERT INTO department_extended_exceptions 
                (department, item_id, item_type, item_name, item_category, exclude_reason, 
                 exclude_type, start_date, end_date, created_by)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    department,
                    item_type,
                    db_item_type,
                    item_name,
                    category,
                    exclude_reason,
                    exclude_type,
                    start_date,
                    end_date,
                    created_by,
                ),
            )
            return {
                "success": True,
                "message": "새로운 부서별 제외 설정이 추가되었습니다.",
                "action": "created",
            }

    def remove_user_exception(self, user_id: int, item_type: str) -> Dict:
        """사용자별 제외 설정 제거 (확장된 버전)"""
        try:
            if item_type.startswith("audit_"):
                # 감사 항목 제외 설정 제거
                item_id = int(item_type.replace("audit_", ""))
                result = execute_query(
                    "UPDATE user_item_exceptions SET is_active = 0 WHERE user_id = %s AND item_id = %s",
                    (user_id, item_id),
                )
            else:
                # 교육/훈련 항목 제외 설정 제거
                result = execute_query(
                    "UPDATE user_extended_exceptions SET is_active = 0 WHERE user_id = %s AND item_id = %s",
                    (user_id, item_type),
                )

            if result > 0:
                return {"success": True, "message": "제외 설정이 비활성화되었습니다."}
            else:
                return {
                    "success": False,
                    "message": "해당 제외 설정을 찾을 수 없습니다.",
                }

        except Exception as e:
            return {"success": False, "message": f"제외 설정 제거 실패: {str(e)}"}

    def remove_department_exception(self, department: str, item_type: str) -> Dict:
        """부서별 제외 설정 제거 (확장된 버전)"""
        try:
            if item_type.startswith("audit_"):
                # 감사 항목 제외 설정 제거
                item_id = int(item_type.replace("audit_", ""))
                result = execute_query(
                    "UPDATE department_item_exceptions SET is_active = 0 WHERE department = %s AND item_id = %s",
                    (department, item_id),
                )
            else:
                # 교육/훈련 항목 제외 설정 제거
                result = execute_query(
                    "UPDATE department_extended_exceptions SET is_active = 0 WHERE department = %s AND item_id = %s",
                    (department, item_type),
                )

            if result > 0:
                return {
                    "success": True,
                    "message": "부서별 제외 설정이 비활성화되었습니다.",
                }
            else:
                return {
                    "success": False,
                    "message": "해당 부서별 제외 설정을 찾을 수 없습니다.",
                }

        except Exception as e:
            return {
                "success": False,
                "message": f"부서별 제외 설정 제거 실패: {str(e)}",
            }

    def get_all_departments(self) -> List[str]:
        """시스템에 등록된 모든 부서 목록 조회"""
        departments = execute_query(
            "SELECT DISTINCT department FROM users WHERE department IS NOT NULL ORDER BY department",
            fetch_all=True,
        )
        return [dept["department"] for dept in departments]

    def get_exception_summary(self) -> Dict:
        """제외 설정 요약 통계"""
        with DatabaseManager.get_db_cursor(commit=False) as cursor:
            # 사용자별 제외 설정 통계
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_user_exceptions,
                    COUNT(CASE WHEN exclude_type = 'permanent' THEN 1 END) as permanent_user_exceptions,
                    COUNT(CASE WHEN exclude_type = 'temporary' THEN 1 END) as temporary_user_exceptions
                FROM user_item_exceptions 
                WHERE is_active = 1
                """)
            user_stats = cursor.fetchone()

            # 부서별 제외 설정 통계
            cursor.execute("""
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
            cursor.execute("""
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
            "top_excluded_items": top_excluded_items,
        }