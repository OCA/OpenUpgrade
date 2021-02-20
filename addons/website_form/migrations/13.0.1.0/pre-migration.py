# Copyright 2021 Bloopark - Bishal Pun
# Copyright 2021 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade

_xmlid_renames = [
    ('website_crm.contactus_thanks', 'website_form.contactus_thanks'),
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_xmlids(env.cr, _xmlid_renames)
    openupgrade.logged_query(
        env.cr, """
        UPDATE ir_ui_view
        SET key='website_form.contactus_thanks'
        WHERE key='website_crm.contactus_thanks'"""
    )
