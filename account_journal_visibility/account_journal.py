# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution	
#    Copyright (C) 2004-2008 Tiny SPRL (<http://tiny.be>). All Rights Reserved
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
import tools
import ir
import pooler


class account_journal(osv.osv):
    _inherit ='account.journal'
    _columns = {
          'group_ids': fields.many2many('res.groups', 'account_journal_groups_rel', 'journal_id', 'groups_id', 'Groups'),
    }
    def search(self, cr, user, args, offset=0, limit=None, order=None, context=None):
            result = []
            list = []
            res = {}
            ids = super(account_journal,self).search(cr, user, args, offset, limit, order, context)
            group = pooler.get_pool(cr.dbname).get('res.users').browse(cr, user, [user])[0].groups_id
            for journal in self.browse(cr, user, ids):
                if journal.group_ids:
                    for g in group:
                        if g in journal.group_ids:
                            result.append(journal.id)
                else:
                    if not len(journal.group_ids):
                        result.append(journal.id)
            return result
account_journal()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

