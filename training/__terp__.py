{
    'name' : 'Training',
    'version' : '0.0.1',
    'author' : 'Tiny SPRL',
    'website' : 'http://www.openerp.com',
    'description' : 'Training',
    'depends' : ['account', 'base_contact_team', 'base_iban', 'product', 'mrp'],
    'init_xml' : [
        'training_sequence.xml'
    ],
    'demo_xml' : [],
    'update_xml' : [
        'partner_view.xml', 
        'base_contact_view.xml', 
        'training_view.xml', 
        'training_wizard.xml',
        'training_report.xml',
    ],
    'active' : False,
    'installable' : True
}
