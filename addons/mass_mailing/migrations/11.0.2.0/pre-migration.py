# -*- coding: utf-8 -*-
# Copyright 2018 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade

COLUMN_RENAMES = {
    'mail_mass_mailing_contact': [
        ('list_id', None),
    ],
}


def switch_mailing_model_list(env):
    """Doing a mass mailing on lists now points to the 'mail.mass_mailing.list'
    model instead of the contact one.
    """
    openupgrade.logged_query(
        env.cr, """
        UPDATE mail_mass_mailing
        SET mailing_model = 'mail.mass_mailing.list'
        WHERE mailing_model = 'mail.mass_mailing.contact'""",
    )


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_columns(env.cr, COLUMN_RENAMES)
    switch_mailing_model_list(env)
