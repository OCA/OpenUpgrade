# coding: utf-8
from openerp.tests import TransactionCase


class TestAccount(TransactionCase):

    def test_reconciliation(self):
        move = self.env.ref('account.test_invoice_1').move_id
        line = move.line_ids.filtered(
            lambda l: l.account_id.internal_type == 'payable')
        self.assertEqual(len(line.matched_debit_ids), 2)
        self.assertEqual(line.amount_residual, 0.0)
        self.assertTrue(line.reconciled)
