# -*- coding: utf-8 -*-
# © 2016 Tecnativa - Vicent Cubells <vicent.cubells@tecnativa.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


column_renames = {
    'hr_applicant': [
        ('priority', None),
        ('availability', None),
    ]}

table_renames = [
    ('hr_recruitment_source', None),
]


@openupgrade.migrate()
def migrate(cr, version):
    openupgrade.rename_columns(cr, column_renames)
    openupgrade.rename_tables(cr, table_renames)
