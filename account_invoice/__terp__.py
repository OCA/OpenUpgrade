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
    "depends" : ["base","account","account_base"],
    "init_xml" : [
    ],

    "demo_xml" : [
    ],

    "update_xml" : [
        "account_sequence.xml",
        "account_invoice_view.xml",
        #"account_inv_report.xml"

    ],
    "active": False,
    "installable": True
}
