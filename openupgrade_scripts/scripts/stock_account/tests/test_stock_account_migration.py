from unittest import mock

from odoo.tests import TransactionCase, tagged

from odoo.addons.openupgrade_framework import openupgrade_test


@openupgrade_test
@tagged("-at_install", "post_install")
class TestStockAccountMigration(TransactionCase):
    def setUp(self):
        super().setUp()
        self.product_avg = self.env["product.product"].search(
            [("name", "=", "AVG product")]
        )
        self.product_fifo = self.env["product.product"].search(
            [("name", "=", "FIFO product")]
        )
        self.product_reval = self.env["product.product"].search(
            [("name", "=", "Revaluation product")]
        )
        self.location_customer = self.env.ref("stock.stock_location_customers")
        self.location_supplier = self.env.ref("stock.stock_location_suppliers")
        self.location_stock = self.env.ref("stock.stock_location_stock")

    def _buy(self, product, price_unit, quantity):
        in_move = self.env["stock.move"].create(
            {
                "product_id": product.id,
                "location_id": self.location_supplier.id,
                "location_dest_id": self.location_stock.id,
                "product_uom_qty": quantity,
            }
        )
        in_move._action_confirm()
        in_move.picked = True
        with mock.patch.object(
            in_move.__class__, "_get_value_from_account_move"
        ) as patched_get_value:
            patched_get_value.return_value = {
                "value": price_unit * quantity,
                "quantity": quantity,
                "description": "None",
            }
            in_move._action_done()
        return in_move

    def _sell(self, product, quantity):
        out_move = self.env["stock.move"].create(
            {
                "product_id": product.id,
                "location_id": self.location_stock.id,
                "location_dest_id": self.location_customer.id,
                "product_uom_qty": quantity,
            }
        )
        out_move._action_confirm()
        out_move.picked = True
        out_move._action_assign(force_qty=quantity)
        out_move._action_done()
        return out_move

    def test_average_price(self):
        self.assertEqual(self.product_avg.standard_price, 22)

        self._buy(self.product_avg, price_unit=24, quantity=4)

        # ( 4*22 (after v18 adjusted price) + 4*24 (v19) ) / 8
        self.assertEqual(self.product_avg.standard_price, 23)

    def test_fifo_price(self):
        self.assertEqual(self.product_fifo.standard_price, 22)

        out_move = self._sell(self.product_fifo, 2)
        # 2*22 (v18)
        self.assertEqual(out_move.value, 44)
        self.assertEqual(self.product_fifo.standard_price, 22)

        self._buy(self.product_fifo, price_unit=24, quantity=4)

        out_move = self._sell(self.product_fifo, 2)
        # 2*24 (v19)
        self.assertEqual(out_move.value, 48)
        self.assertEqual(self.product_fifo.standard_price, 24)

    def test_zero_unit_cost_revaluation(self):
        """A revaluation booked with unit_cost 0 must not zero the cost.

        17.0 writes unit_cost 0 -- not NULL -- when an adjustment changes the total
        value of the stock without a per-unit price, keeping the adjustment in value.
        Carrying that unit_cost straight over to product.value reads 0 as the cost,
        which is worse than leaving it wrong: a zero cost looks like a product that
        has simply never been costed, and it prices every subsequent delivery at
        nothing.

        4 bought at 20 gives a value of 80, and the revaluation adds 40, so the cost
        the migration has to arrive at is 120 / 4 = 30.
        """
        self.assertEqual(self.product_reval.standard_price, 30)
