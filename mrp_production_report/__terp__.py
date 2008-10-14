# -*- encoding: utf-8 -*-
{
    "name" : "Production Report",
    "version" : "1.0",
    "author" : "Tiny",
    "category" : "Generic Modules/Production",
    "depends" : ["base","mrp","sale"],
    "description": """
    On this module,
    ** Add partner on procurement form which set when Sale order confirm.
    ** Add link between production and procument.
    ** New report for production.
    """,
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" : ['mrp_view.xml','mrp_report.xml'],
    "active": False,
    "installable": True
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

