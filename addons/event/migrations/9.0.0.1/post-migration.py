# -*- coding: utf-8 -*-
# © 2016 Tecnativa - Vicent Cubells <vicent.cubells@tecnativa.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


def update_seats_availability(cr):
    cr.execute("""
        UPDATE event_event
        SET seats_availability = 'limited'
        WHERE seats_max IS NOT NULL
    """)
    cr.execute("""
        UPDATE event_event
        SET seats_availability = 'unlimited'
        WHERE seats_max IS NULL OR seats_max = 0
    """)


@openupgrade.migrate()
def migrate(cr, version):
    update_seats_availability(cr)
