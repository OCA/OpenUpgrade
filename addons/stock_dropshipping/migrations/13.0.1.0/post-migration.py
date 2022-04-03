# Copyright 2020 ForgeFlow <http://www.forgeflow.com>
# Copyright 2021 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade
from openupgradelib import openupgrade_merge_records


def run_dropshipping_functions(env):
    companies = env["res.company"].with_context(active_test=False).search([], order="id")
    mapping = {company.id: {} for company in companies}
    # Duplicate/create/adjust sequences
    sequence = env.ref('stock_dropshipping.seq_picking_type_dropship', False)
    if sequence and sequence.exists():
        for i, company in enumerate(companies):
            vals = {
                "code": "stock.dropshipping",
                "name": "Dropship (%s)" % company.name,
                "company_id": company.id,
            }
            if i == 0:
                sequence.write(vals)
                new_sequence = sequence
            else:
                new_sequence = sequence.copy(vals)
            mapping[company.id]["sequence"] = new_sequence
    env['res.company'].create_missing_dropship_sequence()
    for company in companies:
        # Look for missing mapped sequences
        if not mapping[company.id].get("sequence"):
            sequence = env['ir.sequence'].search([
                ('code', '=', 'stock.dropshipping'),
                ('company_id', '=', company.id),
            ])
            mapping[company.id]["sequence"] = sequence
    # Duplicate/create/adjust picking types
    picking_type = env.ref('stock_dropshipping.picking_type_dropship', False)
    if picking_type and picking_type.exists():
        for i, company in enumerate(companies):
            vals = {
                "sequence_id": mapping[company.id]["sequence"].id,
                "company_id": company.id,
                "warehouse_id": False,
            }
            if picking_type.default_location_dest_id.usage != "customer":
                vals["default_location_dest_id"] = env.ref('stock.stock_location_customers').id
            if picking_type.default_location_src_id.usage != "supplier":
                vals["default_location_src_id"] = env.ref('stock.stock_location_suppliers').id
            if i == 0:
                env.cr.execute(
                    """UPDATE stock_picking_type
                    SET company_id = %s, sequence_id = %s, warehouse_id = NULL
                    WHERE id = %s""",
                    (vals["company_id"], vals["sequence_id"], picking_type.id),
                )
                picking_type.invalidate_cache()
                new_picking_type = picking_type
            else:
                new_picking_type = picking_type.copy(vals)
            mapping[company.id]["picking_type"] = new_picking_type
    for company in companies:
        # Look for missing mapped picking types
        if not mapping[company.id].get("picking_type"):
            dropship_picking_type = env['stock.picking.type'].search([
                ('company_id', '=', company.id),
                ('default_location_src_id.usage', '=', 'supplier'),
                ('default_location_dest_id.usage', '=', 'customer'),
            ], limit=1, order='sequence')
            mapping[company.id]["picking_type"] = dropship_picking_type
    env['res.company'].create_missing_dropship_picking_type()
    # Duplicate/create/adjust stock rules
    stock_rule = env.ref('stock_dropshipping.stock_rule_drop_shipping', False)
    dropship_route = env.ref('stock_dropshipping.route_drop_shipping')
    if stock_rule and stock_rule.exists():
        for i, company in enumerate(companies):
            supplier_location = stock_rule.location_src_id
            customer_location = stock_rule.location_id
            if supplier_location.usage != "supplier":
                supplier_location = env.ref('stock.stock_location_suppliers')
            if customer_location.usage != "customer":
                customer_location = env.ref('stock.stock_location_customers')
            dropship_picking_type = mapping[company.id]["picking_type"]
            vals = ({
                "route_id": dropship_route.id,
                "picking_type_id": dropship_picking_type.id,
                "company_id": company.id,
                "location_src_id": supplier_location.id,
                "location_id": customer_location.id,
                "name": "%s → %s" % (supplier_location.name, customer_location.name),
            })
            if i == 0:
                stock_rule.write(vals)
                new_stock_rule = stock_rule
            else:
                new_stock_rule = stock_rule.copy(vals)
            mapping[company.id]["stock_rule"] = new_stock_rule
    env['res.company'].create_missing_dropship_rule()
    for company in companies:
        # Look for missing mapped stock rules
        if not mapping[company.id].get("stock_rule"):
            stock_rule = env["stock.rule"].search([
                ("route_id", "=", dropship_route.id),
                ("company_id", "=", company.id),
            ])
            mapping[company.id]["stock_rule"] = stock_rule
    # Remove old XML-IDs
    env["ir.model.data"].search([
        ("module", "=", "stock_dropshipping"),
        ("name", "in", ["seq_picking_type_dropship",
                        "picking_type_dropship", "stock_rule_drop_shipping"]),
    ]).unlink()
    # now, we redirect referenced records to new records if needed company-wise
    for company in companies[1:]:
        if sequence and sequence.exists():
            openupgrade_merge_records._change_foreign_key_refs(
                env,
                "ir.sequence",
                sequence.ids,
                mapping[company.id]["sequence"].id,
                [],
                "ir_sequence",
                extra_where=" AND company_id = %s" % company.id,
            )
        if picking_type and picking_type.exists():
            openupgrade_merge_records._change_foreign_key_refs(
                env,
                "stock.picking.type",
                picking_type.ids,
                mapping[company.id]["picking_type"].id,
                [],
                "stock_picking_type",
                extra_where=" AND company_id = %s" % company.id,
            )
        if stock_rule and stock_rule.exists():
            openupgrade_merge_records._change_foreign_key_refs(
                env,
                "stock.rule",
                stock_rule.ids,
                mapping[company.id]["stock_rule"].id,
                [],
                "stock_rule",
                extra_where=" AND company_id = %s" % company.id,
            )


@openupgrade.migrate()
def migrate(env, version):
    run_dropshipping_functions(env)
