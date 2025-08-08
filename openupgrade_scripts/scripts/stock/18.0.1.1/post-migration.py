# Copyright 2025 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade, openupgrade_180


def convert_company_dependent(env):
    openupgrade_180.convert_company_dependent(
        env, "product.template", "property_stock_inventory"
    )
    openupgrade_180.convert_company_dependent(
        env, "product.template", "property_stock_production"
    )
    openupgrade_180.convert_company_dependent(env, "product.template", "responsible_id")
    openupgrade_180.convert_company_dependent(
        env, "res.partner", "property_stock_customer"
    )
    openupgrade_180.convert_company_dependent(
        env, "res.partner", "property_stock_supplier"
    )


def _create_default_new_types_for_all_warehouses(env):
    # method mainly based on _create_or_update_sequences_and_picking_types()
    all_warehouses = env["stock.warehouse"].with_context(active_test=False).search([])
    for wh in all_warehouses:
        sequence_data = wh._get_sequence_values()
        for field in ["qc_type_id", "store_type_id", "xdock_type_id"]:
            # choose the next available color for the operation types of this warehouse
            all_used_colors = [
                res["color"]
                for res in env["stock.picking.type"]
                .with_context(active_test=False)
                .search_read(
                    [("warehouse_id", "!=", False), ("color", "!=", False)],
                    ["color"],
                    order="color",
                )
            ]
            available_colors = [
                zef for zef in range(0, 12) if zef not in all_used_colors
            ]
            color = available_colors[0] if available_colors else 0
            # suit for each warehouse: reception, internal, pick, pack, ship
            max_sequence = (
                env["stock.picking.type"]
                .with_context(active_test=False)
                .search_read(
                    [("sequence", "!=", False)],
                    ["sequence"],
                    limit=1,
                    order="sequence desc",
                )
            )
            max_sequence = max_sequence and max_sequence[0]["sequence"] or 0
            values = wh._get_picking_type_update_values()[field]
            create_data, _ = wh._get_picking_type_create_values(max_sequence)
            values.update(create_data[field])
            sequence = env["ir.sequence"].create(sequence_data[field])
            values.update(
                warehouse_id=wh.id,
                color=color,
                sequence_id=sequence.id,
                sequence=max_sequence + 1,
                company_id=wh.company_id.id,
                active=wh.active,
            )
            # create picking type
            picking_type_id = env["stock.picking.type"].create(values).id
            # update picking type for warehouse
            wh.write({field: picking_type_id})


def _set_inter_company_locations(env):
    """See https://github.com/odoo/odoo/commit/08536d687880ca6d9ad5c37b639c0ad4c2599d74"""
    companies = env["res.company"].search([])
    if len(companies) > 1:
        inter_company_location = env.ref("stock.stock_location_inter_company")
        inactive = False
        if not inter_company_location.active:
            inactive = True
            inter_company_location.sudo().write({"active": True})
        for company in companies:
            company.sudo()._set_per_company_inter_company_locations(
                inter_company_location
            )
        if inactive:
            # we leave everything as it was
            inter_company_location.sudo().write({"active": False})


@openupgrade.migrate()
def migrate(env, version):
    convert_company_dependent(env)
    _create_default_new_types_for_all_warehouses(env)
    _set_inter_company_locations(env)
    openupgrade.load_data(env, "stock", "18.0.1.1/noupdate_changes.xml")
    openupgrade.delete_records_safely_by_xml_id(
        env, ["stock.property_stock_customer", "stock.property_stock_supplier"]
    )
