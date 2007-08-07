##############################################################################
#
# Copyright (c) 2005 TINY SPRL. (http://tiny.be) All Rights Reserved.
#
# $Id$
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


import pooler
import time
from report import report_sxw


class auction_total_rml(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(auction_total_rml, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'sum_taxes':self.sum_taxes,
            'sold_item':self.sold_item,
            'sum_buyer':self.sum_buyer()

        })

    def sum_taxes(self, auction_id):
        return len(self.pool.get('auction.lots').search(self.cr,self.uid,([('auction_id','=',auction_id)])))
    def sold_item(self, auction_id):
        return len(self.pool.get('auction.lots').search(self.cr,self.uid,([('state','in',['unsold','draft'])])))
#    def sum_buyer(self, auction_id):
#        return len(self.pool.get('auction.lots').search(self.cr,self.uid,([('auction_id','=',auction_id)],[('ach_uid','>=',[])])))


report_sxw.report_sxw('report.auction.total.rml', 'auction.lots', 'addons/auction/report/auction_total.rml',parser=auction_total_rml)

