# © 2021 Opener B.V. <https://opener.amsterdam>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
from odoo.tests.common import TransactionCase


class TestFieldXmlid(TransactionCase):
    def test_field_xmlid(self):
        """Check that an xmlid was created for the field in its new home
        module after it moved from module 'web' to this module lower down
        in the dependency chain."""
        field = self.env["ir.model.fields"].search(
            [("model", "=", "report.layout"),
             ("name", "=", "view_id")])
        self.assertTrue(field)
        self.assertTrue(
            self.env["ir.model.data"].search(
                [("module", "=", "base"),
                 ("model", "=", field._name),
                 ("res_id", "=", field.id)]))
