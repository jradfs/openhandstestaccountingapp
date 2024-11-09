from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, login_required, current_user, login_user, logout_user
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
import os
from models import db, User, Client, Transaction, Account, FinancialStatement, Task, AuditLog
from utils.accounting import TransactionProcessor, FinancialStatementGenerator, AIAccountingAssistant
from config import config

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Register blueprints
    from routes.auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)
    
    from routes.dashboard import dashboard as dashboard_blueprint
    app.register_blueprint(dashboard_blueprint)
    
    from routes.clients import clients as clients_blueprint
    app.register_blueprint(clients_blueprint)
    
    from routes.transactions import transactions as transactions_blueprint
    app.register_blueprint(transactions_blueprint)
    
    from routes.reports import reports as reports_blueprint
    app.register_blueprint(reports_blueprint)
    
    from routes.tasks import tasks as tasks_blueprint
    app.register_blueprint(tasks_blueprint)
    
    # Create database tables
    with app.app_context():
        db.create_all()
        
        # Create admin user if not exists
        if not User.query.filter_by(email='admin@example.com').first():
            admin = User(
                email='admin@example.com',
                name='Admin User',
                role='admin'
            )
            admin.set_password('admin123')  # Change this in production
            db.session.add(admin)
            db.session.commit()
    
    @app.context_processor
    def utility_processor():
        def format_currency(amount):
            return "${:,.2f}".format(amount)
        
        return dict(format_currency=format_currency)
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=3000)