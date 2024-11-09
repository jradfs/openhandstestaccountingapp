from flask import Blueprint, render_template, request, jsonify, send_file
from flask_login import login_required, current_user
from models import db, Client, Transaction, FinancialStatement, AuditLog
from utils.accounting import FinancialStatementGenerator
from datetime import datetime
import json
import tempfile
import pandas as pd

reports = Blueprint('reports', __name__)

@reports.route('/reports')
@login_required
def index():
    clients = Client.query.all()
    return render_template('reports/index.html', clients=clients)

@reports.route('/reports/generate', methods=['POST'])
@login_required
def generate():
    client_id = request.form.get('client_id', type=int)
    report_type = request.form.get('type')
    start_date = datetime.strptime(request.form.get('start_date'), '%Y-%m-%d')
    end_date = datetime.strptime(request.form.get('end_date'), '%Y-%m-%d')
    
    if not all([client_id, report_type, start_date, end_date]):
        return jsonify({'error': 'Missing required parameters'}), 400
    
    generator = FinancialStatementGenerator()
    
    try:
        if report_type == 'income_statement':
            data = generator.generate_income_statement(client_id, start_date, end_date)
        elif report_type == 'balance_sheet':
            data = generator.generate_balance_sheet(client_id, end_date)
        else:
            return jsonify({'error': 'Invalid report type'}), 400
        
        # Save the report
        statement = FinancialStatement(
            client_id=client_id,
            type=report_type,
            period_start=start_date,
            period_end=end_date,
            data=data,
            generated_by=current_user.id
        )
        db.session.add(statement)
        
        # Log the action
        log = AuditLog(
            user_id=current_user.id,
            action=f'generate_{report_type}',
            details=f'Generated {report_type} for client {client_id}'
        )
        db.session.add(log)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'report_id': statement.id,
            'data': data
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@reports.route('/reports/<int:id>/export')
@login_required
def export(id):
    statement = FinancialStatement.query.get_or_404(id)
    client = Client.query.get(statement.client_id)
    
    # Create Excel file
    with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp:
        writer = pd.ExcelWriter(tmp.name, engine='openpyxl')
        
        # Convert report data to DataFrame
        if statement.type == 'income_statement':
            # Income Statement sheets
            revenue_df = pd.DataFrame(statement.data['details']['revenue_items'].items(),
                                    columns=['Account', 'Amount'])
            expense_df = pd.DataFrame(statement.data['details']['expense_items'].items(),
                                    columns=['Account', 'Amount'])
            
            revenue_df.to_excel(writer, sheet_name='Revenue', index=False)
            expense_df.to_excel(writer, sheet_name='Expenses', index=False)
            
            # Summary sheet
            summary_data = {
                'Item': ['Total Revenue', 'Total Expenses', 'Net Income'],
                'Amount': [
                    statement.data['revenue'],
                    statement.data['expenses'],
                    statement.data['net_income']
                ]
            }
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
            
        elif statement.type == 'balance_sheet':
            # Balance Sheet sheets
            assets_df = pd.DataFrame(statement.data['details']['assets'].items(),
                                   columns=['Account', 'Amount'])
            liabilities_df = pd.DataFrame(statement.data['details']['liabilities'].items(),
                                        columns=['Account', 'Amount'])
            equity_df = pd.DataFrame(statement.data['details']['equity'].items(),
                                   columns=['Account', 'Amount'])
            
            assets_df.to_excel(writer, sheet_name='Assets', index=False)
            liabilities_df.to_excel(writer, sheet_name='Liabilities', index=False)
            equity_df.to_excel(writer, sheet_name='Equity', index=False)
            
            # Summary sheet
            summary_data = {
                'Item': ['Total Assets', 'Total Liabilities', 'Total Equity'],
                'Amount': [
                    statement.data['assets'],
                    statement.data['liabilities'],
                    statement.data['equity']
                ]
            }
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
        
        writer.close()
        
        # Log the export
        log = AuditLog(
            user_id=current_user.id,
            action='export_report',
            details=f'Exported {statement.type} for client {client.business_name}'
        )
        db.session.add(log)
        db.session.commit()
        
        return send_file(
            tmp.name,
            as_attachment=True,
            download_name=f'{client.business_name}_{statement.type}_{statement.period_end.strftime("%Y%m%d")}.xlsx'
        )