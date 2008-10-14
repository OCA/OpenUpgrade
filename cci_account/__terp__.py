# -*- encoding: utf-8 -*-
{
    "name" : "CCI Account",
    "version" : "1.0",
    "author" : "Tiny",
    "website" : "http://tinyerp.com",
    "category" : "Generic Modules/CCI Account",
    "description": """
        specific module for cci project which will use account module (Reports).
    """,
    "depends" : ["base","account","account_invoice_layout","sale","account_analytic_plans","l10n_be","base_vat"],
    "init_xml" : ["cci_account_data.xml"],
    "demo_xml" : [],
    "update_xml" : ["cci_account_wizard.xml","cci_account_view.xml","cci_account_report.xml"],
    "active": False,
    "installable": True
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

