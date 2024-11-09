from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db, Client, Transaction, Task, Account, AuditLog
from datetime import datetime

clients = Blueprint('clients', __name__)

@clients.route('/clients')
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    clients = Client.query.paginate(page=page, per_page=per_page, error_out=False)
    return render_template('clients/index.html', clients=clients)

@clients.route('/clients/new', methods=['GET', 'POST'])
@login_required
def new():
    if request.method == 'POST':
        client = Client(
            business_name=request.form['business_name'],
            business_type=request.form['business_type'],
            tax_id=request.form['tax_id'],
            fiscal_year_end=datetime.strptime(request.form['fiscal_year_end'], '%Y-%m-%d'),
            manager_id=current_user.id
        )
        
        try:
            db.session.add(client)
            
            # Create default accounts for the client
            default_accounts = [
                # Assets
                ('1000', 'Cash', 'asset'),
                ('1100', 'Accounts Receivable', 'asset'),
                ('1200', 'Inventory', 'asset'),
                ('1500', 'Fixed Assets', 'asset'),
                # Liabilities
                ('2000', 'Accounts Payable', 'liability'),
                ('2100', 'Accrued Expenses', 'liability'),
                ('2200', 'Notes Payable', 'liability'),
                # Equity
                ('3000', 'Owner\'s Equity', 'equity'),
                ('3100', 'Retained Earnings', 'equity'),
                # Revenue
                ('4000', 'Sales Revenue', 'revenue'),
                ('4100', 'Service Revenue', 'revenue'),
                ('4200', 'Interest Income', 'revenue'),
                # Expenses
                ('5000', 'Cost of Goods Sold', 'expense'),
                ('5100', 'Salaries Expense', 'expense'),
                ('5200', 'Rent Expense', 'expense'),
                ('5300', 'Utilities Expense', 'expense'),
                ('5400', 'Office Supplies Expense', 'expense')
            ]
            
            for number, name, type_ in default_accounts:
                account = Account(
                    client_id=client.id,
                    number=number,
                    name=name,
                    type=type_
                )
                db.session.add(account)
            
            # Log the action
            log = AuditLog(
                user_id=current_user.id,
                action='create_client',
                details=f'Created client: {client.business_name}'
            )
            db.session.add(log)
            
            db.session.commit()
            flash('Client created successfully')
            return redirect(url_for('clients.index'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating client: {str(e)}')
    
    return render_template('clients/new.html')

@clients.route('/clients/<int:id>')
@login_required
def show(id):
    client = Client.query.get_or_404(id)
    
    # Get recent transactions
    recent_transactions = Transaction.query.filter_by(client_id=id)\
        .order_by(Transaction.date.desc())\
        .limit(5).all()
    
    # Get pending tasks
    pending_tasks = Task.query.filter_by(
        client_id=id,
        status='pending'
    ).order_by(Task.due_date.asc()).all()
    
    # Get account balances
    accounts = Account.query.filter_by(client_id=id).all()
    
    return render_template('clients/show.html',
                         client=client,
                         recent_transactions=recent_transactions,
                         pending_tasks=pending_tasks,
                         accounts=accounts)

@clients.route('/clients/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    client = Client.query.get_or_404(id)
    
    if request.method == 'POST':
        client.business_name = request.form['business_name']
        client.business_type = request.form['business_type']
        client.tax_id = request.form['tax_id']
        client.fiscal_year_end = datetime.strptime(request.form['fiscal_year_end'], '%Y-%m-%d')
        
        try:
            # Log the action
            log = AuditLog(
                user_id=current_user.id,
                action='update_client',
                details=f'Updated client: {client.business_name}'
            )
            db.session.add(log)
            
            db.session.commit()
            flash('Client updated successfully')
            return redirect(url_for('clients.show', id=client.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating client: {str(e)}')
    
    return render_template('clients/edit.html', client=client)

@clients.route('/clients/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    client = Client.query.get_or_404(id)
    
    try:
        # Log the action
        log = AuditLog(
            user_id=current_user.id,
            action='delete_client',
            details=f'Deleted client: {client.business_name}'
        )
        db.session.add(log)
        
        db.session.delete(client)
        db.session.commit()
        flash('Client deleted successfully')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting client: {str(e)}')
    
    return redirect(url_for('clients.index'))