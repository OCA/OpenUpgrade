# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2006 TINY SPRL. (http://tiny.be) All Rights Reserved.
#                    Fabien Pinckaers <fp@tiny.Be>
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
#
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

