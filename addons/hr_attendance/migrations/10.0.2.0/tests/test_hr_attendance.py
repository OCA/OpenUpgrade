# coding: utf-8
# Copyright 2017 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.tests.common import TransactionCase


class TestHrAttendance(TransactionCase):
    def test_check_out(self):
        att1 = self.env.ref('hr_attendance.attendance1')
        self.assertEqual(att1.check_out[-11:], '01 11:51:00')
        self.assertAlmostEqual(att1.worked_hours, 3.5, 1)
        att2 = self.env.ref('hr_attendance.attendance3')
        self.assertEqual(att2.check_out[-11:], '02 19:53:00')
        self.assertAlmostEqual(att2.worked_hours, 7.1, 1)
