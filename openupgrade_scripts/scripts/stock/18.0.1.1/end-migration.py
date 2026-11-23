# Copyright 2025 ForgeFlow S.L. (https://www.forgeflow.com)
# Copyright 2026 Binhex <https://www.binhex.cloud>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


def convert_product_type_defaults(env):
    defaults = env["ir.default"]
    defaults.flush_model()
    env.cr.execute(
        """
        SELECT f.model, d.user_id, d.company_id, d.condition
        FROM ir_default d
        JOIN ir_model_fields f ON f.id = d.field_id
        WHERE f.name = 'type'
            AND f.model IN ('product.template', 'product.product')
            AND d.json_value = '"product"'
        """
    )
    for model, user_id, company_id, condition in env.cr.fetchall():
        scope = dict(user_id=user_id, company_id=company_id, condition=condition)
        defaults.set(model, "type", "consu", **scope)
        defaults.set(model, "is_storable", True, **scope)


def fill_stock_picking_type_default_locations(env):
    PickingType = env["stock.picking.type"].with_context(active_test=False)
    picking_types = PickingType.search([("default_location_src_id", "=", False)])
    picking_types._compute_default_location_src_id()
    picking_types = PickingType.search([("default_location_dest_id", "=", False)])
    picking_types._compute_default_location_dest_id()


@openupgrade.migrate()
def migrate(env, version):
    convert_product_type_defaults(env)
    fill_stock_picking_type_default_locations(env)
