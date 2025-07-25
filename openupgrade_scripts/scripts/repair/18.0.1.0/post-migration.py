# Copyright 2025 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


def fill_stock_warehouse_repair_mto_pull_id(env):
    def _get_global_route_rules_values(self):
        data = _get_global_route_rules_values._original_method(self)
        data_return = {"repair_mto_pull_id": data["repair_mto_pull_id"]}
        return data_return

    # create hook
    _get_global_route_rules_values._original_method = type(
        env["stock.warehouse"]
    )._get_global_route_rules_values
    type(
        env["stock.warehouse"]
    )._get_global_route_rules_values = _get_global_route_rules_values

    warehouses = env["stock.warehouse"].with_context(active_test=False).search([])
    for warehouse in warehouses:
        warehouse._create_or_update_global_routes_rules()

    # delete hook
    type(
        env["stock.warehouse"]
    )._get_global_route_rules_values = _get_global_route_rules_values._original_method


@openupgrade.migrate()
def migrate(env, version):
    fill_stock_warehouse_repair_mto_pull_id(env)
