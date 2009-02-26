{
	"name" : "Partner Parent Companies",
	"version" : "0.2",
	"author"  : "ChriCar Beteiligungs- und Beratungs- GmbH" ,
	"website" : "http://www.chricar.at/ChriCar",
    "description"  : """This module allows to define owners of a partner.
    The owner has to be definend in OpenERP as partner.
    Currently no check is made if max 100% of the capital is defined here
    Contract date+number
    legal and fiscal relevant periods
    Added Participation tab to partners to show Parent and Participations""",
	"category" : "Generic Modules/Others",
	"depends" : ["base"],
	"init_xml" : [],
	"demo_xml" : ["partner_parent_companies_demo.xml"],
	"update_xml" : ["partner_parent_companies_view.xml"],
	"active": False,
	"installable": True
}
