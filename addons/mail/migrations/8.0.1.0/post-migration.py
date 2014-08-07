# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2010-2014 Elico Corp. All Rights Reserved.
#    Augustin Cisterne-Kaas <augustin.cisterne-kaas@elico-corp.com>
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
from openerp.openupgrade import openupgrade, openupgrade_80
from openerp import pooler, SUPERUSER_ID


def move_fields(cr, pool):
    execute = openupgrade.logged_query
    queries = [
        """
        UPDATE res_partner
        SET notify_email = 'always'
        WHERE notify_email != 'none'
        """
    ]
    for sql in queries:
        execute(cr, sql)


@openupgrade.migrate()
def migrate(cr, version):
    pool = pooler.get_pool(cr.dbname)
    move_fields(cr, pool)
    openupgrade.move_field_m2o(
        cr, pool,
        'mail.mail', 'reply_to', 'mail_message_id',
        'mail.message', 'reply_to')
    openupgrade.move_field_m2o(
        cr, pool,
        'mail.mail', 'mail_server_id', 'mail_message_id',
        'mail.message', 'mail_server_id')
    openupgrade_80.set_message_last_post(
        cr, SUPERUSER_ID, pool, ['res.partner', 'mail.group']
    )
