# -*- encoding: utf-8 -*-
{
    "name" : "Partner labels",
    "version" : "1.0",
    "author" : "Zikzakmedia SL",
    "website" : "www.zikzakmedia.com",
    "category" : "Generic Modules",
    "description": """Flexible partner labels:
  * Definition of page sizes, label manufacturers and label formats
  * Flexible label formats (page size, portrait or landscape, manufacturer, rows, columns, width, height, top margin, left margin, ...)
  * Initial data for page sizes and label formats (from Avery and Apli manufacturers)
  * Wizard to print labels. The label format, the printer margins, the font type and size, the first label (row and column) to print on the first page can be set.""",
    "depends" : ["base",],
    "init_xml" : [
        "report_label_data.xml",
    ],
    "demo_xml" : [],
    "update_xml" : [
        "security/ir.model.access.csv",
        "partner_wizard.xml",
        "report_label_view.xml",
    ],
    "active": False,
    "installable": True
}
