# Copyright 2025 Tecnativa - Carlos Lopez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade

column_creates = [("pos.payment", "employee_id", "many2one")]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.add_columns(env, column_creates)
