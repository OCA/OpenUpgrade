# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2013 Credativ Ltd (<http://credativ.co.uk>)
#                          (C) 2013 Therp BV (<http://therp.nl>).
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

from openerp.openupgrade import openupgrade
from openerp.tools.mail import plaintext2html


def convert_mail_bodies(cr):
    """
    Convert plain bodies to sanitized html.
    """
    cr.execute(
        "SELECT id, %(body_text)s FROM email_template "
        "WHERE (body_html IS NULL OR body_html = '') "
        "AND %(body_text)s != '' AND %(body_text)s IS NOT NULL" % {
            'body_text': openupgrade.get_legacy_name('body_text'),
            })
    for row in cr.fetchall():
        body = plaintext2html(row[1])
        cr.execute("UPDATE email_template SET body_html = %s WHERE id = %s",
                   (body, row[0]))

    # Migrate translations of text templates
    cr.execute(
        """
        SELECT tr_text.res_id, tr_text.lang, tr_text.value,
               (SELECT COUNT(*) FROM ir_translation tr_count
                     WHERE tr_count.type = 'model'
                        AND tr_count.name = 'email.template,body_html'
                        AND tr_count.res_id = tr_text.res_id
                        AND tr_count.lang = tr_text.lang) as count
        FROM ir_translation tr_text
        WHERE type = 'model'
              AND name = 'email.template,body_text'
              AND NOT EXISTS (
                  SELECT tr_html.id
                  FROM ir_translation tr_html
                  WHERE tr_html.type = 'model'
                        AND tr_html.name = 'email.template,body_html'
                        AND tr_text.res_id = tr_html.res_id
                        AND tr_text.lang = tr_html.lang
                        AND (tr_html.value is not NULL OR tr_html.value != '')
                  )
        """)

    for (res_id, lang, value, count) in cr.fetchall():
        body = plaintext2html(value)
        if count:
            cr.execute(
                """
                UPDATE ir_translation
                SET value = %s
                WHERE type = 'model'
                      AND name = 'email.template,body_html'
                      AND res_id = %s
                      AND lang = %s
                """, (body, res_id, lang))
        else:
            cr.execute(
                """
                INSERT INTO ir_translation
                (lang, name, type, res_id, value, src)
                VALUES (
                    %s, 'email.template,body_html', 'model', %s, %s,
                    (SELECT body_html
                    FROM email_template et
                    WHERE et.id = %s))
                """, (lang, res_id, body, res_id))


@openupgrade.migrate()
def migrate(cr, version):
    convert_mail_bodies(cr)
