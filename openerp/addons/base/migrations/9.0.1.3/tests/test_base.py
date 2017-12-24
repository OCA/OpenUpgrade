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

    def test_technical_features(self):
        """ Check that the admin user can access technical features """
        self.assertIn(
            self.env.ref('base.user_root'),
            self.env.ref('base.group_no_one').users)

    def test_translation(self):
        """ Existing field name translations are migrated correctly """
        self.assertEqual(
            self.env.ref('base.field_ir_module_module_summary').with_context(
                lang='fr_FR')['field_description'],
            'Custom translation')
