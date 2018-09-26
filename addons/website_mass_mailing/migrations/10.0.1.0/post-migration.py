# -*- coding: utf-8 -*-
# © 2017 Therp BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    cr = env.cr
    # using  sql to map values of popup_content and popup_redirect_url  
    # these two fields have not changed model but have changed module
    # they where previously defined in mass_mail now in website_mass_mail
    sql = "update mail_mass_mailing_list set popup_content = %s" % (
        openupgrade.get_legacy_name('popup_content')
    )
    cr.execute(sql)
    sql = "update mail_mass_mailing_list set popup_redirect_url = %s" % (
        openupgrade.get_legacy_name('popup_redirect_url')
    )
    cr.execute(sql)
