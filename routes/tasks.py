from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db, Task, Client, User, AuditLog
from datetime import datetime

tasks = Blueprint('tasks', __name__)

@tasks.route('/tasks')
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    query = Task.query
    
    # Apply filters
    client_id = request.args.get('client_id', type=int)
    if client_id:
        query = query.filter_by(client_id=client_id)
    
    status = request.args.get('status')
    if status:
        query = query.filter_by(status=status)
    
    priority = request.args.get('priority')
    if priority:
        query = query.filter_by(priority=priority)
    
    assigned_to = request.args.get('assigned_to', type=int)
    if assigned_to:
        query = query.filter_by(assigned_to=assigned_to)
    
    # Get paginated results
    tasks = query.order_by(Task.due_date.asc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    # Get data for filter dropdowns
    clients = Client.query.all()
    users = User.query.all()
    
    return render_template('tasks/index.html',
                         tasks=tasks,
                         clients=clients,
                         users=users)

@tasks.route('/tasks/new', methods=['GET', 'POST'])
@login_required
def new():
    if request.method == 'POST':
        task = Task(
            client_id=request.form['client_id'],
            title=request.form['title'],
            description=request.form.get('description'),
            category=request.form['category'],
            due_date=datetime.strptime(request.form['due_date'], '%Y-%m-%d'),
            priority=request.form['priority'],
            assigned_to=request.form.get('assigned_to', type=int)
        )
        
        try:
            db.session.add(task)
            
            # Log the action
            log = AuditLog(
                user_id=current_user.id,
                action='create_task',
                details=f'Created task: {task.title}'
            )
            db.session.add(log)
            
            db.session.commit()
            flash('Task created successfully')
            return redirect(url_for('tasks.index'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating task: {str(e)}')
    
    clients = Client.query.all()
    users = User.query.all()
    return render_template('tasks/new.html',
                         clients=clients,
                         users=users)

@tasks.route('/tasks/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    task = Task.query.get_or_404(id)
    
    if request.method == 'POST':
        task.client_id = request.form['client_id']
        task.title = request.form['title']
        task.description = request.form.get('description')
        task.category = request.form['category']
        task.due_date = datetime.strptime(request.form['due_date'], '%Y-%m-%d')
        task.priority = request.form['priority']
        task.assigned_to = request.form.get('assigned_to', type=int)
        
        try:
            # Log the action
            log = AuditLog(
                user_id=current_user.id,
                action='update_task',
                details=f'Updated task: {task.title}'
            )
            db.session.add(log)
            
            db.session.commit()
            flash('Task updated successfully')
            return redirect(url_for('tasks.index'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating task: {str(e)}')
    
    clients = Client.query.all()
    users = User.query.all()
    return render_template('tasks/edit.html',
                         task=task,
                         clients=clients,
                         users=users)

@tasks.route('/tasks/<int:id>/update-status', methods=['POST'])
@login_required
def update_status(id):
    task = Task.query.get_or_404(id)
    task.status = request.form['status']
    
    try:
        # Log the action
        log = AuditLog(
            user_id=current_user.id,
            action='update_task_status',
            details=f'Updated task status: {task.title} -> {task.status}'
        )
        db.session.add(log)
        
        db.session.commit()
        flash('Task status updated successfully')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating task status: {str(e)}')
    
    return redirect(url_for('tasks.index'))

@tasks.route('/tasks/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    task = Task.query.get_or_404(id)
    
    try:
        # Log the action
        log = AuditLog(
            user_id=current_user.id,
            action='delete_task',
            details=f'Deleted task: {task.title}'
        )
        db.session.add(log)
        
        db.session.delete(task)
        db.session.commit()
        flash('Task deleted successfully')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting task: {str(e)}')
    
    return redirect(url_for('tasks.index'))