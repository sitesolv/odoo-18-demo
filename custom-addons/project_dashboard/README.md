# Project Dashboard Module

# Project Dashboard Module

## Overview
Comprehensive project analytics and dashboard module that provides insights into project management, financial data, and critical expiry notifications.

## Features

### Dashboard Analytics
- **Project Overview**: Total, ongoing, and completed projects
- **Financial Overview**: Total income, expenses, and net profit
- **Top Customers**: List of highest revenue generating customers

### Expiry Notifications (NEW!)
- **Domain Expiry Tracking**: 
  - Monitor all domains with expiry dates
  - Warning alerts for domains expiring within 7 days
  - Urgent alerts for domains expiring within 3 days or already expired
  - Quick access to view all expiring domains

- **Hosting Service Expiry Tracking**: 
  - Monitor all hosting services with expiry dates
  - Warning alerts for hosting expiring within 7 days
  - Urgent alerts for hosting expiring within 3 days or already expired
  - Quick access to view all expiring hosting services

### Dashboard Features
- **Real-time KPIs**: All metrics are computed in real-time
- **Date Filtering**: Filter financial data by date range
- **Quick Actions**: Direct access to expiring domains and hosting lists
- **Visual Alerts**: Color-coded alerts for urgent notifications
- **Responsive Design**: Works on desktop and mobile devices

## Integration
This module integrates with:
- `project_extended`: For domain and hosting expiry data
- Base project module for project analytics
- Financial modules for income/expense tracking

## Usage
1. Navigate to Project → Dashboard
2. Use the dashboard wizard to set date filters
3. Monitor expiry notifications in the dashboard
4. Click on expiry counts to view detailed lists
5. Use quick action buttons for immediate access to critical items

## Alerts System
- **Orange alerts**: Items expiring within 7 days
- **Red alerts**: Items expiring within 3 days or already expired
- **Header notifications**: Urgent items displayed at the top of dashboard

## Technical Details
- **Models**: `project.dashboard.analytics`, `project.dashboard.analytics.wizard`
- **Dependencies**: base, project, project_extended, web
- **Views**: Form view with custom dashboard layout
- **CSS**: Custom styling for enhanced visual experience

## Features

### Main Dashboard
- **Total Projects**: Shows the total number of projects in the system
- **Ongoing Projects**: Displays projects that are not yet completed
- **Completed Projects**: Shows projects that have been marked as completed
- **Total Income**: Sum of all project income within the selected date range
- **Total Expenses**: Sum of all project expenses within the selected date range
- **Net Profit**: Calculated as Total Income - Total Expenses
- **Top Customers**: Displays the top 5 customers by income generated

### Income Analysis
- **Income Overview**: Monthly income trends with graphs and pivot tables
- **Income by Project**: Pie chart showing income distribution across projects
- **Income by Customer**: Pie chart showing income distribution across customers
- **Filters**: Current month, current year, and custom date ranges

### Expense Analysis
- **Expense Overview**: Monthly expense trends with graphs and pivot tables
- **Expense by Type**: Pie chart showing expenses by type (Domain, Hosting, Salary, etc.)
- **Expense by Project**: Pie chart showing expense distribution across projects
- **Filters**: Current month, current year, expense type filters

## Installation

1. Copy the `project_dashboard` folder to your Odoo addons directory
2. Make sure the `project_extended` module is installed (dependency)
3. Restart your Odoo server
4. Go to Apps → Update Apps List
5. Search for "Project Dashboard" and install it

## Usage

1. **Access the Dashboard**: Go to the main menu and click on "Project Dashboard"
2. **Set Date Range**: Use the wizard to select your desired date range for analysis
3. **View Analytics**: Navigate through different tabs to explore:
   - Dashboard Overview
   - Income Analysis
   - Expense Analysis

## Menu Structure

```
Project Dashboard
├── Dashboard Overview
└── Income Analysis
    ├── Income Overview
    ├── Income by Project
    └── Income by Customer
└── Expense Analysis
    ├── Expense Overview
    ├── Expense by Type
    └── Expense by Project
```

## Technical Details

### Dependencies
- `base`
- `project`
- `project_extended`
- `web`

### Models
- `project.dashboard.analytics`: Main dashboard model with computed KPIs
- `project.dashboard.analytics.wizard`: Wizard for date range selection

### Security
- Access rights configured for all user groups
- Read/Write/Create/Delete permissions for dashboard models

## Customization

The module can be easily customized by:
1. Adding new KPI calculations in the dashboard model
2. Creating additional chart views for income/expense analysis
3. Extending the date filter options
4. Adding new expense types or categories

## Support

For support and customization requests, please contact your system administrator.
