from odoo import http
from odoo.http import request

class ProjectDashboard(http.Controller):

    @http.route('/project/dashboard', auth='user', website=True)
    def project_dashboard(self, **kw):
        projects = request.env['project.project'].sudo().search([])
        income_model = request.env['project.income'].sudo()
        expense_model = request.env['project.expense'].sudo()

        summary = []
        for project in projects:
            income = sum(income_model.search([('project_id', '=', project.id)]).mapped('amount'))
            expense = sum(expense_model.search([('project_id', '=', project.id)]).mapped('amount'))
            summary.append({
                'name': project.name,
                'client': project.partner_id.name,
                'income': income,
                'expense': expense,
                'profit': income - expense
            })

        return request.render('project_reporting.project_dashboard_template', {'summary': summary})
