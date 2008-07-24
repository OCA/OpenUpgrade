# -*- encoding: utf-8 -*-
{
    "name" : "Asterisk",
    "version" : "0.1proto2",
    "author" : "Tiny",
    "category" : "Enterprise Specific Modules/Electronic Industries",
    "depends" : ["base"],
    "init_xml" : [],
    "demo_xml" : ["asterisk_demo.xml"],
    "description": """Manages a list of asterisk servers and IP phones.
This module implements a system to popup the partner form based on phone calls.
This is still a proof of concept, that have been made during Tiny ERP's
technical training session.""",
    "update_xml" : ["asterisk_view.xml","asterisk_wizard.xml"],
    "active": False,
    "installable": True
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

