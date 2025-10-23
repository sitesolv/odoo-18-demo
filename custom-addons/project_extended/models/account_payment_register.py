from odoo import models, fields, api, _
from datetime import timedelta

class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    def action_create_payments(self):
        """Override to trigger project income creation when payments are registered from invoices"""
        result = super().action_create_payments()
        
        # Handle different return types from the parent method
        payment_ids = []
        
        if isinstance(result, dict):
            # If result is a dictionary, try to get payment IDs
            res_id = result.get('res_id')
            if res_id:
                if isinstance(res_id, int):
                    payment_ids = [res_id]
                elif isinstance(res_id, list):
                    payment_ids = res_id
        elif isinstance(result, bool) or not result:
            # If result is boolean or None, find recent payments
            recent_payments = self.env['account.payment'].search([
                ('create_date', '>=', fields.Datetime.now() - timedelta(minutes=5)),
                ('payment_type', '=', 'inbound'),
                ('create_uid', '=', self.env.uid)
            ])
            payment_ids = recent_payments.ids
        
        # Process the payments for project income creation
        if payment_ids:
            payment_records = self.env['account.payment'].browse(payment_ids)
            for payment in payment_records:
                if payment.payment_type == 'inbound':
                    # Immediate processing
                    payment._create_project_income_from_payment()
                    # Delayed processing to catch any late reconciliations
                    self.env['account.payment']._schedule_delayed_processing(payment.id)
        
        return result

class AccountPaymentMethod(models.Model):
    _inherit = 'account.payment.method'

    def _get_payment_method_information(self):
        """Override to add custom processing info"""
        res = super()._get_payment_method_information()
        return res
