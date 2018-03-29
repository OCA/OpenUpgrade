# © 2018 Opener B.V. <https://opener.amsterdam>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.tests.common import TransactionCase


class TestAccountingConfiguration(TransactionCase):
    def test_accounting_configuration(self):
        """ Check if configuration is set to done for companies with moves """
        move = self.env['account.move'].search([], limit=1)
        self.assertTrue(move.company_id.account_setup_coa_done)
        company_no_accounting = self.env['res.company'].search(
            [('name', '=', 'Company without accounting')])
        self.assertFalse(company_no_accounting.account_setup_coa_done)
