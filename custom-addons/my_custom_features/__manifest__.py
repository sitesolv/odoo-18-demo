# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'My Custom Features for Inventory',
    'version': '18.0.1.0.0',
    'summary': 'Adds custom features and messages to Odoo Inventory.',
    'description': """
        This module provides custom functionalities and a demonstration message
        for the Odoo Inventory application's overview page.
    """,
    'category': 'Inventory/Inventory',
    'author': 'Your Name/Company', # Replace with your name or company
    'website': 'https://www.example.com', # Replace with your website or leave empty
    'license': 'LGPL-3',
    'depends': [
        'base',
        'stock', # We are extending the Inventory app, so 'stock' module is a dependency
    ],
    'data': [
        # XML files defining views, reports, etc. go here
        'views/inventory_dashboard_message_views.xml', # This file will be created next
    ],
    'installable': True,
    'application': False, # Set to True if it's a standalone business application
    'auto_install': False,
}