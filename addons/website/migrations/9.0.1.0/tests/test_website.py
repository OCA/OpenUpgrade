# -*- coding: utf-8 -*-
# Copyright 2016 Tecnativa - Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from openerp.tests import TransactionCase


class TestSale(TransactionCase):
    def test_website(self):
        self.assertTrue(self.env.ref('website.default_website').cdn_filters)
        self.assertEqual(
            self.env.ref('website.homepage').key, 'website.homepage',
        )
