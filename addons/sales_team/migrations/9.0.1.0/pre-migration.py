# -*- coding: utf-8 -*-
# © 2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(cr, version):
    openupgrade.rename_tables(
        cr, [
            ('crm_case_section', 'crm_team'),
            ('crm_case_stage', 'crm_stage'),
        ]
    )
    openupgrade.rename_columns(
        cr, {
            'res_users': [
                ('default_section_id', 'sale_team_id'),
            ],
        }
    )
