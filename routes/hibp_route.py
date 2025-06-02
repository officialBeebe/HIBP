import json
from collections import OrderedDict

from flask import Blueprint, request, jsonify, Response
from email_validator import validate_email, EmailNotValidError
from services.database_service import get_account_record, get_all_account_breaches, upsert_breach, upsert_account_breach
from api.hibp_api import hibp  # helper wrapping the requests logic
from config import logger

hibp_bp = Blueprint('hibp', __name__)

@hibp_bp.route('/hibp/update/account/breaches', methods=['POST'])
def update_account_breaches_route():
    data = request.get_json(silent=True)
    if not data or 'email' not in data:
        return jsonify({'error': 'Missing email'}), 400

    try:
        email_info = validate_email(data['email'])
        email = email_info.normalized
    except EmailNotValidError as e:
        return jsonify({'error': str(e)}), 400

    breaches = hibp(email)
    if breaches is None:
        return jsonify({'error': f'Failed to retrieve breaches for {email}'}), 502

    account = get_account_record(email)
    if not account:
        return jsonify({'error': f'No account found for {email}'}), 404

    try:
        for breach in breaches:
            breach_id = upsert_breach(breach)
            upsert_account_breach(account, breach_id)
    except Exception as e:
        logger.error(f"Failed to upsert breaches {email}:{e}")
        return jsonify({"error": str(e)}), 500

    return jsonify({'status': 'updated'}), 200



@hibp_bp.route('/hibp/account/breaches', methods=['GET'])
def account_breaches_route():
    email = request.args.get('email')
    if not email:
        return jsonify({'error': 'Missing email'}), 400

    try:
        email_info = validate_email(email)
        email = email_info.normalized
    except EmailNotValidError as e:
        return jsonify({'error': str(e)}), 400

    account_breaches = get_all_account_breaches(email)
    # return jsonify({email: account_breaches})

    # Fix to return JSON in an ordered format
    ordered_breaches = []

    for breach in account_breaches:
        # Convert datetime to RFC 1123 format or ISO 8601
        dt = breach["breach_date"]
        modified_str = dt.strftime("%a, %d %b %Y %H:%M:%S GMT") if hasattr(dt, 'strftime') else str(dt)

        ordered_breaches.append(OrderedDict([
            ("name", breach["name"]),
            ("breach_date", modified_str),
            ("data_classes", breach["data_classes"]),
            ("description", breach["description"]),
        ]))

    payload = OrderedDict([
        (email, ordered_breaches)
    ])

    return Response(json.dumps(payload), mimetype='application/json')