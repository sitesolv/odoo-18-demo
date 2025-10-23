from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import timedelta

class HostingDetail(models.Model):
    _name = 'project.hosting'
    _description = 'Hosting Details'

    name = fields.Char("Hosting Service Provider", required=True)
    provider = fields.Char("Provider", required=True)  # Keep for backward compatibility
    bought_date = fields.Date(required=True)
    expiry_date = fields.Date(required=True)
    username = fields.Char("Username")
    password = fields.Char("Password")
    description = fields.Text("Additional Information")
    project_id = fields.Many2one('project.project', required=True)
    client_id = fields.Many2one('res.partner', string="Client Name", required=True)
    reminder_sent = fields.Boolean(default=False)
    urgent_notification = fields.Boolean(default=False)
    cost = fields.Float("Cost")
    
    # Computed fields for notification status
    expiry_status = fields.Selection([
        ('valid', 'Valid'),
        ('warning', 'Expires Soon'),
        ('urgent', 'Urgent'),
        ('expired', 'Expired')
    ], compute='_compute_expiry_status', store=True)
    
    days_to_expiry = fields.Integer(compute='_compute_days_to_expiry')

    def name_get(self):
        """Override name_get to show hosting service with expiry status"""
        result = []
        for record in self:
            status_emoji = {
                'valid': '✅',
                'warning': '⚠️',
                'urgent': '🚨',
                'expired': '❌'
            }
            emoji = status_emoji.get(record.expiry_status, '')
            name = f"{emoji} {record.name}"
            result.append((record.id, name))
        return result

    @api.model_create_multi
    def create(self, vals_list):
        """Override create to automatically add expense when hosting is created"""
        hostings = super().create(vals_list)
        for hosting in hostings:
            if hosting.cost and hosting.cost > 0:
                # Create expense record
                self.env['project.expense'].create({
                    'project_id': hosting.project_id.id,
                    'expense_type': 'hosting',
                    'amount': hosting.cost,
                    'date': hosting.bought_date or fields.Date.today(),
                    'description': f"Hosting: {hosting.name}",
                    'notes': f"Hosting service {hosting.name} from {hosting.provider or 'Unknown Provider'}"
                })
        return hostings

    def write(self, vals):
        """Override write to update expense when hosting cost is changed"""
        result = super().write(vals)
        if 'cost' in vals:
            for hosting in self:
                # Find existing expense for this hosting
                expense = self.env['project.expense'].search([
                    ('project_id', '=', hosting.project_id.id),
                    ('expense_type', '=', 'hosting'),
                    ('description', '=', f"Hosting: {hosting.name}")
                ], limit=1)
                
                cost = vals.get('cost', hosting.cost)
                if cost and cost > 0:
                    if expense:
                        # Update existing expense
                        expense.write({
                            'amount': cost,
                            'date': vals.get('bought_date', hosting.bought_date) or fields.Date.today(),
                            'notes': f"Hosting service {hosting.name} from {hosting.provider or 'Unknown Provider'}"
                        })
                    else:
                        # Create new expense if none exists
                        self.env['project.expense'].create({
                            'project_id': hosting.project_id.id,
                            'expense_type': 'hosting',
                            'amount': cost,
                            'date': vals.get('bought_date', hosting.bought_date) or fields.Date.today(),
                            'description': f"Hosting: {hosting.name}",
                            'notes': f"Hosting service {hosting.name} from {hosting.provider or 'Unknown Provider'}"
                        })
        return result

    @api.depends('expiry_date')
    def _compute_expiry_status(self):
        today = fields.Date.today()
        for hosting in self:
            if hosting.expiry_date:
                days_diff = (hosting.expiry_date - today).days
                if days_diff < 0:
                    hosting.expiry_status = 'expired'
                elif days_diff <= 3:
                    hosting.expiry_status = 'urgent'
                elif days_diff <= 7:
                    hosting.expiry_status = 'warning'
                else:
                    hosting.expiry_status = 'valid'
            else:
                hosting.expiry_status = 'valid'

    @api.depends('expiry_date')
    def _compute_days_to_expiry(self):
        today = fields.Date.today()
        for hosting in self:
            if hosting.expiry_date:
                hosting.days_to_expiry = (hosting.expiry_date - today).days
            else:
                hosting.days_to_expiry = 0

    @api.model
    def check_expiry(self):
        """Check for hosting services expiring within 7 days or already expired"""
        today = fields.Date.today()
        upcoming = today + timedelta(days=7)
        
        # Find services expiring within 7 days
        expiring = self.search([
            ('expiry_date', '<=', upcoming), 
            ('expiry_date', '>=', today), 
            ('reminder_sent', '=', False)
        ])
        
        # Find expired services
        expired = self.search([
            ('expiry_date', '<', today),
            ('urgent_notification', '=', False)
        ])
        
        for hosting in expiring:
            self._create_notification(hosting, 'warning')
            # Send email to client
            self._send_client_email(hosting, 'warning')
            hosting.reminder_sent = True
            
        for hosting in expired:
            self._create_notification(hosting, 'urgent')
            # Send email to client for expired hosting
            self._send_client_email(hosting, 'urgent')
            hosting.urgent_notification = True

    def _send_client_email(self, hosting, notification_type):
        """Send email notification to client about hosting expiry"""
        if not hosting.client_id.email:
            return  # Skip if client has no email
            
        # Check if auto email sending is enabled
        auto_send = self.env['ir.config_parameter'].sudo().get_param('project_extended.auto_send_emails', 'True')
        if auto_send.lower() != 'true':
            return
            
        if notification_type == 'urgent':
            template_ref = 'project_extended.email_template_hosting_expired_client'
        else:
            template_ref = 'project_extended.email_template_hosting_expiring_client'
            
        try:
            template = self.env.ref(template_ref)
            if template:
                mail_id = template.send_mail(hosting.id, force_send=True)
                # Log successful email sending
                import logging
                _logger = logging.getLogger(__name__)
                _logger.info(f"Hosting expiry email sent to {hosting.client_id.email} for hosting {hosting.name}, mail_id: {mail_id}")
                return mail_id
            else:
                import logging
                _logger = logging.getLogger(__name__)
                _logger.error(f"Email template {template_ref} not found")
        except Exception as e:
            # Log error but don't stop the process
            import logging
            _logger = logging.getLogger(__name__)
            _logger.error(f"Failed to send hosting expiry email to {hosting.client_id.email}: {str(e)}")
        return False
    
    def _create_notification(self, hosting, notification_type):
        """Create a notification for hosting expiry"""
        if notification_type == 'urgent':
            title = f"URGENT: Hosting Expired - {hosting.name}"
            message = f"Hosting service '{hosting.name}' for project '{hosting.project_id.name}' has expired on {hosting.expiry_date}. Immediate action required!"
        else:
            days_left = (hosting.expiry_date - fields.Date.today()).days
            title = f"Hosting Expires Soon - {hosting.name}"
            message = f"Hosting service '{hosting.name}' for project '{hosting.project_id.name}' will expire in {days_left} days on {hosting.expiry_date}."
        
        # Create activity for project manager
        self.env['mail.activity'].create({
            'activity_type_id': self.env.ref('mail.mail_activity_data_warning').id,
            'res_model': 'project.project',
            'res_id': hosting.project_id.id,
            'user_id': hosting.project_id.user_id.id or self.env.user.id,
            'summary': title,
            'note': message,
            'date_deadline': fields.Date.today(),
        })
        
        # Also send system notification
        self.env['bus.bus']._sendone(
            (self._cr.dbname, 'res.partner', hosting.project_id.user_id.partner_id.id or self.env.user.partner_id.id),
            'simple_notification',
            {
                'title': title,
                'message': message,
                'type': 'danger' if notification_type == 'urgent' else 'warning',
                'sticky': True if notification_type == 'urgent' else False,
            }
        )

    @api.model
    def send_automated_expiry_reminders(self):
        """Send automated email reminders for expiring/expired hosting services"""
        import logging
        _logger = logging.getLogger(__name__)
        
        today = fields.Date.today()
        
        # Check if automated emails are enabled
        auto_send = self.env['ir.config_parameter'].sudo().get_param('project_extended.auto_send_emails', 'True')
        if auto_send.lower() != 'true':
            _logger.info("Automated hosting expiry emails are disabled")
            return
        
        # Find hosting services that need reminders
        # 1. Hosting expiring in 7 days (warning)
        warning_hostings = self.search([
            ('expiry_date', '=', today + timedelta(days=7)),
            ('client_id.email', '!=', False),
        ])
        
        # 2. Hosting expiring in 3 days (urgent)
        urgent_hostings = self.search([
            ('expiry_date', '=', today + timedelta(days=3)),
            ('client_id.email', '!=', False),
        ])
        
        # 3. Hosting expiring in 1 day (very urgent)
        very_urgent_hostings = self.search([
            ('expiry_date', '=', today + timedelta(days=1)),
            ('client_id.email', '!=', False),
        ])
        
        # 4. Hosting that expired today
        expired_hostings = self.search([
            ('expiry_date', '=', today),
            ('client_id.email', '!=', False),
        ])
        
        # Send emails
        total_sent = 0
        
        # Warning emails (7 days)
        for hosting in warning_hostings:
            if self._send_automated_email(hosting, 'warning'):
                total_sent += 1
                
        # Urgent emails (3 days)
        for hosting in urgent_hostings:
            if self._send_automated_email(hosting, 'urgent'):
                total_sent += 1
                
        # Very urgent emails (1 day)
        for hosting in very_urgent_hostings:
            if self._send_automated_email(hosting, 'urgent'):
                total_sent += 1
                
        # Expired emails
        for hosting in expired_hostings:
            if self._send_automated_email(hosting, 'expired'):
                total_sent += 1
        
        _logger.info(f"Automated hosting expiry reminder: {total_sent} emails sent successfully")
        return total_sent

    def _send_automated_email(self, hosting, email_type):
        """Send automated email using the same HTML generation as manual reminders"""
        try:
            # Get company information
            company = self.env.company
            company_email = company.email or self.env.user.email or 'info@yourcompany.com'
            company_name = company.name or 'Your Company'
            
            # Format expiry date
            expiry_date_formatted = hosting.expiry_date.strftime('%B %d, %Y')
            
            # Build email content based on type
            if email_type in ['urgent', 'expired']:
                # Urgent/Expired email
                subject = f"🚨 URGENT: Your Hosting Service \"{hosting.name}\" Has Expired!" if email_type == 'expired' else f"🚨 URGENT: Your Hosting Service \"{hosting.name}\" Expires Soon!"
                
                if email_type == 'expired':
                    days_message = "Hosting service has expired!"
                    status_message = f"⚠️ Your hosting service \"{hosting.name}\" ({hosting.provider}) expired on {expiry_date_formatted}"
                    urgent_message = "IMMEDIATE ACTION REQUIRED! Your hosting service has expired and your website may be offline."
                else:
                    days_message = f"Days remaining: {hosting.days_to_expiry} days"
                    status_message = f"⚠️ Your hosting service \"{hosting.name}\" ({hosting.provider}) expires on {expiry_date_formatted}"
                    urgent_message = "URGENT: Your hosting service expires very soon!"
                
                # Build HTML email body
                body_html = self._build_urgent_email_html(hosting, company_email, company_name, status_message, days_message, urgent_message)
            else:
                # Warning email
                subject = f"⚠️ Important: Your Hosting Service \"{hosting.name}\" is Expiring Soon"
                body_html = self._build_warning_email_html(hosting, company_email, company_name, expiry_date_formatted)
            
            # Send email
            mail_values = {
                'subject': subject,
                'body_html': body_html,
                'email_to': hosting.client_id.email,
                'email_from': company_email,
                'reply_to': company_email,
                'auto_delete': True,
            }
            
            mail = self.env['mail.mail'].create(mail_values)
            mail.send()
            
            # Log success
            import logging
            _logger = logging.getLogger(__name__)
            _logger.info(f"Automated hosting expiry email sent to {hosting.client_id.email} for hosting {hosting.name}")
            return True
            
        except Exception as e:
            # Log error but don't stop the process
            import logging
            _logger = logging.getLogger(__name__)
            _logger.error(f"Failed to send automated hosting expiry email to {hosting.client_id.email}: {str(e)}")
            return False

    def _build_urgent_email_html(self, hosting, company_email, company_name, status_message, days_message, urgent_message):
        """Build urgent email HTML content"""
        return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>URGENT: Hosting Alert</title>
</head>
<body style="margin: 0; padding: 0; font-family: Arial, sans-serif; background-color: #f4f4f4;">
    <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #f4f4f4; padding: 20px;">
        <tr>
            <td align="center">
                <table width="600" cellpadding="0" cellspacing="0" style="background-color: white; border-radius: 10px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                    <tr>
                        <td style="background-color: #dc3545; color: white; padding: 30px; text-align: center;">
                            <h1 style="margin: 0; font-size: 24px;">🚨 URGENT: Hosting Alert</h1>
                        </td>
                    </tr>
                    <tr>
                        <td style="padding: 30px;">
                            <p style="font-size: 16px; margin-bottom: 20px; color: #333;">
                                Dear <strong>{hosting.client_id.name}</strong>,
                            </p>
                            
                            <div style="background-color: #f8d7da; border-left: 4px solid #dc3545; padding: 15px; margin: 20px 0; border-radius: 4px;">
                                <p style="margin: 0; font-size: 16px; color: #721c24;">
                                    <strong>{status_message}</strong>
                                </p>
                                <p style="margin: 10px 0 0 0; font-size: 14px; color: #721c24;">
                                    {days_message}
                                </p>
                            </div>
                            
                            <p style="font-size: 16px; margin: 20px 0; color: #dc3545;">
                                <strong>{urgent_message}</strong>
                            </p>
                            
                            <p style="font-size: 16px; margin: 20px 0; color: #333;">
                                Please contact us immediately to renew your hosting service.
                            </p>
                        </td>
                    </tr>
                    <tr>
                        <td style="background-color: #fff3cd; padding: 25px; border: 2px solid #ffc107;">
                            <h3 style="color: #856404; margin: 0 0 15px 0; font-size: 18px;">🆘 URGENT CONTACT REQUIRED:</h3>
                            <p style="margin: 8px 0; color: #333;">
                                <strong>📧 Email:</strong> 
                                <a href="mailto:{company_email}" style="color: #dc3545; text-decoration: none; font-weight: bold;">
                                    {company_email}
                                </a>
                            </p>
                            <p style="margin: 8px 0; color: #333;">
                                <strong>📱 Mobile:</strong> 
                                <a href="tel:0762682176" style="color: #dc3545; text-decoration: none; font-weight: bold;">0762682176</a>
                            </p>
                        </td>
                    </tr>
                    <tr>
                        <td style="background-color: #f8f9fa; padding: 20px; text-align: center; border-top: 1px solid #dee2e6;">
                            <p style="color: #6c757d; font-size: 14px; margin: 0;">
                                Urgent regards,<br/>
                                <strong>{company_name} Team</strong>
                            </p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>"""

    def _build_warning_email_html(self, hosting, company_email, company_name, expiry_date_formatted):
        """Build warning email HTML content"""
        return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Hosting Expiry Notice</title>
</head>
<body style="margin: 0; padding: 0; font-family: Arial, sans-serif; background-color: #f4f4f4;">
    <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #f4f4f4; padding: 20px;">
        <tr>
            <td align="center">
                <table width="600" cellpadding="0" cellspacing="0" style="background-color: white; border-radius: 10px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                    <tr>
                        <td style="background-color: #f39c12; color: white; padding: 30px; text-align: center;">
                            <h1 style="margin: 0; font-size: 24px;">⚠️ Hosting Expiry Notice</h1>
                        </td>
                    </tr>
                    <tr>
                        <td style="padding: 30px;">
                            <p style="font-size: 16px; margin-bottom: 20px; color: #333;">
                                Dear <strong>{hosting.client_id.name}</strong>,
                            </p>
                            
                            <div style="background-color: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin: 20px 0; border-radius: 4px;">
                                <p style="margin: 0; font-size: 16px; color: #856404;">
                                    <strong>Your hosting service "{hosting.name}" ({hosting.provider}) expires on {expiry_date_formatted}</strong>
                                </p>
                                <p style="margin: 10px 0 0 0; font-size: 14px; color: #856404;">
                                    Days remaining: <strong>{hosting.days_to_expiry} days</strong>
                                </p>
                            </div>
                            
                            <p style="font-size: 16px; margin: 20px 0; color: #333;">
                                Please renew your hosting service before the expiry date.
                            </p>
                            
                            <div style="background-color: #f8d7da; border-left: 4px solid #dc3545; padding: 15px; margin: 20px 0; border-radius: 4px;">
                                <p style="margin: 0; font-size: 16px; color: #721c24;">
                                    <strong>Please renew quickly to avoid website downtime!</strong>
                                </p>
                            </div>
                        </td>
                    </tr>
                    <tr>
                        <td style="background-color: #e3f2fd; padding: 25px;">
                            <h3 style="color: #1976d2; margin: 0 0 15px 0; font-size: 18px;">📞 Need Assistance? Contact Us:</h3>
                            <p style="margin: 8px 0; color: #333;">
                                <strong>📧 Email:</strong> 
                                <a href="mailto:{company_email}" style="color: #1976d2; text-decoration: none;">
                                    {company_email}
                                </a>
                            </p>
                            <p style="margin: 8px 0; color: #333;">
                                <strong>📱 Mobile:</strong> 
                                <a href="tel:0762682176" style="color: #1976d2; text-decoration: none;">0762682176</a>
                            </p>
                        </td>
                    </tr>
                    <tr>
                        <td style="background-color: #f8f9fa; padding: 20px; text-align: center; border-top: 1px solid #dee2e6;">
                            <p style="color: #6c757d; font-size: 14px; margin: 0;">
                                Best regards,<br/>
                                <strong>{company_name} Team</strong>
                            </p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>"""
