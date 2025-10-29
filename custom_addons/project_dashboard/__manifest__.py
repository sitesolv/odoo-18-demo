{
    'name': 'Project Dashboard',
    'version': '1.1.0',
    'category': 'Project',
    'summary': 'Comprehensive project analytics dashboard with expiry notifications',
    'description': """
        Project Dashboard Module
        ========================
        
        This module provides a comprehensive dashboard for project management with:
        * Total projects overview
        * Ongoing projects tracking
        * Top customers analysis
        * Total income and expenses
        * Net profit calculations
        * Income analysis with charts
        * Expense analysis with charts
        * Domain expiry notifications and tracking
        * Hosting service expiry notifications and tracking
        * Real-time alerts for urgent renewals
        * Quick access to expiring services
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'depends': [
        'base',
        'project',
        'project_extended',
        'web',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/dashboard_views.xml',
        'views/income_analysis_views.xml',
        'views/expense_analysis_views.xml',
        'views/project_dashboard_menus.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'project_dashboard/static/src/css/dashboard.css',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
