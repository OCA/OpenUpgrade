import unittest

from odoo.tests.common import TransactionCase

from odoo.addons.openupgrade_framework import openupgrade_test


@openupgrade_test
class TestStockMigration(TransactionCase):
    @unittest.skip("Should be executed at end-migration")
    def test_picking_type_required_fields(self):
        """Test that newly required fields are set"""
        for picking_type in self.env["stock.picking.type"].search([]):
            self.assertTrue(picking_type.default_location_src_id)
            self.assertTrue(picking_type.default_location_dest_id)

    def test_pull_moves(self):
        """
        Test that pull moves have been migrated correctly and new moves yield the
        same result
        """
        product = self.env.ref("openupgrade_test_stock.pull_product")
        stock_location = self.env.ref("stock.stock_location_stock")
        intermediate_location = self.env.ref(
            "openupgrade_test_stock.intermediate_pull_location"
        )
        customer_location = self.env.ref("stock.stock_location_customers")

        moves = self.env["stock.move"].search([("product_id", "=", product.id)])
        from_stock = moves.filtered(lambda x: x.location_id == stock_location)
        from_intermediate = moves.filtered(
            lambda x: x.location_id == intermediate_location
        )

        self.assertEqual(from_stock.location_dest_id, intermediate_location)
        self.assertEqual(from_stock.location_final_id, intermediate_location)

        self.assertEqual(from_intermediate.location_dest_id, customer_location)
        self.assertEqual(from_intermediate.location_final_id, customer_location)

        rules = self.env["stock.rule"].search(
            [
                "|",
                ("location_src_id", "=", intermediate_location.id),
                ("location_dest_id", "=", intermediate_location.id),
            ]
        )
        for rule in rules:
            self.assertEqual(rule.location_dest_from_rule, True)

        procurement_group = self.env["procurement.group"].create(
            {
                "name": "2 step procurement v18",
            }
        )
        self.env["procurement.group"].run(
            [
                self.env["procurement.group"].Procurement(
                    product_id=product,
                    product_qty=42,
                    product_uom=product.uom_id,
                    location_id=customer_location,
                    name="2 step procurement",
                    origin="/",
                    company_id=self.env.company,
                    values={"group_id": procurement_group},
                ),
            ]
        )

        new_moves = (
            self.env["stock.move"].search([("product_id", "=", product.id)]) - moves
        )
        from_stock = new_moves.filtered(lambda x: x.location_id == stock_location)
        from_intermediate = new_moves.filtered(
            lambda x: x.location_id == intermediate_location
        )

        self.assertEqual(from_stock.location_dest_id, intermediate_location)
        self.assertEqual(from_stock.location_final_id, intermediate_location)

        self.assertEqual(from_intermediate.location_dest_id, customer_location)
        self.assertEqual(from_intermediate.location_final_id, customer_location)

    def test_push_moves(self):
        """
        Test that push moves have been migrated correctly and new moves yield the
        same result
        """
        product = self.env.ref("openupgrade_test_stock.push_product")
        stock_location = self.env.ref("stock.stock_location_stock")
        intermediate_location = self.env.ref(
            "openupgrade_test_stock.intermediate_push_location"
        )
        customer_location = self.env.ref("stock.stock_location_customers")

        moves = self.env["stock.move"].search([("product_id", "=", product.id)])

        from_stock = moves.filtered(lambda x: x.location_id == stock_location)
        from_intermediate = moves.filtered(
            lambda x: x.location_id == intermediate_location
        )

        self.assertEqual(from_stock.location_dest_id, intermediate_location)
        self.assertEqual(from_stock.location_final_id, customer_location)

        self.assertEqual(from_intermediate.location_dest_id, customer_location)
        self.assertEqual(from_intermediate.location_final_id, customer_location)

        in_move = self.env["stock.move"].create(
            {
                "name": "in",
                "location_id": self.env.ref("stock.stock_location_suppliers").id,
                "location_dest_id": stock_location.id,
                "location_final_id": customer_location.id,
                "route_ids": [(6, 0, moves.route_ids.ids)],
                "product_id": product.id,
                "quantity": 42,
                "product_uom_qty": 42,
                "picked": True,
            }
        )
        in_move._action_done()
        in_move.move_dest_ids.picked = True
        in_move.move_dest_ids._action_done()

        new_moves = (
            self.env["stock.move"].search([("product_id", "=", product.id)]) - moves
        )

        from_stock = new_moves.filtered(lambda x: x.location_id == stock_location)
        from_intermediate = new_moves.filtered(
            lambda x: x.location_id == intermediate_location
        )

        self.assertEqual(from_stock.location_dest_id, intermediate_location)
        self.assertEqual(from_stock.location_final_id, customer_location)

        self.assertEqual(from_intermediate.location_dest_id, customer_location)
        self.assertEqual(from_intermediate.location_final_id, customer_location)
