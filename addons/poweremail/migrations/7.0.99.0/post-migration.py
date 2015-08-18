# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2014 Therp BV (<http://therp.nl>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
import logging
from openerp import pooler, SUPERUSER_ID
from openerp.openupgrade import openupgrade
from openerp.tools.mail import plaintext2html

logger = logging.getLogger('OpenUpgrade')


def migrate_templates(cr, pool):
    """
    Migrate poweremail templates to OpenERP email templates.
    """
    cr.execute(
        """
        SELECT
            id,
            def_body_text,   -- -> convert to html if necessary
            def_to,          -- -> email_to
            def_body_html,   -- -> body_html, if set
            file_name,       -- -> report_name (translatable)
            object_name,     -- -> model_id, o2m on ir.model
            report_template, -- -> report_template
            def_cc,          -- -> email_cc
            def_subject,     -- -> subject (translatable)
            lang,            -- -> lang, placeholder
            name,            -- -> name
            use_sign,            -- -> user_signature (boolean)
            enforce_from_account, -- -> o2m on poweremail_core_accounts entry
            ref_ir_act_window, -- -> ref_ir_act_window (update context etc)
            ref_ir_value      -- -> ref_ir_value
        FROM poweremail_templates
        """)
    for row in cr.fetchall():
        vals = {
            'email_to': row[2] or False,
            'report_name': row[4] or False,
            'model_id': row[5] or False,
            'report_template': row[6] or False,
            'email_cc': row[7] or False,
            'subject': row[8] or False,
            'lang': row[9] or False,
            'name': row[10] or False,
            'user_signature': row[11] or False,
            'ref_ir_act_window': row[13] or False,
            'ref_ir_value': row[14] or False,
            'body_html': row[3] if row[3] else plaintext2html(row[1] or '')
            }

        if row[11]:
            cr.execute(
                "SELECT name, email_id FROM poweremail_core_accounts "
                "WHERE id = %s", (row[11],))
            vals['email_from'] = "%s <%s>" % cr.fetchone()

        template_id = pool['email.template'].create(
            cr, SUPERUSER_ID, vals)

        # Update translations
        for old_name, name in [
                ('def_body_html', 'body_html'),
                ('def_subject', 'subject'),
                ('file_name', 'report_name')]:
            openupgrade.logged_query(
                cr,
                """
                UPDATE ir_translation
                SET name = %s, res_id = %s
                WHERE name = %s AND type = 'model' AND res_id = %s
                    AND value IS NOT NULL AND value != ''
                """, ('email.template,' + name, template_id,
                      'poweremail.templates,' + old_name, row[0]))

        # Convert text body translations to html
        cr.execute(
            """
            SELECT id, value FROM ir_translation
            WHERE name = 'poweremail.templates,def_body_text'
                AND res_id = %s AND value IS NOT NULL AND value != ''
            """, (row[0],))
        for trans in cr.fetchall():
            pool['ir.translation'].write(
                cr, SUPERUSER_ID, [trans[0]],
                {
                    'value': plaintext2html(trans[1]),
                    'name': 'email.template,body_html',
                    })

        # adapt window action
        if row[13]:
            # Can't use ORM write because this triggers a check on
            # the action's source model which may not be instantiated
            # at this point
            openupgrade.logged_query(
                cr,
                """
                UPDATE ir_act_window
                SET res_model = 'mail.compose.message',
                    context = %s, view_id = NULL
                WHERE id = %s""",
                (
                    "{'default_composition_mode': 'mass_mail', "
                    "'default_template_id' : %d, "
                    "'default_use_template': True}" % template_id, row[13]))

        # if this template has an xmlid, its owner will be happy about this
        cr.execute(
            "UPDATE ir_model_data SET model='email.template', res_id=%s "
            "WHERE model='poweremail.templates' and res_id=%s",
            (template_id, row[0]))


def migrate_emails(cr, pool):
    """
    Migrate mails from poweremail mailbox table to mail.mail
    """
    folder2state = {
        'inbox': 'received',
        'drafts': 'cancel',
        'outbox': 'outgoing',
        'trash': 'cancel',
        'followup': 'received',
        'sent': 'sent',
        }

    cr.execute(
        """
        SELECT
            id,
            pem_from,
            pem_to,
            pem_cc,
            pem_subject,
            pem_body_text,
            pem_body_html,
            folder, --> state
            date_mail --> date (both are datetime)
        FROM poweremail_mailbox
        """)

    for row in cr.fetchall():
        vals = {
            'type': 'email',
            'auto_delete': False,
            'state': folder2state[row[7]],
            'email_from': row[1] or False,
            'email_to': row[2] or False,
            'email_cc': row[3] or False,
            'subject': row[4] or False,
            'date': row[8],
            'body_html': row[6] if row[6] else plaintext2html(row[5] or ''),
            }

        # Migrate attachments from m2m table
        cr.execute(
            """
            SELECT att_id FROM mail_attachments_rel
            WHERE mail_id = %s""", (row[0],))
        vals['attachment_ids'] = [(6, 0, [att[0] for att in cr.fetchall()])]

        # Create mail
        mail_id = pool['mail.mail'].create(cr, SUPERUSER_ID, vals)

        # Update attachment references
        cr.execute(
            """
            UPDATE ir_attachment
            SET res_model = 'mail.mail', res_id = %s
            WHERE res_model = 'poweremail.mailbox' AND res_id = %s""",
            (mail_id, row[0]))


@openupgrade.migrate()
def migrate(cr, version):
    pool = pooler.get_pool(cr.dbname)
    migrate_templates(cr, pool)
    migrate_emails(cr, pool)
