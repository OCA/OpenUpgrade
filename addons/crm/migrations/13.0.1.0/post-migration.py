# Copyright 2020 Payam Yasaie <https://www.tashilgostar.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


def fill_crm_stage_is_won(cr):
    openupgrade.logged_query(
        cr, """
        UPDATE crm_stage
        SET is_won = TRUE
        WHERE {column} = 100
        """.format(
            column=openupgrade.get_legacy_name('probability')
        ),
    )


@openupgrade.migrate()
def migrate(env, version):
    fill_crm_stage_is_won(env.cr)
    openupgrade.load_data(env.cr, 'crm', 'migrations/13.0.1.0/noupdate_changes.xml')
