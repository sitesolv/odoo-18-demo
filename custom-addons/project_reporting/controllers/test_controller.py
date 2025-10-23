from odoo import http
from odoo.http import request
import json

class ProjectReportingTest(http.Controller):

    @http.route('/project/test-data', auth='user', website=True)
    def test_project_data(self, **kw):
        """Test endpoint to check if income/expense data is accessible"""
        
        result = {
            'user_info': {
                'uid': request.env.uid,
                'user_name': request.env.user.name,
                'groups': [g.name for g in request.env.user.groups_id],
            },
            'module_tests': {},
            'model_tests': {},
            'data_samples': {},
            'dashboard_data': {},
            'errors': []
        }
        
        # Test if project_extended module is installed
        try:
            project_extended = request.env['ir.module.module'].search([
                ('name', '=', 'project_extended'),
                ('state', '=', 'installed')
            ])
            result['module_tests']['project_extended_installed'] = bool(project_extended)
        except Exception as e:
            result['errors'].append(f"Error checking project_extended: {e}")
        
        # Test model accessibility
        for model_name in ['project.income', 'project.expense', 'project.project']:
            try:
                model = request.env[model_name]
                count = model.search_count([])
                result['model_tests'][model_name] = {
                    'accessible': True,
                    'record_count': count
                }
                
                # Get sample data
                if count > 0:
                    sample = model.search([], limit=1)
                    if model_name == 'project.income':
                        result['data_samples'][model_name] = {
                            'amount': sample.amount,
                            'project': sample.project_id.name,
                            'client': sample.client_id.name if sample.client_id else 'None',
                            'date': str(sample.date)
                        }
                    elif model_name == 'project.expense':
                        result['data_samples'][model_name] = {
                            'amount': sample.amount,
                            'project': sample.project_id.name,
                            'type': sample.expense_type,
                            'date': str(sample.date)
                        }
                    elif model_name == 'project.project':
                        result['data_samples'][model_name] = {
                            'name': sample.name,
                            'partner': sample.partner_id.name if sample.partner_id else 'None',
                            'active': sample.active
                        }
                        
            except Exception as e:
                result['model_tests'][model_name] = {
                    'accessible': False,
                    'error': str(e)
                }
        
        # Test dashboard data
        try:
            dashboard_model = request.env['project.reporting.dashboard']
            dashboard_data = dashboard_model.get_dashboard_data()
            result['dashboard_data'] = dashboard_data
        except Exception as e:
            result['errors'].append(f"Dashboard error: {e}")
        
        # Test direct SQL queries
        try:
            request.env.cr.execute("SELECT table_name FROM information_schema.tables WHERE table_name LIKE 'project_%'")
            tables = [row[0] for row in request.env.cr.fetchall()]
            result['database_tables'] = tables
        except Exception as e:
            result['errors'].append(f"Database query error: {e}")
        
        return f"""
        <html>
        <head>
            <title>Project Reporting Test</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .section {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; }}
                .error {{ color: red; }}
                .success {{ color: green; }}
                pre {{ background: #f5f5f5; padding: 10px; overflow-x: auto; }}
            </style>
        </head>
        <body>
            <h1>Project Reporting Data Test</h1>
            
            <div class="section">
                <h2>Test Results Summary</h2>
                <p><strong>Project Extended Installed:</strong> 
                   <span class="{'success' if result['module_tests'].get('project_extended_installed') else 'error'}">
                   {result['module_tests'].get('project_extended_installed', 'Unknown')}
                   </span>
                </p>
                
                <h3>Model Access Results:</h3>
                <ul>
                    {''.join([f"<li><strong>{model}:</strong> {'✓' if data.get('accessible') else '✗'} ({data.get('record_count', 'N/A')} records)</li>" for model, data in result['model_tests'].items()])}
                </ul>
                
                <h3>Errors:</h3>
                <ul>
                    {''.join([f"<li class='error'>{error}</li>" for error in result['errors']])}
                </ul>
            </div>
            
            <div class="section">
                <h2>Detailed Results</h2>
                <pre>{json.dumps(result, indent=2, default=str)}</pre>
            </div>
            
            <div class="section">
                <h2>Quick Actions</h2>
                <p><a href="/web#action={request.env.ref('project_extended.action_project_income').id}&model=project.income">View Project Income Records</a></p>
                <p><a href="/web#action={request.env.ref('project_extended.action_project_expense').id}&model=project.expense">View Project Expense Records</a></p>
                <p><a href="/project/dashboard">Go to Project Dashboard</a></p>
            </div>
        </body>
        </html>
        """
