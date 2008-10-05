#!/usr/bin/env python
# -*- coding: utf-8 -*-
{
	"name" : "City for base_contat",
	"version" : "1.0",
	"author" : "Pablo Rocandio",
	"description": """Zip code, city, state and country fields are replaced with a location field in partner form when base_contact module is installed.
This module helps to keep homogenous address data in our database.""",
	"depends" : ["base", "base_contact", "city"],
	"init_xml" : [],
	"update_xml" : [
	    'city_view.xml',
	    ],
	"active": False,
	"installable": True
}