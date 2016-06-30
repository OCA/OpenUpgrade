# coding: utf-8
from openerp.tests.common import TransactionCase


class TestSalesTeam(TransactionCase):
    def test_sales_team(self):
        """ Check that existing crm case section was migrated successfully """
        self.assertTrue(
            self.env['crm.team'].search([('name', '=', 'Indirect Sales')]))
