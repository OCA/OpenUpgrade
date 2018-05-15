# -*- coding: utf-8 -*-
# © 2017 Opener B.V. <https://opener.am>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.tests import common


class TestDeferred(common.TransactionCase):

    def test_binary_attachments(self):
        """ Binary fields are migrated to attachments """
        if not self.env.get('slide.slide'):
            return  # test does not apply
        slide = self.env.ref('website_slides.slide_9')
        self.assertTrue(
            self.env['ir.attachment'].search([
                ('res_model', '=', 'slide.slide'),
                ('res_field', '=', 'datas'),
                ('res_id', '=', slide.id),
            ]).datas)

    def test_invalid_custom_view(self):
        """ Check that an invalid custom view has been set to inactive """
        view = self.env['ir.ui.view'].with_context(active_test=False).search([
            ('name', '=', 'Invalid custom view')])
        self.assertTrue(view)
        self.assertFalse(view.active)
