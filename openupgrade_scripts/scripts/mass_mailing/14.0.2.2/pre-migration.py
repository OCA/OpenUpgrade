# Copyright 2021 ForgeFlow S.L.  <https://www.forgeflow.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade

_xmlid_renames = [
    (
        "mass_mailing.view_mail_mass_mailing_contact_form",
        "mass_mailing.mailing_contact_view_form",
    ),
    (
        "mass_mailing.view_mail_mass_mailing_contact_graph",
        "mass_mailing.mailing_contact_view_graph",
    ),
    (
        "mass_mailing.view_mail_mass_mailing_contact_kanban",
        "mass_mailing.mailing_contact_view_kanban",
    ),
    (
        "mass_mailing.view_mail_mass_mailing_contact_pivot",
        "mass_mailing.mailing_contact_view_pivot",
    ),
    (
        "mass_mailing.view_mail_mass_mailing_contact_search",
        "mass_mailing.mailing_contact_view_search",
    ),
    (
        "mass_mailing.view_mail_mass_mailing_contact_tree",
        "mass_mailing.mailing_contact_view_tree",
    ),
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_xmlids(env.cr, _xmlid_renames)
