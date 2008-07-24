# -*- encoding: utf-8 -*-
{
    "name" : "Module Merger",
    "version" : "1.0",
    "author" : "Tiny",
    "website" : "http://tinyerp.com",
    "category" : "Generic Modules/Base",
    "description": """
    * The wizard asks a many2many of modules
    * And then generate a module which is the merge of all selected modules
    * The new module is provided as a .zip file

    The merge will works in all situations:
    * Merging all .py files with the same name in the new module
    * merging all .xml files and take care of id's.
    """,
    "depends" : ["base"],
    "init_xml" : [ ],
    "demo_xml" : [ ],
    "update_xml" : [ "base_module_merge_wizard.xml" ],
    "installable": True
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

