from flask import Flask
from routes.hibp import hibp_bp
from routes.subscribe import sub_bp

app = Flask("Have I Been Pwned Alert Service")

@app.route('/', methods=['GET'])
def index_route():
    return '''
            <h1>Welcome to the Have I Been Pwned Alert App!</h1>
            <p><a href="/subscribe">Subscribe</a> | <a href="/unsubscribe">Unsubscribe</a></p>
        '''

# Register blueprints
app.register_blueprint(hibp_bp)
app.register_blueprint(sub_bp)

if __name__ == '__main__':
    app.run()
