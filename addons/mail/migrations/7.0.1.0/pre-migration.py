# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2013 Therp BV (<http://therp.nl>).
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

column_renames = {
    'mail_message': [
        # Existing fields to ignore
        ('subtype', None),
        ('headers', None),
        ('original', None),
        # Existing fields to transform
        ('body_text', None),
        ('body_html', None),
        ('partner_id', None),
        ('user_id', None),
        # Existing fields to move to mail.mail
        ('email_to', None),
        ('email_cc', None),
        ('email_bcc', None),
        ('mail_server_id', None),
        ('reply_to', None),
        ('references', None),
        ('state', None),
        ('auto_delete', None),
        ]}


def precreate_author_id(cr):
    """
    Precreate the 'author_id' column so as to prevent an error
    when its default function gets called during the upgrade
    process.
    """
    cr.execute('ALTER TABLE "mail_message" ADD COLUMN "author_id" int4')


@openupgrade.migrate()
def migrate(cr, version):
    openupgrade.rename_columns(cr, column_renames)
    precreate_author_id(cr)
