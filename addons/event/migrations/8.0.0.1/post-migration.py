# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 HBEE (http://www.hbee.eu)
#    @author: Paulius Sladkevičius <paulius@hbee.eu>
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

from openerp import pooler, SUPERUSER_ID
from openerp.openupgrade import openupgrade, openupgrade_80
from openerp.tools.mail import plaintext2html


def convert_field_to_html(cr, table, legacy_field_name, new_field_name):
    """
    Convert text field value to HTML value
    """
    cr.execute(
        "SELECT id, %(field)s FROM %(table)s "
        "WHERE %(field)s IS NOT NULL OR %(field)s != '' " % {
            'field': legacy_field_name,
            'table': table,
    })
    for row in cr.fetchall():
        html = plaintext2html(row[1])
        cr.execute(
            "UPDATE %(table)s SET %(field)s = %s WHERE id = %s" % {
                'field': new_field_name,
                'table': table,
            }, (html, row[0])
        )


@openupgrade.migrate()
def migrate(cr, version):
    pool = pooler.get_pool(cr.dbname)
    openupgrade_80.set_message_last_post(
        cr, SUPERUSER_ID, pool, ['event.event', 'event.registration'])
    convert_field_to_html(cr, 'event_event', 'note', 'description')
