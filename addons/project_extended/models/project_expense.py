from odoo import models, fields, api
from odoo.exceptions import ValidationError

class ProjectExpense(models.Model):
    _name = 'project.expense'
    _description = 'Project Expense'
    _order = 'date desc, id desc'

    project_id = fields.Many2one('project.project', required=True, string='Project')
    employee_id = fields.Many2one('hr.employee', string="Employee (if salary)")
    expense_type = fields.Selection([
        ('domain', 'Domain'),
        ('hosting', 'Hosting'),
        ('salary', 'Salary'),
        ('licenses', 'Licenses'),
        ('development', 'Development'),
        ('design', 'Design'),
        ('other', 'Other')
    ], string="Type", required=True)
    custom_expense_type = fields.Char("Custom Type")  # For other services with dynamic names
    amount = fields.Float(required=True, string='Amount')
    date = fields.Date(required=True, string='Date')
    notes = fields.Text(string='Notes')
    description = fields.Char(string='Description')
    
    # Computed fields for better reporting
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)
    project_name = fields.Char(related='project_id.name', string='Project Name')
    
    @api.constrains('amount')
    def _check_amount(self):
        for record in self:
            if record.amount <= 0:
                raise ValidationError("Expense amount must be positive.")
    
    def name_get(self):
        result = []
        for record in self:
            # Use custom expense type if available, otherwise use the selection value
            expense_type_display = record.custom_expense_type or record.expense_type.title()
            name = f"{record.project_name} - {expense_type_display} - {record.amount:,.2f} ({record.date})"
            result.append((record.id, name))
        return result
