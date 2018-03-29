# © 2018 Opener B.V. <https://opener.amsterdam>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging
from openupgradelib import openupgrade
from odoo.tests.common import TransactionCase


class TestTaxExigibility(TransactionCase):
    def test_tax_exigibility(self):
        logger = logging.getLogger(__name__)
        if not openupgrade.column_exists(
                self.env.cr, 'account_tax',
                openupgrade.get_legacy_name('use_cash_basis')):
            logger.debug('account_tax_cash_basis was not installed, skip test')
            return
        tax = self.env.ref('l10n_generic_coa.1_purchase_tax_template')
        other_tax = self.env.ref('l10n_generic_coa.1_sale_tax_template')
        self.assertTrue(tax.company_id.tax_exigibility)
        self.assertEqual(tax.tax_exigibility, 'on_payment')
        self.assertEqual(other_tax.tax_exigibility, 'on_invoice')
