# Copyright 2021 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    openupgrade.delete_records_safely_by_xml_id(
        env, [("stock_landed_costs.seq_type_stock_landed_costs")],
    )
