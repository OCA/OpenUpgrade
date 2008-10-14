# -*- encoding: utf-8 -*-
{
    "name" : "Test New Features",
    "version" : "1.0",
    "author" : "Tiny",
    "website" : "http://tinyerp.com",
    "category" : "Generic Modules",
    "description": """The module adds google map field in partner address
so that we can directly open google map from the
url widget.""",
    "depends" : ["base","sale"],
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" : ["test_view.xml","test_workflow.xml"],
    "active": False,
    "installable": True
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

