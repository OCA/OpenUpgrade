# -*- coding: utf-8 -*-
# Copyright 2017 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade
import json


def convert_blog_post_cover(env):
    """Switch opacity value for posts, as now in v10 the meaning of that
    property is for an upper solid frame, not for the image itself.
    """
    post_obj = env['blog.post'].with_context(active_test=False)
    for post in post_obj.search([('cover_properties', '!=', False)]):
        props = json.loads(post.cover_properties)
        if 'opacity' in props:
            props['opacity'] = str(abs(1 - float(props['opacity'])))
        post.cover_properties = json.dumps(props)


@openupgrade.migrate()
def migrate(env, version):
    convert_blog_post_cover(env)
