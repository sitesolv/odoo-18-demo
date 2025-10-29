from odoo import http
from odoo.http import request
import json
from datetime import datetime


class ProjectDashboardController(http.Controller):

    @http.route('/dashboard/project_financial', type='http', auth='user', website=False)
    def project_financial_dashboard(self, **kwargs):
        """Render the project financial dashboard"""
        
        # Get all active projects
        projects = request.env['project.project'].search([('active', '=', True)])
        
        # Prepare dashboard data
        dashboard_data = []
        total_company_income = 0
        total_company_expense = 0
        
        for project in projects:
            # Get income data
            income_records = request.env['project.income'].search([('project_id', '=', project.id)])
            total_income = sum(income_records.mapped('amount'))
            
            # Get expense data
            expense_records = request.env['project.expense'].search([('project_id', '=', project.id)])
            total_expense = sum(expense_records.mapped('amount'))
            
            # Calculate profit and margin
            net_profit = total_income - total_expense
            profit_margin = (net_profit / total_income * 100) if total_income > 0 else 0
            
            # Determine status
            if net_profit > 0:
                status = 'Profitable'
                status_class = 'text-success'
            elif net_profit < 0:
                status = 'Loss'
                status_class = 'text-danger'
            else:
                status = 'Break Even'
                status_class = 'text-warning'
            
            dashboard_data.append({
                'id': project.id,
                'name': project.name,
                'client': project.partner_id.name if project.partner_id else 'No Client',
                'total_income': total_income,
                'total_expense': total_expense,
                'net_profit': net_profit,
                'profit_margin': profit_margin,
                'status': status,
                'status_class': status_class,
            })
            
            # Add to company totals
            total_company_income += total_income
            total_company_expense += total_expense
        
        # Calculate company totals
        company_net_profit = total_company_income - total_company_expense
        company_profit_margin = (company_net_profit / total_company_income * 100) if total_company_income > 0 else 0
        
        # Determine company status
        if company_net_profit > 0:
            company_status = 'Profitable'
            company_status_class = 'text-success'
        elif company_net_profit < 0:
            company_status = 'Loss'
            company_status_class = 'text-danger'
        else:
            company_status = 'Break Even'
            company_status_class = 'text-warning'
        
        company_summary = {
            'total_income': total_company_income,
            'total_expense': total_company_expense,
            'net_profit': company_net_profit,
            'profit_margin': company_profit_margin,
            'status': company_status,
            'status_class': company_status_class,
            'project_count': len(dashboard_data),
        }
        
        values = {
            'projects': dashboard_data,
            'company_summary': company_summary,
            'currency_symbol': request.env.company.currency_id.symbol or '$',
            'context_today': datetime.now,
        }
        
    @http.route('/dashboard/project_financial/data', type='json', auth='user')
    def project_financial_dashboard_data(self, **kwargs):
        """Return dashboard data as JSON for client action"""
        
        # Get all active projects
        projects = request.env['project.project'].search([('active', '=', True)])
        
        # Prepare dashboard data
        dashboard_data = []
        total_company_income = 0
        total_company_expense = 0
        
        for project in projects:
            # Get income data
            income_records = request.env['project.income'].search([('project_id', '=', project.id)])
            total_income = sum(income_records.mapped('amount'))
            
            # Get expense data
            expense_records = request.env['project.expense'].search([('project_id', '=', project.id)])
            total_expense = sum(expense_records.mapped('amount'))
            
            # Calculate profit and margin
            net_profit = total_income - total_expense
            profit_margin = (net_profit / total_income * 100) if total_income > 0 else 0
            
            # Determine status
            if net_profit > 0:
                status = 'Profitable'
                status_class = 'text-success'
            elif net_profit < 0:
                status = 'Loss'
                status_class = 'text-danger'
            else:
                status = 'Break Even'
                status_class = 'text-warning'
            
            dashboard_data.append({
                'id': project.id,
                'name': project.name,
                'client': project.partner_id.name if project.partner_id else 'No Client',
                'total_income': total_income,
                'total_expense': total_expense,
                'net_profit': net_profit,
                'profit_margin': profit_margin,
                'status': status,
                'status_class': status_class,
            })
            
            # Add to company totals
            total_company_income += total_income
            total_company_expense += total_expense
        
        # Calculate company totals
        company_net_profit = total_company_income - total_company_expense
        company_profit_margin = (company_net_profit / total_company_income * 100) if total_company_income > 0 else 0
        
        # Determine company status
        if company_net_profit > 0:
            company_status = 'Profitable'
            company_status_class = 'text-success'
        elif company_net_profit < 0:
            company_status = 'Loss'
            company_status_class = 'text-danger'
        else:
            company_status = 'Break Even'
            company_status_class = 'text-warning'
        
        company_summary = {
            'total_income': total_company_income,
            'total_expense': total_company_expense,
            'net_profit': company_net_profit,
            'profit_margin': company_profit_margin,
            'status': company_status,
            'status_class': company_status_class,
            'project_count': len(dashboard_data),
        }
        
        return {
            'projects': dashboard_data,
            'company_summary': company_summary,
            'currency_symbol': request.env.company.currency_id.symbol or '$',
        }
    
    @http.route('/dashboard/debug', type='http', auth='user', website=False)
    def debug_dashboard_data(self, **kwargs):
        """Debug endpoint to see raw dashboard data"""
        try:
            # Get all active projects
            projects = request.env['project.project'].search([('active', '=', True)])
            
            debug_info = {
                'total_projects': len(projects),
                'projects_list': [],
                'income_records': 0,
                'expense_records': 0,
                'total_income': 0,
                'total_expense': 0
            }
            
            for project in projects:
                # Get income data
                income_records = request.env['project.income'].search([('project_id', '=', project.id)])
                total_income = sum(income_records.mapped('amount'))
                
                # Get expense data
                expense_records = request.env['project.expense'].search([('project_id', '=', project.id)])
                total_expense = sum(expense_records.mapped('amount'))
                
                debug_info['projects_list'].append({
                    'name': project.name,
                    'income': total_income,
                    'expense': total_expense,
                    'profit': total_income - total_expense
                })
                
                debug_info['income_records'] += len(income_records)
                debug_info['expense_records'] += len(expense_records)
                debug_info['total_income'] += total_income
                debug_info['total_expense'] += total_expense
            
            debug_info['net_profit'] = debug_info['total_income'] - debug_info['total_expense']
            
            html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Dashboard Debug</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; }}
                    .summary {{ background: #f0f0f0; padding: 15px; margin: 10px 0; }}
                    .project {{ border: 1px solid #ccc; padding: 10px; margin: 5px 0; }}
                    .income {{ color: green; }}
                    .expense {{ color: red; }}
                    .profit {{ color: blue; }}
                </style>
            </head>
            <body>
                <h1>Dashboard Debug Information</h1>
                <div class="summary">
                    <h2>Summary</h2>
                    <p><strong>Total Projects:</strong> {debug_info['total_projects']}</p>
                    <p class="income"><strong>Total Income:</strong> ${debug_info['total_income']:,.2f}</p>
                    <p class="expense"><strong>Total Expenses:</strong> ${debug_info['total_expense']:,.2f}</p>
                    <p class="profit"><strong>Net Profit:</strong> ${debug_info['net_profit']:,.2f}</p>
                    <p><strong>Income Records:</strong> {debug_info['income_records']}</p>
                    <p><strong>Expense Records:</strong> {debug_info['expense_records']}</p>
                </div>
                
                <h2>Project Details</h2>
                {chr(10).join([f'<div class="project"><strong>{p["name"]}</strong><br>Income: ${p["income"]:,.2f} | Expense: ${p["expense"]:,.2f} | Profit: ${p["profit"]:,.2f}</div>' for p in debug_info['projects_list']])}
                
                <p><a href="/web">Back to Odoo</a> | <a href="/dashboard/project_financial/data">Raw JSON Data</a></p>
            </body>
            </html>
            """
            return html
            
        except Exception as e:
            return f"<html><body><h1>Error</h1><p>{str(e)}</p><p><a href='/web'>Back to Odoo</a></p></body></html>"
    
    @http.route('/dashboard/test', type='http', auth='user', website=False)
    def test_dashboard(self, **kwargs):
        """Simple test dashboard to verify everything is working"""
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Dashboard Test</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                .success { color: green; font-size: 24px; font-weight: bold; }
                .info { color: blue; margin: 20px 0; }
            </style>
        </head>
        <body>
            <h1 class="success">✅ Dashboard Controller is Working!</h1>
            <p class="info">This proves that:</p>
            <ul>
                <li>The controller is properly loaded</li>
                <li>Authentication is working</li>
                <li>Routes are accessible</li>
            </ul>
            <p><a href="/web">Back to Odoo</a></p>
        </body>
        </html>
        """
        return html
