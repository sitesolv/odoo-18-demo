from odoo import models, fields, api
from odoo.exceptions import ValidationError

class ProjectIncome(models.Model):
    _name = 'project.income'
    _description = 'Project Income'
    _order = 'date desc, id desc'

    project_id = fields.Many2one('project.project', required=True, string='Project')
    client_id = fields.Many2one('res.partner', required=True, string='Client')
    amount = fields.Float(required=True, string='Amount')
    date = fields.Date(required=True, string='Date')
    description = fields.Char(string='Description')
    
    # Fields to track invoice payment relationship
    payment_id = fields.Many2one('account.payment', string='Payment', ondelete='cascade')
    invoice_id = fields.Many2one('account.move', string='Invoice', ondelete='cascade')
    source_type = fields.Selection([
        ('manual', 'Manual Entry'),
        ('payment', 'Invoice Payment'),
    ], string='Source Type', default='manual')
    
    # Computed fields for better reporting
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)
    project_name = fields.Char(related='project_id.name', string='Project Name')
    client_name = fields.Char(related='client_id.name', string='Client Name')
    
    @api.constrains('amount')
    def _check_amount(self):
        for record in self:
            if record.amount <= 0:
                raise ValidationError("Income amount must be positive.")
    
    def name_get(self):
        result = []
        for record in self:
            name = f"{record.project_name} - {record.amount:,.2f} ({record.date})"
            result.append((record.id, name))
        return result
