# -*- encoding: utf-8 -*-
{
    "name" : "Tiny ERP TV & Radio Program Grid Module",
    "version" : "1.1",
    "author" : "Jordi Esteve. Zikzakmedia SL",
    "description" : """This module allows to control TV & Radio channels, programs, grid of date/time of broadcasting and podcasts

channel <--n---m--> program <--1---n--> broadcast <--1---n--> podcast

Features:
    * Menu entries to see daily and weekly broadcasts
    * The date/time end of each broadcast is computed automatically
    * The broadcasts can be copied from a range of days to other
    * A TinyERP cron is provided to copy broadcasts every day
    * Several broadcasting reports are included
    * Several wizards to synchronize the channels, programs and broadcasts to a
      mysql-php web site are included. They can be also synchronized automatically.""",
    "website" : "www.zikzakmedia.com",
    "category" : "Generic Modules/Others",
    "license" : "GPL-2",
    "depends" : ["base"],
    "init_xml" : ['radiotv_data.xml',],
    "demo_xml" : [],
    "update_xml" : [
        "security/radiotv_security.xml",
        "security/ir.model.access.csv",
        'radiotv_view.xml',
        'radiotv_report.xml',
        'radiotv_wizard.xml',
    ],
    "installable" : True,
    "active" : False,

}