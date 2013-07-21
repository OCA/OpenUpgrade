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
        "WHERE body_html IS NULL AND body_html != '' AND body_text IS NOT NULL" % {
            'body_text': openupgrade.get_legacy_name('body_text'),
            })
    for row in cr.fetchall():
        body = plaintext2html(row[1])
        cr.execute("UPDATE mail_message SET body_html = %s WHERE id = %s", body, row[0])

@openupgrade.migrate()
def migrate(cr, version):
    convert_mail_bodies(cr)

