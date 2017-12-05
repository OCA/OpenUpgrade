# coding: utf-8
from openerp.tests.common import TransactionCase


class TestAccountSequence(TransactionCase):
    def test_account_sequence(self):
        """ Fiscalyear sequences are migrated to date ranges """
        sequence = self.env.ref('account.sequence_sale_journal')
        self.assertTrue(sequence.use_date_range)
        self.assertEqual(sequence.date_range_ids.number_next, 42)
