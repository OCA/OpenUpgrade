{
	"name" : "Audit Trail",
	"version" : "1.0",
	"depends" : ["base","account","sale","purchase","mrp"],
	"website" : "http://tinyerp.com",
	"author" : "Tiny",
	"init_xml" : [],
	"description": "Allows the administrator to track every user operations on all objects of the system.",
	"category" : "Generic Modules/Others",
	"update_xml" : ["audittrail_view.xml"],
	"demo_xml" : ["audittrail_demo.xml"],
	"active" : False,
	"installable": True
}