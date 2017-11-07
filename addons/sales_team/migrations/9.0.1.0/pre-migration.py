# -*- coding: utf-8 -*-
# Copyright 2015 Eficent Business and IT Consulting Services S.L. -
# Jordi Ballester Alomar
# Copyright 2015 Serpent Consulting Services Pvt. Ltd. - Sudhir Arya
# Copyright 2016 Opener B.V. - Stefan Rijnhart
# Copyright 2017 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade

field_renames = [
    ('res.users', 'res_users', 'default_section_id', 'sale_team_id'),
    # renamings with oldname attribute - They also need the rest of operations
    ('res.partner', 'res_partner', 'section_id', 'team_id'),
]


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    cr = env.cr
    openupgrade.rename_xmlids(cr, [
        ('sales_team.section_sales_department',
         'sales_team.team_sales_department'),
    ])
    openupgrade.rename_tables(cr, [('crm_case_section', 'crm_team')])
    openupgrade.rename_models(cr, [('crm.case.section', 'crm.team')])
    openupgrade.rename_fields(env, field_renames)
