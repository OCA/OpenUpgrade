# -*- coding: utf-8 -*-
# Copyright 2017 Tecnativa - Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


def convert_blog_post_cover(env):
    """Upload image as attachment and change cover_properties for using it."""
    attachment_obj = env['ir.attachment']
    base_url = env['ir.config_parameter'].get_param('web.base.url')
    for post in env['blog.post'].search([]):
        env.cr.execute(
            """SELECT {} FROM blog_post WHERE id=%s""".format(
                openupgrade.get_legacy_name('background_image')
            ), (post.id, )
        )
        row = env.cr.fetchone()
        attachment = attachment_obj.create({
            'name': 'blog_post_{}_cover'.format(post.id),
            'type': 'binary',
            'db_datas': row[0],
            'res_model': 'ir.ui.view',
            'public': True,
        })
        post.cover_properties = (
            '{{"background-image": "url({}/web/image/{})",'
            ' "opacity": "1",'
            ' "background-color": "oe_none",'
            ' "resize_class": "cover cover_full"}}'
        ).format(base_url, attachment.id)


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    openupgrade.load_data(
        env.cr, 'website_blog', 'migrations/9.0.1.0/noupdate_changes.xml',
    )
    convert_blog_post_cover(env)
