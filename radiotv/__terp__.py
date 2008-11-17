# -*- encoding: utf-8 -*-
{
    "name" : "Tiny ERP TV & Radio Program Grid Module",
    "version" : "1.1",
    "author" : "Jordi Esteve. Zikzakmedia SL",
    "description" : """This module allows to control TV & Radio channels, programs, grid of date/time of broadcasting and podcasts

channel <-------> program <-------> broadcast <-------> podcast
         n     m           1      n            1     n

Features:
    * Menu entries to see daily and weekly broadcasts
    * The date/time end of each broadcast is computed automatically
    * The broadcasts can be copied from a range of days to other
    * A TinyERP cron is provided to copy broadcasts every day 
    * Several broadcasting reports are included
    * Several wizards to synchronize the channels, programs and broadcasts to a
      mysql-php web site are included. They can be also synchronized automatically.""",
    "website" : "www.zikzakmedia.com",
    "license" : "GPL-2",
    "depends" : ["base"],
    "init_xml" : ['radiotv_data.xml',],
    "demo_xml" : [],
    "update_xml" : ['radiotv_view.xml', 'radiotv_report.xml', 'radiotv_wizard.xml',],
    "installable" : True,
    "active" : False,

}