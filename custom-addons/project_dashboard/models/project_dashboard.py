from odoo import models, fields, api
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


class ProjectDashboard(models.Model):
    _name = 'project.dashboard.analytics'
    _description = 'Project Dashboard Analytics'

    name = fields.Char(string='Dashboard Name', default='Project Analytics')
    
    # KPI Fields
    total_projects = fields.Integer(string='Total Projects', compute='_compute_project_kpis')
    ongoing_projects = fields.Integer(string='Ongoing Projects', compute='_compute_project_kpis')
    completed_projects = fields.Integer(string='Completed Projects', compute='_compute_project_kpis')
    
    total_income = fields.Float(string='Total Income', compute='_compute_financial_kpis')
    total_expenses = fields.Float(string='Total Expenses', compute='_compute_financial_kpis')
    net_profit = fields.Float(string='Net Profit', compute='_compute_financial_kpis')
    
    # Date filters
    date_from = fields.Date(string='Date From', default=lambda self: fields.Date.today().replace(day=1))
    date_to = fields.Date(string='Date To', default=fields.Date.today)
    
    # Top customers data
    top_customer_ids = fields.Many2many('res.partner', string='Top Customers', compute='_compute_top_customers')
    
    # Expiry notifications
    expiring_domains_count = fields.Integer(string='Expiring Domains', compute='_compute_expiry_notifications')
    expiring_hosting_count = fields.Integer(string='Expiring Hosting', compute='_compute_expiry_notifications')
    urgent_domains_count = fields.Integer(string='Urgent Domains', compute='_compute_expiry_notifications')
    urgent_hosting_count = fields.Integer(string='Urgent Hosting', compute='_compute_expiry_notifications')
    
    @api.depends('date_from', 'date_to')
    def _compute_project_kpis(self):
        for record in self:
            # Total projects
            record.total_projects = self.env['project.project'].search_count([])
            
            # Ongoing projects (active projects)
            record.ongoing_projects = self.env['project.project'].search_count([
                ('active', '=', True)
            ])
            
            # Completed projects (inactive projects)
            record.completed_projects = self.env['project.project'].search_count([
                ('active', '=', False)
            ])
    
    @api.depends('date_from', 'date_to')
    def _compute_financial_kpis(self):
        for record in self:
            domain = []
            if record.date_from:
                domain.append(('date', '>=', record.date_from))
            if record.date_to:
                domain.append(('date', '<=', record.date_to))
            
            # Total income
            incomes = self.env['project.income'].search(domain)
            record.total_income = sum(incomes.mapped('amount'))
            
            # Total expenses
            expenses = self.env['project.expense'].search(domain)
            record.total_expenses = sum(expenses.mapped('amount'))
            
            # Net profit
            record.net_profit = record.total_income - record.total_expenses
    
    @api.depends('date_from', 'date_to')
    def _compute_top_customers(self):
        for record in self:
            domain = []
            if record.date_from:
                domain.append(('date', '>=', record.date_from))
            if record.date_to:
                domain.append(('date', '<=', record.date_to))
            
            # Get income data grouped by customer
            incomes = self.env['project.income'].search(domain)
            customer_income = {}
            
            for income in incomes:
                customer_id = income.client_id.id
                if customer_id not in customer_income:
                    customer_income[customer_id] = 0
                customer_income[customer_id] += income.amount
            
            # Sort by income and get top 5
            sorted_customers = sorted(customer_income.items(), key=lambda x: x[1], reverse=True)[:5]
            top_customer_ids = [customer[0] for customer in sorted_customers]
            
            record.top_customer_ids = [(6, 0, top_customer_ids)]
    
    def _compute_expiry_notifications(self):
        """Compute expiring domains and hosting counts"""
        for record in self:
            # Expiring domains (warning, urgent, expired)
            expiring_domains = self.env['project.domain'].search([
                ('expiry_status', 'in', ['warning', 'urgent', 'expired'])
            ])
            record.expiring_domains_count = len(expiring_domains)
            
            # Urgent domains (urgent and expired)
            urgent_domains = self.env['project.domain'].search([
                ('expiry_status', 'in', ['urgent', 'expired'])
            ])
            record.urgent_domains_count = len(urgent_domains)
            
            # Expiring hosting (warning, urgent, expired)
            expiring_hosting = self.env['project.hosting'].search([
                ('expiry_status', 'in', ['warning', 'urgent', 'expired'])
            ])
            record.expiring_hosting_count = len(expiring_hosting)
            
            # Urgent hosting (urgent and expired)
            urgent_hosting = self.env['project.hosting'].search([
                ('expiry_status', 'in', ['urgent', 'expired'])
            ])
            record.urgent_hosting_count = len(urgent_hosting)

    def get_income_analysis_data(self):
        """Get income analysis data for charts"""
        domain = []
        if self.date_from:
            domain.append(('date', '>=', self.date_from))
        if self.date_to:
            domain.append(('date', '<=', self.date_to))
        
        incomes = self.env['project.income'].search(domain)
        
        # Monthly income data
        monthly_data = {}
        for income in incomes:
            month_key = income.date.strftime('%Y-%m')
            if month_key not in monthly_data:
                monthly_data[month_key] = 0
            monthly_data[month_key] += income.amount
        
        # Project-wise income
        project_data = {}
        for income in incomes:
            project_name = income.project_name
            if project_name not in project_data:
                project_data[project_name] = 0
            project_data[project_name] += income.amount
        
        # Customer-wise income
        customer_data = {}
        for income in incomes:
            customer_name = income.client_name
            if customer_name not in customer_data:
                customer_data[customer_name] = 0
            customer_data[customer_name] += income.amount
        
        return {
            'monthly': monthly_data,
            'projects': project_data,
            'customers': customer_data,
        }
    
    def get_expense_analysis_data(self):
        """Get expense analysis data for charts"""
        domain = []
        if self.date_from:
            domain.append(('date', '>=', self.date_from))
        if self.date_to:
            domain.append(('date', '<=', self.date_to))
        
        expenses = self.env['project.expense'].search(domain)
        
        # Monthly expense data
        monthly_data = {}
        for expense in expenses:
            month_key = expense.date.strftime('%Y-%m')
            if month_key not in monthly_data:
                monthly_data[month_key] = 0
            monthly_data[month_key] += expense.amount
        
        # Expense type data
        type_data = {}
        for expense in expenses:
            expense_type = expense.expense_type
            if expense_type not in type_data:
                type_data[expense_type] = 0
            type_data[expense_type] += expense.amount
        
        # Project-wise expense
        project_data = {}
        for expense in expenses:
            project_name = expense.project_name
            if project_name not in project_data:
                project_data[project_name] = 0
            project_data[project_name] += expense.amount
        
        return {
            'monthly': monthly_data,
            'types': type_data,
            'projects': project_data,
        }

    def action_refresh(self):
        """Refresh dashboard data"""
        # Force recompute of all computed fields
        self._compute_project_kpis()
        self._compute_financial_kpis()
        self._compute_top_customers()
        self._compute_expiry_notifications()
        return True

    def action_refresh(self):
        """Refresh dashboard data"""
        # Force recomputation of all computed fields
        self._compute_project_kpis()
        self._compute_financial_kpis()
        self._compute_top_customers()
        self._compute_expiry_notifications()
        
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }
    
    def action_view_expiring_domains(self):
        """View expiring domains"""
        return {
            'type': 'ir.actions.act_window',
            'name': '⚠️ Expiring Domains',
            'res_model': 'project.domain',
            'view_mode': 'list,form',
            'domain': [('expiry_status', 'in', ['warning', 'urgent', 'expired'])],
            'context': {'search_default_urgent': 1, 'search_default_warning': 1, 'search_default_expired': 1},
            'target': 'current',
        }
    
    def action_view_expiring_hosting(self):
        """View expiring hosting services"""
        return {
            'type': 'ir.actions.act_window',
            'name': '⚠️ Expiring Hosting Services',
            'res_model': 'project.hosting',
            'view_mode': 'list,form',
            'domain': [('expiry_status', 'in', ['warning', 'urgent', 'expired'])],
            'context': {'search_default_urgent': 1, 'search_default_warning': 1, 'search_default_expired': 1},
            'target': 'current',
        }
    
    def action_view_urgent_domains(self):
        """View urgent domains"""
        return {
            'type': 'ir.actions.act_window',
            'name': '🚨 Urgent Domains',
            'res_model': 'project.domain',
            'view_mode': 'list,form',
            'domain': [('expiry_status', 'in', ['urgent', 'expired'])],
            'context': {'search_default_urgent': 1, 'search_default_expired': 1},
            'target': 'current',
        }
    
    def action_view_urgent_hosting(self):
        """View urgent hosting services"""
        return {
            'type': 'ir.actions.act_window',
            'name': '🚨 Urgent Hosting Services',
            'res_model': 'project.hosting',
            'view_mode': 'list,form',
            'domain': [('expiry_status', 'in', ['urgent', 'expired'])],
            'context': {'search_default_urgent': 1, 'search_default_expired': 1},
            'target': 'current',
        }
    
    def get_expiry_summary(self):
        """Get a summary of expiring domains and hosting for quick view"""
        domain_data = self.env['project.domain'].search([
            ('expiry_status', 'in', ['warning', 'urgent', 'expired'])
        ])
        hosting_data = self.env['project.hosting'].search([
            ('expiry_status', 'in', ['warning', 'urgent', 'expired'])
        ])
        
        # Group by status
        domain_summary = {
            'warning': len(domain_data.filtered(lambda d: d.expiry_status == 'warning')),
            'urgent': len(domain_data.filtered(lambda d: d.expiry_status == 'urgent')),
            'expired': len(domain_data.filtered(lambda d: d.expiry_status == 'expired')),
        }
        
        hosting_summary = {
            'warning': len(hosting_data.filtered(lambda h: h.expiry_status == 'warning')),
            'urgent': len(hosting_data.filtered(lambda h: h.expiry_status == 'urgent')),
            'expired': len(hosting_data.filtered(lambda h: h.expiry_status == 'expired')),
        }
        
        return {
            'domains': domain_summary,
            'hosting': hosting_summary,
            'total_domains': len(domain_data),
            'total_hosting': len(hosting_data),
        }


class ProjectDashboardWizard(models.TransientModel):
    _name = 'project.dashboard.analytics.wizard'
    _description = 'Project Dashboard Wizard'
    
    date_from = fields.Date(string='Date From', default=lambda self: fields.Date.today().replace(day=1))
    date_to = fields.Date(string='Date To', default=fields.Date.today)
    
    def action_view_dashboard(self):
        # Create or update dashboard record
        dashboard = self.env['project.dashboard.analytics'].search([], limit=1)
        if not dashboard:
            dashboard = self.env['project.dashboard.analytics'].create({
                'name': 'Project Analytics Dashboard',
                'date_from': self.date_from,
                'date_to': self.date_to,
            })
        else:
            dashboard.write({
                'date_from': self.date_from,
                'date_to': self.date_to,
            })
        
        return {
            'type': 'ir.actions.act_window',
            'name': 'Project Dashboard',
            'res_model': 'project.dashboard.analytics',
            'res_id': dashboard.id,
            'view_mode': 'form',
            'target': 'current',
        }
