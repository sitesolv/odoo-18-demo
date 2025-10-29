from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class ProjectProjectExtended(models.Model):
    _inherit = 'project.project'

    total_income = fields.Float(string='Total Income', compute='_compute_financial_data', store=False)
    total_expense = fields.Float(string='Total Expense', compute='_compute_financial_data', store=False)
    net_profit = fields.Float(string='Net Profit', compute='_compute_financial_data', store=False)
    profit_margin = fields.Float(string='Profit Margin %', compute='_compute_financial_data', store=False)
    financial_status = fields.Char(string='Financial Status', compute='_compute_financial_data', store=False)
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)

    @api.depends('name')
    def _compute_financial_data(self):
        """Compute financial data for each project"""
        for project in self:
            # Get income data
            income_records = self.env['project.income'].search([('project_id', '=', project.id)])
            total_income = sum(income_records.mapped('amount'))
            
            # Get expense data
            expense_records = self.env['project.expense'].search([('project_id', '=', project.id)])
            total_expense = sum(expense_records.mapped('amount'))
            
            # Calculate profit and margin
            net_profit = total_income - total_expense
            profit_margin = (net_profit / total_income * 100) if total_income > 0 else 0
            
            # Determine status
            if net_profit > 0:
                status = 'Profitable'
            elif net_profit < 0:
                status = 'Loss'
            else:
                status = 'Break Even'
            
            # Set computed fields
            project.total_income = total_income
            project.total_expense = total_expense
            project.net_profit = net_profit
            project.profit_margin = profit_margin
            project.financial_status = status

    def view_income(self):
        """Action to view project income"""
        return {
            'name': f'Income for {self.name}',
            'type': 'ir.actions.act_window',
            'res_model': 'project.income',
            'view_mode': 'list,form',
            'domain': [('project_id', '=', self.id)],
            'context': {'default_project_id': self.id},
        }

    def view_expenses(self):
        """Action to view project expenses"""
        return {
            'name': f'Expenses for {self.name}',
            'type': 'ir.actions.act_window',
            'res_model': 'project.expense',
            'view_mode': 'list,form',
            'domain': [('project_id', '=', self.id)],
            'context': {'default_project_id': self.id},
        }
