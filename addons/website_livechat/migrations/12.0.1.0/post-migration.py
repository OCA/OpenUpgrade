# Copyright 2019 Eficent <http://www.eficent.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade, openupgrade_120


@openupgrade.migrate()
def migrate(env, version):
    openupgrade_120.convert_field_bootstrap_3to4(
        env, 'im_livechat.channel', 'website_description',
    )
