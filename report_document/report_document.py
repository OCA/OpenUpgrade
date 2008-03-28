##############################################################################
#
# Copyright (c) 2004-2006 TINY SPRL. (http://tiny.be) All Rights Reserved.
#
# $Id: sale.py 1005 2005-07-25 08:41:42Z nicoe $
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

from osv import fields,osv
import time


class report_document_user(osv.osv):
    _name = "report.document.user"
    _description = "Files details by Users"
    _auto = False
    _columns = {
        'name': fields.date('Month', readonly=True),
        'user_id':fields.integer('Owner', readonly=True),
        'user':fields.char('User',size=64,readonly=True),
        'file_title': fields.char('File Name',size=64,readonly=True),
        'directory': fields.char('Directory',size=64,readonly=True),
        'create_date': fields.datetime('Date Created', readonly=True),
        'file_size': fields.integer('File Size', readonly=True),
        'nbr':fields.integer('# of Files', readonly=True),
     }
    def init(self, cr):
         cr.execute("""
            create or replace view report_document_user as (
                 select
                     min(f.id) as id,
                     f.user_id as user_id,
                     u.name as user,
                     count(*) as nbr,
                     substring(f.create_date for 7)||'-'||'01' as name,
                     d.name as directory,
                     f.create_date as create_date,
                     f.file_size as file_size,
                     min(f.title) as file_title
                 from ir_attachment f
                     inner join document_directory d on (f.parent_id=d.id and d.name<>'')
                     inner join res_users u on (f.user_id=u.id)
                 group by d.name,f.parent_id,d.type,f.create_date,f.user_id,f.file_size,u.name
             )
         """)
report_document_user()
