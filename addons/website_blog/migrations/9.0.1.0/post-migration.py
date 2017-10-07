# -*- coding: utf-8 -*-
# Copyright 2017 Tecnativa - Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


def convert_blog_post_cover(env):
    """Put default value for posts without cover image and put URL of the
    cover in field cover_properties for using it for the rest."""
    post_obj = env['blog.post']
    # Without cover image
    env.cr.execute(
        "SELECT id FROM blog_post WHERE {} IS NULL".format(
            openupgrade.get_legacy_name('background_image')
        )
    )
    posts = post_obj.browse([x[0] for x in env.cr.fetchall()])
    posts.write({'cover_properties': post_obj._defaults['cover_properties']})
    # With cover image
    env.cr.execute(
        "SELECT id, {0} FROM blog_post WHERE {0} IS NOT NULL".format(
            openupgrade.get_legacy_name('background_image')
        )
    )
    for row in env.cr.fetchall():
        post = post_obj.browse(row[0])
        post.cover_properties = (
            '{{"background-image": "url({})",'
            ' "opacity": "1",'
            ' "background-color": "oe_none",'
            ' "resize_class": "cover cover_full"}}'
        ).format(row[1])


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    openupgrade.load_data(
        env.cr, 'website_blog', 'migrations/9.0.1.0/noupdate_changes.xml',
    )
    convert_blog_post_cover(env)
