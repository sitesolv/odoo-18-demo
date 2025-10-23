from odoo import models, fields, api

class OtherService(models.Model):
    _name = 'project.other.service'
    _description = 'Other Services'

    name = fields.Char("Service Name", required=True)
    date = fields.Date("Date", required=True)
    cost = fields.Float("Cost")
    username = fields.Char("Username")
    password = fields.Char("Password")
    description = fields.Text("Additional Information")
    project_id = fields.Many2one('project.project', string="Project", required=True)
    client_id = fields.Many2one('res.partner', string="Client", required=True)

    def name_get(self):
        """Override name_get to show service name with date"""
        result = []
        for record in self:
            name = f"{record.name} ({record.date})"
            result.append((record.id, name))
        return result

    @api.model_create_multi
    def create(self, vals_list):
        """Override create to automatically add expense when other service is created"""
        services = super().create(vals_list)
        for service in services:
            if service.cost and service.cost > 0:
                # Create expense record with custom type
                self.env['project.expense'].create({
                    'project_id': service.project_id.id,
                    'expense_type': 'other',
                    'custom_expense_type': service.name,  # Use service name as expense type
                    'amount': service.cost,
                    'date': service.date or fields.Date.today(),
                    'description': f"Other Service: {service.name}",
                    'notes': f"Service: {service.name} - {service.description or 'No additional notes'}"
                })
        return services

    def write(self, vals):
        """Override write to update expense when other service cost is changed"""
        result = super().write(vals)
        if 'cost' in vals or 'name' in vals:
            for service in self:
                # Find existing expense for this service
                expense = self.env['project.expense'].search([
                    ('project_id', '=', service.project_id.id),
                    ('expense_type', '=', 'other'),
                    ('description', '=', f"Other Service: {service.name}")
                ], limit=1)
                
                cost = vals.get('cost', service.cost)
                if cost and cost > 0:
                    if expense:
                        # Update existing expense
                        expense.write({
                            'custom_expense_type': vals.get('name', service.name),
                            'amount': cost,
                            'date': vals.get('date', service.date) or fields.Date.today(),
                            'description': f"Other Service: {vals.get('name', service.name)}",
                            'notes': f"Service: {vals.get('name', service.name)} - {vals.get('description', service.description) or 'No additional notes'}"
                        })
                    else:
                        # Create new expense if none exists
                        self.env['project.expense'].create({
                            'project_id': service.project_id.id,
                            'expense_type': 'other',
                            'custom_expense_type': vals.get('name', service.name),
                            'amount': cost,
                            'date': vals.get('date', service.date) or fields.Date.today(),
                            'description': f"Other Service: {vals.get('name', service.name)}",
                            'notes': f"Service: {vals.get('name', service.name)} - {vals.get('description', service.description) or 'No additional notes'}"
                        })
        return result
