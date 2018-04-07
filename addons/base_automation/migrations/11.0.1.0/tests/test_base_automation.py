# Copyright 2018 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests import common


class TestBaseAutomation(common.TransactionCase):
    def test_rule_on_write(self):
        record = self.env.ref('base_automation.test_rule_on_write')
        self.assertTrue(record)
        self.assertEquals(record.filter_domain, "[('state', '=', 'done')]")
        self.assertEquals(record.filter_pre_domain, "[('state', '=', 'open')]")
        self.assertEquals(record.trigger, "on_write")
        self.assertEquals(record.state, "object_write")
        self.assertTrue(record.fields_lines)
        self.assertEquals(record.fields_lines.value,
                          self.env.ref('base.user_demo'))

    def test_rule_followers_multi(self):
        record = self.env.ref('base_automation.test_rule_followers_multi')
        self.assertTrue(record)
        self.assertTrue(record.child_ids)
        rules = self.env['base.automation'].search([
            ('name', '=', 'Test rule followers multi'),
        ])
        self.assertEquals(len(rules), 2)
        new_record = rules - record
        self.assertEquals(new_record.state, "followers")
        followers = new_record.partners
        self.assertIn(self.env.ref('base.partner_root'), followers)
        self.assertIn(self.env.ref('base.partner_demo'), followers)
