# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    "name" : "Bayesian Filter",
    "version" : "1.0",
    "author" : "Tiny",
    "description" :  """This module allowed to automate actions to be performed on customers request, based on bayes. First we need to train some email contains in bayes to related category then after guess the email contain using bayes and then send a template of email to the customer. if no email contains is train in bayes then bayes filter will not work and no guess for any email contain. if you try to guess email contain without train email contain then no guess result is found, then can not send a template of email to the responsible customer to right category.

For example, suppose you receive lots of email into sales@openerp.com. Some emails are in French, some are in English and others in Spanish. first we need to train some email contain to related category. then any email contain to guess it will filter to related category and send a template of email to the right category and to the responsible person. suppose if received email is in French language then it will automatically  send email template  in French language.

Required Package:-
    -> python-reverend""",
    "category" : "Generic Modules/Others",
    "depends" : ['crm_configuration',"base"],
    "init_xml" : [],
    "demo_xml" : ['crm_bayes_demo.xml'],
    "update_xml" : ['crm_bayes_wizard.xml','crm_bayes_view.xml','security/ir.model.access.csv'],
    "active": False,
    "installable": True
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
