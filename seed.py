from datetime import datetime, timedelta
import random
from app import create_app
from models import db, User, Client, Transaction, Account, Task, AuditLog
from werkzeug.security import generate_password_hash

def create_test_data():
    app = create_app()
    
    with app.app_context():
        # Clear existing data
        print("Clearing existing data...")
        Task.query.delete()
        Transaction.query.delete()
        Account.query.delete()
        AuditLog.query.delete()
        Client.query.delete()
        User.query.delete()
        db.session.commit()
        
        # Create users
        print("Creating users...")
        admin = User(
            email='admin@example.com',
            name='Admin User',
            role='admin',
            password_hash=generate_password_hash('admin123')
        )
        db.session.add(admin)
        
        staff_users = []
        for i in range(3):
            user = User(
                email=f'staff{i+1}@example.com',
                name=f'Staff User {i+1}',
                role='staff',
                password_hash=generate_password_hash(f'staff{i+1}')
            )
            staff_users.append(user)
            db.session.add(user)
        
        db.session.commit()
        
        # Create clients
        print("Creating clients...")
        business_types = ['Corporation', 'LLC', 'Partnership', 'Sole Proprietorship']
        clients = []
        
        for i in range(10):
            client = Client(
                business_name=f'Test Company {i+1}',
                business_type=random.choice(business_types),
                tax_id=f'TAX-{100000+i}',
                fiscal_year_end=datetime(2024, 12, 31),
                manager_id=random.choice([admin.id] + [u.id for u in staff_users])
            )
            clients.append(client)
            db.session.add(client)
        
        db.session.commit()
        
        # Create accounts for each client
        print("Creating accounts...")
        account_types = {
            'asset': [
                ('1000', 'Cash'),
                ('1100', 'Accounts Receivable'),
                ('1200', 'Inventory'),
                ('1500', 'Fixed Assets')
            ],
            'liability': [
                ('2000', 'Accounts Payable'),
                ('2100', 'Accrued Expenses'),
                ('2200', 'Notes Payable')
            ],
            'equity': [
                ('3000', "Owner's Equity"),
                ('3100', 'Retained Earnings')
            ],
            'revenue': [
                ('4000', 'Sales Revenue'),
                ('4100', 'Service Revenue'),
                ('4200', 'Interest Income')
            ],
            'expense': [
                ('5000', 'Cost of Goods Sold'),
                ('5100', 'Salaries Expense'),
                ('5200', 'Rent Expense'),
                ('5300', 'Utilities Expense'),
                ('5400', 'Office Supplies Expense')
            ]
        }
        
        for client in clients:
            for acc_type, accounts in account_types.items():
                for number, name in accounts:
                    account = Account(
                        client_id=client.id,
                        number=number,
                        name=name,
                        type=acc_type,
                        balance=random.uniform(1000, 50000) if acc_type in ['asset', 'liability'] else 0
                    )
                    db.session.add(account)
        
        db.session.commit()
        
        # Create transactions
        print("Creating transactions...")
        transaction_descriptions = [
            'Monthly rent payment',
            'Office supplies purchase',
            'Client payment received',
            'Utility bill payment',
            'Equipment purchase',
            'Employee salary payment',
            'Insurance premium',
            'Bank fees',
            'Consulting revenue',
            'Software subscription'
        ]
        
        for client in clients:
            # Get client's accounts
            client_accounts = Account.query.filter_by(client_id=client.id).all()
            account_dict = {acc.type: acc for acc in client_accounts}
            
            # Create 50 transactions per client
            for _ in range(50):
                # Random date in the last 6 months
                date = datetime.now() - timedelta(days=random.randint(0, 180))
                
                # Randomly choose if it's an expense or revenue
                is_expense = random.random() < 0.6  # 60% chance of being an expense
                
                if is_expense:
                    amount = random.uniform(100, 5000)
                    category = 'expense'
                    account = random.choice([acc for acc in client_accounts if acc.type == 'expense'])
                else:
                    amount = random.uniform(1000, 10000)
                    category = 'revenue'
                    account = random.choice([acc for acc in client_accounts if acc.type == 'revenue'])
                
                transaction = Transaction(
                    client_id=client.id,
                    date=date,
                    description=random.choice(transaction_descriptions),
                    amount=amount,
                    transaction_type='debit' if is_expense else 'credit',
                    category=category,
                    account=account.name,
                    status=random.choice(['pending', 'processed', 'reviewed']),
                    processed_by=random.choice([admin.id] + [u.id for u in staff_users])
                )
                db.session.add(transaction)
        
        db.session.commit()
        
        # Create tasks
        print("Creating tasks...")
        task_titles = [
            'Prepare monthly financial statements',
            'Review bank reconciliation',
            'Process payroll',
            'File tax returns',
            'Update client records',
            'Prepare invoice batch',
            'Review expense reports',
            'Update accounting software',
            'Client meeting preparation',
            'Audit preparation'
        ]
        
        task_categories = ['invoicing', 'payroll', 'taxes', 'reconciliation', 'reporting', 'other']
        
        for client in clients:
            # Create 5-10 tasks per client
            for _ in range(random.randint(5, 10)):
                due_date = datetime.now() + timedelta(days=random.randint(1, 30))
                
                task = Task(
                    client_id=client.id,
                    title=random.choice(task_titles),
                    description=f'Task details for {client.business_name}',
                    category=random.choice(task_categories),
                    due_date=due_date,
                    priority=random.choice(['high', 'medium', 'low']),
                    status=random.choice(['pending', 'completed']),
                    assigned_to=random.choice([admin.id] + [u.id for u in staff_users])
                )
                db.session.add(task)
        
        db.session.commit()
        
        # Create audit logs
        print("Creating audit logs...")
        actions = ['create_client', 'update_client', 'create_transaction', 'generate_report', 'create_task']
        
        for _ in range(100):
            log = AuditLog(
                user_id=random.choice([admin.id] + [u.id for u in staff_users]),
                action=random.choice(actions),
                details=f'Test audit log entry at {datetime.now()}'
            )
            db.session.add(log)
        
        db.session.commit()
        
        print("Test data creation completed!")
        print("\nTest Users:")
        print("Admin:")
        print("  Email: admin@example.com")
        print("  Password: admin123")
        print("\nStaff Users:")
        for i in range(3):
            print(f"  Email: staff{i+1}@example.com")
            print(f"  Password: staff{i+1}")

if __name__ == '__main__':
    create_test_data()