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


def _assign_newsletter_xml_id(env):
    """If you come from v12 or before, there was a mailing list called 'Newsletter' as
    data. This list dissapeared in v13, so on OpenUpgrade v13, we removed the associated
    XML-ID for preserving it.
    As now in v14 it's being introduced again (although with other XML-ID), the unique
    name contraint makes the migration to crash, so we need to detect if a mailing list
    with such name exists, and give it in advance the required XML-ID for avoiding the
    duplicity.
    """
    env.cr.execute("SELECT id FROM mailing_list WHERE name='Newsletter'")
    row = env.cr.fetchone()
    if row:
        openupgrade.logged_query(
            env.cr,
            """INSERT INTO ir_model_data
            (module, name, res_id, model, noupdate)
            VALUES
            ('mass_mailing', 'mailing_list_data', %s, 'mailing.list', True)
            """,
            (row[0],),
        )


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_xmlids(env.cr, _xmlid_renames)
    _assign_newsletter_xml_id(env)
