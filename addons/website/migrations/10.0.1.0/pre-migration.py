# -*- coding: utf-8 -*-
# © 2017 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    # rename groups' xmlids
    openupgrade.rename_xmlids(env.cr, [
        ('base.group_website_designer', 'website.group_website_designer'),
        ('base.group_website_publisher', 'website.group_website_publisher'),
    ])
    # clean out group assignments for qweb views
    env.cr.execute(
        "delete from ir_ui_view_group_rel "
        "where view_id in (select id from ir_ui_view where type='qweb')"
    )
