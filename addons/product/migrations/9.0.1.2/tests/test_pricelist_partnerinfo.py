# coding: utf-8
# © 2017 Opener B.V. (<https://opener.amsterdam>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp.tests.common import TransactionCase


class TestPricelistPartnerinfo(TransactionCase):
    def test_pricelist_partnerinfo(self):
        """ Validate pricelistinfo migrated to existing and new supplierinfo
        """
        product = self.env.ref('product.product_product_4_product_template')
        company_eu = self.env.ref('base.main_company')
        company_us = self.env.ref('multi_company.res_company_oerp_us')
        self.assertEqual(len(product.seller_ids), 4)
        self.assertTrue(
            self.env['product.supplierinfo'].search([
                ('product_code', '=', 'PPCD'),
                ('product_name', '=', 'partner product name'),
                ('product_tmpl_id', '=', product.id),
                ('currency_id', '=', self.env.ref('base.EUR').id),
                ('company_id', '=', company_eu.id),
                ('min_qty', '=', 1),
                ('price', '=', 2),
                ('sequence', '=', 3),
                ('delay', '=', 2),
            ]))
        self.assertTrue(
            self.env['product.supplierinfo'].search([
                ('product_code', '=', 'PPCD'),
                ('product_name', '=', 'partner product name'),
                ('product_tmpl_id', '=', product.id),
                ('currency_id', '=', self.env.ref('base.EUR').id),
                ('company_id', '=', company_eu.id),
                ('min_qty', '=', 10),
                ('price', '=', 1.5),
                ('sequence', '=', 3),
                ('delay', '=', 2),
            ]))
        self.assertTrue(
            self.env['product.supplierinfo'].search([
                ('product_code', '=', 'OPPCD'),
                ('product_name', '=', 'other partner product name'),
                ('product_tmpl_id', '=', product.id),
                ('currency_id', '=', self.env.ref('base.USD').id),
                ('company_id', '=', company_us.id),
                ('min_qty', '=', 2),
                ('price', '=', 3),
                ('sequence', '=', 2),
                ('delay', '=', 4),
            ]))
        self.assertTrue(
            self.env['product.supplierinfo'].search([
                ('product_code', '=', 'OPPCD'),
                ('product_name', '=', 'other partner product name'),
                ('product_tmpl_id', '=', product.id),
                ('currency_id', '=', self.env.ref('base.USD').id),
                ('company_id', '=', company_us.id),
                ('min_qty', '=', 15),
                ('price', '=', 2),
                ('sequence', '=', 2),
                ('delay', '=', 4),
            ]))
