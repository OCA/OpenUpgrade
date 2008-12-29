{
    'name' : 'Base Contact Team',
    'author' : 'Tiny SPRL',
    'version' : '0.1',
    'website' : 'http://www.openerp.com',
    "category" : "Generic Modules/Base",
    'description' : 'With this module will help you to manages teams of contacts for different purposes.',
    'depends' : ['base_contact'],
    'init_xml' : [],
    'update_xml' : ['security/ir.model.access.csv','base_contact_team_view.xml'],
    'demo_xml' : [],
    'installable' : True,
    'active' : False,
}
