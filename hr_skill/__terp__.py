# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution	
#    Copyright (C) 2004-2008 Tiny SPRL (<http://tiny.be>). All Rights Reserved
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
    "name" : "Skill Management",
    "version" : "0.1",
    "author" : "Tiny",
    "category" : "Generic Modules/Human Resources",
    "website": "http://www.openerp.com",
    "depends" : ["hr"],
    "description": "Generic and powerfull skill management system. This module allows you to manage your company and employees skills, interviews, ...",
#   "demo_xml" : ["hr_skill.weight.category.csv","hr_skill.weight.csv","hr_skill.skill.csv",\
#               "hr_skill.profile.csv","hr_skill.position.csv","hr_skill.experience.csv",\
#               "hr_skill.experience.category.csv","hr_skill.evaluation.category.csv"],
#   "demo_xml" : ["hr_skill.evaluation.csv"],
    "init_xml" : [],
    "update_xml" : ['security/ir.model.access.csv','hr_skill_report.xml','hr_skill_view.xml','hrskill_view.xml','lang_wiz_view.xml',],
    "active": False,
    "installable": True
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

