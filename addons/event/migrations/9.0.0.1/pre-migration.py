# -*- coding: utf-8 -*-
# Copyright 2016 Tecnativa - Vicent Cubells <vicent.cubells@tecnativa.com>
# Copyright 2017 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


field_renames = [
    # renamings with oldname attribute - They also need the rest of operations
    ('event.event', 'event_event', 'type', 'event_type_id'),
]

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


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    cr = env.cr
    openupgrade.rename_fields(env, field_renames)
    openupgrade.rename_columns(cr, column_renames)
