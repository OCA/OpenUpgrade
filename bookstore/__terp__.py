# -*- encoding: utf-8 -*-
{
    "name" : "Bookstore Verticalisation",
    "version" : "1.0",
    "author" : "Tiny",
    "category" : "Data Module",
    "depends" : ["library","delivery"],
    "init_xml" : ["partner_sequence.xml","bookstore_data.xml"],
    "update_xml": ["bookstore_view.xml","lot_sequence.xml",
                   "bookstore_report.xml","bookstore_access.xml",
                ],
    "demo_xml" : ['book_data.xml'],
    "installable": True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

