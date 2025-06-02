import requests
from flask import Blueprint, request, jsonify, Response, render_template_string, render_template
from email_validator import validate_email, EmailNotValidError

from forms import SubscribeForm, UnsubscribeForm
from services.database_service import get_all_account_breaches, get_account_record, add_account, delete_account
from config import logger, config

sub_bp = Blueprint('subscribe', __name__)

from forms import SubscribeForm
from flask import render_template

@sub_bp.route('/subscribe', methods=['GET', 'POST'])
def subscribe_route():
    form = SubscribeForm()

    if form.validate_on_submit():
        email = form.email.data.strip().lower()

        # Email validation using `email_validator`
        try:
            email_info = validate_email(email)
            email = email_info.normalized
        except EmailNotValidError as e:
            form.email.errors.append(str(e))
            return render_template("subscribe/subscribe_form.html", form=form)

        # Ensure account exists
        try:
            if not get_account_record(email):
                add_account(email)
        except Exception as e:
            logger.exception(f"Failed to subscribe user {email}")
            return f"Subscribe failed: {e}", 500

        # Attempt to fetch breaches
        breaches = []
        try:
            resp = requests.post("http://localhost:5000/hibp/update/account/breaches", json={"email": email})
            if resp.status_code == 200:
                breaches = get_all_account_breaches(email)
                breaches = sorted(breaches, key=lambda b: b['breach_date'], reverse=True)
            elif resp.status_code == 204:
                logger.info(f"No breaches found for {email}")
            else:
                return f"Breaches update failed: {resp.text}", 500
        except Exception as e:
            logger.exception("Breaches update failed")
            return f"Breaches update failed: {e}", 500

        # Show success view
        return render_template("subscribe/subscribe_success.html", email=email, breaches=breaches)

    return render_template("subscribe/subscribe_form.html", form=form)


@sub_bp.route('/unsubscribe', methods=['GET', 'POST'])
def unsubscribe_route():
    form = UnsubscribeForm()

    if form.validate_on_submit():
        email = form.email.data.strip().lower()
        try:
            email_info = validate_email(email)
            email = email_info.normalized
        except EmailNotValidError as e:
            form.email.errors.append(str(e))
            return render_template("unsubscribe/unsubscribe_form.html", form=form)

        try:
            delete_account(email)
            return render_template("unsubscribe/unsubscribe_success.html", email=email)
        except Exception as e:
            logger.exception(f"Unsubscribe failed for {email}")
            return f"Unsubscribe failed: {e}", 500

    return render_template("unsubscribe/unsubscribe_form.html", form=form)

