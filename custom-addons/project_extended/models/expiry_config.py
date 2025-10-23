from odoo import models, fields, api

class ExpiryNotificationConfig(models.TransientModel):
    _inherit = 'res.config.settings'

    # Email configuration for expiry notifications
    expiry_notification_email = fields.Char(
        string='Email for Expiry Notifications',
        help='Email address that will be used to send domain and hosting expiry notifications to clients',
        config_parameter='project_extended.expiry_notification_email'
    )
    
    expiry_notification_mobile = fields.Char(
        string='Mobile Number for Support',
        help='Mobile number that will be displayed in expiry notification emails',
        config_parameter='project_extended.expiry_notification_mobile',
        default='0762682176'
    )
    
    # Notification timing settings
    domain_warning_days = fields.Integer(
        string='Domain Warning Days',
        help='Number of days before expiry to send warning notifications',
        config_parameter='project_extended.domain_warning_days',
        default=7
    )
    
    domain_urgent_days = fields.Integer(
        string='Domain Urgent Days',
        help='Number of days before expiry to send urgent notifications',
        config_parameter='project_extended.domain_urgent_days',
        default=3
    )
    
    hosting_warning_days = fields.Integer(
        string='Hosting Warning Days',
        help='Number of days before expiry to send warning notifications',
        config_parameter='project_extended.hosting_warning_days',
        default=7
    )
    
    hosting_urgent_days = fields.Integer(
        string='Hosting Urgent Days',
        help='Number of days before expiry to send urgent notifications',
        config_parameter='project_extended.hosting_urgent_days',
        default=3
    )
    
    # Email sending options
    auto_send_emails = fields.Boolean(
        string='Auto Send Email Notifications',
        help='Automatically send email notifications to clients when domains/hosting are expiring',
        config_parameter='project_extended.auto_send_emails',
        default=True
    )
