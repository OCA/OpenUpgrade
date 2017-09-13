# -*- coding: utf-8 -*-
# @ 2014-Today: Odoo Community Association, Microcom
# © 2015 Eficent Business and IT Consulting Services S.L. -
# Jordi Ballester Alomar
# © 2015 Serpent Consulting Services Pvt. Ltd. - Sudhir Arya
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


def map_priority(cr):
    openupgrade.map_values(
        cr,
        openupgrade.get_legacy_name('priority'),
        'priority',
        [('2', '1')],
        table='project_task', write='sql')


def map_template_state(cr):
    openupgrade.map_values(
        cr,
        openupgrade.get_legacy_name('state'),
        'state',
        [('template', 'draft')],
        table='project_project', write='sql')


def copy_user_id(cr):
    openupgrade.logged_query(cr, """
        UPDATE project_project p
        SET user_id = a.user_id
        FROM account_analytic_account a
        WHERE a.id = p.analytic_account_id
        """)


@openupgrade.migrate()
def migrate(cr, version):
    map_priority(cr)
    map_template_state(cr)
    copy_user_id(cr)
    openupgrade.convert_field_to_html(
        cr, 'project_task', openupgrade.get_legacy_name('description'),
        'description'
    )
    openupgrade.load_data(
        cr, 'project', 'migrations/9.0.1.1/noupdate_changes.xml',
    )
