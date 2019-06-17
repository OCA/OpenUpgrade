# Copyright 2019 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from psycopg2.extensions import AsIs
from openupgradelib import openupgrade


def remove_web_planner_constraints(env):
    """Remove foreign constraints on merged `web_planner` module for avoiding
    errors when removing referenced records.
    """
    constraint_list = [
        'web_planner_create_uid_fkey',
        'web_planner_menu_id_fkey',
        'web_planner_view_id_fkey',
        'web_planner_write_uid_fkey',
    ]
    for constraint in constraint_list:
        openupgrade.logged_query(
            env.cr, "ALTER TABLE web_planner DROP CONSTRAINT %s",
            (AsIs(constraint), ),
        )


@openupgrade.migrate()
def migrate(env, version):
    remove_web_planner_constraints(env)
