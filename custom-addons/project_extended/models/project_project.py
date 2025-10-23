from odoo import models, fields, api

class ProjectProject(models.Model):
    _inherit = 'project.project'

    # Related fields for domains, hosting, other services, incomes, and expenses
    domain_ids = fields.One2many('project.domain', 'project_id', string='Domains')
    hosting_ids = fields.One2many('project.hosting', 'project_id', string='Hosting Services')
    other_service_ids = fields.One2many('project.other.service', 'project_id', string='Other Services')
    income_ids = fields.One2many('project.income', 'project_id', string='Incomes')
    expense_ids = fields.One2many('project.expense', 'project_id', string='Expenses')
    
    # Computed fields for totals
    total_income = fields.Float(string='Total Income', compute='_compute_totals', store=True)
    total_expense = fields.Float(string='Total Expenses', compute='_compute_totals', store=True)
    net_profit = fields.Float(string='Net Profit', compute='_compute_totals', store=True)
    amount_due = fields.Float(string='Amount Due', compute='_compute_amount_due', store=False)
    domain_count = fields.Integer(string='Domain Count', compute='_compute_counts')
    hosting_count = fields.Integer(string='Hosting Count', compute='_compute_counts')
    other_service_count = fields.Integer(string='Other Services Count', compute='_compute_counts')
    
    # Notification status for expiring domains/hosting
    has_expiring_domains = fields.Boolean(compute='_compute_expiry_notifications')
    has_expiring_hosting = fields.Boolean(compute='_compute_expiry_notifications')
    has_urgent_notifications = fields.Boolean(compute='_compute_expiry_notifications')
    
    @api.depends('income_ids.amount', 'expense_ids.amount')
    def _compute_totals(self):
        for record in self:
            record.total_income = sum(record.income_ids.mapped('amount'))
            record.total_expense = sum(record.expense_ids.mapped('amount'))
            record.net_profit = record.total_income - record.total_expense
    
    @api.depends('task_ids', 'name')
    def _compute_amount_due(self):
        for record in self:
            amount_due = 0.0
            
            try:
                # Find invoices related to this project through sale orders
                related_invoices = self.env['account.move']
                
                # Method 1: Find through sale order lines linked to project tasks
                task_sale_lines = record.task_ids.mapped('sale_line_id')
                if task_sale_lines:
                    sale_orders = task_sale_lines.mapped('order_id')
                    related_invoices |= sale_orders.mapped('invoice_ids').filtered(
                        lambda inv: inv.move_type == 'out_invoice' and inv.state == 'posted'
                    )
                
                # Method 2: Find through project's direct sale_line_id if exists
                if hasattr(record, 'sale_line_id') and record.sale_line_id:
                    sale_order = record.sale_line_id.order_id
                    related_invoices |= sale_order.invoice_ids.filtered(
                        lambda inv: inv.move_type == 'out_invoice' and inv.state == 'posted'
                    )
                
                # Method 3: Search by project name in invoice origin/reference fields
                if record.name:
                    try:
                        origin_invoices = self.env['account.move'].search([
                            '|',
                            ('invoice_origin', 'ilike', record.name),
                            ('ref', 'ilike', record.name),
                            ('move_type', '=', 'out_invoice'),
                            ('state', '=', 'posted')
                        ])
                        related_invoices |= origin_invoices
                    except Exception:
                        # If invoice_origin field doesn't exist, try other methods
                        pass
                
                # Calculate total amount due from all related invoices
                amount_due = sum(related_invoices.mapped('amount_residual'))
                
            except Exception as e:
                # If any error occurs, set amount_due to 0
                amount_due = 0.0
                
            record.amount_due = amount_due
    
    @api.depends('domain_ids', 'hosting_ids', 'other_service_ids')
    def _compute_counts(self):
        for record in self:
            record.domain_count = len(record.domain_ids)
            record.hosting_count = len(record.hosting_ids)
            record.other_service_count = len(record.other_service_ids)
    
    @api.depends('domain_ids.expiry_status', 'hosting_ids.expiry_status')
    def _compute_expiry_notifications(self):
        for record in self:
            domain_warning = record.domain_ids.filtered(lambda d: d.expiry_status in ['warning', 'urgent', 'expired'])
            hosting_warning = record.hosting_ids.filtered(lambda h: h.expiry_status in ['warning', 'urgent', 'expired'])
            
            record.has_expiring_domains = bool(domain_warning)
            record.has_expiring_hosting = bool(hosting_warning)
            
            urgent_domains = record.domain_ids.filtered(lambda d: d.expiry_status in ['urgent', 'expired'])
            urgent_hosting = record.hosting_ids.filtered(lambda h: h.expiry_status in ['urgent', 'expired'])
            record.has_urgent_notifications = bool(urgent_domains or urgent_hosting)

    def refresh_amount_due(self):
        """Method to manually refresh amount due calculation"""
        self._compute_amount_due()
        
    @api.model
    def refresh_all_projects_amount_due(self):
        """Method to refresh amount due for all projects"""
        projects = self.search([])
        projects._compute_amount_due()
