# Copyright 2019 Eficent <http://www.eficent.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade, openupgrade_120


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(
        env.cr, 'website_blog', 'migrations/12.0.1.0/noupdate_changes.xml')
    openupgrade_120.convert_field_bootstrap_3to4(
        env, 'blog.post', 'content',
    )
