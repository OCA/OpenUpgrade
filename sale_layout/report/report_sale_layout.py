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
import time
import pooler
from report import report_sxw

parents = {
    'tr':1,
    'li':1,
    'story': 0,
    'section': 0
    }

class sale_order_1(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(sale_order_1, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'sale_order_lines': self.sale_order_lines,
            'repeat_In':self.repeat_In,
        })
        self.context = context

    def repeat_In(self, lst, name, nodes_parent=False,td=False,width=[],value=[],type=[]):
        self._node.data = ''
        node = self._find_parent(self._node, nodes_parent or parents)
        ns = node.nextSibling

        value=['tax_id','product_uom_qty','product_uom','price_unit','discount','price_subtotal']
        type=['string','string','string','string','string','string']
        width=[66,46,24,66,55,54]
        td=6

        tableFlag=0

        if not lst:
            lst.append(1)
        for ns in node.childNodes :
            if tableFlag==1:
                break
            if ns and ns.nodeName!='#text' and ns.tagName=='blockTable' and td :
                tableFlag=1

                width_str = ns._attrs['colWidths'].nodeValue
                ns.removeAttribute('colWidths')
                total_td = td * len(value)

                if not width:
                    for v in value:
                        width.append(30)
                for v in range(len(value)):
                    width_str +=',%d'%width[v]

                ns.setAttribute('colWidths',width_str)

                child_list =  ns.childNodes

                for child in child_list:
                    if child.nodeName=='tr':
                        lc = child.childNodes[1]
#                        for t in range(td):
                        i=0
                        for v in value:
                            t2="[[%s['layout_type']=='text' and removeParentNode('tr')]]"%(name)
                            t1= "[[ %s['%s'] ]]"%(name,v)
                            t3="[[ %s['layout_type']=='subtotal' and ( setTag('para','para',{'fontName':'Helvetica-Bold'})) ]]"%name
                            newnode = lc.cloneNode(1)

                            newnode.childNodes[1].lastChild.data = t1 + t2 +t3
                            child.appendChild(newnode)
                            newnode=False
                            i+=1

        return super(sale_order_1,self).repeatIn(lst, name, nodes_parent=False)

    def sale_order_lines(self,sale_order):
        result =[]
        sub_total={}
        info=[]
        order_lines=[]
        res={}
        list_in_seq={}
        ids = self.pool.get('sale.order.line').search(self.cr, self.uid, [('order_id', '=', sale_order.id)])
        ids.sort()
        for id in range(0,len(ids)):
            info = self.pool.get('sale.order.line').browse(self.cr, self.uid,ids[id], self.context.copy())
            list_in_seq[info]=info.sequence
        i=1
        j=0
        final=sorted(list_in_seq.items(), lambda x, y: cmp(x[1], y[1]))
        order_lines=[x[0] for x in final]
        sum_flag={}
        sum_flag[j]=-1
        for entry in order_lines:
            res={}

            if entry.layout_type=='article':
                res['tax_id']=', '.join(map(lambda x: x.name, entry.tax_id)) or ''
                res['name']=entry.name
                res['product_uom_qty']="%.2f"%(entry.product_uos and entry.product_uos_qty or entry.product_uom_qty  or 0.00)
                res['product_uom']=entry.product_uos and entry.product_uos.name or entry.product_uom.name 
                res['price_unit']="%.2f"%(entry.price_unit or 0.00)
                res['discount']="%.2f"%(entry.discount and entry.discount or 0.00)
                res['price_subtotal']="%.2f"%(entry.price_subtotal)
                sub_total[i]=entry.price_subtotal
                i=i+1
                res['note']=entry.notes
                res['currency']=sale_order.pricelist_id.currency_id.name
                res['layout_type']=entry.layout_type
                
            else:

                res['product_uom_qty']=''
                res['price_unit']=''
                res['discount']=''
                res['tax_id']=''
                res['layout_type']=entry.layout_type
                res['note']=entry.notes
                res['product_uom']=''

                if entry.layout_type=='subtotal':
                    res['name']=entry.name
                    sum=0
                    sum_id=0
                    if sum_flag[j]==-1:
                        temp=1
                    else:
                        temp=sum_flag[j]

                    for sum_id in range(temp,len(sub_total)+1):
                        sum+=sub_total[sum_id]
                    sum_flag[j+1]= sum_id +1

                    j=j+1
                    res['price_subtotal']="%.2f"%(sum)
                    res['currency']=sale_order.pricelist_id.currency_id.name
                    res['quantity']=''
                    res['price_unit']=''
                    res['discount']=''
                    res['tax_id']=''
                    res['product_uom']=''
                elif entry.layout_type=='title':
                    res['name']=entry.name
                    res['price_subtotal']=''
                    res['currency']=''
                elif entry.layout_type=='text':
                    res['name']=entry.name
                    res['price_subtotal']=''
                    res['currency']=''
                elif entry.layout_type=='line':
                    res['product_uom_qty']='____________'
                    res['price_unit']='______________'
                    res['discount']='____________'
                    res['tax_id']='_________________'
                    res['product_uom']='_____'
                    res['name']='________________________________________'
                    res['price_subtotal']='_______________________'
                    res['currency']='_______'
                elif entry.layout_type=='break':
                    res['layout_type']=entry.layout_type
                    res['name']=entry.name
                    res['price_subtotal']=''
                    res['currency']=''
                else:
                    res['name']=entry.name
                    res['price_subtotal']=''
                    res['currency']=sale_order.pricelist_id.currency_id.name

            result.append(res)
        return result
report_sxw.report_sxw('report.sale.order.layout', 'sale.order', 'addons/sale_layout/report/report_sale_layout.rml', parser=sale_order_1)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

