# coding: utf-8
from openerp.tests.common import TransactionCase


class TestCrmClaim(TransactionCase):

    def test_claim_category(self):
        "Check if claim category XML ids have been migrated properly"
        self.assertEqual(
            self.env.ref('crm_claim.crm_claim_1').categ_id,
            self.env.ref('crm_claim.categ_claim1'))
        category = self.env['ir.model.data'].search([
            ('name', '=', 'categ_claim1'),
            ('module', '=', 'crm_claim')])
        self.assertEqual(category.model, 'crm.claim.category')
