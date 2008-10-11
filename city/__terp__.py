#!/usr/bin/env python
# -*- coding: utf-8 -*-
{
	"name" : "City",
	"version" : "1.0",
	"author" : "Pablo Rocandio",
	"description": """Creates a model for storing cities
Zip code, city, state and country fields are replaced with a location field in partner and partner contact forms.
This module helps to keep homogenous address data in our database.""",
	"depends" : ["base"],
	"init_xml" : [],
	"update_xml" : [
	    'city_view.xml',
	    ],
	"active": False,
	"installable": True
}