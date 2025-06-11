# back-end/app/routes/manual_check_periods.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.manual_check_period_service import ManualCheckPeriodService

manual_check_periods_bp = Blueprint('manual_check_periods', __name__)
period_service = ManualCheckPeriodService()


@manual_check_periods_bp.route('/periods', methods=['GET'])
@jwt_required()
def get_periods():
    """기간 목록 조회"""
    try:
        year = request.args.get('year', type=int)
        check_type = request.args.get('check_type')
        
        periods = period_service.get_periods(year, check_type)
        
        return jsonify({
            "success": True,
            "data": periods
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@manual_check_periods_bp.route('/periods/status', methods=['GET'])
@jwt_required()
def get_period_status():
    """기간 상태 요약 조회"""
    try:
        year = request.args.get('year', type=int)
        
        status = period_service.get_current_status(year)
        
        return jsonify({
            "success": True,
            "data": status
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@manual_check_periods_bp.route('/periods', methods=['POST'])
@jwt_required()
def create_period():
    """기간 생성"""
    try:
        current_user = get_jwt_identity()
        data = request.get_json()
        
        # 필수 필드 검증
        required_fields = ['check_type', 'period_year', 'period_name', 'start_date', 'end_date']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    "success": False,
                    "error": f"필수 필드가 누락되었습니다: {field}"
                }), 400
        
        # 점검 유형 검증
        if data['check_type'] not in period_service.CHECK_TYPES:
            return jsonify({
                "success": False,
                "error": "올바르지 않은 점검 유형입니다."
            }), 400
        
        data['created_by'] = current_user['username']
        
        period_service.create_period(data)
        
        return jsonify({
            "success": True,
            "message": "기간이 성공적으로 생성되었습니다."
        })
    except ValueError as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@manual_check_periods_bp.route('/periods/<int:period_id>', methods=['PUT'])
@jwt_required()
def update_period(period_id):
    """기간 수정"""
    try:
        data = request.get_json()
        
        # 필수 필드 검증
        required_fields = ['period_name', 'start_date', 'end_date']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    "success": False,
                    "error": f"필수 필드가 누락되었습니다: {field}"
                }), 400
        
        period_service.update_period(period_id, data)
        
        return jsonify({
            "success": True,
            "message": "기간이 성공적으로 수정되었습니다."
        })
    except ValueError as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@manual_check_periods_bp.route('/periods/<int:period_id>', methods=['DELETE'])
@jwt_required()
def delete_period(period_id):
    """기간 삭제"""
    try:
        period_service.delete_period(period_id)
        
        return jsonify({
            "success": True,
            "message": "기간이 성공적으로 삭제되었습니다."
        })
    except ValueError as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@manual_check_periods_bp.route('/periods/<int:period_id>/complete', methods=['POST'])
@jwt_required()
def complete_period(period_id):
    """기간 완료 처리"""
    try:
        current_user = get_jwt_identity()
        
        period_service.complete_period(period_id, current_user['username'])
        
        return jsonify({
            "success": True,
            "message": "기간이 완료 처리되었습니다. 미실시 사용자들이 자동으로 통과 처리되었습니다."
        })
    except ValueError as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@manual_check_periods_bp.route('/periods/<int:period_id>/reopen', methods=['POST'])
@jwt_required()
def reopen_period(period_id):
    """기간 재개"""
    try:
        period_service.reopen_period(period_id)
        
        return jsonify({
            "success": True,
            "message": "기간이 재개되었습니다. 자동 통과 처리된 결과가 삭제되었습니다."
        })
    except ValueError as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@manual_check_periods_bp.route('/periods/check-types', methods=['GET'])
@jwt_required()
def get_check_types():
    """점검 유형 목록 조회"""
    return jsonify({
        "success": True,
        "data": [
            {"value": key, "label": value}
            for key, value in period_service.CHECK_TYPES.items()
        ]
    })


@manual_check_periods_bp.route('/periods/expired', methods=['GET'])
@jwt_required()
def get_expired_periods():
    """만료된 기간 조회 (자동 완료 처리 대상)"""
    try:
        expired_periods = period_service.get_expired_periods()
        
        return jsonify({
            "success": True,
            "data": expired_periods
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500