# -*- coding: utf-8 -*-
# © 2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp.tests.common import TransactionCase


class TestAnalytic(TransactionCase):
    def test_analytic(self):
        self.assertTrue(
            all(
                self.env['ir.ui.view'].search([
                    ('model', '=', 'account.analytic.line'),
                ]).mapped('xml_id')
            )
        )
