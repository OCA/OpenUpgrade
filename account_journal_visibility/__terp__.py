# -*- encoding: utf-8 -*-
{
    "name" : "Accounting journal visibility",
    "version" : "1.0",
    "depends" : ["account"],
    "author" : "Tiny",
    "category" : "Generic Modules/Accounting",
    "description": """
    Using this module :
    when we open the journals list, people will only see journal for which they are allowed
    (means their group is specified on the journal definition). and also
    Only people in the group defined on the journal will be able to see the invoices of this journal.
    """,
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" : ["account_journal_view.xml"],
    "active": False,
    "installable": True
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

