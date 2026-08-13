from odoo.tests import TransactionCase, tagged

from odoo.addons.openupgrade_framework import openupgrade_test


@openupgrade_test
@tagged("post_install")
class TestHrExpenseMigration(TransactionCase):
    def test_hr_expense_state(self):
        """
        Test that expenses have the expected state after migration
        """
        self.assertEqual(
            self.env.ref("hr_expense.hotel_bill_expense").state,
            "draft",
        )
        self.assertEqual(
            self.env.ref("hr_expense.pizzas_bill_expense").state,
            "submitted",
        )
        self.assertEqual(
            self.env.ref("hr_expense.chair_bill_expense").state,
            "posted",
        )
        self.assertEqual(
            self.env.ref("hr_expense.travel_demo_by_car_expense").state,
            "paid",
        )

    def test_product_uoms(self):
        """
        Test that expense products' UOMs where updated where possible
        """
        self.assertEqual(
            self.env.ref("hr_expense.expense_product_gift").uom_id,
            self.env.ref("uom.product_uom_km"),
            "Gift UOM should not have been changed because it's used in posted move",
        )
        self.assertEqual(
            self.env.ref("hr_expense.expense_product_communication").uom_id,
            self.env.ref("uom.product_uom_unit"),
            "Communication UOM should have been updated to unit",
        )
