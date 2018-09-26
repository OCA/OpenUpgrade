# -*- coding: utf-8 -*-
# © 2017 Therp BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    cr = env.cr
    openupgrade.copy_columns(
        cr, {
            'mail_mass_mailing_list': [
                ('popup_content', None, None),
                ('popup_redirect_url', None, None)
            ],
        })
