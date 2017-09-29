# -*- coding: utf-8 -*-
# © 2017 Opener B.V. <https://opener.am>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp.tests import common


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
