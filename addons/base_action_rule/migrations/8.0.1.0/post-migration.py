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

from openerp.openupgrade import openupgrade


@openupgrade.migrate()
def migrate(cr, version):
    openupgrade.logged_query(
        cr,
        "UPDATE base_action_rule SET kind = 'on_create_or_write', "
        "trg_date_range = null, trg_date_range_type = null "
        "where trg_date_id = null"
    )
    openupgrade.logged_query(
        cr,
        "UPDATE base_action_rule SET kind = 'on_time', filter_pre_id = null "
        "where trg_date_id != null"
    )
