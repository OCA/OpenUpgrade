# Copyright 2018 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests import common


class TestWebsite(common.TransactionCase):
    def test_fill_website_page(self):
        view = self.env.ref('website.view_test_website_page')
        self.assertTrue(view.page_ids)

    def test_preserve_existing_website_pages(self):
        view = self.env.ref('website.homepage')
        self.assertEquals(len(view.page_ids), 1)

    def test_link_websites_with_pages(self):
        view = self.env.ref('website.view_test_website_page')
        website = self.env.ref('website.default_website')
        self.assertEquals(view.page_ids.website_ids, website)

    def test_add_website_homepages(self):
        website = self.env.ref('website.default_website')
        homepage = self.env.ref('website.homepage').page_ids
        self.assertEquals(website.homepage_id, homepage)
