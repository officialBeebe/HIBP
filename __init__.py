from flask import Flask
from config import config

from routes.subscribe_route import sub_bp
from routes.hibp_route import hibp_bp

def create_app(_config=config):
    app = Flask(__name__)
    app.secret_key = _config.SERVICE_SECRET_KEY

    app.register_blueprint(sub_bp)
    app.register_blueprint(hibp_bp)

    @app.route('/', methods=['GET'])
    def index_route():
        return '''
                <h1>Welcome to the Have I Been Pwned Alert App!</h1>
                <p><a href="/subscribe">Subscribe</a> | <a href="/unsubscribe">Unsubscribe</a></p>
            '''

    return app