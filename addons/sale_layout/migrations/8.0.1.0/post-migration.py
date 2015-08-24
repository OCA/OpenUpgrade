# -*- coding: utf-8 -*-
##############################################################################
#
#    This module copyright (C) 2015 Therp BV (<http://therp.nl>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp import SUPERUSER_ID, api
from openerp.openupgrade import openupgrade


def migrate_sale_order_lines(env):
    env.cr.execute(
            "select id, layout_type from sale_order_line "
            "where layout_type not in ('article', 'text')")
    line_layouts = dict(env.cr.fetchall())

    for sale_order in env['sale.order'].search(
            [('order_line', 'in', line_layouts.keys())]):
        current_section = None
        sequence = 1
        for line in sale_order.order_line:
            layout_type = line_layouts.get(line.id)
            if layout_type == 'title':
                current_section = env['sale_layout.category'].create({
                    'name': line.name,
                    'subtotal': False,
                    'separator': False,
                    'pagebreak': False,
                    'sequence': sequence,
                })
                sequence += 1
                if not line.product_id and line.state in ('draft', 'cancel'):
                    line.unlink()
                continue
            if not current_section:
                continue
            line.write({'sale_layout_cat_id': current_section.id})
            if layout_type in ('subtotal', 'line', 'break'):
                field = {
                    'subtotal': 'subtotal',
                    'line': 'separator',
                    'break': 'pagebreak',
                }[layout_type]
                current_section.write({field: True})
                if not line.product_id and line.state in ('draft', 'cancel'):
                    line.unlink()

def migrate_invoice_lines(env):
    env.cr.execute(
            "select id, state from account_invoice_line "
            "where state not in ('article', 'text')")

    line_layouts = dict(env.cr.fetchall())

    for invoice in env['account.invoice'].search(
            [('invoice_line', 'in', line_layouts.keys())]):
        current_section = None
        sequence = 1
        for line in invoice.invoice_line:
            layout_type = line_layouts.get(line.id)
            if layout_type == 'title':
                current_section = env['sale_layout.category'].create({
                    'name': line.name,
                    'subtotal': False,
                    'separator': False,
                    'pagebreak': False,
                    'sequence': sequence,
                })
                sequence += 1
                if not line.product_id:
                    line.unlink()
                continue
            if not current_section:
                continue
            line.write({'sale_layout_cat_id': current_section.id})
            if layout_type in ('subtotal', 'line', 'break'):
                field = {
                    'subtotal': 'subtotal',
                    'line': 'separator',
                    'break': 'pagebreak',
                }[layout_type]
                current_section.write({field: True})
                if not line.product_id:
                    line.unlink()

@openupgrade.migrate()
def migrate(cr, version):
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        migrate_sale_order_lines(env)
        # see if account_invoice_layout is installed, migrate that too
        if env['ir.module.module'].search([
                ('name', '=', 'account_invoice_layout'),
                ('state', '!=', 'uninstalled')]):
            migrate_invoice_lines(env)
