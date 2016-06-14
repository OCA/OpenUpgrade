# -*- coding: utf-8 -*-
# © 2016 Savoir-faire Linux (<http://www.savoirfairelinux.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from psycopg2.extensions import AsIs
from openerp.openupgrade import openupgrade

from openerp import SUPERUSER_ID
from openerp.api import Environment


_logger = logging.getLogger(__name__)


@openupgrade.migrate()
def migrate(cr, version):
    if not version:
        return
    env = Environment(cr, SUPERUSER_ID, {})
    convert_action_mail_server_email(env)


def convert_action_mail_server_email(env):
    def convert_body(body):
        return body.replace("[[", "${").replace("]]", "}")

    def convert_subject(subject):
        subject = subject.strip()
        if subject.startswith('object.'):
            subject = "${%s}" % subject
        return subject

    actions = env['ir.actions.server'].search([
        ('state', '=', 'email'),
        ('template_id', '=', False),
    ])

    _logger.info(
        'Transfering existing ir.actions.server emails to '
        'email templates.'
    )

    for action in actions:

        subject_column = openupgrade.get_legacy_name('subject')

        env.cr.execute(
            """
            SELECT email, %s, message
            FROM ir_act_server
            WHERE id = %s
            """, (AsIs(subject_column), action.id, ))

        (email, subject, message) = env.cr.fetchone()

        email_template = env['email.template'].create({
            'name': action.name,
            'model_id': action.model_id.id,
            'email_from': convert_subject(email),
            'subject': convert_body(subject),
            'body_html': convert_body(message),
        })

        action.template_id = email_template.id
