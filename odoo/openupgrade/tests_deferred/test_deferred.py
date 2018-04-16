# -*- coding: utf-8 -*-
# © 2017 Opener B.V. <https://opener.am>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.tests import common


class TestDeferred(common.TransactionCase):
    def test_invalid_custom_view(self):
        """ Check that an invalid custom view has been set to inactive """
        view = self.env['ir.ui.view'].with_context(active_test=False).search([
            ('name', '=', 'Invalid custom view')])
        self.assertTrue(view)
        self.assertFalse(view.active)
