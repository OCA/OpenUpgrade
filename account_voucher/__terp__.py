{
    "name" : "India Accounting",
    "version" : "1.0",
    "author" : "Tiny",
    "description": """
    India Accounting module includes all the basic requirenment of 
    Basic Accounting, plus new things which available are 
    * Indian Account Chart
    * New Invoice - (Local, Retail)
    * Invoice Report
    * Tax structure
    * Journals 
    * VAT Declaration report
    * Accounting Periods
    """,
    "category" : "Generic Modules/Accounting",
    "website" : "http://tinyerp.com",
    "depends" : ["base", "account"],
    "init_xml" : [
    ],
    
    "demo_xml" : [
    ],
    
    "update_xml" : [
        "account_voucher_sequence.xml",
        "account_view.xml",
        "account_report.xml",
        "account_voucher_workflow.xml",
        "account_voucher_wizard.xml",
        "voucher_view.xml",
    ],
    'certificate': '0037580727101',
    "active": False,
    "installable": True,
}
