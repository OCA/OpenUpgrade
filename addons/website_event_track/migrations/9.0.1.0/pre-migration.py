# -*- coding: utf-8 -*-
# Copyright 2017 Tecnativa - Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade

column_renames = {
    'event_event': [
        ('timezone_of_event', None),
    ],
    'event_track': [
        ('stage_id', None),
    ]
}


@openupgrade.migrate()
def migrate(cr, version):
    openupgrade.rename_columns(cr, column_renames)
    openupgrade.float_to_integer(cr, 'event_sponsor', 'sequence')
