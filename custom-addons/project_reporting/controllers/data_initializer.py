from odoo import http
from odoo.http import request
from datetime import date

class ProjectDataInitializer(http.Controller):

    @http.route('/project/init-demo-data', auth='user', website=True)
    def init_demo_data(self, **kw):
        """Initialize demo data for testing"""
        
        try:
            # Check if data already exists
            existing_income = request.env['project.income'].search_count([])
            existing_expense = request.env['project.expense'].search_count([])
            
            if existing_income > 0 or existing_expense > 0:
                return f"""
                <html>
                <head><title>Demo Data</title></head>
                <body>
                    <h1>Demo Data Already Exists</h1>
                    <p>Found {existing_income} income records and {existing_expense} expense records.</p>
                    <p><a href="/project/test-data">Test Data Page</a> | <a href="/project/dashboard">Dashboard</a></p>
                </body>
                </html>
                """
            
            # Create demo projects
            projects_data = [
                {
                    'name': 'E-commerce Website',
                    'partner_id': 1,  # Base partner
                    'active': True
                },
                {
                    'name': 'Mobile App Development', 
                    'partner_id': 1,
                    'active': True
                },
                {
                    'name': 'Corporate Website',
                    'partner_id': 1,
                    'active': True
                }
            ]
            
            created_projects = []
            for project_data in projects_data:
                # Check if project already exists
                existing = request.env['project.project'].search([('name', '=', project_data['name'])], limit=1)
                if existing:
                    created_projects.append(existing)
                else:
                    project = request.env['project.project'].create(project_data)
                    created_projects.append(project)
            
            # Create demo income records
            income_data = [
                {
                    'project_id': created_projects[0].id,
                    'client_id': 1,
                    'amount': 15000.00,
                    'date': date(2024, 1, 15),
                    'description': 'Initial project payment'
                },
                {
                    'project_id': created_projects[0].id,
                    'client_id': 1,
                    'amount': 10000.00,
                    'date': date(2024, 2, 15),
                    'description': 'Milestone 2 payment'
                },
                {
                    'project_id': created_projects[1].id,
                    'client_id': 1,
                    'amount': 25000.00,
                    'date': date(2024, 1, 20),
                    'description': 'Mobile app development contract'
                },
                {
                    'project_id': created_projects[2].id,
                    'client_id': 1,
                    'amount': 8000.00,
                    'date': date(2024, 2, 1),
                    'description': 'Website design payment'
                }
            ]
            
            created_income = []
            for income in income_data:
                record = request.env['project.income'].create(income)
                created_income.append(record)
            
            # Create demo expense records
            expense_data = [
                {
                    'project_id': created_projects[0].id,
                    'amount': 2500.00,
                    'expense_type': 'hosting',
                    'date': date(2024, 1, 20),
                    'description': 'Annual hosting costs'
                },
                {
                    'project_id': created_projects[0].id,
                    'amount': 1200.00,
                    'expense_type': 'licenses',
                    'date': date(2024, 1, 25),
                    'description': 'Software licenses'
                },
                {
                    'project_id': created_projects[1].id,
                    'amount': 3000.00,
                    'expense_type': 'development',
                    'date': date(2024, 1, 30),
                    'description': 'Development tools and services'
                },
                {
                    'project_id': created_projects[1].id,
                    'amount': 800.00,
                    'expense_type': 'hosting',
                    'date': date(2024, 2, 5),
                    'description': 'Cloud hosting services'
                },
                {
                    'project_id': created_projects[2].id,
                    'amount': 1500.00,
                    'expense_type': 'design',
                    'date': date(2024, 2, 10),
                    'description': 'Design assets and stock photos'
                }
            ]
            
            created_expenses = []
            for expense in expense_data:
                record = request.env['project.expense'].create(expense)
                created_expenses.append(record)
            
            return f"""
            <html>
            <head>
                <title>Demo Data Created</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; }}
                    .success {{ color: green; }}
                    .section {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; }}
                </style>
            </head>
            <body>
                <h1>Demo Data Successfully Created</h1>
                
                <div class="section">
                    <h2 class="success">✓ Created {len(created_projects)} Projects</h2>
                    <ul>
                        {''.join([f"<li>{p.name} (ID: {p.id})</li>" for p in created_projects])}
                    </ul>
                </div>
                
                <div class="section">
                    <h2 class="success">✓ Created {len(created_income)} Income Records</h2>
                    <p>Total Income: ${sum([i.amount for i in created_income]):,.2f}</p>
                </div>
                
                <div class="section">
                    <h2 class="success">✓ Created {len(created_expenses)} Expense Records</h2>
                    <p>Total Expenses: ${sum([e.amount for e in created_expenses]):,.2f}</p>
                </div>
                
                <div class="section">
                    <h2>Quick Links</h2>
                    <p><a href="/project/test-data">Test Data Page</a></p>
                    <p><a href="/project/dashboard">View Dashboard</a></p>
                    <p><a href="/web#action=project.open_view_project_all">View Projects</a></p>
                </div>
            </body>
            </html>
            """
            
        except Exception as e:
            return f"""
            <html>
            <head><title>Error</title></head>
            <body>
                <h1>Error Creating Demo Data</h1>
                <p style="color: red;">{str(e)}</p>
                <p><a href="/project/test-data">Test Data Page</a></p>
            </body>
            </html>
            """
