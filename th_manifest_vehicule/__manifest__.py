# -*- coding: utf-8 -*-
{
    'name': 'Module de manifest',
    'version': '1.2.2',
    'price': 15.99,
    'currency': 'EUR',
    'license': 'AGPL-3',
    'summary': """
       Module de manifest
    """,
    'category': 'account',
    'author': 'Thomas ATCHA',
    'maintainer': 'Thomas ATCHA',
    'company': 'Thomas ATCHA',
    'website': 'https://digitaltg.net',
    'depends': ['base','mail', 'account','contacts'],
    'data': [
        'security/ir.model.access.csv',
        'views/manifest_vehicule_view.xml',
        'views/seqence_view.xml',
        'views/account_view.xml',
        'reports/manifest_report_view.xml',
        'reports/manifest_list_report_view.xml',
        'reports/manifest_financial_report_view.xml',
        'wizards/manifest_list_view.xml',
        'wizards/financial_report_view.xml',
        'wizards/operation_view.xml',
    ],
    
    'images':[],
    'installable': True,
    'application': False,
    'auto_install': False,
}
