# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution	
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from osv import fields,osv
import time
import pooler

class use_control_time(osv.osv):
    _name = "use.control.time"
    _order = "date desc"
    _rec_name = 'date'
    _columns = {
        'user_id': fields.many2one('res.users', 'User', ondelete='set null'),
        'date': fields.datetime('Date'),
        'duration': fields.float('Duration'),
        'uploaded': fields.boolean('Uploaded')
    }
    def write(self, cr, uid, ids, data, context={}):
        return True
    def unlink(self, cr, uid, ids, context={}):
        return True
use_control_time()

class use_control_time_month_user(osv.osv):
    _name = "use.control.time.month.user"
    _description = "Time of Use per Month"
    _auto = False
    _rec_name = 'date'
    _columns = {
        'user_id': fields.many2one('res.users', 'User', ondelete='set null'),
        'date': fields.date('Month'),
        'duration': fields.float('Duration'),
    }
    def init(self, cr):
        cr.execute("""
            create or replace view use_control_time_month_user as (
                select
                    min(id) as id,
                    user_id,
                    to_char(date, 'YYYY-MM-01') as date,
                    sum(duration) as duration
                from
                    use_control_time
                group by
                    user_id,
                    to_char(date, 'YYYY-MM-01')
            )""")
use_control_time_month_user()


class use_control_time_month(osv.osv):
    _name = "use.control.time.month"
    _description = "Time of Use per Month"
    _auto = False
    _rec_name = 'date'
    _columns = {
        'date': fields.date('Month'),
        'duration': fields.float('Duration'),
    }
    def init(self, cr):
        cr.execute("""
            create or replace view use_control_time_month as (
                select
                    min(id) as id,
                    to_char(date, 'YYYY-MM-01') as date,
                    sum(duration) as duration
                from
                    use_control_time
                group by
                    to_char(date, 'YYYY-MM-01')
            )""")
use_control_time_month()

class use_control_db_block(osv.osv):
    _name = "use.control.db.block"
    _description = "Containt the blocking message"

    _columns = {
        'name': fields.text('Block message', required=True),
    }

    def create(self, cr, uid, values, context=None):
        self.unlink(cr, uid, self.search(cr, uid, [], context), context)
        return super(use_control_db_block, self).create(cr, uid, values, context)

    def copy(self, cr, uid, id, context):
        return id

use_control_db_block()

