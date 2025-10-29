{
    'name': 'Dashboard - Project Reporting',
    'version': '1.0',
    'depends': ['project', 'hr', 'project_extended', 'web'],
    'category': 'Productivity',
    'license': 'LGPL-3',
    'data': [
        'views/client_action.xml',
        'views/menu_views.xml',
        'views/graph_views.xml',
        'views/dashboard_views.xml',
        'views/dashboard_template.xml',
        'views/project_dashboard_kanban.xml',
        'views/project_reporting_views.xml',
        'views/project_dashboard_simple.xml',
        'reports/report.xml',
        'reports/project_summary_template.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'project_reporting/static/src/js/project_dashboard_client.js',
            'project_reporting/static/src/xml/dashboard_template.xml',
            'project_reporting/static/src/scss/dashboard.scss',
        ],
    },
    'installable': True,
    'application': True,
}
