# -*- encoding: utf-8 -*-

{
    'name': 'cci Data 1',
    'category': 'Data Module 1',
    'init_xml':[],
    'author': 'OpenERP',
    'depends': ['base','cci_partner'],
    'version': '1.0',
    'active': False,
    'demo_xml': [],
    'update_xml':[
#        'res.groups.csv',
#        'res.users.csv',
#        'ir.model.access.csv',
        'res.partner.state.csv',
        'res.partner.state2.csv',

    ],
    'installable': True
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

