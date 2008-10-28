# -*- encoding: utf-8 -*-

{
    'name': 'Import accounting entries from Bob',
    'description': """
        This module provide an easy way to migrate your financial data from Bob software to OpenERP. It includes the import of
            * chart of accounts,
            * financial journals,
            * customers, suppliers and prospects,
            * contacts,
            * accounting entries

        Once the module is installed, all you have to do is run the configuration wizard and provide OpenERP the location of the Bob directory where are your data.
""",
    'category': 'Data Module',
    'init_xml':[],
    'author': 'Tiny',
    'depends': ['base_contact','account_l10nbe_domiciliation','l10n_be'],
    'version': '1.0',
    'active': False,
    'demo_xml': [],
    'update_xml':[
        'misc_data.xml',
        'account_bob_import_config.xml',
    ],
     'installable': True
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

