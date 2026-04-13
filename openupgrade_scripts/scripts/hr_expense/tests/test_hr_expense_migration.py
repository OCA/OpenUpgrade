from odoo.tests import TransactionCase

from odoo.addons.openupgrade_framework import openupgrade_test


@openupgrade_test
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
