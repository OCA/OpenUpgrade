# -*- coding: utf-8 -*-
# © 2017 Therp BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    cr = env.cr
    # not using sql to restore account_type but map values
    # these two fields have not changed model but have changed model
    # they where previously defined in mass_mail now in website_mass_mail
    # we restore them in their place on the same table
    sql = "update mail_mass_mailing_list set popup_content = %s" % (
        openupgrade.get_legacy_name('popup_content')
    )
    cr.execute(sql)
    sql = "update mail_mass_mailing_list set popup_redirect_url = %s" % (
        openupgrade.get_legacy_name('popup_redirect_url')
    )
