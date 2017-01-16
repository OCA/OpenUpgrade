# -*- coding: utf-8 -*-
# © 2016 Tecnativa - Vicent Cubells <vicent.cubells@tecnativa.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


column_renames = {
    'event_event': [
        ('email_confirmation_id', None),
        ('email_registration_id', None),
    ],
    'event_type': [
        ('default_email_event', None),
        ('default_email_registration', None),
    ],
    'res_partner': [
        ('speaker', None),
    ],
}


@openupgrade.migrate()
def migrate(cr, version):
    openupgrade.rename_columns(cr, column_renames)
