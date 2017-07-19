# coding: utf-8
from openerp.tests.common import TransactionCase


class TestAnalytic(TransactionCase):

    def test_analytic(self):
        self.assertFalse(
            self.env.ref('analytic.ou_analytic_account_c1').active
        )
        self.assertTrue(
            self.env.ref('analytic.ou_analytic_account_n1').active
        )
