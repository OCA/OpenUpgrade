# coding: utf-8
from openerp.tests.common import TransactionCase


class TestPortalSale(TransactionCase):
    def test_portal_sale(self):
        """ Check loading of modified noupdate data """
        self.assertEqual(
            self.env.ref('portal_sale.email_template_edi_invoice').partner_to,
            '${object.partner_id.id}')
        self.assertIn(
            self.env.ref('base.group_portal'),
            self.env.ref('portal_sale.portal_personal_contact').groups)
