from odoo.tests import TransactionCase

from odoo.addons.openupgrade_framework import openupgrade_test


@openupgrade_test
class TestStockMigration(TransactionCase):
    def test_move_quantity(self):
        """
        Test that we add reserved_qty to quantity for assigned moves
        """
        picking = self.env.ref("stock.outgoing_shipment_main_warehouse4")
        self.assertEqual(picking.move_ids.quantity, 16)
        picking = self.env.ref("stock.incomming_shipment2")
        self.assertEqual(picking.move_ids.quantity, 125)

    def test_returned_picking(self):
        """
        Test that we correctly link returned pickings to their origin picking
        """
        returned_picking = self.env.ref("stock.outgoing_shipment_main_warehouse1")
        self.assertTrue(returned_picking.return_ids)

    def test_return_location(self):
        """
        Test that we set the default return location for pickings from the warehouse's
        return picking type from v16
        """
        picking_type = self.env.ref("stock.picking_type_in")
        stock_location = self.env.ref("stock.stock_location_stock")
        self.assertEqual(picking_type.default_location_return_id, stock_location)
