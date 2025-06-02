import requests
from flask import Blueprint, request, jsonify, Response, render_template_string, render_template
from email_validator import validate_email, EmailNotValidError

from services.database_service import get_all_account_breaches, get_account_record, subscribe, unsubscribe
from config import logger

sub_bp = Blueprint('subscribe', __name__)

subscribe_form_html = """
        <form method="POST">
            <p>Subscribe to receive automatic alerts about security breaches associated with your email address.</p>
            <input name="email" type="email" />
            <input type="submit" value="Subscribe" />
        </form>
    """

unsubscribe_form_html = """
        <form method="POST">
            <p>Unsubscribe from breach alerts.</p>
            <input name="email" type="email" required />
            <input type="submit" value="Unsubscribe" />
        </form>
    """

@sub_bp.route('/subscribe', methods=['GET', 'POST'])
def subscribe_route():
    if request.method == 'GET':
        return render_template_string(subscribe_form_html)

    # POST handling
    data = request.form if not request.is_json else request.get_json()
    email = data.get('email')

    if not email:
        return "Email is required", 400

    try:
        email_info = validate_email(email)
        email = email_info.normalized
    except EmailNotValidError as e:
        return str(e), 400

    try:
        if not get_account_record(email):
            subscribe(email)
    except Exception as e:
        logger.exception("Subscribe failed")
        return f"Subscribe failed: {e}", 500

    try:
        # Send internal POST to update breaches
        resp = requests.post("http://localhost:5000/hibp/update/account/breaches", json={"email": email})
        if resp.status_code != 200:
            return f"Breaches update failed: {resp.json()}", 500
    except Exception as e:
        logger.exception("Breaches update failed")
        return f"Breaches update failed: {e}", 500

    try:
        breaches = get_all_account_breaches(email)
        breaches = sorted(breaches, key=lambda b: b['breach_date'], reverse=True)
        print(breaches)
        return render_template("subscribe/subscribe.html", email=email, breaches=breaches)
    except Exception as e:
        logger.exception("Failed to get account breaches for new subscriber")
        return f"New subscriber breach check failed: {e}", 500

@sub_bp.route('/unsubscribe', methods=['GET', 'POST'])
def unsubscribe_route():
    if request.method == 'GET':
        return render_template_string(unsubscribe_form_html)

    # POST handling
    data = request.form if not request.is_json else request.get_json()
    email = data.get('email')

    if not email:
        return "Email is required", 400

    try:
        email_info = validate_email(email)
        email = email_info.normalized
    except EmailNotValidError as e:
        return str(e), 400

    try:
        unsubscribe(email)
        return f"Unsubscribed {email}", 200
    except Exception as e:
        logger.exception("Unsubscribe failed")
        return f"Unsubscribe failed: {e}", 500