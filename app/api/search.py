from flask import jsonify, request, abort
from flask_login import current_user
from app import Config
from app.api import bp
from app.api.auth import token_auth
from app.api.errors import bad_request
import requests


@bp.route('/search', methods=['GET'])
@token_auth.login_required
def search():
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    album = request.args.get('album')
    artist = request.args.get('artist')
    params = {
        'page': page,
        'limit': per_page,
        'api_key': Config.LAST_API_KEY,
        'format': 'json'
    }

    if album is not None:
        params['method'] = 'album.search'
        params['album'] = album
    elif artist is not None:
        params['method'] = 'artist.search'
        params['artist'] = artist
    else:
        return bad_request('please provide a album or artist')

    r = requests.get(Config.LAST_API_URL, params=params)

    return jsonify(r.json())

    
