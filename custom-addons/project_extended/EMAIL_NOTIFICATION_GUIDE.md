# Email Notification System for Domain and Hosting Expiry

## Overview
The system automatically sends professional email notifications to clients when their domains or hosting services are about to expire or have already expired.

## Email Templates Created

### 1. Domain Expiring Soon
- **Template ID**: `email_template_domain_expiring_client`
- **Trigger**: 7 days before expiry (configurable)
- **Subject**: ⚠️ Important: Your Domain "domain.com" is Expiring Soon

### 2. Domain Expired (Urgent)
- **Template ID**: `email_template_domain_expired_client`
- **Trigger**: When domain has expired
- **Subject**: 🚨 URGENT: Your Domain "domain.com" Has Expired!

### 3. Hosting Expiring Soon
- **Template ID**: `email_template_hosting_expiring_client`
- **Trigger**: 7 days before expiry (configurable)
- **Subject**: ⚠️ Important: Your Hosting Service "service" is Expiring Soon

### 4. Hosting Expired (Urgent)
- **Template ID**: `email_template_hosting_expired_client`
- **Trigger**: When hosting has expired
- **Subject**: 🚨 URGENT: Your Hosting Service "service" Has Expired!

## Email Content Features

### Professional Design
- Modern, responsive HTML design
- Color-coded alerts (orange for warning, red for urgent)
- Professional styling with proper branding
- Mobile-friendly layout

### Personalized Content
- Client name personalization
- Specific domain/hosting service details
- Exact expiry dates
- Days remaining/overdue calculations

### Contact Information
- Company email address (configurable)
- Mobile number: 0762682176 (configurable)
- Clickable email and phone links

### Clear Call-to-Action
- Urgent messaging for immediate attention
- Professional language encouraging quick renewal
- Contact details prominently displayed

## Configuration

### Email Settings
Navigate to: **Project Tracking → Settings**

1. **Email for Expiry Notifications**: Set your company email address
2. **Mobile Number for Support**: Configure support phone number (default: 0762682176)
3. **Auto Send Email Notifications**: Enable/disable automatic email sending

### Timing Configuration
- **Domain Warning Days**: Days before expiry to send warning (default: 7)
- **Domain Urgent Days**: Days before expiry to send urgent alerts (default: 3)
- **Hosting Warning Days**: Days before expiry to send warning (default: 7)
- **Hosting Urgent Days**: Days before expiry to send urgent alerts (default: 3)

## Automatic Execution

### Cron Jobs
The system runs daily checks via scheduled actions:
- **Check Domain Expiry**: Runs daily at midnight
- **Check Hosting Expiry**: Runs daily at midnight

### Email Sending Logic
1. **Warning Emails**: Sent once when item reaches warning threshold
2. **Urgent Emails**: Sent once when item becomes urgent/expired
3. **Prevention of Duplicates**: Uses flags to prevent duplicate emails
4. **Error Handling**: Gracefully handles email sending errors

## Manual Testing

### Send Test Emails
You can manually test email sending:
1. Go to Domain/Hosting list view
2. Select records to test
3. Use "Action" → "Send Test Email" (available in development mode)

### Email Queue
Monitor sent emails in: **Settings → Technical → Email → Emails**

## Email Template Variables

### Available Variables
- `${object.name}`: Domain/hosting service name
- `${object.client_id.name}`: Client name
- `${object.expiry_date}`: Expiry date
- `${object.provider}`: Hosting provider (for hosting emails)
- `${user.company_id.name}`: Company name
- Custom config parameters for email and mobile

### Configuration Parameters
- `project_extended.expiry_notification_email`: Company email
- `project_extended.expiry_notification_mobile`: Support mobile number
- `project_extended.auto_send_emails`: Enable/disable auto emails

## Email Body Sample

### Domain Expiring Email
```
Dear [Client Name],

⚠️ Your domain "example.com" is expiring on July 30, 2025
Days remaining: 5 days

To ensure uninterrupted service and avoid any downtime, please renew your domain as soon as possible.

Please renew quickly to avoid service disruption!

📞 Need Assistance? Contact Us:
📧 Email: your-company@email.com
📱 Mobile: 0762682176

Best regards,
Your Company Team
```

## Troubleshooting

### Common Issues
1. **Emails not sending**: Check if auto_send_emails is enabled in settings
2. **Wrong email address**: Configure proper email in Project Extended Settings
3. **Cron not running**: Check if scheduled actions are active

### Email Logs
Check email sending status in: **Settings → Technical → Email → Mail**
