# -*- coding: utf-8 -*-
# © 2018 Opener B.V. <https://opener.am>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.tests import common


class TestDeferred(common.TransactionCase):
    def test_system_user(self):
        """ There is now a distinct admin user which does not have ID 1 """
        self.assertEqual(self.env.ref('base.user_root').id, 1)
        self.assertTrue(
            self.env.ref('base.user_root') != self.env.ref('base.user_admin'))
        self.assertTrue(
            self.env.ref('base.user_root').partner_id !=
            self.env.ref('base.user_admin').partner_id)
