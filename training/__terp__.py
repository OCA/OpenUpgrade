{
    'name' : 'Training',
    'version' : '0.0.1',
    'author' : 'Tiny SPRL',
    'website' : 'http://www.openerp.com',
    'description' : 'Training',
    'depends' : ['account', 'base_contact_team', 'base_iban', 'product'],
    'init_xml' : [],
    'demo_xml' : [],
    'update_xml' : [
        'training_view.xml', 
        'training_wizard.xml',
    ],
    'active' : False,
    'installable' : True
}
