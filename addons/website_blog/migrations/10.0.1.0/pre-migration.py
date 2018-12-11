# -*- coding: utf-8 -*-
# Copyright 2018 Tecnativa - David Vidal
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


_field_renames_website_blog_mgmt = [
    ('blog.post', 'blog_post', 'website_publication_date', 'published_date'),
]


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    cr = env.cr
    if openupgrade.column_exists(cr, 'blog_post', 'website_publication_date'):
        # If website_blog_mgmt was installed
        openupgrade.rename_fields(env, _field_renames_website_blog_mgmt)
