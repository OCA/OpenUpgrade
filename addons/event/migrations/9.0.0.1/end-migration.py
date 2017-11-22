# -*- coding: utf-8 -*-
# Copyright 2017 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


def create_multiple_attendees_registration_records(env):
    """On v8, we have one event.registration record = one or several attendees
    according nb_register field.

    But on v9 we have one event.registration record = one attended, so here
    we duplicate the existing record for representing the same number of
    records than attendees.

    Done in end-migration for having all the possible fields in
    event.registration already loaded.
    """
    # Pre-create a column for storing original reference
    column_name = openupgrade.get_legacy_name('original_registration_id')
    table = 'event_registration'
    if not openupgrade.column_exists(env.cr, table, column_name):
        openupgrade.logged_query(
            env.cr, """
            ALTER TABLE %s 
            ADD COLUMN %s INTEGER""" % (table, column_name)
        )
    env.cr.execute(
        'SELECT id, nb_register FROM %s WHERE nb_register > 1' % table
    )
    data = dict(env.cr.fetchall())
    for registration in env['event.registration'].browse(data.keys()):
        new_registrations = env['event.registration']
        for i in range(data[registration.id] - 1):
            new_registrations += registration.copy()
        openupgrade.logged_query(
            env.cr, """
            UPDATE %s
            SET %s = %%s
            WHERE id IN %%s""" % (table, column_name),
            (registration.id, tuple(new_registrations.ids))
        )


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    create_multiple_attendees_registration_records(env)
