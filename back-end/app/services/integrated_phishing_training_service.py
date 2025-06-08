# app/services/integrated_phishing_training_service.py
# 기존 PhishingTrainingService와 TrainingPeriodService를 통합

from app.utils.database import execute_query, execute_query_with_transaction
from datetime import datetime, date
from typing import List, Dict, Optional, Any
import csv
import io


class IntegratedPhishingTrainingService:
    """악성메일 모의훈련 통합 서비스 - 기간 관리 + 훈련 기록 관리"""

    # ================== 기간 관리 기능 ==================

    def get_training_periods(
        self, year: Optional[int] = None, active_only: bool = True
    ) -> List[Dict]:
        """훈련 기간 목록 조회"""
        try:
            conditions = []
            params = []

            if active_only:
                conditions.append("is_active = 1")

            if year:
                conditions.append("training_year = %s")
                params.append(year)

            where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""

            query = f"""
                SELECT 
                    period_id,
                    training_year,
                    training_period,
                    start_date,
                    end_date,
                    is_completed,
                    completed_at,
                    completed_by,
                    description,
                    created_by,
                    created_at,
                    updated_at
                FROM phishing_training_periods
                {where_clause}
                ORDER BY training_year DESC, 
                         CASE training_period 
                             WHEN 'first_half' THEN 1 
                             WHEN 'second_half' THEN 2 
                             ELSE 3 
                         END
            """

            periods = execute_query(query, params)

            # 각 기간별 통계 추가
            for period in periods:
                stats = self.get_period_statistics(
                    period["training_year"], period["training_period"]
                )
                period["statistics"] = stats

            return periods

        except Exception as e:
            raise ValueError(f"기간 목록 조회 실패: {str(e)}")

    def get_training_period_by_id(self, period_id: int) -> Optional[Dict]:
        """특정 기간 상세 조회"""
        try:
            periods = execute_query(
                """
                SELECT 
                    period_id, training_year, training_period, start_date, end_date,
                    is_completed, completed_at, completed_by, description,
                    created_by, created_at, updated_at, is_active
                FROM phishing_training_periods
                WHERE period_id = %s AND is_active = 1
                """,
                (period_id,),
            )

            if not periods:
                return None

            period = periods[0]

            # 통계 정보 추가
            period["statistics"] = self.get_period_statistics(
                period["training_year"], period["training_period"]
            )

            return period

        except Exception as e:
            raise ValueError(f"기간 조회 실패: {str(e)}")

    def create_training_period(self, data: Dict, created_by: str) -> Dict:
        """훈련 기간 생성"""
        try:
            # 유효성 검사
            required_fields = [
                "training_year",
                "training_period",
                "start_date",
                "end_date",
            ]
            for field in required_fields:
                if not data.get(field):
                    raise ValueError(f"필수 필드가 누락되었습니다: {field}")

            # 날짜 유효성 검사
            start_date = datetime.strptime(str(data["start_date"]), "%Y-%m-%d").date()
            end_date = datetime.strptime(str(data["end_date"]), "%Y-%m-%d").date()

            if start_date >= end_date:
                raise ValueError("종료일은 시작일보다 늦어야 합니다.")

            # 중복 검사
            existing = execute_query(
                """
                SELECT period_id FROM phishing_training_periods
                WHERE training_year = %s AND training_period = %s AND is_active = 1
                """,
                (data["training_year"], data["training_period"]),
            )

            if existing:
                raise ValueError(
                    f"{data['training_year']}년 {data['training_period']} 기간이 이미 존재합니다."
                )

            # 기간 생성
            result = execute_query(
                """
                INSERT INTO phishing_training_periods 
                (training_year, training_period, start_date, end_date, description, created_by)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (
                    data["training_year"],
                    data["training_period"],
                    start_date,
                    end_date,
                    data.get("description", ""),
                    created_by,
                ),
            )

            if result > 0:
                # 생성된 기간 정보 반환
                return self.get_training_period_by_id(result)
            else:
                raise ValueError("기간 생성에 실패했습니다.")

        except Exception as e:
            raise ValueError(f"기간 생성 실패: {str(e)}")

    def update_training_period(self, period_id: int, data: Dict) -> bool:
        """훈련 기간 수정"""
        try:
            # 기존 기간 존재 확인
            existing = self.get_training_period_by_id(period_id)
            if not existing:
                raise ValueError("존재하지 않는 훈련 기간입니다.")

            if existing["is_completed"]:
                raise ValueError("완료된 기간은 수정할 수 없습니다.")

            # 날짜 유효성 검사
            if data.get("start_date") and data.get("end_date"):
                start_date = datetime.strptime(
                    str(data["start_date"]), "%Y-%m-%d"
                ).date()
                end_date = datetime.strptime(str(data["end_date"]), "%Y-%m-%d").date()

                if start_date >= end_date:
                    raise ValueError("종료일은 시작일보다 늦어야 합니다.")

            # 업데이트할 필드 구성
            update_fields = []
            params = []

            updatable_fields = [
                "training_year",
                "training_period",
                "start_date",
                "end_date",
                "description",
            ]
            for field in updatable_fields:
                if field in data:
                    update_fields.append(f"{field} = %s")
                    params.append(data[field])

            if not update_fields:
                raise ValueError("수정할 데이터가 없습니다.")

            # updated_at 추가
            update_fields.append("updated_at = NOW()")
            params.append(period_id)

            query = f"""
                UPDATE phishing_training_periods 
                SET {', '.join(update_fields)}
                WHERE period_id = %s AND is_active = 1
            """

            result = execute_query(query, params)
            return result > 0

        except Exception as e:
            raise ValueError(f"기간 수정 실패: {str(e)}")

    def delete_training_period(self, period_id: int) -> bool:
        """훈련 기간 삭제 (소프트 삭제)"""
        try:
            # 기간 존재 확인
            existing = self.get_training_period_by_id(period_id)
            if not existing:
                raise ValueError("존재하지 않는 훈련 기간입니다.")

            if existing["is_completed"]:
                raise ValueError("완료된 기간은 삭제할 수 없습니다.")

            # 관련 훈련 기록이 있는지 확인
            records = execute_query(
                """
                SELECT COUNT(*) as count FROM phishing_training
                WHERE training_year = %s AND training_period = %s
                """,
                (existing["training_year"], existing["training_period"]),
            )

            if records[0]["count"] > 0:
                raise ValueError("관련 훈련 기록이 있는 기간은 삭제할 수 없습니다.")

            # 소프트 삭제
            result = execute_query(
                """
                UPDATE phishing_training_periods 
                SET is_active = 0, updated_at = NOW()
                WHERE period_id = %s
                """,
                (period_id,),
            )

            return result > 0

        except Exception as e:
            raise ValueError(f"기간 삭제 실패: {str(e)}")

    # ================== 기간 완료 처리 기능 ==================

    def complete_training_period(self, period_id: int, completed_by: str) -> Dict:
        """
        훈련 기간 완료 처리 - 기간 완료 + 미실시 사용자 성공 처리를 하나의 트랜잭션으로 처리
        """
        try:

            def complete_all_transaction(cursor):
                # 1. 기간 정보 조회 및 검증
                cursor.execute(
                    """
                    SELECT period_id, training_year, training_period, is_completed, 
                           start_date, end_date, description
                    FROM phishing_training_periods
                    WHERE period_id = %s AND is_active = 1
                    """,
                    (period_id,),
                )

                period_info = cursor.fetchone()
                if not period_info:
                    raise ValueError("존재하지 않는 훈련 기간입니다.")

                if period_info["is_completed"]:
                    raise ValueError("이미 완료된 기간입니다.")

                # 2. 미실시 사용자 목록 먼저 조회
                cursor.execute(
                    """
                    SELECT pt.user_id, u.username, u.name, pt.training_result
                    FROM phishing_training pt
                    INNER JOIN users u ON pt.user_id = u.uid
                    WHERE pt.training_year = %s 
                      AND pt.training_period = %s 
                      AND pt.training_result = 'pending'
                      AND (pt.log_type IS NULL OR pt.log_type = '')
                    """,
                    (period_info["training_year"], period_info["training_period"]),
                )

                pending_users = cursor.fetchall()
                pending_count = len(pending_users)

                # 3. 기간 완료 처리
                cursor.execute(
                    """
                    UPDATE phishing_training_periods
                    SET is_completed = 1, 
                        completed_at = NOW(), 
                        completed_by = %s, 
                        updated_at = NOW()
                    WHERE period_id = %s
                    """,
                    (completed_by, period_id),
                )

                period_updated = cursor.rowcount

                # 4. 미실시 사용자들을 성공 처리
                users_updated = 0
                if pending_count > 0:
                    cursor.execute(
                        """
                        UPDATE phishing_training pt
                        SET pt.training_result = 'pass', 
                            pt.updated_at = NOW(),
                            pt.completion_note = CONCAT(
                                COALESCE(pt.completion_note, ''), 
                                IF(pt.completion_note IS NULL OR pt.completion_note = '', '', '; '),
                                '기간 완료로 인한 자동 성공 처리 (', NOW(), ')'
                            )
                        WHERE pt.training_year = %s 
                          AND pt.training_period = %s 
                          AND pt.training_result = 'pending'
                          AND (pt.log_type IS NULL OR pt.log_type = '')
                        """,
                        (period_info["training_year"], period_info["training_period"]),
                    )
                    users_updated = cursor.rowcount

                # 5. 최종 통계 조회
                cursor.execute(
                    """
                    SELECT 
                        training_result,
                        COUNT(*) as count
                    FROM phishing_training
                    WHERE training_year = %s AND training_period = %s
                    GROUP BY training_result
                    """,
                    (period_info["training_year"], period_info["training_period"]),
                )

                final_stats = {
                    row["training_result"]: row["count"] for row in cursor.fetchall()
                }

                return {
                    "period_info": period_info,
                    "period_updated": period_updated,
                    "pending_users": pending_users,
                    "pending_count": pending_count,
                    "users_updated": users_updated,
                    "final_stats": final_stats,
                }

            result = execute_query_with_transaction(complete_all_transaction)

            # 결과 로깅
            print(f"=== 훈련 기간 완료 처리 결과 ===")
            print(
                f"기간: {result['period_info']['training_year']}년 {result['period_info']['training_period']}"
            )
            print(f"기간 업데이트: {result['period_updated']}개")
            print(f"미실시 사용자: {result['pending_count']}명")
            print(f"성공 처리된 사용자: {result['users_updated']}명")
            print(f"최종 통계: {result['final_stats']}")

            return result

        except Exception as e:
            print(f"완료 처리 실패: {str(e)}")
            raise ValueError(f"완료 처리 실패: {str(e)}")

    def reopen_training_period(self, period_id: int) -> bool:
        """훈련 기간 재개 (완료 상태 취소)"""
        try:
            result = execute_query(
                """
                UPDATE phishing_training_periods
                SET is_completed = 0, completed_at = NULL, completed_by = NULL, updated_at = NOW()
                WHERE period_id = %s AND is_active = 1
                """,
                (period_id,),
            )
            return result > 0
        except Exception as e:
            raise ValueError(f"재개 처리 실패: {str(e)}")

    # ================== 통계 및 현황 조회 기능 ==================

    def get_period_statistics(self, training_year: int, training_period: str) -> Dict:
        """특정 기간의 통계 조회"""
        try:
            stats = execute_query(
                """
                SELECT 
                    training_result,
                    COUNT(*) as count,
                    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 1) as percentage
                FROM phishing_training
                WHERE training_year = %s AND training_period = %s
                GROUP BY training_result
                ORDER BY 
                    CASE training_result 
                        WHEN 'pass' THEN 1 
                        WHEN 'fail' THEN 2 
                        WHEN 'pending' THEN 3 
                        ELSE 4 
                    END
                """,
                (training_year, training_period),
            )

            # 총 사용자 수 조회
            total_result = execute_query(
                """
                SELECT COUNT(*) as total FROM phishing_training
                WHERE training_year = %s AND training_period = %s
                """,
                (training_year, training_period),
            )

            total_users = total_result[0]["total"] if total_result else 0

            return {
                "total_users": total_users,
                "by_result": stats,
                "summary": {
                    "pass_count": next(
                        (s["count"] for s in stats if s["training_result"] == "pass"), 0
                    ),
                    "fail_count": next(
                        (s["count"] for s in stats if s["training_result"] == "fail"), 0
                    ),
                    "pending_count": next(
                        (
                            s["count"]
                            for s in stats
                            if s["training_result"] == "pending"
                        ),
                        0,
                    ),
                    "pass_rate": next(
                        (
                            s["percentage"]
                            for s in stats
                            if s["training_result"] == "pass"
                        ),
                        0,
                    ),
                    "fail_rate": next(
                        (
                            s["percentage"]
                            for s in stats
                            if s["training_result"] == "fail"
                        ),
                        0,
                    ),
                },
            }

        except Exception as e:
            raise ValueError(f"통계 조회 실패: {str(e)}")

    def get_period_completion_status(self, period_id: int) -> Dict:
        """특정 기간의 완료 처리 상태 및 상세 통계 조회"""
        try:
            # 기간 정보 조회
            period_info = self.get_training_period_by_id(period_id)
            if not period_info:
                raise ValueError("존재하지 않는 훈련 기간입니다.")

            # 상세 통계 조회 (로그 타입별)
            detailed_stats = execute_query(
                """
                SELECT 
                    training_result,
                    log_type,
                    COUNT(*) as count
                FROM phishing_training
                WHERE training_year = %s AND training_period = %s
                GROUP BY training_result, log_type
                ORDER BY training_result, log_type
                """,
                (period_info["training_year"], period_info["training_period"]),
            )

            # 최근 활동 조회
            recent_activities = execute_query(
                """
                SELECT 
                    u.username, u.name, pt.training_result, pt.log_type,
                    pt.action_time, pt.updated_at
                FROM phishing_training pt
                INNER JOIN users u ON pt.user_id = u.uid
                WHERE pt.training_year = %s AND pt.training_period = %s
                ORDER BY pt.updated_at DESC
                LIMIT 10
                """,
                (period_info["training_year"], period_info["training_period"]),
            )

            return {
                "period_info": period_info,
                "statistics": period_info["statistics"],
                "detailed_stats": detailed_stats,
                "recent_activities": recent_activities,
            }

        except Exception as e:
            raise ValueError(f"완료 상태 조회 실패: {str(e)}")

    def get_training_summary(self, year: Optional[int] = None) -> Dict:
        """전체 훈련 요약 통계 (관리자용)"""
        try:
            current_year = year or datetime.now().year

            # 연도별 기간 통계
            year_stats = execute_query(
                """
                SELECT 
                    tp.training_year,
                    tp.training_period,
                    tp.is_completed,
                    COUNT(pt.user_id) as total_users,
                    SUM(CASE WHEN pt.training_result = 'pass' THEN 1 ELSE 0 END) as pass_count,
                    SUM(CASE WHEN pt.training_result = 'fail' THEN 1 ELSE 0 END) as fail_count,
                    SUM(CASE WHEN pt.training_result = 'pending' THEN 1 ELSE 0 END) as pending_count
                FROM phishing_training_periods tp
                LEFT JOIN phishing_training pt ON 
                    tp.training_year = pt.training_year AND 
                    tp.training_period = pt.training_period
                WHERE tp.training_year = %s AND tp.is_active = 1
                GROUP BY tp.training_year, tp.training_period, tp.is_completed
                ORDER BY tp.training_period
                """,
                (current_year,),
            )

            # 전체 완료율 계산
            total_users = sum(stat["total_users"] or 0 for stat in year_stats)
            total_pass = sum(stat["pass_count"] or 0 for stat in year_stats)
            overall_pass_rate = (
                (total_pass / total_users * 100) if total_users > 0 else 0
            )

            return {
                "year": current_year,
                "overall_statistics": {
                    "total_users": total_users,
                    "total_pass": total_pass,
                    "overall_pass_rate": round(overall_pass_rate, 1),
                },
                "period_statistics": year_stats,
            }

        except Exception as e:
            raise ValueError(f"요약 통계 조회 실패: {str(e)}")

    # ================== 훈련 기록 관리 기능 ==================

    def get_training_status(self, username: str, year: int) -> Dict:
        """사용자의 악성메일 모의훈련 현황 조회"""
        try:
            # 사용자 정보 조회
            user_result = execute_query(
                "SELECT uid, username, name FROM users WHERE username = %s", (username,)
            )

            if not user_result:
                raise ValueError("사용자를 찾을 수 없습니다.")

            user = user_result[0]

            # 훈련 기록 조회
            training_records = execute_query(
                """
                SELECT 
                    training_year, training_period, email_template, log_type,
                    email_sent_time, action_time, training_result, client_ip,
                    response_time_minutes, completion_note
                FROM phishing_training
                WHERE user_id = %s AND training_year = %s
                ORDER BY training_period
                """,
                (user["uid"], year),
            )

            # 기간별 현황 요약
            periods = ["first_half", "second_half"]
            status_summary = {}

            for period in periods:
                record = next(
                    (r for r in training_records if r["training_period"] == period),
                    None,
                )
                if record:
                    status_summary[period] = {
                        "status": record["training_result"],
                        "email_template": record["email_template"],
                        "log_type": record["log_type"],
                        "action_time": record["action_time"],
                        "response_time_minutes": record["response_time_minutes"],
                    }
                else:
                    status_summary[period] = {
                        "status": "not_assigned",
                        "email_template": None,
                        "log_type": None,
                        "action_time": None,
                        "response_time_minutes": None,
                    }

            return {
                "user": user,
                "year": year,
                "records": training_records,
                "summary": status_summary,
            }

        except Exception as e:
            raise ValueError(f"훈련 현황 조회 실패: {str(e)}")

    def get_all_training_records(
        self,
        year: int,
        period: Optional[str] = None,
        result: Optional[str] = None,
        page: int = 1,
        page_size: int = 50,
    ) -> Dict:
        """모든 모의훈련 기록 조회 (관리자용) - 페이지네이션 지원"""
        try:
            conditions = ["pt.training_year = %s"]
            params = [year]

            if period:
                conditions.append("pt.training_period = %s")
                params.append(period)

            if result:
                conditions.append("pt.training_result = %s")
                params.append(result)

            where_clause = "WHERE " + " AND ".join(conditions)

            # 전체 개수 조회
            count_query = f"""
                SELECT COUNT(*) as total
                FROM phishing_training pt
                INNER JOIN users u ON pt.user_id = u.uid
                {where_clause}
            """

            total_result = execute_query(count_query, params)
            total_count = total_result[0]["total"]

            # 페이지네이션 계산
            offset = (page - 1) * page_size
            total_pages = (total_count + page_size - 1) // page_size

            # 데이터 조회
            data_query = f"""
                SELECT 
                    pt.user_id, u.username, u.name, u.department,
                    pt.training_year, pt.training_period, pt.email_template,
                    pt.log_type, pt.email_sent_time, pt.action_time,
                    pt.training_result, pt.client_ip, pt.response_time_minutes,
                    pt.completion_note, pt.created_at, pt.updated_at
                FROM phishing_training pt
                INNER JOIN users u ON pt.user_id = u.uid
                {where_clause}
                ORDER BY pt.training_year DESC, pt.training_period DESC, u.username
                LIMIT %s OFFSET %s
            """

            params.extend([page_size, offset])
            records = execute_query(data_query, params)

            return {
                "records": records,
                "pagination": {
                    "current_page": page,
                    "total_pages": total_pages,
                    "page_size": page_size,
                    "total_count": total_count,
                    "has_next": page < total_pages,
                    "has_prev": page > 1,
                },
                "filters": {"year": year, "period": period, "result": result},
            }

        except Exception as e:
            raise ValueError(f"훈련 기록 조회 실패: {str(e)}")

    def create_training_record(self, data: Dict) -> bool:
        """개별 훈련 기록 생성"""
        try:
            # 필수 필드 검증
            required_fields = ["user_id", "training_year", "training_period"]
            for field in required_fields:
                if not data.get(field):
                    raise ValueError(f"필수 필드가 누락되었습니다: {field}")

            # 중복 검사
            existing = execute_query(
                """
                SELECT 1 FROM phishing_training
                WHERE user_id = %s AND training_year = %s AND training_period = %s
                """,
                (data["user_id"], data["training_year"], data["training_period"]),
            )

            if existing:
                raise ValueError("이미 해당 사용자의 훈련 기록이 존재합니다.")

            # 기본값 설정
            training_result = data.get("training_result", "pending")

            # 응답시간 계산
            response_time_minutes = None
            if data.get("email_sent_time") and data.get("action_time"):
                try:
                    sent_time = datetime.fromisoformat(str(data["email_sent_time"]))
                    action_time = datetime.fromisoformat(str(data["action_time"]))
                    response_time_minutes = int(
                        (action_time - sent_time).total_seconds() / 60
                    )
                except:
                    pass

            # 훈련 기록 생성
            result = execute_query(
                """
                INSERT INTO phishing_training 
                (user_id, training_year, training_period, email_template, log_type,
                 email_sent_time, action_time, training_result, client_ip, 
                 response_time_minutes, completion_note)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    data["user_id"],
                    data["training_year"],
                    data["training_period"],
                    data.get("email_template"),
                    data.get("log_type"),
                    data.get("email_sent_time"),
                    data.get("action_time"),
                    training_result,
                    data.get("client_ip"),
                    response_time_minutes,
                    data.get("completion_note"),
                ),
            )

            return result > 0

        except Exception as e:
            raise ValueError(f"훈련 기록 생성 실패: {str(e)}")

    def update_training_record(self, data: Dict) -> bool:
        """개별 모의훈련 기록 수정"""
        try:
            # 필수 필드 검증
            required_fields = ["user_id", "training_year", "training_period"]
            for field in required_fields:
                if not data.get(field):
                    raise ValueError(f"필수 필드가 누락되었습니다: {field}")

            # 기존 기록 존재 확인
            existing = execute_query(
                """
                SELECT 1 FROM phishing_training
                WHERE user_id = %s AND training_year = %s AND training_period = %s
                """,
                (data["user_id"], data["training_year"], data["training_period"]),
            )

            if not existing:
                raise ValueError("수정할 훈련 기록을 찾을 수 없습니다.")

            # 응답시간 재계산
            response_time_minutes = data.get("response_time_minutes")
            if data.get("email_sent_time") and data.get("action_time"):
                try:
                    sent_time = datetime.fromisoformat(str(data["email_sent_time"]))
                    action_time = datetime.fromisoformat(str(data["action_time"]))
                    response_time_minutes = int(
                        (action_time - sent_time).total_seconds() / 60
                    )
                except:
                    pass

            # 기록 수정
            result = execute_query(
                """
                UPDATE phishing_training 
                SET email_template = %s, log_type = %s, email_sent_time = %s,
                    action_time = %s, training_result = %s, client_ip = %s,
                    response_time_minutes = %s, completion_note = %s, updated_at = NOW()
                WHERE user_id = %s AND training_year = %s AND training_period = %s
                """,
                (
                    data.get("email_template"),
                    data.get("log_type"),
                    data.get("email_sent_time"),
                    data.get("action_time"),
                    data.get("training_result", "pending"),
                    data.get("client_ip"),
                    response_time_minutes,
                    data.get("completion_note"),
                    data["user_id"],
                    data["training_year"],
                    data["training_period"],
                ),
            )

            return result > 0

        except Exception as e:
            raise ValueError(f"훈련 기록 수정 실패: {str(e)}")

    def delete_training_record(
        self, user_id: int, training_year: int, training_period: str
    ) -> bool:
        """모의훈련 기록 삭제"""
        try:
            result = execute_query(
                """
                DELETE FROM phishing_training
                WHERE user_id = %s AND training_year = %s AND training_period = %s
                """,
                (user_id, training_year, training_period),
            )

            return result > 0

        except Exception as e:
            raise ValueError(f"훈련 기록 삭제 실패: {str(e)}")

    # ================== 일괄 처리 기능 ==================

    def get_training_excel_template(self) -> str:
        """모의훈련 업로드 템플릿 생성"""
        output = io.StringIO()
        writer = csv.writer(output)

        # 헤더 작성
        headers = [
            "username",
            "training_year",
            "training_period",
            "email_template",
            "log_type",
            "email_sent_time",
            "action_time",
            "training_result",
            "client_ip",
            "completion_note",
        ]
        writer.writerow(headers)

        # 샘플 데이터
        sample_row = [
            "user01",
            "2025",
            "first_half",
            "악성 메일 클릭",
            "스크립트 첨부파일 열람",
            "2025-03-01 09:00:00",
            "2025-03-01 09:15:00",
            "fail",
            "192.168.1.100",
            "첨부파일 실행으로 인한 실패",
        ]
        writer.writerow(sample_row)

        return output.getvalue()

    def bulk_upload_training_records(self, csv_data: str, uploaded_by: str) -> Dict:
        """CSV 데이터를 통한 훈련 기록 일괄 업로드"""
        try:
            # CSV 파싱
            csv_reader = csv.DictReader(io.StringIO(csv_data))

            success_records = []
            error_records = []

            for row_num, record in enumerate(csv_reader, start=2):  # 헤더 다음부터
                try:
                    # 사용자 조회
                    user_result = execute_query(
                        "SELECT uid, username, name FROM users WHERE username = %s",
                        (record.get("username", "").strip(),),
                    )

                    if not user_result:
                        error_records.append(
                            {
                                "row": row_num,
                                "record": record,
                                "error": f"사용자 '{record.get('username')}' 을 찾을 수 없습니다.",
                            }
                        )
                        continue

                    user = user_result[0]

                    # 기간 변환
                    period_map = {
                        "상반기": "first_half",
                        "하반기": "second_half",
                        "first_half": "first_half",
                        "second_half": "second_half",
                    }

                    training_period = period_map.get(
                        record.get("training_period", "").strip()
                    )
                    if not training_period:
                        error_records.append(
                            {
                                "row": row_num,
                                "record": record,
                                "error": f"훈련 기간 '{record.get('training_period')}' 이 유효하지 않습니다.",
                            }
                        )
                        continue

                    # 훈련 결과 결정
                    training_result = "pending"
                    if record.get("log_type", "").strip():
                        training_result = "fail"  # 로그유형이 있으면 실패
                    elif (
                        record.get("email_sent_time", "").strip()
                        and not record.get("action_time", "").strip()
                    ):
                        training_result = "pass"  # 메일 발송했지만 액션이 없으면 통과
                    elif record.get("training_result", "").strip():
                        training_result = record["training_result"].strip()

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
                            pass

                    # 데이터 준비
                    training_data = {
                        "user_id": user["uid"],
                        "training_year": int(
                            record.get("training_year", datetime.now().year)
                        ),
                        "training_period": training_period,
                        "email_template": record.get("email_template", "").strip(),
                        "log_type": record.get("log_type", "").strip(),
                        "email_sent_time": record.get("email_sent_time", "").strip()
                        or None,
                        "action_time": record.get("action_time", "").strip() or None,
                        "training_result": training_result,
                        "client_ip": record.get("client_ip", "").strip(),
                        "response_time_minutes": response_time_minutes,
                        "completion_note": record.get("completion_note", "").strip(),
                    }

                    # 중복 체크 및 업데이트/삽입
                    existing = execute_query(
                        """
                        SELECT 1 FROM phishing_training
                        WHERE user_id = %s AND training_year = %s AND training_period = %s
                        """,
                        (
                            training_data["user_id"],
                            training_data["training_year"],
                            training_data["training_period"],
                        ),
                    )

                    if existing:
                        # 기존 기록 업데이트
                        self.update_training_record(training_data)
                        success_records.append(
                            {
                                "row": row_num,
                                "action": "updated",
                                "username": user["username"],
                                "year": training_data["training_year"],
                                "period": training_data["training_period"],
                            }
                        )
                    else:
                        # 새 기록 생성
                        self.create_training_record(training_data)
                        success_records.append(
                            {
                                "row": row_num,
                                "action": "created",
                                "username": user["username"],
                                "year": training_data["training_year"],
                                "period": training_data["training_period"],
                            }
                        )

                except Exception as e:
                    error_records.append(
                        {"row": row_num, "record": record, "error": str(e)}
                    )

            return {
                "success_count": len(success_records),
                "error_count": len(error_records),
                "success_records": success_records,
                "error_records": error_records,
                "uploaded_by": uploaded_by,
                "uploaded_at": datetime.now().isoformat(),
            }

        except Exception as e:
            raise ValueError(f"일괄 업로드 실패: {str(e)}")

    def export_training_data(
        self, year: int, period: Optional[str] = None, result: Optional[str] = None
    ) -> str:
        """훈련 데이터 CSV 내보내기"""
        try:
            records = self.get_all_training_records(
                year=year,
                period=period,
                result=result,
                page=1,
                page_size=10000,  # 대용량 처리
            )["records"]

            output = io.StringIO()
            writer = csv.writer(output)

            # 헤더 작성
            headers = [
                "사용자명",
                "이름",
                "부서",
                "훈련연도",
                "훈련기간",
                "이메일템플릿",
                "로그유형",
                "메일발송시간",
                "액션시간",
                "훈련결과",
                "클라이언트IP",
                "응답시간(분)",
                "완료메모",
                "생성일시",
                "수정일시",
            ]
            writer.writerow(headers)

            # 데이터 작성
            for record in records:
                row = [
                    record["username"],
                    record["name"],
                    record.get("department", ""),
                    record["training_year"],
                    record["training_period"],
                    record.get("email_template", ""),
                    record.get("log_type", ""),
                    record.get("email_sent_time", ""),
                    record.get("action_time", ""),
                    record["training_result"],
                    record.get("client_ip", ""),
                    record.get("response_time_minutes", ""),
                    record.get("completion_note", ""),
                    record.get("created_at", ""),
                    record.get("updated_at", ""),
                ]
                writer.writerow(row)

            return output.getvalue()

        except Exception as e:
            raise ValueError(f"데이터 내보내기 실패: {str(e)}")

    # ================== 옵션 데이터 제공 ==================

    def get_period_options(self) -> List[Dict]:
        """훈련 기간 옵션 목록"""
        return [
            {"value": "first_half", "label": "상반기"},
            {"value": "second_half", "label": "하반기"},
        ]

    def get_result_options(self) -> List[Dict]:
        """훈련 결과 옵션 목록"""
        return [
            {"value": "pass", "label": "통과"},
            {"value": "fail", "label": "실패"},
            {"value": "pending", "label": "미실시"},
        ]

    def get_available_years(self) -> List[int]:
        """사용 가능한 훈련 연도 목록"""
        try:
            years = execute_query(
                """
                SELECT DISTINCT training_year 
                FROM phishing_training_periods 
                WHERE is_active = 1
                ORDER BY training_year DESC
                """
            )
            return [year["training_year"] for year in years]
        except:
            current_year = datetime.now().year
            return [current_year - 1, current_year, current_year + 1]

    # ================== 유틸리티 함수 ==================

    def validate_period_data(self, data: Dict) -> bool:
        """기간 데이터 유효성 검사"""
        required_fields = ["training_year", "training_period", "start_date", "end_date"]

        for field in required_fields:
            if not data.get(field):
                raise ValueError(f"필수 필드가 누락되었습니다: {field}")

        # 날짜 형식 검사
        try:
            start_date = datetime.strptime(str(data["start_date"]), "%Y-%m-%d")
            end_date = datetime.strptime(str(data["end_date"]), "%Y-%m-%d")

            if start_date >= end_date:
                raise ValueError("종료일은 시작일보다 늦어야 합니다.")

        except ValueError as e:
            if "time data" in str(e):
                raise ValueError("날짜 형식이 올바르지 않습니다. (YYYY-MM-DD)")
            raise e

        # 기간 값 검사
        valid_periods = ["first_half", "second_half"]
        if data["training_period"] not in valid_periods:
            raise ValueError(
                f"훈련 기간은 {', '.join(valid_periods)} 중 하나여야 합니다."
            )

        return True
