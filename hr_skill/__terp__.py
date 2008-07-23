# -*- encoding: utf-8 -*-
{
    "name" : "Skill Management",
    "version" : "0.1",
    "author" : "Tiny",
    "category" : "Generic Modules/Human Resources",
    "website": "http://www.tinyerp.com",
    "depends" : ["hr"],
    "description": "Generic and powerfull skill management system. This module allows you to manage your company and employees skills, interviews, ...",
#   "demo_xml" : ["hr_skill.weight.category.csv","hr_skill.weight.csv","hr_skill.skill.csv",\
#               "hr_skill.profile.csv","hr_skill.position.csv","hr_skill.experience.csv",\
#               "hr_skill.experience.category.csv","hr_skill.evaluation.category.csv"],
#   "demo_xml" : ["hr_skill.evaluation.csv"],
    "init_xml" : [],
    "update_xml" : ['hr_skill_report.xml','hr_skill_view.xml','hrskill_view.xml','lang_wiz_view.xml',],
    "active": False,
    "installable": True
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

