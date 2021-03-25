# Copyright 2020 ForgeFlow <http://www.forgeflow.com>
# Copyright 2020 Andrii Skrypka
# Copyright 2021 Tecnativa - Carlos Dauden
# Copyright 2021 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from openupgradelib import openupgrade
from odoo import _
from odoo.tools.float_utils import float_compare, float_is_zero, float_round
from odoo.addons.base.models.ir_model import query_insert

_logger = logging.getLogger(__name__)

# Declare global variant to avoid that it is passed between methods
precision_price = 0


def _prepare_common_svl_vals(move, product):
    return {
        "create_uid": move["write_uid"],
        "create_date": move["date"],
        "write_uid": move["write_uid"],
        "write_date": move["date"],
        "stock_move_id": move["id"],
        "company_id": move["company_id"],
        "product_id": move["product_id"],
        "description": move["reference"] and "%s - %s" % (move["reference"], product.name) or product.name,
        "value": 0.0,
        "unit_cost": 0.0,
        "remaining_qty": 0.0,
        "remaining_value": 0.0,
        "quantity": 0.0,
        "old_product_price_history_id": None,
    }


def _prepare_in_svl_vals(move, quantity, unit_cost, product, is_dropship):
    vals = _prepare_common_svl_vals(move, product)
    vals.update({
        "value": float_round(unit_cost * quantity, precision_digits=precision_price),
        "unit_cost": unit_cost,
        "quantity": quantity,
    })
    if product.cost_method in ("average", "fifo") and not is_dropship:
        vals["remaining_qty"] = quantity
        vals["remaining_value"] = vals["value"]
    return vals


def _prepare_out_svl_vals(move, quantity, unit_cost, product):
    # Quantity is negative for out valuation layers.
    quantity = -quantity
    vals = _prepare_common_svl_vals(move, product)
    vals.update({
        "value": float_round(unit_cost * quantity, precision_digits=precision_price),
        "unit_cost": unit_cost,
        "quantity": quantity,
        "remaining_qty": 0.0,
        "remaining_value": 0.0,
    })
    return vals


def _prepare_man_svl_vals(price_history_rec, previous_price, quantity, company, product):
    diff = price_history_rec["cost"] - previous_price
    value = float_round(diff * quantity, precision_digits=precision_price)
    svl_vals = {
        "create_uid": price_history_rec["write_uid"],
        "create_date": price_history_rec["datetime"],
        "write_uid": price_history_rec["write_uid"],
        "write_date": price_history_rec["datetime"],
        "stock_move_id": None,
        "company_id": company.id,
        "product_id": product.id,
        "description": _("Product value manually modified (from %s to %s)"
                         ) % (previous_price, price_history_rec["cost"]),
        "value": value,
        "unit_cost": 0.0,
        "remaining_qty": 0.0,
        "remaining_value": 0.0,
        "quantity": 0.0,
        "old_product_price_history_id": price_history_rec["id"],
    }
    return svl_vals


def get_product_price_history(env, company_id, product_id):
    env.cr.execute("""
        SELECT id, company_id, product_id, datetime, cost, create_uid, write_uid, write_date
        FROM product_price_history
        WHERE company_id = %s AND product_id = %s
        ORDER BY datetime, id
    """, (company_id, product_id))
    return env.cr.dictfetchall()


def get_stock_moves(env, company_id, product_id):
    env.cr.execute("""
        SELECT sm.id, sm.company_id, sm.product_id, sm.date, sm.product_qty, sm.reference,
            COALESCE(sm.price_unit, 0.0) AS price_unit,
            sm.create_uid, sm.create_date, sm.write_uid, sm.write_date,
            CASE WHEN (sl.usage <> 'internal' AND (sl.usage <> 'transit' OR sl.company_id <> sm.company_id))
                   AND (sld.usage = 'internal' OR (sld.usage = 'transit' AND sld.company_id = sm.company_id))
                   THEN 'in'
                 WHEN (sl.usage = 'internal' OR (sl.usage = 'transit' AND sl.company_id = sm.company_id))
                   AND (sld.usage <> 'internal' AND (sld.usage <> 'transit' OR sld.company_id <> sm.company_id))
                   THEN 'out'
                 WHEN sl.usage = 'supplier' AND sld.usage = 'customer' THEN 'dropship'
                 WHEN sl.usage = 'customer' AND sld.usage = 'supplier' THEN 'dropship_return'
                 ELSE 'other'
            END AS move_type
        FROM stock_move sm LEFT JOIN stock_location sl ON sl.id = sm.location_id
            LEFT JOIN stock_location sld ON sld.id = sm.location_dest_id
        WHERE sm.company_id = %s AND sm.product_id = %s
            AND state = 'done'
        ORDER BY sm.date, sm.id
    """, (company_id, product_id))
    return env.cr.dictfetchall()


@openupgrade.logging()
def generate_stock_valuation_layer(env):
    openupgrade.logged_query(
        env.cr, """
            ALTER TABLE stock_valuation_layer
            ADD COLUMN old_product_price_history_id integer""",
    )
    company_obj = env["res.company"]
    product_obj = env["product.product"]
    # Needed to modify global variable
    global precision_price
    precision_price = env["decimal.precision"].precision_get("Product Price")
    precision_uom = env["decimal.precision"].precision_get(
        "Product Unit of Measure"
    )
    companies = company_obj.search([])
    products = product_obj.with_context(active_test=False).search([("type", "in", ("product", "consu"))])
    all_svl_list = []
    for product in products:
        for company in companies:
            history_lines = get_product_price_history(env, company.id, product.id)
            moves = get_stock_moves(env, company.id, product.id)
            svl_in_vals_list = []
            svl_out_vals_list = []
            svl_man_vals_list = []
            svl_in_index = 0
            h_index = 0
            previous_price = 0.0
            previous_qty = 0.0
            for move in moves:
                is_dropship = True if move["move_type"] in ("dropship", "dropship_return") else False
                if product.cost_method in ("average", "standard"):
                    # useless for Fifo because we have price unit in stock.move
                    # Add manual adjusts
                    have_qty = not float_is_zero(previous_qty, precision_digits=precision_uom)
                    while h_index < len(history_lines) and history_lines[h_index]["datetime"] < move["date"]:
                        price_history_rec = history_lines[h_index]
                        if float_compare(price_history_rec["cost"], previous_price, precision_digits=precision_price):
                            if have_qty:
                                svl_vals = _prepare_man_svl_vals(
                                    price_history_rec, previous_price, previous_qty, company, product)
                                svl_man_vals_list.append(svl_vals)
                            previous_price = price_history_rec["cost"]
                        h_index += 1
                # Add in svl
                if move["move_type"] == "in" or is_dropship:
                    total_qty = previous_qty + move["product_qty"]
                    # TODO: is needed vaccum if total_qty is negative?
                    if float_is_zero(total_qty, precision_digits=precision_uom):
                        previous_price = move["price_unit"]
                    else:
                        previous_price = float_round(
                            (previous_price * previous_qty + move["price_unit"] * move["product_qty"]) / total_qty,
                            precision_digits=precision_price)
                    svl_vals = _prepare_in_svl_vals(
                        move, move["product_qty"], move["price_unit"], product, is_dropship)
                    svl_in_vals_list.append(svl_vals)
                    previous_qty = total_qty
                # Add out svl
                if move["move_type"] == "out" or is_dropship:
                    qty = move["product_qty"]
                    if product.cost_method in ("average", "fifo") and not is_dropship:
                        # Reduce remaininig qty in svl of type "in"
                        while qty > 0 and svl_in_index < len(svl_in_vals_list):
                            if svl_in_vals_list[svl_in_index]["remaining_qty"] >= qty:
                                candidate_cost = (svl_in_vals_list[svl_in_index]["remaining_value"] /
                                                  svl_in_vals_list[svl_in_index]["remaining_qty"])
                                svl_in_vals_list[svl_in_index]["remaining_qty"] -= qty
                                svl_in_vals_list[svl_in_index]["remaining_value"] = float_round(
                                    candidate_cost * svl_in_vals_list[svl_in_index]["remaining_qty"],
                                    precision_digits=precision_price)
                                qty = 0
                            else:
                                qty -= svl_in_vals_list[svl_in_index]["remaining_qty"]
                                svl_in_vals_list[svl_in_index]["remaining_qty"] = 0.0
                                svl_in_vals_list[svl_in_index]["remaining_value"] = 0.0
                                svl_in_index += 1
                    svl_vals = _prepare_out_svl_vals(
                        move, move["product_qty"], previous_price, product)
                    svl_out_vals_list.append(svl_vals)
                    previous_qty -= move["product_qty"]
            # Add manual adjusts after last move
            if product.cost_method in ("average", "standard") and not float_is_zero(
                    previous_qty, precision_digits=precision_uom):
                # useless for Fifo because we have price unit on product form
                while h_index < len(history_lines):
                    price_history_rec = history_lines[h_index]
                    if float_compare(price_history_rec["cost"], previous_price, precision_digits=precision_price):
                        svl_vals = _prepare_man_svl_vals(
                            price_history_rec, previous_price, previous_qty, company, product)
                        svl_man_vals_list.append(svl_vals)
                        previous_price = price_history_rec["cost"]
                    h_index += 1
            all_svl_list.extend(svl_in_vals_list + svl_out_vals_list + svl_man_vals_list)
    if all_svl_list:
        all_svl_list = sorted(all_svl_list, key=lambda k: (k["create_date"]))
        _logger.info("To create {} svl records".format(len(all_svl_list)))
        query_insert(env.cr, "stock_valuation_layer", all_svl_list)


@openupgrade.migrate()
def migrate(env, version):
    generate_stock_valuation_layer(env)
    openupgrade.delete_records_safely_by_xml_id(
        env, [
            "stock_account.default_cost_method",
            "stock_account.default_valuation",
            "stock_account.property_stock_account_input_prd",
            "stock_account.property_stock_account_output_prd",
        ]
    )
