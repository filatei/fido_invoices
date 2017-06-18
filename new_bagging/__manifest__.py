# -*- coding: utf-8 -*-
{
    'name': "Fido Bagger Records",

    'summary': "FIDO HR Extension For Baggers",

    'description': "FIDO HR Extension For Baggers",

    'author': "GTS",
    'website': "http://www.fidowater.ng",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'HR',
    'version': '1.1',

    # any module necessary for this one to work correctly
    'depends': ['hr'],

    # always loaded
    'data': ['fidobagging_view.xml'],
    'installabe': True,
}