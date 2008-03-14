{
    "name" : "Customer Relationship Management",
    "version" : "1.0",
    "author" : "Tiny",
    "website" : "http://tinyerp.com/module_crm.html",
    "category" : "Generic Modules/CRM & SRM",
    "description": """ The Tiny ERP case and request tracker enables a group of
people to intelligently and efficiently manage tasks, issues, and requests.
It manages key tasks such as communication, identification, prioritization,
assignment, resolution and notification.

The CRM module has a email gateway for the synchronisation interface
between mails and Tiny ERP.""",
    "depends" : ["base","crm"],
    "init_xml" : [],
    "demo_xml" : ["crm_demo.xml"],
    "update_xml" : ["crm_view.xml"],
    "active": False,
    "installable": True
}