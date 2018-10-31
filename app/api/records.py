from flask import jsonify, request, abort
from flask_login import current_user
from app.api import bp
from app.api.auth import token_auth
from app.models import Record, User


@bp.route('/records', methods=['GET'])
@token_auth.login_required
def get_records():
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    data = Record.to_collection_dict(
        Record.query, page, per_page, 'api.get_records')
    return jsonify(data)


@bp.route('/records/mine', methods=['GET'])
@token_auth.login_required
def get_my_records():
    user = User.check_token(request.headers.get('Authorization').split(" ")[1])
    if not user:
        abort(401)
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    data = Record.to_collection_dict(Record.query.filter_by(
        user_id=user.id), page, per_page, 'api.get_my_records')
    return jsonify(data)


@bp.route('/records/<int:id>', methods=['GET'])
@token_auth.login_required
def get_record(id):
    return jsonify(Record.query.get_or_404(id).to_dict())
