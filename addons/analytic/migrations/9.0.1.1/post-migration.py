# -*- coding: utf-8 -*-
# © 2015 Eficent Business and IT Consulting Services S.L. -
# Jordi Ballester Alomar
# © 2015 Serpent Consulting Services Pvt. Ltd. - Sudhir Arya
# © 2016 Therp BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade
from openerp import SUPERUSER_ID, api


def set_partner_id(cr):
    openupgrade.logged_query(cr, """
    UPDATE account_analytic_line a
    SET partner_id = aa.partner_id
    FROM account_analytic_account aa
    WHERE a.account_id = aa.id AND a.partner_id IS NULL
    """)


def create_tags(cr):
    """Create tags for former state and type fields."""
    env = api.Environment(cr, SUPERUSER_ID, {})
    cr.execute(
        "select 'state', %(state)s, array_agg(id) "
        'from account_analytic_account '
        'where %(state)s is not null group by %(state)s '
        "union select 'type', %(type)s, array_agg(id) "
        'from account_analytic_account '
        'where %(type)s is not null group by %(type)s ' % {
            'type': openupgrade.get_legacy_name('type'),
            'state': openupgrade.get_legacy_name('state'),
        }
    )
    for prefix, name, ids in cr.fetchall():
        tag = env['account.analytic.tag'].create({
            'name': '%s - %s' % (prefix, name)
        })
        env['account.analytic.account'].browse(ids).write({
            'tag_ids': [(4, tag.id)],
        })


def set_analytic_account_visibility(cr):
    """Hide view analytic accounts with previous state considered as closed.

    It also hides analytic accounts of type=view. If we want to restore the
    visibility of these accounts, we have to perform:
        UPDATE account_analytic_account SET account_type='normal'
        WHERE %s = 'view' AND %s NOT IN ('cancelled', 'close') % (
            openupgrade.get_legacy_name('type'),
            openupgrade.get_legacy_name('state'),
        )
    """
    openupgrade.map_values(
        cr, openupgrade.get_legacy_name('state'), 'account_type', [
            ('cancelled', 'closed'),
            ('close', 'closed'),
        ], table='account_analytic_account',
    )
    openupgrade.logged_query(
        cr,
        """UPDATE account_analytic_account
        SET account_type='closed'
        WHERE %s = 'view'""" % openupgrade.get_legacy_name('type')
    )


@openupgrade.migrate()
def migrate(cr, version):
    set_partner_id(cr)
    create_tags(cr)
    set_analytic_account_visibility(cr)
