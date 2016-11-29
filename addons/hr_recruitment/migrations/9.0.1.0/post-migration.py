# -*- coding: utf-8 -*-
# © 2016 Tecnativa <vicent.cubells@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade
from openerp import fields
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
            new_date += timedelta(days=applicant[2])
        openupgrade.logged_query(
            cr,
            """
            UPDATE hr_applicant SET availability = %s
            WHERE id = %s
            """ % (new_date, applicant[0]))


@openupgrade.migrate()
def migrate(cr, version):
    openupgrade.load_data(cr, 'survey',
                          'migrations/9.0.1.0/noupdate_changes.xml')
    openupgrade.map_values(
        cr,
        openupgrade.get_legacy_name('priority'),
        'priority',
        [('4', '3'), ('3', '1'), ('2', '0'), ('1', '0')],
        table='hr_applicant', write='sql')
    update_applicant_availability(cr)
