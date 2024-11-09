from flask import Blueprint, render_template
from flask_login import login_required, current_user
from models import Client, Transaction, Task, FinancialStatement
from datetime import datetime, timedelta
from sqlalchemy import func

dashboard = Blueprint('dashboard', __name__)

@dashboard.route('/')
@login_required
def index():
    # Get statistics
    stats = {
        'total_clients': Client.query.count(),
        'pending_transactions': Transaction.query.filter_by(status='pending').count(),
        'pending_tasks': Task.query.filter_by(status='pending').count(),
        'reports_generated': FinancialStatement.query.filter(
            FinancialStatement.created_at >= datetime.utcnow() - timedelta(days=30)
        ).count()
    }
    
    # Get recent transactions
    recent_transactions = Transaction.query.order_by(
        Transaction.date.desc()
    ).limit(5).all()
    
    # Add status colors for transactions
    for transaction in recent_transactions:
        if transaction.status == 'pending':
            transaction.status_color = 'warning'
        elif transaction.status == 'processed':
            transaction.status_color = 'success'
        else:
            transaction.status_color = 'info'
    
    # Get upcoming tasks
    upcoming_tasks = Task.query.filter(
        Task.due_date >= datetime.utcnow(),
        Task.status == 'pending'
    ).order_by(Task.due_date.asc()).limit(5).all()
    
    # Add priority colors for tasks
    for task in upcoming_tasks:
        if task.priority == 'high':
            task.priority_color = 'danger'
        elif task.priority == 'medium':
            task.priority_color = 'warning'
        else:
            task.priority_color = 'success'
    
    return render_template('dashboard/index.html',
                         stats=stats,
                         recent_transactions=recent_transactions,
                         upcoming_tasks=upcoming_tasks)