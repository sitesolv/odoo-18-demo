from odoo import models, fields, api

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    auto_send_expiry_emails = fields.Boolean(
        string='Auto Send Expiry Emails',
        config_parameter='project_extended.auto_send_emails',
        default=True,
        help='Automatically send email reminders to clients when domains and hosting services are about to expire'
    )