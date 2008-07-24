# -*- encoding: utf-8 -*-
{
    "name" : "Webmail",
    "version" : "1.0",
    "depends" : ["base"],
    "author" : "Tiny",
    "description": """Webmail module covers:
        - Mail server configuration.
        - Sending and Receiving mail
    """,
    "website" : "http://tinyerp.com",
    "category" : "Generic Modules",
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" : [
                    "webmail_view.xml",
                    "webmail_wizard.xml",
                    ],
    "active": False,
    "installable": True
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

