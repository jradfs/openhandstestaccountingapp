import pandas as pd
import numpy as np
from datetime import datetime
from typing import List, Dict, Any
from models import Transaction, Account, FinancialStatement

class TransactionProcessor:
    @staticmethod
    def process_csv(file_path: str) -> List[Dict[str, Any]]:
        df = pd.read_csv(file_path)
        required_columns = ['date', 'description', 'amount', 'category', 'account']
        
        # Validate columns
        if not all(col in df.columns for col in required_columns):
            raise ValueError("CSV file missing required columns")
        
        # Convert date strings to datetime
        df['date'] = pd.to_datetime(df['date'])
        
        # Clean and validate amounts
        df['amount'] = pd.to_numeric(df['amount'].str.replace('[$,]', '', regex=True))
        
        # Determine transaction type based on amount
        df['transaction_type'] = np.where(df['amount'] >= 0, 'credit', 'debit')
        df['amount'] = abs(df['amount'])
        
        return df.to_dict('records')

class FinancialStatementGenerator:
    @staticmethod
    def generate_income_statement(client_id: int, start_date: datetime, end_date: datetime) -> Dict:
        # Query transactions for the period
        transactions = Transaction.query.filter(
            Transaction.client_id == client_id,
            Transaction.date.between(start_date, end_date)
        ).all()
        
        # Calculate totals
        revenue = sum(t.amount for t in transactions if t.category == 'revenue')
        expenses = sum(t.amount for t in transactions if t.category == 'expense')
        net_income = revenue - expenses
        
        return {
            'revenue': float(revenue),
            'expenses': float(expenses),
            'net_income': float(net_income),
            'details': {
                'revenue_items': self._group_by_account(transactions, 'revenue'),
                'expense_items': self._group_by_account(transactions, 'expense')
            }
        }
    
    @staticmethod
    def generate_balance_sheet(client_id: int, as_of_date: datetime) -> Dict:
        # Query all accounts
        accounts = Account.query.filter_by(client_id=client_id).all()
        
        assets = sum(a.balance for a in accounts if a.type == 'asset')
        liabilities = sum(a.balance for a in accounts if a.type == 'liability')
        equity = sum(a.balance for a in accounts if a.type == 'equity')
        
        return {
            'assets': float(assets),
            'liabilities': float(liabilities),
            'equity': float(equity),
            'details': {
                'assets': self._group_accounts(accounts, 'asset'),
                'liabilities': self._group_accounts(accounts, 'liability'),
                'equity': self._group_accounts(accounts, 'equity')
            }
        }
    
    @staticmethod
    def _group_by_account(transactions: List[Transaction], category: str) -> Dict:
        result = {}
        filtered_transactions = [t for t in transactions if t.category == category]
        for trans in filtered_transactions:
            if trans.account not in result:
                result[trans.account] = 0
            result[trans.account] += float(trans.amount)
        return result
    
    @staticmethod
    def _group_accounts(accounts: List[Account], account_type: str) -> Dict:
        result = {}
        filtered_accounts = [a for a in accounts if a.type == account_type]
        for account in filtered_accounts:
            result[account.name] = float(account.balance)
        return result

class AIAccountingAssistant:
    @staticmethod
    def categorize_transaction(description: str, amount: float) -> Dict[str, str]:
        # TODO: Implement ML-based transaction categorization
        # This is a placeholder for future ML implementation
        return {
            'category': 'expense',  # Predicted category
            'account': 'office_expenses',  # Predicted account
            'confidence': '0.85'  # Prediction confidence
        }
    
    @staticmethod
    def detect_anomalies(transactions: List[Transaction]) -> List[Dict]:
        # TODO: Implement anomaly detection
        # This is a placeholder for future ML implementation
        anomalies = []
        return anomalies