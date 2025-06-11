# manual_check_controller.py
# back-end/app/controllers/ 폴더에 생성

from flask import Blueprint, request, jsonify, send_file
from app.services.manual_check_service import ManualCheckService
from app.utils.decorators import token_required, handle_exceptions
import io
from datetime import datetime

manual_check_bp = Blueprint('manual_check', __name__)
manual_check_service = ManualCheckService()


@manual_check_bp.route('/template', methods=['GET'])
@handle_exceptions
def download_template():
    """엑셀 업로드 템플릿 다운로드"""
    template_data = manual_check_service.get_excel_template()

    output = io.BytesIO()
    output.write(template_data.encode('utf-8-sig'))
    output.seek(0)

    return send_file(output, mimetype='text/csv', as_attachment=True,
                     download_name='manual_check_template.csv')


@manual_check_bp.route('/bulk-upload', methods=['POST'])
@token_required
@handle_exceptions
def bulk_upload():
    """엑셀 파일 일괄 업로드"""
    if 'file' not in request.files:
        return jsonify({'error': '파일이 업로드되지 않았습니다.'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': '파일이 선택되지 않았습니다.'}), 400

    try:
        result = manual_check_service.process_bulk_upload(
            file=file, uploaded_by=request.current_user['username'])
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@manual_check_bp.route('/results', methods=['GET'])
@token_required
@handle_exceptions
def get_check_results():
    """점검 결과 목록 조회"""
    year = request.args.get('year', datetime.now().year)
    period = request.args.get('period')
    department = request.args.get('department')
    result_filter = request.args.get('result')
    page = int(request.args.get('page', 1))
    size = int(request.args.get('size', 20))

    results = manual_check_service.get_check_results(year=year, period=period,
                                                     department=department,
                                                     result_filter=result_filter,
                                                     page=page, size=size)
    return jsonify(results)


@manual_check_bp.route('/results/<int:check_id>', methods=['PUT'])
@token_required
@handle_exceptions
def update_check_result(check_id):
    """점검 결과 수정"""
    data = request.json
    result = manual_check_service.update_check_result(
        check_id=check_id, update_data=data,
        updated_by=request.current_user['username'])
    return jsonify(result)


@manual_check_bp.route('/results/<int:check_id>', methods=['DELETE'])
@token_required
@handle_exceptions
def delete_check_result(check_id):
    """점검 결과 삭제"""
    result = manual_check_service.delete_check_result(check_id)
    return jsonify(result)


@manual_check_bp.route('/stats', methods=['GET'])
@token_required
@handle_exceptions
def get_check_statistics():
    """점검 통계 조회"""
    year = request.args.get('year', datetime.now().year)
    period = request.args.get('period')

    stats = manual_check_service.get_check_statistics(year, period)
    return jsonify(stats)


@manual_check_bp.route('/export', methods=['GET'])
@token_required
@handle_exceptions
def export_results():
    """점검 결과 내보내기"""
    year = request.args.get('year')
    period = request.args.get('period')

    csv_data = manual_check_service.export_results_to_csv(year, period)

    return send_file(io.BytesIO(csv_data.encode('utf-8-sig')), mimetype='text/csv',
                     as_attachment=True,
                     download_name=f'manual_check_results_{year}_{period}.csv')