# Copyright 2022 ForgeFlow S.L.  <https://www.forgeflow.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    # Disappeared constraint
    openupgrade.delete_sql_constraint_safely(
        env, "bus", "bus_presence", "bus_user_presence_unique"
    )
