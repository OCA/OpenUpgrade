# -*- coding: utf-8 -*-
# © 2015 Eficent Business and IT Consulting Services S.L. -
# Jordi Ballester Alomar
# © 2015 Serpent Consulting Services Pvt. Ltd. - Sudhir Arya
# © 2016 Opener B.V. - Stefan Rijnhart
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(cr, version):
    openupgrade.rename_xmlids(cr, [
        ('sales_team.section_sales_department',
         'sales_team.team_sales_department'),
    ])
    openupgrade.rename_tables(cr, [('crm_case_section', 'crm_team')])
    openupgrade.rename_models(cr, [('crm.case.section', 'crm.team')])
    openupgrade.rename_columns(cr, {
        'res_users': [('default_section_id', 'sale_team_id')]})
