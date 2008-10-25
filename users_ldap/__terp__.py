# -*- encoding: utf-8 -*-
{
    "name" : "Authenticate users with ldap server",
    "version" : "0.1",
    "depends" : ["base"],
    "author" : "Tiny",
    "description": """Add support for authentication by ldap server""",
    "website" : "http://tinyerp.com/",
    "category" : "Generic Modules/Others",
    "init_xml" : [
    ],
    "demo_xml" : [
    ],
    "update_xml" : [
        "users_ldap_view.xml",
    ],
    "active": False,
    "installable": True
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

