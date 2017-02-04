# coding: utf-8
from openerp.tests import common


class TestAccount(common.SavepointCase):
    def test_blog_post_cover(self):
        post = self.env['blog.post'].search([
            ('name', '=', 'The Future of Emails'),
        ])
        self.assertTrue(post.cover_properties)
        self.assertIn('/web/image', post.cover_properties)
