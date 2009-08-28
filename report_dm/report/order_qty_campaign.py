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

import datetime

from report.interface import report_rml
from report.interface import toxml 

import pooler
from tools.translate import _


def lengthmonth(year, month):
    if month == 2 and ((year % 4 == 0) and ((year % 100 != 0) or (year % 400 == 0))):
        return 29
    return [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month]

def segment_create_xml(cr, uid, s_id, som, eom, origin):
    # Computing the qty by segment
    cond = " where segment_id = %s and s.date_order >= '%s' and s.date_order < '%s' "%(s_id, som.strftime('%Y-%m-%d'), eom.strftime('%Y-%m-%d'))
    if origin : 
        cond += " and origin = '%s' " %origin
    sql = "select count(id) as qty, s.date_order from sale_order s %s group by s.date_order"%cond
    cr.execute(sql)        
    
    # Sum by day
    month = {}
    res = cr.dictfetchall()
    for r in res:
        day = int(r['date_order'][-2:])
        month[day] = month.get(day, 0.0) + r['qty']
    
    xml = '''
    <time-element date="%s">
        <amount>%.2f</amount>
    </time-element>
    '''
    time_xml = ([xml % (day, amount) for day, amount in month.iteritems()])
    
    pool = pooler.get_pool(cr.dbname)
        
    segment = pool.get('dm.campaign.proposition.segment').browse(cr,uid,s_id).name
    # Computing the xml
    xml = '''
    <segment id="%d" name="%s">
    %s
    </segment>
    ''' % (s_id, toxml(segment), '\n'.join(time_xml))
    return xml

class report_custom(report_rml):

    def get_month_name(self, cr, uid, month):
        _months = {1:_("January"), 2:_("February"), 3:_("March"), 4:_("April"), 5:_("May"), 6:_("June"), 7:_("July"), 8:_("August"), 9:_("September"), 10:_("October"), 11:_("November"), 12:_("December")}
        return _months[month]
    
    def get_weekday_name(self, cr, uid, weekday):
        _weekdays = {1:_('Mon'), 2:_('Tue'), 3:_('Wed'), 4:_('Thu'), 5:_('Fri'), 6:_('Sat'), 7:_('Sun')}
        return _weekdays[weekday]

    def create_xml(self, cr, uid, ids, data, context):

        camp_id = data['form']['camp_id']
        pool = pooler.get_pool(cr.dbname)
        
        origin=[(False,)]        
        if data['form']['origin_partner'] :
            cr.execute("select distinct origin from sale_order")
            origin = cr.fetchall()
            origin.sort()
        
        segment_id = pool.get('dm.campaign.proposition.segment').search(cr,uid,[('campaign_id','=',camp_id)])
        
        
        sql = "select count(s.id),segment_id ,to_char(s.date_order, 'YYYY-MM-DD') as date from sale_order s where segment_id in %s group by to_char(s.date_order, 'YYYY-MM-DD') , segment_id "%str(tuple(segment_id))
        
        cr.execute(sql)
        res = cr.fetchall()
        
        # Computing the dates (start of month: som, and end of month: eom)
        som = datetime.date(data['form']['year'], data['form']['month'], 1)
        eom = som + datetime.timedelta(lengthmonth(som.year, som.month))
        date_xml = ['<date month_year="%s  -  %d" />' % (self.get_month_name(cr, uid, som.month), som.year), '<days>']
        date_xml += ['<day number="%d" name="%s" weekday="%d" />' % (x, self.get_weekday_name(cr, uid, som.replace(day=x).weekday()+1), som.replace(day=x).weekday()+1) for x in range(1, lengthmonth(som.year, som.month)+1)]
        date_xml.append('</days>')
        date_xml.append('<cols>3.75cm%s,1.25cm</cols>\n' % (',.75cm' * lengthmonth(som.year, som.month)))
        

        story_xml = ''
        for i in range(len(origin)) :
            segment_xml=''
            for s_id in segment_id:
                segment_xml += segment_create_xml(cr, uid, s_id, som, eom, origin[i][0])
            story_xml += "<story s_id='%d' name='%s'> %s </story>"%(i+1,origin[i][0],segment_xml)

            
        # Computing the xml
        xml = '''<?xml version="1.0" encoding="UTF-8" ?>
        <report>%s
        %s
        </report>
        ''' % (date_xml , story_xml )

        return xml

report_custom('report.dm.order.quantity.campaign', 'dm.campaign', '', 'addons/report_dm/report/order_qty_campaign.xsl')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

