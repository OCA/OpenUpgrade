# -*- coding: utf-8 -*-
{
	"name" : "Multilogin portal",
	"version" : "1.0",
	"depends" : ["base"],
	"author" : "Ferme Urbaine",
	"description": """Allows xmlrpc queries from partners email+password as:
	- Customer standard user
	- Provider standard user

Allows xmlrpc queries from computers (IP automatically recognized) as:
	- Computer standard user

Standard users are set into res.company.
For multi-company, please alter this code.""",
	"website" : "http://www.lafermedusart.com",
	"category" : "Generic Modules/Base",
	"init_xml" : [
	],
	"demo_xml" : [
	],
	"update_xml" : [
		"res_view.xml"
	],
	"active": False,
	"installable": True
}
