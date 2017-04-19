# -*- coding: utf-8 -*-
{
    'name': "FIDO INVOICES",

    'summary': "Inherit and add to Customer Invoices",

    'description': "Inherit and add to Customer Invoices",

    'author': "FPL",
    'website': "http://www.fidowater.ng",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Accounting',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','account_accountant'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/fido_invoices_views.xml',
        'views/fido_invoices_report.xml',
        'views/fido_report_invoice.xml',

        #  'views/templates.xml',
    ],
}