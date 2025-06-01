from flask import Blueprint, request, jsonify, Response, render_template_string
from email_validator import validate_email, EmailNotValidError
from services.subscribe_service import subscribe, unsubscribe
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
        subscribe(email)
        return f"Subscribed {email}", 200
    except Exception as e:
        logger.exception("Subscribe failed")
        return f"Subscribe failed: {e}", 500

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