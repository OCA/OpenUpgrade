# coding: utf-8
# Copyright 2018 Opener B.V. <https://opener.amsterdam>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging
from psycopg2.extensions import AsIs
from openupgradelib import openupgrade
from openerp.tests.common import TransactionCase

_logger = logging.getLogger(__name__)


class TestProcurementRule(TransactionCase):
    def get_procurement(self, procure_method, supply_method):
        stock = self.env.ref('stock.stock_location_stock')
        customers = self.env.ref('stock.stock_location_customers')
        self.env.cr.execute(
            """ SELECT po.id FROM procurement_order po
            JOIN product_product pp ON po.product_id = pp.id
            JOIN product_template pt ON pp.product_tmpl_id = pt.id
            WHERE po.%s = %s AND pt.%s = %s
                AND po.state NOT IN ('cancel', 'done')""", (
                    AsIs(openupgrade.get_legacy_name('procure_method')),
                    procure_method,
                    AsIs(openupgrade.get_legacy_name('supply_method')),
                    supply_method))
        procurement_ids = [proc_id for proc_id, in self.env.cr.fetchall()]
        procurement = self.env['stock.move'].search([
            ('location_id', '=', stock.id),
            ('location_dest_id', '=', customers.id),
            ('procurement_id', 'in', procurement_ids)
        ], limit=1).procurement_id
        if not procurement:
            _logger.warn(
                'No pending procurement found for a %s/%s product',
                procure_method, supply_method)
        return procurement

    def test_procurement_rule(self):
        """ Make2stock procurements for outgoing moves got a 'move' rule
        assigned. """
        try:
            self.env['stock.location.route']
        except KeyError:
            return

        for (procure_method, supply_method, action) in [
                ('make_to_order', 'buy', 'buy'),
                ('make_to_stock', 'buy', 'move'),
                ('make_to_order', 'produce', 'manufacture'),
                ('make_to_stock', 'produce', 'move')]:
            procurement = self.get_procurement(procure_method, supply_method)
            if procurement:
                self.assertEqual(procurement.rule_id.action, action)
