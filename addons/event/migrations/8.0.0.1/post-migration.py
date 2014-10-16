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
from openerp.openupgrade.openupgrade import (migrate, convert_field_to_html,
                                             get_legacy_name)
from openerp.openupgrade.openupgrade_80 import set_message_last_post


@migrate()
def migrate(cr, version):
    pool = pooler.get_pool(cr.dbname)
    set_message_last_post(
        cr, SUPERUSER_ID, pool, ['event.event', 'event.registration'])
    convert_field_to_html(cr, 'event_event', get_legacy_name('note'),
                          'description')
