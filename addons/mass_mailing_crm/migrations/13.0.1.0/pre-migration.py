# Copyright 2020 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


_xmlid_renames = [
    ('mass_mailing_crm.mail_mass_mailing_view_form',
     'mass_mailing_crm.mailing_mailing_view_form'),
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_xmlids(env.cr, _xmlid_renames)
