# Copyright 2024 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade

_xmlid_renames = [
    (
        "gamification.ir_cron_consolidate_last_month",
        "gamification.ir_cron_consolidate",
    )
]


def new_tracking_fields(env):
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE gamification_karma_tracking
            ADD COLUMN IF NOT EXISTS origin_ref varchar;
        UPDATE gamification_karma_tracking
        SET origin_ref = 'res.users,' || user_id;
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE gamification_karma_tracking
            ADD COLUMN IF NOT EXISTS origin_ref_model_name varchar;
        UPDATE gamification_karma_tracking
        SET origin_ref_model_name = 'res.users';
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_xmlids(env.cr, _xmlid_renames)
    openupgrade.copy_columns(
        env.cr,
        {
            "gamification_karma_tracking": [
                ("tracking_date", None, None),
            ]
        },
    )
    new_tracking_fields(env)
