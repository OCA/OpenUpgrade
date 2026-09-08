from odoo.tests import TransactionCase, tagged

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
            order.order_line.mapped("name"),
            (
                "non-optional line",
                "non-optional line2",
                "/",
                "some option",
                "another option",
            ),
        )
        self.assertItemsEqual(
            order.order_line.mapped("is_optional"), (False, False, True, False, False)
        )
        self.assertItemsEqual(
            map(lambda x: x._is_line_optional(), order.order_line),
            (False, False, False, True, True),
        )
        self.assertItemsEqual(
            template.sale_order_template_line_ids.mapped("name"),
            ("/", "some option", "another option"),
        )
        self.assertItemsEqual(
            template.sale_order_template_line_ids.mapped("is_optional"),
            (True, False, False),
        )


@openupgrade_test
@tagged("-at_install", "post_install")
class TestSaleManagementMigrationPost(TransactionCase):
    def test_sale_order_template_migration(self):
        template = self.env["sale.order.template"].search(
            [("name", "=", "Sale order template")],
        )
        self.assertItemsEqual(
            template.sale_order_template_line_ids.with_context(lang="fr_FR").mapped(
                "name"
            ),
            ("Section produits optionnels", "some option", "another option"),
        )
        self.assertItemsEqual(
            template.sale_order_template_line_ids.with_context(lang="en_US").mapped(
                "name"
            ),
            ("Optional Products Section", "some option", "another option"),
        )
