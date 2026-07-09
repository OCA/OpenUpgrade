# Copyright 2026 Tecnativa - Carlos Lopez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade

from odoo.addons.base_automation.models.base_automation import TIME_TRIGGERS


def _precreate_base_automation_trg_date_range_mode(env):
    openupgrade.add_columns(
        env,
        [
            (
                "base.automation",
                "trg_date_range_mode",
                "selection",
                False,
                "base_automation",
            )
        ],
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE base_automation
        SET trg_date_range_mode = CASE
            WHEN trg_date_range < 0 THEN 'before'
            ELSE 'after'
            END
        WHERE trigger IN %s
        """,
        (tuple(TIME_TRIGGERS),),
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE base_automation
        SET trg_date_range = ABS(trg_date_range)
        WHERE trg_date_range < 0
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    _precreate_base_automation_trg_date_range_mode(env)
