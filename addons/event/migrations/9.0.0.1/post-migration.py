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


def insert_confirmation_email(cr):
    # Insert and save at least email registration templates although relations
    # and models are changed in version 9.0
    cr.execute("""
        INSERT INTO event_mail
        (event_id, interval_nbr, interval_unit, interval_type, template_id)
        SELECT id, 1, 'now', 'after_sub', %(template_id)s
        FROM event_event
        WHERE %(template_id)s IS NOT NULL
    """ % {'template_id': openupgrade.get_legacy_name('email_registration_id')}
    )


@openupgrade.migrate()
def migrate(cr, version):
    update_seats_availability(cr)
    insert_confirmation_email(cr)
