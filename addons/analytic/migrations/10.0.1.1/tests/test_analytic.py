# coding: utf-8
from openerp.tests.common import TransactionCase


class TestAnalytic(TransactionCase)

    def test_analytic(self):
        self.assertTrue(
            self.env.ref('analytic.ou_analytic_account_c1').active == False
        )
        self.assertTrue(
            self.env.ref('analytic.ou_analytic_account_n1').active == True
        )
