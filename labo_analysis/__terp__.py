{
    "name" : "Labo analysis create Progenus project",
    "version" : "1.0",
    "author" : "Tiny",
    "category" : "Enterprise Specific Modules/Industries",
    "depends" : ["base", "account", "product", "stock","crm","labo_stock","labo_tool"],
    "init_xml" : ["labo_analysis_data.xml",'labo_analysis_view.xml',"labo_analysis_sequence.xml",'labo_analysis_report.xml','labo_analysis_wizard.xml','analysis_view.xml','analysis_view_empche.xml', 'labo_analysis_view2.xml'],
    "demo_xml" : [],#'labo_anlysis_demo.xml'],
    "description": "Progenus project Labo analysis object",
    "update_xml" : ["labo_analysis_data.xml",'labo_analysis_view.xml',"labo_analysis_sequence.xml",'labo_analysis_report.xml','labo_analysis_wizard.xml','analysis_view.xml','analysis_view_empche.xml','labo_analysis_view2.xml'],
    "active": False,
    "installable": True
}
