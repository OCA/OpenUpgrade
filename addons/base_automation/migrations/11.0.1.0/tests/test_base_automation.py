# Copyright 2018 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests import common


class TestBaseAutomation(common.TransactionCase):
    def test_rule_on_create(self):
        record = self.env['base.automation'].search([
            ('name', '=', 'Test rule on write'),
        ])
        self.assertTrue(record)
        self.assertEquals(record.filter_domain, "[('state', '=', 'done')]")
        self.assertEquals(record.filter_pre_domain, "[('state', '=', 'open')]")
        self.assertEquals(record.trigger, "on_write")
