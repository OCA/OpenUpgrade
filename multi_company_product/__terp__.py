# -*- encoding: utf-8 -*-

{
    "name" : "MultiCompany Product",
    "version" : "1.1",
    "depends" : [
                   'base',
                   'product',
                ],
    "author" : "Axelor",
    "description": """The Module allows to define each product for many companies with their cost price and sale price
    and that update cost price and sale price as per userwise company, for the purpose of multicompany""",
    
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
