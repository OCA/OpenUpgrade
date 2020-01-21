# -*- coding: utf-8 -*-
# © 2016 Tecnativa <vicent.cubells@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade
from openerp import api, fields, SUPERUSER_ID
from datetime import timedelta


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
    env = api.Environment(cr, SUPERUSER_ID, {})
    uso = env['utm.source']
    cr.execute("SELECT id, name FROM hr_recruitment_source")
    for (recruit_src_id, recruit_src_name) in cr.fetchall():
        utm_source = uso.create({
            'name': recruit_src_name,
            })
        cr.execute(
            'UPDATE hr_applicant SET source_id=%s WHERE ' +
            openupgrade.get_legacy_name('source_id') +
            '=%s',
            (utm_source.id, recruit_src_id))


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
