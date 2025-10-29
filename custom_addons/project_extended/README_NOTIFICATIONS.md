# Project Extended - Domain and Hosting Expiry Notifications

## Overview
This enhanced version of the Project Extended addon includes comprehensive domain and hosting expiry notification system to help you stay on top of important renewal dates.

## New Features

### 🚨 Expiry Notification System
- **Automatic monitoring** of domain and hosting service expiry dates
- **Smart notifications** with different urgency levels:
  - **🟢 Valid**: More than 7 days until expiry
  - **🟡 Warning**: 4-7 days until expiry  
  - **🔴 Urgent**: 1-3 days until expiry
  - **⚫ Expired**: Already expired

### 📧 Notification Methods
1. **System Notifications**: Real-time browser notifications
2. **Activity Reminders**: Assigned to project managers
3. **Email Alerts**: Automatic email notifications (for domains)
4. **Visual Alerts**: Color-coded status indicators in all views

### 📊 Dashboard Features
- **Expiry Dashboard**: Centralized view of all expiring services
- **Project-Level Alerts**: Warning banners on project forms
- **Quick Access Menus**: Direct links to expiring domains/hosting
- **Status Badges**: Clear visual indicators throughout the system

### 🔄 Automated Monitoring
- **Daily Checks**: Scheduled actions run daily to check expiry dates
- **Smart Reset**: Notifications reset when dates are updated
- **No Duplicate Alerts**: System prevents spam notifications

## Usage

### Adding Domains and Hosting Services
1. Navigate to a project
2. Use the "Domains" or "Hosting Services" tabs
3. Add bought date and expiry date for each service
4. The system automatically calculates and monitors expiry status

### Viewing Notifications
- **Project Level**: Check project forms for alert banners
- **Dashboard**: Use "🚨 Expiry Dashboard" menu item
- **Lists**: Use "⚠️ Expiring Domains" and "⚠️ Expiring Hosting" menus
- **Filters**: Use search filters to focus on specific statuses

### Managing Notifications
- **Reset Notifications**: Use the "Reset Notifications" action on records
- **Manual Check**: Scheduled actions can be run manually if needed
- **Update Dates**: Simply update expiry dates to clear alerts

## Implementation Details

### Models Added
- `project.hosting`: Hosting service management with expiry tracking
- `project.expiry.dashboard`: Dashboard data provider

### Models Enhanced  
- `project.domain`: Added expiry status and notification tracking
- `project.project`: Added hosting relationship and notification indicators

### Security
- All models respect existing project security rules
- Notifications only sent to project managers or assigned users

### Scheduled Actions
- `check_domain_expiry`: Daily check for domain expirations
- `check_hosting_expiry`: Daily check for hosting expirations

## Configuration

### Email Templates
Email notifications for domains use the existing template:
- `project_extended.email_template_domain_expiry`

### Notification Settings
Notification thresholds:
- Warning: 7 days before expiry
- Urgent: 3 days before expiry  
- Expired: Past expiry date

### Cron Jobs
Both cron jobs run daily at server time. Adjust timing in:
- Settings > Technical > Scheduled Actions

## Demo Data
The module includes demo data with various expiry scenarios:
- Valid services (safe)
- Warning services (7 days)  
- Urgent services (2-3 days)
- Expired services (past due)

This helps test the notification system immediately after installation.

## Support
For questions or issues with the notification system, check:
1. System logs for scheduled action execution
2. Activity feeds for generated activities  
3. Notification settings for users
4. Email server configuration for email alerts
