# -*- encoding: utf-8 -*-
#
# Plan comptable général pour le Maroc,
# Mise en forme et paramétrage par http://sisatlas.com
# 
{
    "name" : "Maroc Plan comptable général pour les sociétés",
    "version" : "1.0",
    "author" : "SISatlas",
    "category" : "Localisation/Account charts",
    "website": "http://comptabilite.erp-libre.info",
    "depends" : ["base", "account"],
    "init_xml" : [],
    "update_xml" : ["types_de_comptes.xml","currency.xml","plan-maroc.xml","taxes.xml"],
    "demo_xml" : [],
    "active": False,
    "installable": True
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

