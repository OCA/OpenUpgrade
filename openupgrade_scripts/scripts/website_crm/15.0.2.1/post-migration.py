# Copyright 2023 Tecnativa - Pilar Vargas
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


def migrate_website_crm_views(env):
    """Update the arch_db field by replacing the occurrences of "mail.mail" with "crm.lead"
    in "website.contactus". This is done to adapt the functionality in Odoo v15 where the
    default action is used to send an email and to ensure that the configuration is not
    lost for the that the configuration is not lost to create an opportunity that in previous
    versions was configured by default by a was configured by default by a replacement in
    the form view."""
    for website in env["website"].search([]):
        website_contactus_view = website.with_context(website_id=website.id).viewref(
            "website.contactus"
        )
        website_contactus_arch_db = website_contactus_view.arch_db
        if 'data-model_name="mail.mail"' in website_contactus_arch_db:
            new_arch = website_contactus_arch_db.replace(
                'data-model_name="mail.mail"', 'data-model_name="crm.lead"'
            )
            website_contactus_view.with_context(website_id=website.id).arch = new_arch


@openupgrade.migrate()
def migrate(env, version):
    migrate_website_crm_views(env)
