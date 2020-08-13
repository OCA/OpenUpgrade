# Copyright 2020 ForgeFlow <http://www.forgeflow.com>
# Copyright 2020 Andrii Skrypka
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade
from odoo import _
from odoo.osv import expression
from odoo.tools.float_utils import float_is_zero


@openupgrade.logging()
def generate_stock_valuation_layer(env):
    """ Generate stock.valuation.layers according to stock.move and product.price.history"""
    openupgrade.logged_query(
        env.cr, """
        ALTER TABLE stock_valuation_layer
        ADD COLUMN old_product_price_history_id integer""",
    )
    std_price_update = {}  # keep standard price at datetime
    done_moves = env['stock.move'].with_context(
        tz='UTC', tracking_disable=True).search([
            ('state', '=', 'done'),
        ], order='company_id, product_id, date ASC')
    for move in done_moves:
        diff = move.quantity_done
        if move._is_in() and diff > 0 or move._is_out() and diff < 0:
            _product_price_update_before_done(env, move, std_price_update)
            _create_in_svl(env, move, std_price_update)
            if move.product_id.cost_method in ('average', 'fifo'):
                _run_fifo_vacuum(env, move.product_id, move.company_id, std_price_update)
        elif move._is_in() and diff < 0 or move._is_out() and diff > 0:
            _create_out_svl(env, move, std_price_update)
        elif move._is_dropshipped() and diff > 0 or move._is_dropshipped_returned() and diff < 0:
            _create_dropshipped_svl(env, move, std_price_update)
        elif move._is_dropshipped() and diff < 0 or move._is_dropshipped_returned() and diff > 0:
            _create_dropshipped_svl(env, move, std_price_update)


def _product_price_update_before_done(env, move, std_price_update):
    # adapt standard price on incomming moves if the product cost_method is 'average'
    if move.with_context(force_company=move.company_id.id).product_id.cost_method == 'average':
        product = move.product_id.with_context(force_company=move.company_id.id)
        value_svl, product_tot_qty_available = _compute_value_svl(env, product, move.company_id)
        rounding = move.product_id.uom_id.rounding
        valued_move_lines = move._get_in_move_lines()
        qty_done = 0.0
        for valued_move_line in valued_move_lines:
            qty_done += valued_move_line.product_uom_id._compute_quantity(
                valued_move_line.qty_done, move.product_id.uom_id)
        qty = qty_done
        if float_is_zero(product_tot_qty_available, precision_rounding=rounding):
            new_std_price = _get_price_unit(move, std_price_update)
        elif float_is_zero(product_tot_qty_available + move.product_qty, precision_rounding=rounding) or \
                float_is_zero(product_tot_qty_available + qty, precision_rounding=rounding):
            new_std_price = _get_price_unit(move, std_price_update)
        else:
            # Get the standard price
            amount_unit = move.product_id.with_context(force_company=move.company_id.id).standard_price
            new_std_price = (
                (amount_unit * product_tot_qty_available) + (_get_price_unit(move, std_price_update) * qty)
            ) / (product_tot_qty_available + qty)
        std_price_update[move.company_id.id, move.product_id.id] = new_std_price


def _create_in_svl(env, move, std_price_update):
    move = move.with_context(force_company=move.company_id.id)
    valued_move_lines = move._get_in_move_lines()
    valued_quantity = 0.0
    for valued_move_line in valued_move_lines:
        valued_quantity += valued_move_line.product_uom_id._compute_quantity(
            valued_move_line.qty_done, move.product_id.uom_id)
    _change_standard_price(env, move, std_price_update)  # Create SVL for manual updated standard price
    unit_cost = abs(_get_price_unit(move, std_price_update))  # May be negative (i.e. decrease an out move).
    if move.product_id.cost_method == 'standard':
        unit_cost = std_price_update.get((move.company_id.id, move.product_id.id), move.product_id.standard_price)
    vals = move.product_id._prepare_in_svl_vals(valued_quantity, unit_cost)
    vals.update(move._prepare_common_svl_vals())
    vals.update({
        'create_date': move.date,
        'create_uid': move.create_uid.id or 1,
        'write_date': move.date,
        'write_uid': move.create_uid.id or 1,
    })
    _create_stock_valuation_layer(env, [vals])


def _create_out_svl(env, move, std_price_update):
    move = move.with_context(force_company=move.company_id.id)
    valued_move_lines = move._get_out_move_lines()
    valued_quantity = 0.0
    for valued_move_line in valued_move_lines:
        valued_quantity += valued_move_line.product_uom_id._compute_quantity(
            valued_move_line.qty_done, move.product_id.uom_id)
    if float_is_zero(valued_quantity, precision_rounding=move.product_id.uom_id.rounding):
        return
    _change_standard_price(env, move, std_price_update)
    vals = move.product_id._prepare_out_svl_vals(valued_quantity, move.company_id)
    vals.update(move._prepare_common_svl_vals())
    vals.update({
        'create_date': move.date,
        'create_uid': move.create_uid.id or 1,
        'write_date': move.date,
        'write_uid': move.create_uid.id or 1,
    })
    _create_stock_valuation_layer(env, [vals])


def _create_dropshipped_svl(env, move, std_price_update):
    svl_vals_list = []
    move = move.with_context(force_company=move.company_id.id)
    valued_move_lines = move.move_line_ids
    valued_quantity = 0.0
    for valued_move_line in valued_move_lines:
        valued_quantity += valued_move_line.product_uom_id._compute_quantity(
            valued_move_line.qty_done, move.product_id.uom_id)
    quantity = valued_quantity
    _change_standard_price(env, move, std_price_update)
    unit_cost = _get_price_unit(move, std_price_update)
    company = move.product_id.env.company
    if move.product_id.cost_method == 'standard' and (company.id, move.product_id.id) in std_price_update:
        unit_cost = std_price_update[(company.id, move.product_id.id)]
    common_vals = dict(move._prepare_common_svl_vals(),
                       remaining_qty=0, create_date=move.date, create_uid=move.create_uid.id,
                       write_date=move.date, write_uid=move.create_uid.id)
    # create the in
    in_vals = {
        'unit_cost': unit_cost,
        'value': unit_cost * quantity,
        'quantity': quantity,
    }
    in_vals.update(common_vals)
    svl_vals_list.append(in_vals)
    # create the out
    out_vals = {
        'unit_cost': unit_cost,
        'value': unit_cost * quantity * -1,
        'quantity': quantity * -1,
    }
    out_vals.update(common_vals)
    svl_vals_list.append(out_vals)
    _create_stock_valuation_layer(env, svl_vals_list)


def _run_fifo_vacuum(env, product, company, std_price_update):
    product.ensure_one()
    if company is None:
        company = env.company
    svls_to_vacuum = env['stock.valuation.layer'].search([
        ('product_id', '=', product.id),
        ('remaining_qty', '<', 0),
        ('stock_move_id', '!=', False),
        ('company_id', '=', company.id),
    ], order='create_date, id')
    for svl_to_vacuum in svls_to_vacuum:
        domain = [
            ('company_id', '=', svl_to_vacuum.company_id.id),
            ('product_id', '=', product.id),
            ('remaining_qty', '>', 0),
            '|',
            ('create_date', '>', svl_to_vacuum.create_date),
            '&', ('create_date', '=', svl_to_vacuum.create_date), ('id', '>', svl_to_vacuum.id)
        ]
        candidates = env['stock.valuation.layer'].search(domain)
        if not candidates:
            break
        qty_to_take_on_candidates = abs(svl_to_vacuum.remaining_qty)
        qty_taken_on_candidates = 0
        tmp_value = 0
        for candidate in candidates:
            qty_taken_on_candidate = min(candidate.remaining_qty, qty_to_take_on_candidates)
            qty_taken_on_candidates += qty_taken_on_candidate
            candidate_unit_cost = candidate.remaining_value / candidate.remaining_qty
            value_taken_on_candidate = qty_taken_on_candidate * candidate_unit_cost
            value_taken_on_candidate = candidate.currency_id.round(value_taken_on_candidate)
            new_remaining_value = candidate.remaining_value - value_taken_on_candidate
            candidate_vals = {
                'remaining_qty': candidate.remaining_qty - qty_taken_on_candidate,
                'remaining_value': new_remaining_value
            }
            candidate.write(candidate_vals)
            qty_to_take_on_candidates -= qty_taken_on_candidate
            tmp_value += value_taken_on_candidate
            if float_is_zero(qty_to_take_on_candidates, precision_rounding=product.uom_id.rounding):
                break
        # Get the estimated value we will correct.
        remaining_value_before_vacuum = svl_to_vacuum.unit_cost * qty_taken_on_candidates
        new_remaining_qty = svl_to_vacuum.remaining_qty + qty_taken_on_candidates
        corrected_value = remaining_value_before_vacuum - tmp_value
        svl_to_vacuum.write({
            'remaining_qty': new_remaining_qty,
        })
        # Don't create a layer or an accounting entry if the corrected value is zero.
        if svl_to_vacuum.currency_id.is_zero(corrected_value):
            continue
        corrected_value = svl_to_vacuum.currency_id.round(corrected_value)
        move = svl_to_vacuum.stock_move_id
        vals = {
            'product_id': product.id,
            'value': corrected_value,
            'unit_cost': 0,
            'quantity': 0,
            'remaining_qty': 0,
            'stock_move_id': move.id,
            'company_id': move.company_id.id,
            'description': 'Revaluation of %s (negative inventory)' % move.picking_id.name or move.name,
            'stock_valuation_layer_id': svl_to_vacuum.id,
            'create_date': move.date,
            'create_uid': move.create_uid.id or 1,
            'write_date': move.date,
            'write_uid': move.create_uid.id or 1,
        }
        _create_stock_valuation_layer(env, [vals])
        # If some negative stock were fixed, we need to recompute the standard price.
        product = product.with_context(force_company=company.id)
        value_svl, quantity_svl = _compute_value_svl(env, product, company)
        if product.cost_method == 'average' \
                and not float_is_zero(quantity_svl, precision_rounding=product.uom_id.rounding):
            std_price_update[company.id, product.id] = value_svl / quantity_svl


def _change_standard_price(env, move, std_price_update):
    """ Create stock.valuation.layer for manual updated standard_price from a product form"""
    product = move.product_id
    if product.cost_method in ('standard', 'average'):
        company = product.env.company
        last_svl = move.env['stock.valuation.layer'].search([
            ('product_id', '=', product.id),
            ('company_id', '=', company.id),
        ], order='create_date desc, id desc', limit=1)
        if not last_svl:
            return
        value_svl, quantity_svl = _compute_value_svl(env, product, company)
        if not float_is_zero(quantity_svl, precision_rounding=product.uom_id.rounding):
            env.cr.execute("""
            SELECT id, company_id, product_id, datetime, cost, create_uid, write_uid, write_date
            FROM product_price_history
            WHERE company_id = %s AND product_id = %s AND datetime < %s AND datetime > %s
            ORDER BY company_id, product_id, datetime
            """, (company.id, product.id, move.date, last_svl.create_date))
            pph_data = env.cr.fetchall()
            price_at_date = last_svl.unit_cost
            for pph in pph_data:
                diff = pph[4] - price_at_date
                value = company.currency_id.round(quantity_svl * diff)
                if not company.currency_id.is_zero(value):
                    vals = {
                        'company_id': company.id,
                        'product_id': product.id,
                        'description': _('Product value manually modified (from %s to %s)') % (price_at_date, pph[4]),
                        'value': value,
                        'quantity': 0,
                        'old_product_price_history_id': pph[0],
                        'create_date': pph[3],
                        'create_uid': pph[5] or 1,
                        'write_uid': pph[6] or 1,
                        'write_date': pph[7],
                    }
                    _create_stock_valuation_layer(env, [vals])
                    std_price_update[company.id, product.id] = pph[4]


def _get_price_unit(move, std_price_update):
    """ Returns the unit price to value this stock move """
    move.ensure_one()
    price_unit = move.price_unit
    # If the move is a return, use the original move's price unit.
    returned_svl = move.env['stock.valuation.layer'].search([
        ('stock_move_id', '=', move.origin_returned_move_id.id),
    ], order='create_date desc, id desc', limit=1)
    if move.origin_returned_move_id and returned_svl:
        price_unit = returned_svl.unit_cost
    if not move.company_id.currency_id.is_zero(price_unit):
        return price_unit
    return std_price_update.get(move.company_id.id, move.product_id.id) or move.product_id.standard_price


def _create_stock_valuation_layer(env, vals_list):
    for vals in vals_list:
        if 'account_move_id' not in vals:
            vals['account_move_id'] = _get_related_account_move(env, vals).id or None
        columns = vals.keys()
        query = """
            INSERT INTO stock_valuation_layer ({})
            VALUES({})
        """.format(', '.join(columns), ", ".join(["%({})s".format(col) for col in columns]))
        env.cr.execute(query, vals)


def _get_related_account_move(env, svl_vals):
    """ Return Account move related to Stock Valuation Layer"""
    domain = []
    if svl_vals.get('stock_move_id'):
        domain = expression.AND([domain, [('stock_move_id', '=', svl_vals['stock_move_id'])]])
    if svl_vals.get('old_product_price_history_id'):
        env.cr.execute("""
            SELECT create_date
            FROM product_price_history
            WHERE id = %s
        """, (svl_vals['old_product_price_history_id'],))
        create_date = env.cr.fetchone()[0]
        domain = expression.AND([domain, [('create_date', '=', create_date)]])
    if not domain:
        return env['account.move']
    account_moves = env['account.move'].search(domain)
    if len(account_moves) > 1:
        return env['account.move']
    return account_moves


def _compute_value_svl(env, product, company):
    # We call this function because the product doesn't have in cache correct value
    # when we create SVL by SQL
    # use sql instead of ORM because it saves ~30% time
    env.cr.execute("""
        SELECT product_id, sum(value) AS value, sum(quantity) AS quantity
        FROM stock_valuation_layer
        WHERE product_id = %s AND company_id = %s
        GROUP BY product_id
    """, (product.id, company.id))
    result = env.cr.fetchone()
    if result:
        return company.currency_id.round(result[1]), result[2]
    return 0.0, 0.0


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
