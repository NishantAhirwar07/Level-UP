import os
from flask import Flask, render_template, jsonify
from config import Config
from extensions import db, csrf, limiter


def create_app(config_object=Config):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_object)

    # Flask's instance directory is not guaranteed to exist on a fresh deploy.
    os.makedirs(app.instance_path, exist_ok=True)

    db.init_app(app)
    csrf.init_app(app)
    limiter.init_app(app)

    from routes.auth import auth_bp
    from routes.dashboard import dashboard_bp
    from routes.tasks import tasks_bp
    from routes.habits import habits_bp
    from routes.finance import finance_bp
    from routes.budgets import budgets_bp
    from routes.reports import reports_bp
    for blueprint in (auth_bp, dashboard_bp, tasks_bp, habits_bp, finance_bp, budgets_bp, reports_bp):
        app.register_blueprint(blueprint)

    @app.get('/health')
    def health():
        return jsonify(status='ok'), 200

    @app.errorhandler(400)
    def bad_request(_):
        return render_template('error.html', code=400, message='Please check your submitted information.'), 400

    @app.errorhandler(403)
    def forbidden(_):
        return render_template('error.html', code=403, message='You do not have permission to view this page.'), 403

    @app.errorhandler(404)
    def not_found(_):
        return render_template('error.html', code=404, message='The page or record was not found.'), 404

    @app.errorhandler(429)
    def rate_limited(_):
        return render_template('error.html', code=429, message='Too many attempts. Please wait and try again.'), 429

    @app.errorhandler(500)
    def server_error(error):
        app.logger.exception('Unhandled application error: %s', error)
        db.session.rollback()
        return render_template('error.html', code=500, message='Something went wrong. Please try again.'), 500

    @app.cli.command('init-db')
    def init_db():
        with app.app_context():
            db.create_all()
            print('LifeFlow database tables are ready.')

    return app


app = create_app()

if __name__ == '__main__':
    app.run(debug=app.config.get('DEBUG', False))
