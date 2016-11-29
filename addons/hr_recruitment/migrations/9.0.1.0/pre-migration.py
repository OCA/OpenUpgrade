# -*- coding: utf-8 -*-
# © 2016 Tecnativa - Vicent Cubells <vicent.cubells@tecnativa.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


column_renames = {
    'hr_applicant': [
        ('priority', None),
        ('availability', None),
    ]}


def migrate_applicant_source(cr):
    cr.execute(
        """
            SELECT id
            FROM hr_recruitment_source
        """)
    for old_id in cr.fetchall():
        cr.execute("INSERT_INTO utm_source (name) "
                   "SELECT name "
                   "FROM hr_recruitment_source "
                   "RETURNING id")
        new_id = cr.fetchone()[0]
        cr.execute("UPDATE hr_applicant "
                   "SET source_id = %s "
                   "WHERE source_id = %s",
                   (new_id, old_id[0]))


@openupgrade.migrate()
def migrate(cr, version):
    openupgrade.rename_columns(cr, column_renames)
    migrate_applicant_source(cr)
