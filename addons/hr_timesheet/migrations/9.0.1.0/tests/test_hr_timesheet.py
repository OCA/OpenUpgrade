# coding: utf-8
from openerp.tests.common import TransactionCase


class TestHrTimesheet(TransactionCase):
    def test_hr_timesheet(self):
        self.env.cr.execute(
            "SELECT line_id FROM hr_analytic_timesheet LIMIT 1")
        line_id, = self.env.cr.fetchone()
        line = self.env['account.analytic.line'].browse(line_id)
        self.assertTrue(line.is_timesheet)
