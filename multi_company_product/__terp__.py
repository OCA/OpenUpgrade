# -*- encoding: utf-8 -*-

{
    "name" : "MultiCompany Product",
    "version" : "1.1",
    "depends" : [
                    "account", 
                    "stock",
                    "sale",
                ],
    "author" : "Axelor",
    "description": """Multi company Product Module
    """,
    'website': 'http://www.axelor.com',
    'init_xml': [],
    'update_xml': [
                
        'product_view.xml',

    ],
    'demo_xml': [],
    'installable': True,
    'active': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
