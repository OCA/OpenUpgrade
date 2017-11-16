# -*- coding: utf-8 -*-
# © 2017 Opener B.V. <https://opener.am>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp.tests import common


class TestDeferred(common.TransactionCase):

    def test_binary_attachments(self):
        """ Binary fields are migrated to attachments """
        self.assertTrue(
            self.env['ir.attachment'].search([
                ('res_model', '=', 'res.partner'),
                ('res_field', '=', 'image'),
                ('res_name', '=', 'Axelor...'),
            ]).datas)

    def test_hr_attendance_view_removed(self):
        """ This view, which had the noupdate flag, is now successfully removed
        """
        with self.assertRaisesRegexp(ValueError, 'External ID not found'):
            self.env.ref('hr_attendance.hr_attendace_group')
