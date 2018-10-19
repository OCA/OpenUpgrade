# -*- coding: utf-8 -*-
# © 2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import api, SUPERUSER_ID
from openerp.tools import html_sanitize
from openupgradelib import openupgrade


def migrate_phonecalls(env):
    """Convert each phonecall to a logged activity. If you have crm_phonecall
    OCA module in your environment, this is not done, and the module is marked
    instead to be installed, as the module replaces exactly this feature and
    you save this time.
    """
    module = env['ir.module.module'].search([('name', '=', 'crm_phonecall')])
    if module:
        if module.state == 'uninstalled':
            module.state = 'to install'
        return
    activity = env.ref('crm.crm_activity_data_call')
    env.cr.execute(
        'select id, opportunity_id, partner_id, '
        'coalesce(user_id, write_uid, create_uid) as user_id, '
        'name, description, partner_phone, partner_mobile '
        'from crm_phonecall '
        "where active and state not in ('cancel')")
    env = env(context={
        'mail_post_autofollow': False,
        'mail_create_nosubscribe': True,
    })
    for phonecall in env.cr.dictfetchall():
        record = env['res.users'].browse(phonecall['user_id'])
        if phonecall['opportunity_id']:  # pragma: no cover
            record = env['crm.lead'].browse(phonecall['opportunity_id'])
        if phonecall['partner_id']:
            record = env['res.partner'].browse(phonecall['partner_id'])
        body = (
            '<div>%(description)s</div><div>%(partner_phone)s</div>'
            '<div>%(partner_mobile)s</div><div>Phone call %(id)s</div>'
        ) % {
            key: html_sanitize(value)
            for key, value in phonecall.iteritems()
        }
        record.message_post(
            body=body, subject=phonecall['name'] or 'Phone call',
            subtype_id=activity.subtype_id.id)


@openupgrade.migrate()
def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    migrate_phonecalls(env)
    openupgrade.load_data(
        cr, 'crm', 'migrations/9.0.1.0/noupdate_changes.xml',
    )
