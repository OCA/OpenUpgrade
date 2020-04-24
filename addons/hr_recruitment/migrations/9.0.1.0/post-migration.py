# -*- coding: utf-8 -*-
# Copyright 2016 Tecnativa <vicent.cubells@tecnativa.com>
# Copyright 2020 Akretion - Alexis de Lattre
# Copyright 2020 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade
from openerp import fields
from datetime import timedelta
from psycopg2 import sql


def update_applicant_availability(cr):
    cr.execute(
        """
            SELECT id, create_date, %s
            FROM hr_applicant
        """ % (openupgrade.get_legacy_name('availability'),)
    )
    for applicant in cr.fetchall():
        new_date = fields.Date.from_string(applicant[1])
        if applicant[2]:
            new_date += timedelta(days=int(applicant[2]))
        new_date = fields.Date.to_string(new_date)
        openupgrade.logged_query(
            cr,
            """
            UPDATE hr_applicant SET availability = %s
            WHERE id = %s
            """, (new_date, applicant[0]))


def migrate_applicant_source(cr):
    column = openupgrade.get_legacy_name('hr_recruitment_source')
    openupgrade.logged_query(cr, sql.SQL(
        "ALTER TABLE utm_source ADD {} INT4").format(sql.Identifier(column)))
    openupgrade.logged_query(
        cr, sql.SQL("""
        INSERT INTO utm_source
        (create_uid, create_date, write_uid, write_date, name, {})
        SELECT create_uid, create_date, write_uid, write_date, name, id
        FROM hr_recruitment_source
        """).format(sql.Identifier(column)),
    )
    openupgrade.logged_query(
        cr, sql.SQL("""
        UPDATE hr_applicant ha SET source_id = us.id
        FROM utm_source us WHERE us.{} = ha.{}
        """).format(
            sql.Identifier(column),
            sql.Identifier(openupgrade.get_legacy_name('source_id'))),
    )


@openupgrade.migrate()
def migrate(cr, version):
    openupgrade.load_data(cr, 'hr_recruitment',
                          'migrations/9.0.1.0/noupdate_changes.xml')
    openupgrade.map_values(
        cr,
        openupgrade.get_legacy_name('priority'),
        'priority',
        [('1', '0'), ('2', '0'), ('3', '1'), ('4', '3')],
        table='hr_applicant', write='sql')
    update_applicant_availability(cr)
    migrate_applicant_source(cr)
