# -*- coding: utf-8 -*-
# © 2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp.tests import common


class TestBase(common.TransactionCase):
    def test_is_company(self):
        # check if some partners are migrated the way we expect
        self.assertTrue(self.env.ref('base.main_partner').is_company)
        self.assertEqual(
            self.env.ref('base.main_partner').company_type, 'company')
        self.assertFalse(self.env.ref('base.user_root').is_company)
        self.assertEqual(
            self.env.ref('base.user_root').company_type, 'person')
