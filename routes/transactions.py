from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from models import db, Transaction, Client, Account, AuditLog
from utils.accounting import TransactionProcessor, AIAccountingAssistant
import os
from datetime import datetime

transactions = Blueprint('transactions', __name__)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

@transactions.route('/transactions')
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    query = Transaction.query
    
    # Apply filters
    client_id = request.args.get('client_id', type=int)
    if client_id:
        query = query.filter_by(client_id=client_id)
    
    status = request.args.get('status')
    if status:
        query = query.filter_by(status=status)
    
    date_from = request.args.get('date_from')
    if date_from:
        query = query.filter(Transaction.date >= datetime.strptime(date_from, '%Y-%m-%d'))
    
    date_to = request.args.get('date_to')
    if date_to:
        query = query.filter(Transaction.date <= datetime.strptime(date_to, '%Y-%m-%d'))
    
    # Get paginated results
    transactions = query.order_by(Transaction.date.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    # Get all clients for the filter dropdown
    clients = Client.query.all()
    
    return render_template('transactions/index.html',
                         transactions=transactions,
                         clients=clients)

@transactions.route('/transactions/upload', methods=['POST'])
@login_required
def upload():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    
    file = request.files['file']
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    
    if file and allowed_file(file.filename):
        client_id = request.form.get('client_id', type=int)
        if not client_id:
            flash('Please select a client')
            return redirect(request.url)
        
        filename = secure_filename(file.filename)
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        try:
            # Process the CSV file
            processor = TransactionProcessor()
            transactions_data = processor.process_csv(filepath)
            
            # Use AI to categorize transactions
            ai_assistant = AIAccountingAssistant()
            
            # Save transactions to database
            for trans_data in transactions_data:
                # Get AI suggestions
                ai_categories = ai_assistant.categorize_transaction(
                    trans_data['description'],
                    trans_data['amount']
                )
                
                transaction = Transaction(
                    client_id=client_id,
                    date=trans_data['date'],
                    description=trans_data['description'],
                    amount=trans_data['amount'],
                    transaction_type=trans_data['transaction_type'],
                    category=ai_categories['category'],
                    account=ai_categories['account'],
                    status='pending',
                    processed_by=current_user.id
                )
                db.session.add(transaction)
            
            db.session.commit()
            
            # Log the action
            log = AuditLog(
                user_id=current_user.id,
                action='upload_transactions',
                details=f'Uploaded {len(transactions_data)} transactions for client {client_id}'
            )
            db.session.add(log)
            db.session.commit()
            
            flash(f'Successfully processed {len(transactions_data)} transactions')
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error processing file: {str(e)}')
        finally:
            # Clean up the uploaded file
            os.remove(filepath)
    
    return redirect(url_for('transactions.index'))

@transactions.route('/transactions/<int:id>/update', methods=['POST'])
@login_required
def update(id):
    transaction = Transaction.query.get_or_404(id)
    
    if 'status' in request.form:
        transaction.status = request.form['status']
    
    if 'category' in request.form:
        transaction.category = request.form['category']
    
    if 'account' in request.form:
        transaction.account = request.form['account']
    
    db.session.commit()
    
    # Log the update
    log = AuditLog(
        user_id=current_user.id,
        action='update_transaction',
        details=f'Updated transaction {id}'
    )
    db.session.add(log)
    db.session.commit()
    
    return redirect(url_for('transactions.index'))

@transactions.route('/transactions/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    transaction = Transaction.query.get_or_404(id)
    
    # Log the deletion
    log = AuditLog(
        user_id=current_user.id,
        action='delete_transaction',
        details=f'Deleted transaction {id}'
    )
    
    db.session.delete(transaction)
    db.session.add(log)
    db.session.commit()
    
    flash('Transaction deleted successfully')
    return redirect(url_for('transactions.index'))