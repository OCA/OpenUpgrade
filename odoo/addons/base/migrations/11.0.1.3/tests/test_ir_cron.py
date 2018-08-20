# coding: utf-8
# Copyright 2018 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo.tests.common import TransactionCase


class TestIrCron(TransactionCase):
    def test_ir_cron(self):
        cron = self.env.ref('base.cron_test_migration')
        self.assertTrue(cron)
        self.assertTrue(cron.ir_actions_server_id)
        self.assertEquals(
            cron.ir_actions_server_id.code,
            'model._commercial_sync_from_company()',
        )
