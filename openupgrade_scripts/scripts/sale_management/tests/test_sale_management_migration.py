from odoo.tests import TransactionCase

from odoo.addons.openupgrade_framework import openupgrade_test


@openupgrade_test
class TestSaleManagementMigration(TransactionCase):
    def test_sale_order_template_migration(self):
        template = self.env["sale.order.template"].search(
            [("name", "=", "Sale order template")],
        )
        order = self.env["sale.order"].search(
            [("sale_order_template_id", "=", template.id)]
        )
        self.assertItemsEqual(
            order.order_line.mapped("name"), ("some option", "another option")
        )
        self.assertItemsEqual(order.order_line.mapped("is_optional"), (True, True))
        self.assertItemsEqual(
            template.sale_order_template_line_ids.mapped("is_optional"), (True, True)
        )
