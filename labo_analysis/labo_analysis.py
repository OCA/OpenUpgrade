#
# Copyright (c) 2005-2006 TINY SPRL. (http://tiny.be) All Rights Reserved.
#
# $Id: product_expiry.py 4304 2006-10-25 09:54:51Z ged $
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

import datetime
from osv import fields,osv
import pooler
import netsvc
import time
from xml import dom
from xml.parsers import expat
class labo_analysis_view(osv.osv):
    _name = "labo.analysis.view"
    _columns = {
        'name': fields.char('Analysis View', size=64, required=True),
        'columns_id': fields.one2many('analysis.column', 'view_id', 'Columns')
}
    _order = "name"
labo_analysis_view()

class labo_analysis_type(osv.osv):
    _name = "labo.analysis.type"
    _description = "labo_analysis_type object"
    _rec_name="code"

#    def create( self, cr, uid, vals, context=None):
#        type_id = super(labo_analysis_type, self).create(cr, uid, vals,context=context)
#        analyse = self.browse(cr, uid, type_id)
#        xml1=""
#        xml2=""
#        xml3=""
#        xml4=""
#        xml5=""
#        xml6=""
#        xml_curr=""
#        xml_curr = '''<?xml version="1.0"?>\n
#        <form string="Analysis Request">
#            <notebook>
#                <page string="General">
#                    <field name="name" select="1" />
#                    <field name="type_id" domain="[('id','=',%d)]" context="{'id':(%d,'tutu')}"/>
#                    <field name="begining_date" />
#                    <field name="date_reception" />
#                    <field name="date_planned" />
#                    <field name="date_closed" />
#                    <field name="cond_reception"/>
#                    <field name="ref_client"  on_change="onchange_pricelist(ref_client)" select="1" />
#                    <field name="pricelist_id" />
#                    <field name="user_id" select="1" />
#                    <field name="invoice_ids" />
#                    <field name="urgent" />
#                    <field name="accredit" />
#                    <field name="desc_1" colspan="4" nolabel="1"/>
#                    <newline/>
#
#                    <field name="desc_2" colspan="4" nolabel="1"/>
#                    <field name="desc_3" colspan="4" nolabel="1"/>
#                    <field name="state" colspan="4" nolabel="1"/>
#                     <group col="4" colspan="4">
#                        <button name="button_draft" string="Set to Draft" states="cancel" type="object"/>
#                        <button name="button_cancel" string="Cancel" states="running" type="object"/>
#                        <button name="button_running" string="Running" states="draft" type="object"/>
#                        <button name="button_closed" string="Closed" states="draft,running" type="object"/>
#                    </group>
#                    </page>
#                <page string="Cases">
#                    <field name="case_id" nolabel="1"/>
#                </page>
#                <page string="Send to">
#                    <field name="send_to_ids" nolabel="1"/>
#                </page>
#            </notebook>
#        </form>
#            '''
#        xml = '''<?xml version="1.0"?>\n
#        <form string="Analysis Request">
#            <notebook>
#                <page string="General">
#                    <field name="name" select="1" />
#                    <field name="type_id" domain="[('id','=',%d)]" context="{'id':(%d,'tutu')}"/>
#                    <field name="begining_date" />
#                    <field name="date_reception" />
#                    <field name="date_planned" />
#                    <field name="date_closed" />
#                    <field name="cond_reception"/>
#                    <field name="ref_client"  on_change="onchange_pricelist(ref_client)" select="1" />
#                    <field name="pricelist_id" />
#                    <field name="user_id" select="1" />
#                    <field name="invoice_ids" />
#                    <field name="urgent" />
#                    <field name="accredit" />
#                    <field name="desc_1" colspan="4" nolabel="1"/>
#                    <newline/>
#
#                    <field name="desc_2" colspan="4" nolabel="1"/>
#                    <field name="desc_3" colspan="4" nolabel="1"/>
#                    <field name="state" colspan="4" nolabel="1"/>
#                     <group col="4" colspan="4">
#                        <button name="button_draft" string="Set to Draft" states="cancel" type="object"/>
#                        <button name="button_cancel" string="Cancel" states="running" type="object"/>
#                        <button name="button_running" string="Running" states="draft" type="object"/>
#                        <button name="button_closed" string="Closed" states="draft,running" type="object"/>
#                    </group>
#                    </page>
#                <page string="Cases">
#                    <field name="case_id" nolabel="1"/>
#                </page>
#                <page string="Send to">
#                    <field name="send_to_ids" context="{'request_id': active_id}" nolabel="1"/>
#                </page>
#                <page string="Analysis Lines" >
#                    <field name="sample_ids"  mode="tree,form" editable="top" nolabel="1">
#                    '''%(type_id, type_id)
#        """TREE"""
#        xml+='<tree string="Analysis samples"  colspan="4">'
#        xml3+='<form string="Analysis Samples" > <notebook> <page string="Information">'
#        xml4+='<tree string="Analysis Samples" >'
#        fields=[]
#        widths={}
#        for field in analyse.view_id.columns_id:
#            fields.append(field.field)
#            attrs = []
#            if field.field in widths:
#                attrs.append('width="'+str(widths[field.field])+'"')
#            xml += '''<field name="%s" %s sequence = "%s" required="%s" select="%d" />\n''' % (field.field,' '.join(attrs), field.sequence, (field.required or 0), 2 )
#            xml4 += '''<field name="%s" %s sequence = "%s" required="%s" select="%d" readonly="%s" />\n''' % (field.field,' '.join(attrs), field.sequence, (field.required or 0), 2,(field.readonly or 0))
#        xml4 += '''</tree> '''
#        xml += '''</tree> '''
#        """FORM"""
#        xml+="""<form string="Analysis Request" colspan="4" >
#                <notebook><page string="lines">
#        """
#
#        fields=[]
#        widths={}
#        for field in analyse.view_id.columns_id:
#            fields.append(field.field)
#            attrs = []
#        #    if field.field == 'send_to_ids':
#        #        xml1+="""
#        #        <page string="Send to" >
#        #        <field name="send_to_ids"/>
#        #        </page>
#        #        """
#        #        xml5+="""
#        #        <page string="Send to" >
#        #        <field name="send_to_ids"/>
#        #        </page>
#        #        """
#            if field.field == 'history_ids':
#                xml2+="""
#                <page string="History" >
#                <field name="history_ids"/>
#                </page>
#                """
#                xml6+="""
#                <page string="History" >
#                <field name="history_ids"/>
#                </page>
#                """
#            else:
#        #        attrs.append('required="0" select="1"')
#                if field.field in widths:
#                    attrs.append('width="'+str(widths[field.field])+'"')
#                xml += '''<field name="%s" %s sequence = "%s" required="%s" select="%d" readonly="%s" />\n''' % (field.field,' '.join(attrs), field.sequence, (field.required or 0), 2, (field.readonly or 0))
#        #    xml += """<field name="%s" %s />\n """ % (field.field,' '.join(attrs))
#                if field.field=='progenus_number':
#                    xml3 += '''<field name="progenus_number" sequence = "%s" required="%s" select="1" readonly="%s" />\n''' % ( field.sequence, (field.required or 0), (field.readonly or 0))
#                else:
#                    xml3 += '''<field name="%s" %s sequence = "%s" required="%s" select="%d" readonly="%s" />\n''' % (field.field,' '.join(attrs), field.sequence, (field.required or 0), 2, (field.readonly or 0) )
#        #    xml3 += """<field name="%s" %s />\n """ % (field.field,' '.join(attrs))
#        xml+="""</page>"""
#        if xml1 or xml5:
#            xml+=xml1
#            xml3+=xml5
##        if xml2 or xml6:
##            xml+=xml2
##            xml3+=xml6
#        xml3+='''</page>'''
#        if xml2 or xml6:
#            xml+=xml2
#            xml3+=xml6
#        xml3+='''</notebook></form>'''
#        xml+="""</notebook>"""
#        xml += '''</form> '''
#
#        xml+='''</field></page>    </notebook>    </form>'''
#        xml_tree = '''<?xml version="1.0"?>
#                <tree string="Analysis Request">
#                    <field name="name" />
#                    <field name="begining_date" />
#                    <field name="cond_reception"/>
#                    <field name="type_id" domain="[('id','=',%d)]" />
#                    <field name="user_id"/>
#                    <field name="date_closed" />
#                    <field name="date_planned" />
#                    <field name="ref_client" />
#                    <field name="pricelist_id" />
#                </tree>'''% type_id
#
#        view_mode = 'form,tree'
#        print "XML3",xml_tree
#        print "curr",xml_curr
#        print "xml",xml
#        mod_obj = pooler.get_pool(cr.dbname).get('ir.model.data')
#        model_data_id = mod_obj._get_id(cr, uid, 'labo_analysis','menu_progenus')
#        model = mod_obj.browse(cr, uid, model_data_id)
#        parent_menu_id = model.res_id
#        icon = 'STOCK_JUSTIFY_FILL'
#        menu_id=self.pool.get('ir.ui.menu').create(cr, uid, {
#            'name': vals['code'],
#            'parent_id': parent_menu_id,
#            'icon': icon
#        })
#        views=[]
#        vies=[]
#        vies1=[]
#        view_obj=pooler.get_pool(cr.dbname).get('ir.ui.view')
######View for relates
#        model_data_view_id= mod_obj._get_id(cr, uid, 'labo_analysis','menu_curr_year')
#        model_view = mod_obj.browse(cr, uid, model_data_view_id)
#        parent_menu_view_id = model_view.res_id
#        icon = 'STOCK_JUSTIFY_FILL'
#        menu_view_id=self.pool.get('ir.ui.menu').create(cr, uid, {
#            'name': vals['code'],
#            'parent_id': parent_menu_view_id,
#            'icon': icon
#        })
#        view_ui_create_curr=view_obj.create(cr,uid,{
#        'name': 'Requests'+"  "+vals['code'],
#        'model': 'labo.analysis.request',
#        'arch': xml_tree,
#        })
#
#        act_win_t_curr=self.pool.get('ir.actions.act_window.view').create(cr,uid,{
#        'view_id': view_ui_create_curr,
#        'view_mode':'tree',
#        })
#
#        vies1.append(act_win_t_curr)
#        view_ui_create_curr_x=view_obj.create(cr,uid,{
#        'name': 'Requests'+vals['code'],
#        'model': 'labo.analysis.request',
#        'arch': xml_curr
#        })
#
#        act_win_curr_x=self.pool.get('ir.actions.act_window.view').create(cr,uid,{
#        'view_id': view_ui_create_curr_x,
#        'view_mode':'form',
#        })
#
#        vies1.append(act_win_curr_x)
#
#        action_id_curr_x = self.pool.get('ir.actions.act_window').create(cr,uid, {
#            'name': 'Requests',
#            'res_model': 'labo.analysis.request',
#            'view_type': 'form',
#            'view_mode': view_mode,
#            'view_ids': [(6,0,vies1)],
#            'domain':str([('type_id','=', type_id)])
#        #    'domain':str([('type_id','=', type_id),('name','ilike',time.strftime('%Y'))])
#
#        })
#
#        self.pool.get('ir.values').create(cr, uid, {
#            'name': 'Open Requests',
#            'key2': 'tree_but_open',
#            'model': 'ir.ui.menu',
#            'res_id': menu_view_id,
#            'value': 'ir.actions.act_window,%d'%action_id_curr_x,
#            'object': True
#        })
#
####end create view
#        print "vals",vals['code']
#        print "XMLLL",xml_tree
#        print "FIN XML"
#####BEGIN SAMPLES
#        model_data_id_samples = mod_obj._get_id(cr, uid, 'labo_analysis','menu_progenus_samples')
#        model_samples = mod_obj.browse(cr, uid, model_data_id_samples)
#        parent_menu_id_samples = model_samples.res_id
#        menu_id_samples=self.pool.get('ir.ui.menu').create(cr, uid, {
#            'name': 'Samples'+'  '+vals['code'],
#            'parent_id': parent_menu_id_samples,
#            'icon': icon
#        })
#        view_ui_create_t=view_obj.create(cr,uid,{
#        'name': 'labo_sample_'+vals['code']+'_tree',
#        'model': 'labo.sample',
#        'type' : 'tree',
#        'arch': xml4,
#        })
#
#        act_win_t=self.pool.get('ir.actions.act_window.view').create(cr,uid,{
#        'view_id': view_ui_create_t,
#        'view_mode':'tree',
#        })
#
#        vies.append(act_win_t)
#        view_ui_create_x=view_obj.create(cr,uid,{
#        'name': 'labo_sample_'+vals['code']+'_form',
#        'model': 'labo.sample',
#        'type' : 'form',
#        'arch': xml3
#        })
#
#        act_win_x=self.pool.get('ir.actions.act_window.view').create(cr,uid,{
#        'view_id': view_ui_create_x,
#        'view_mode':'form',
#        })
#
#        vies.append(act_win_x)
#
#        action_id_x = self.pool.get('ir.actions.act_window').create(cr,uid, {
#            'name': 'Samples',
#            'res_model': 'labo.sample',
#            'view_type': 'form',
#            'view_mode': view_mode,
#            'view_ids': [(6,0,vies)],
#            'domain':str([('sample_id.type_id','=', type_id)]),
#            'context':{'is_view':vals['code']},
#        })
#        print "action_s",action_id_x
#
#        self.pool.get('ir.values').create(cr, uid, {
#            'name': 'Open1 samples',
#            'key2': 'tree_but_open',
#            'model': 'ir.ui.menu',
#            'res_id': menu_id_samples,
#            'value': 'ir.actions.act_window,%d'%action_id_x,
#            'object': True
#        })
#
#####END
#        view_ui_create2=view_obj.create(cr,uid,{
#        'name': 'Analysis tree'+vals['code'],
#        'model': 'labo.analysis.request',
#        'arch': xml_tree
#        })
#
#        view_ui_create=view_obj.create(cr,uid,{
#        'name': 'Analysis form'+vals['code'],
#        'model': 'labo.analysis.request',
#        'arch': xml
#        })
#
#        act_win2=self.pool.get('ir.actions.act_window.view').create(cr,uid,{
#        'sequence':1,
#        'view_id': view_ui_create2,
#        'view_mode':'tree',
#        })
#
#        views.append(act_win2)
#        act_win=self.pool.get('ir.actions.act_window.view').create(cr,uid,{
#        'view_id': view_ui_create,
#        'view_mode':'form',
#        })
#
#        views.append(act_win)
##        views.append(act_win_curr_x)
#        action_id = self.pool.get('ir.actions.act_window').create(cr,uid, {
#            'name': 'Analysis Request',
#            'res_model': 'labo.analysis.request',
#            'view_type': 'form',
#            'view_mode': view_mode,
#            'view_ids': [(6,0,views)],
#       #     'context':"{'isarticleprod':True,'sample_id': active_id,'type_id':" + str(type_id) + "}",
#            'domain':str([('type_id','=', type_id)]),
#        })
#
##        ir_sequence_type_id = self.pool.get('ir.sequence.type').create(cr,uid,{
##                'name':'Labo analysis request ' + str(vals['code']),
##                'code':'labo.analysis.request.' + str(vals['code']),
##
##        })
##        ir_sequence_id = self.pool.get('ir.sequence').create(cr,uid,{
##                'name':'Labo analysis request ' + str(vals['code']),
##                'code':'labo.analysis.request.' + str(vals['code']),
##                'prefix':'%(year)s/',
##                'padding':4,
##        })
#        self.pool.get('ir.values').create(cr, uid, {
#            'name': 'Open Analysis',
#            'key2': 'tree_but_open',
#            'model': 'ir.ui.menu',
#            'res_id': menu_id,
#            'value': 'ir.actions.act_window,%d'%action_id,
#            'object': True
#        })
##        # create act
##        action_id_x_bis = self.pool.get('ir.actions.act_window').create(cr,uid, {
##            'name': 'Requests',
##            'res_model': 'labo.sample',
##            'src_model':'labo.analysis.request',
##            'view_type': 'form',
##        #    'view_mode': view_mode,
##    #        'view_ids': [(6,0,vies)],
##            'view_id': act_win_t,
##        #    'domain':str([('sample_id','=', active_id)]),    })
#        return type_id
#
    _columns = {
        'request_id':fields.one2many('labo.analysis.request','type_id','Demandes'),
        'view_id': fields.many2one('labo.analysis.view','view',   ondelete='cascade'),
        'code': fields.char('Code', size=64,  select=True),
        'product_id' : fields.many2one('product.product', 'Product',  ondelete='cascade',change_default=True),
    }
    _defaults = {
                }
labo_analysis_type()


class labo_analysis_request(osv.osv):
    _name = "labo.analysis.request"
    _description = "Labo Request"
    _order="name desc"

    def name_get(self, cr, uid, ids, context={}):
        if not len(ids):
            return []
        res = [(r.id, (r.type_id and r.type_id.code  or '')+'/' +(r.name or '') ) for r in self.browse(cr, uid, ids, context)]
        return res


    def button_draft(self,cr,uid,ids,*a):
        return super(labo_analysis_request, self).write(cr,uid,ids, {'state':'draft'})
    def button_closed(self,cr,uid,ids,*a):
        return super(labo_analysis_request, self).write(cr,uid,ids, {'state':'closed','date_closed': time.strftime('%Y-%m-%d')})
    def button_running(self,cr,uid,ids,*a):
        return super(labo_analysis_request, self).write(cr,uid,ids, {'state':'running'})
    def button_cancel(self,cr,uid,ids,*a):
        return super(labo_analysis_request, self).write(cr,uid,ids, {'state':'cancel'})

    def _get_sequence(self, cr, uid, context):

        type_id = context.get('type_id', 0)
        if type_id=='EMPDOG' or type_id=='EMPDOG_2' or type_id=='EMPCHE':
            obj_type = self.pool.get('labo.analysis.type').browse(cr,uid,type_id)
            return self.pool.get('ir.sequence').get(cr, uid, 'labo.analysis.request.' + str(obj_type.code))
        return self.pool.get('ir.sequence').get(cr, uid, 'labo.analysis.request')

    def _default_type(self, cr, uid, context={}):
        if 'type_id' in context and context['type_id']:
            id_type = self.pool.get('labo.analysis.type').search(cr,uid,[('code','ilike',context['type_id'])])
            return id_type and id_type[0]


    _columns = {
        'case_id':fields.many2many('crm.case','cas_request_rel','cas_id','request_id','Case'),# readonly=True),
        'accredit':fields.boolean('Accredit', select=2),
        'urgent':fields.boolean('Urgent',select=2),
        'user_id': fields.many2one('res.users', 'User',  ondelete='cascade', select=2),
        'cond_reception':fields.char('Conditions reception',size=64, select=2),
        'date_closed': fields.date('Closing date', select=2),
        'date_planned':fields.date('Planned date', select=2),
        'date_reception':fields.date('Reception date', select=2),
        'date_awe':fields.date('Awe date', select=2),
        'name': fields.char('Name', size=64, required=True, select=True),
        'ref_client':fields.many2one('res.partner','Client',  ondelete='cascade', select=1),
        'sample_ids':fields.one2many('labo.sample','sample_id','Samples'),
        'pricelist_id':fields.many2one('product.pricelist', 'Pricelist',  ondelete='cascade', select=2),
#        'lot_ids1':fields.many2many('stock.reactives','lot_request_rel','lot_id','request_id', 'Lot'),
        'begining_date':fields.date('Date of sending', select=2),
        'type_id':fields.many2one('labo.analysis.type', 'Type',  ondelete='cascade', required=True),
        'invoice_ids': fields.many2one('account.invoice', 'Labo Invoice',  ondelete='cascade', select=2),
#        'user_id': fields.many2one('res.users', 'User',  ondelete='cascade', select=2),
#        'test_way':fields.char('Way of testing', size=64),
        'desc_1':fields.text('Description 1'),
        'desc_2':fields.char('Description 2', size=64, select=2),
        'desc_3':fields.char('Description 3', size=64, select=2),
    #    'file_res': fields.binary('File Results'),
#        'file_setup':fields.one2many('analysis.setup', 'req_id','Set up'),
        'state': fields.selection([('draft','Draft'), ('running','Running'),('closed','Close'),('cancel','Cancel')], 'State', readonly=True, select=1),
        'send_to_ids':fields.many2many('res.partner','partner_request_rel','send_id','request_id','Send to'),
            }
    _defaults = {
        'name': lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid, 'labo.analysis.request'),
        'date_reception': lambda *a: time.strftime('%Y-%m-%d'),
        'state':lambda *a:'draft',
        'accredit': lambda *a: True,
        'type_id': _default_type
        }

#    def create(self, cr, uid, vals, context=None, check=True):
##        tmp_sample_lines = vals['sample_ids']
#        if  vals.has_key("sample_ids"):
#            tmp_sample_lines = vals['sample_ids']
#            vals.update({'sample_ids':[]})
#            samp_id = super(labo_analysis_request, self).create(cr, uid, vals, context)
#            for line in tmp_sample_lines:
#                line[2].update({'sample_id':samp_id})
#            vals.update({'sample_ids':tmp_sample_lines})
#            super(labo_analysis_request, self).write(cr, uid,[samp_id], vals, context)
#        else:
#            samp_id = super(labo_analysis_request, self).create(cr, uid, vals, context)
#        return samp_id


 #   def write(self, cr, uid, ids, vals, context=None, check=True, update_check=True):

 #       if not context:
 #           context={}
 #       if 'sample_ids' not in vals:
 #           vals.update({'sample_ids':[]})
 #           for line in vals['sample_ids']:
 #               line[2].update({'sample_id':ids[0]})
##            return  super(labo_analysis_request, self).write(cr, uid,ids, vals, context)
 #       else :
 #           for line in vals['sample_ids']:
 #               if line[2] <> False :
 #                   line[2].update({'sample_id':ids[0]})
 #       return  super(labo_analysis_request, self).write(cr, uid,ids, vals, context)
##
    def default_get(self, cr, uid, fields, context=None):
        data = super(labo_analysis_request,self).default_get(cr,uid,fields,context)
        if 'isdog' in context:
            empdogids = self.pool.get('labo.analysis.type').search(cr,uid,[('code','like','')])
            data['type_id'] = empdogids and empdogids[0] or None

        return data

    def onchange_pricelist(self, cr, uid, ids,ref_client,context={}):
        if not ref_client:
            return {}
        part = self.pool.get('res.partner').browse(cr, uid, ref_client)
        v_part=part.property_product_pricelist.id or False
        return {'value': {'pricelist_id': v_part}}

    def invoice_create(self,cr, uid,ids,context={}):
        invoices = {}
        taxes=[]
        a=0
        c=[]
        inv_ref=self.pool.get('account.invoice')
        for req in self.browse(cr,uid,ids,context):
            cr.execute("select count(distinct(s.progenus_number)) from labo_sample s, labo_analysis_request r where s.sample_id=r.id and r.name = %s and  to_be_invoiced = 't'", (req.name,))
           # cr.execute("select count(distinct(s.progenus_number)) from labo_sample s, labo_analysis_request r where s.sample_id=r.id and r.name = %s and  to_be_invoiced = 't' and (nc_reanalyse='f' and final_c='f' and nc_gle='f')", (req.name,))
            res=cr.fetchone()
            a=int(res[0])
            if a==0:
                continue
            partner_id = req.ref_client.id
            req_name = req.name
            cr.execute("SELECT distinct(f.name) FROM file_history f, labo_sample s, labo_analysis_request r where r.id=%d and "\
                        "s.sample_id=r.id and f.sample_id=s.id and f.name ilike '%%.env'"%(req.id))
            file_names=cr.fetchall()
            files=",".join([x[0] for x in file_names if x])
            if not req.ref_client.id:
                raise osv.except_osv('Missed Client !', 'The object "%s" has no client assigned.' % (req.name,))
            if (req.ref_client.id) in invoices:
                inv_id = invoices[(req.ref_client.id)]
            else:
                res = self.pool.get('res.partner').address_get(cr, uid, [req.ref_client.id], ['contact', 'invoice'])
                if not res['invoice']:
                    raise osv.except_osv('Missed address of the client !', 'Please set an address to "%s" ' % (req.ref_client and req.ref_client.name,))
                contact_addr_id = res['contact']
                invoice_addr_id = res['invoice']
                inv = {
                    'name': 'Demande:' + files,
                    'partner_id': req.ref_client.id,
                    'type': 'in_invoice',
                }
                inv.update(inv_ref.onchange_partner_id(cr,uid, [], 'in_invoice',req.ref_client.id)['value'])
                inv_id = inv_ref.create(cr, uid, inv, context)
                invoices[req.ref_client.id] = inv_id
            if req.ref_client and req.ref_client.property_account_tax:
                taxes.append(req.ref_client.property_account_tax.id)
            elif req.type_id and req.type_id.product_id:
                taxes = map(lambda x: x.id, req.type_id.product_id.taxes_id)
            price = self.pool.get('product.pricelist').price_get(cr, uid, [req.pricelist_id.id],
                req.type_id.product_id.id, 1.0, req.ref_client)[req.pricelist_id.id]
            if price is False:
                raise osv.except_osv('No valid pricelist line found !',
                "You have to change either the product defined on the type of analysis or the pricelist.")
            inv_line= {
                'invoice_id': inv_id,
                'account_id':req.ref_client.property_account_receivable.id,
                'quantity': a,
                'product_id': req.type_id.product_id.id,
                'name': req.name,
                'invoice_line_tax_id': [(6,0,taxes)],
                'price_unit': price,
            }
            self.pool.get('account.invoice.line').create(cr, uid, inv_line,context)
            inv_ref.button_compute(cr, uid, invoices.values())
        for inv in inv_ref.browse(cr, uid, invoices.values(), context):
            inv_ref.write(cr, uid, [inv.id], {
                'check_total': inv.amount_total
            })
            wf_service = netsvc.LocalService('workflow')
            wf_service.trg_validate(uid, 'account.invoice', inv.id, 'invoice_open', cr)
            self.write(cr,uid,[req.id],{'invoice_ids':inv_id})

        return invoices.values()


  #  def fields_view_get(self, cr, user, view_id, view_type='form', context=None, toolbar=False):
  #      if context.get('type_id',0)=='EMPDOG':
  #          if view_type=='form':
  #              view_ids = self.pool.get('ir.ui.view').search(cr,user,[('name','=','EMPDOG REQUEST')])
  #              view_id=view_ids and view_ids[0]
  #              return super(labo_analysis_request, self).fields_view_get( cr, user, view_id, view_type, context, toolbar)
  #          if view_type=='tree':
  #              view_ids = self.pool.get('ir.ui.view').search(cr,user,[('name','=','EMPDOG')])
  #              view_id=view_ids and view_ids[0]
  #              return super(labo_analysis_request, self).fields_view_get( cr, user, view_id, view_type, context, toolbar)
  #      return super(labo_analysis_request, self).fields_view_get( cr, user, view_id, view_type, context, toolbar)

labo_analysis_request()


#class analysis_run(osv.osv):
#    _name = "analysis.run"
#    _description = "Analysis run"
#    _rec_name='run_setup'
#    _columns = {
#        'run_setup': fields.char('Run',size=64),
##        'file_setup': fields.char('File setup',size=64),
#    }
#    _defaults = {
#        'run_setup': lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid, 'analysis.setup'),
#        }
#analysis_run()


class labo_followsheet(osv.osv):
    _name = "labo.followsheet"
    _description = "Labo Followsheet"
    _columns = {
        'name':fields.char('Page number',size=12),
#        'sample_id':fields.many2one('labo.sample','Samples'),
        'date_f': fields.date('Date')
    }
    _defaults = {
        'name': lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid, 'labo.followsheet'),
        }
labo_followsheet()

class set_up(osv.osv):
    _name = "labo.setup"
    _description = "Set up"
    _columns = {
        'name':fields.char('Page number',size=12, select="1"),
#        'setup_id': fields.one2many('analysis.run','set_up', 'Analysis')
        'date_s': fields.date('Date', select="1")
    }
    _defaults = {
        'name': lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid, 'analysis.setup'),
        }
set_up()


class labo_extraction(osv.osv):
    _name = "labo.plate"
    _description = "Extraction Plate"
    _columns = {
        'name':fields.char('Plate number',size=12, select="1"),
        'date_p': fields.date('Date', select="1")
    }
    _defaults = {
        'name': lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid, 'labo.plate'),
        }
labo_extraction()

#class analysis_set_up(osv.osv):
#    _name = "analysis.setup"
#    _description = "Analysis Set up"
#    _columns = {
#        'well':fields.char('Well',size=64),
#        'name':fields.char('Well',size=64),
#        'run_setup': fields.char('Run',size=64),
#        'set_up':fields.many2one('labo.setup', 'Feuille de setup',  ondelete='cascade'),
#        'res': fields.char('Res',size=64),
#        'sample_id1':fields.many2one('labo.sample','Sample' ),
#        }
#    _defaults = {
#        'run_setup': lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid, 'analysis.setup'),
#        }
#analysis_set_up()


class analysis_set_up(osv.osv):
    _name = "analysis.setup"
    _description = "Analysis Set up"
    _rec_name="well"
    _order = "set_up, well asc"

    _columns = {
        'well':fields.integer('Well'),
    #    'name':fields.char('Well',size=64),
        'run_setup': fields.char('Run',size=64),
        'set_up':fields.many2one('labo.setup', 'Feuille de setup',  ondelete='cascade'),
        'res': fields.char('Res',size=64),
    #    'sample_id1':fields.many2one('labo.sample','Sample' ),
        }

    def name_get(self, cr, uid, ids, context={}):
        if not len(ids):
            return []
        res = [(r.id, (r.set_up and r.set_up.date_s or '')+' ['+(r.set_up and r.set_up.name or '')+']' + ' - '+ str(r.well) ) for r in self.browse(cr, uid, ids, context)]
        return res


    _defaults = {
        'run_setup': lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid, 'analysis.setup'),
        }
analysis_set_up()

class labo_labo(osv.osv):
    _name="labo.labo"
    _description="Labo"
    _columns={
        'name':fields.char('Labo name', size=64),
        'code':fields.char('Labo code', size=64),
        'ref':fields.char('Labo ref', size=64),
}
labo_labo()

def _get_rque(self, cr, uid, context):
    obj = self.pool.get('labo.rque')
    rk_ids= obj.search(cr,uid,[])
    if not len(rk_ids):
        return []
    res = obj.read(cr, uid,rk_ids ,['name','code'], context)
    return [(r['code'], r['name']) for r in res]
class labo_dog(osv.osv):
    _name="labo.dog"
    _description="Labo dog"
    _order="progenus_number desc"
    def button_prog_child(self,cr,uid,ids,*a):
        ref_c = pooler.get_pool(cr.dbname).get('labo.dog')
        seq_obj = pooler.get_pool(cr.dbname).get('ir.sequence')
        h_id=self.browse(cr,uid,ids)
        p_num=h_id[0] and h_id[0].progenus_number
        if not p_num :
            try:
                cr.execute("SELECT number_next,code from ir_sequence where name like 'Progenus Number' ")
                res=cr.fetchone()
                return ref_c.write(cr,uid,[h_id[0].id], {'progenus_number': seq_obj.get(cr,uid,res[1]),
                                                        'date_reception':time.strftime('%Y-%m-%d')
                })
            except:
                return True
        return True
    def button_prog_femal(self,cr,uid,ids,*a):
        ref_c = pooler.get_pool(cr.dbname).get('labo.dog')
        seq_obj = pooler.get_pool(cr.dbname).get('ir.sequence')
        h_id=self.browse(cr,uid,ids)
        labo_ref=h_id[0] and h_id[0].parent_m_id and h_id[0].parent_m_id.labo_id and h_id[0].parent_m_id.labo_id.ref
        p_num=h_id[0] and h_id[0].parent_m_id and h_id[0].parent_m_id.progenus_number
        type_a=h_id[0] and h_id[0].parent_m_id and h_id[0].parent_m_id.type_animal
        if p_num:
            return True
        elif labo_ref!='1':
            if type_a=="horse":
                cr.execute("SELECT number_next,code from ir_sequence where prefix like 'ch'")
                res=cr.fetchone()
            elif type_a=="dog":
                cr.execute("SELECT number_next,code from ir_sequence where prefix like 'cc'")
                res=cr.fetchone()
        elif labo_ref=='1':
            cr.execute("SELECT number_next,code from ir_sequence where name like 'Progenus Number' ")
            res=cr.fetchone()
        try:
            return ref_c.write(cr,uid,[h_id[0].parent_m_id.id], {'progenus_number': seq_obj.get(cr,uid,res[1]),
                                                            'date_reception':time.strftime('%Y-%m-%d') })
        except:
            raise osv.except_osv('Missed Femal !', 'The child "%s" has no mother.' % ( h_id[0].progenus_number,))
        return True

    def button_prog_mal(self,cr,uid,ids,*a):
        ref_c = pooler.get_pool(cr.dbname).get('labo.dog')
        seq_obj = pooler.get_pool(cr.dbname).get('ir.sequence')
        h_id=self.browse(cr,uid,ids)
        labo_ref=h_id[0] and h_id[0].parent_f_id and h_id[0].parent_f_id.labo_id and h_id[0].parent_f_id.labo_id.ref
        p_num=h_id[0] and h_id[0].parent_f_id and h_id[0].parent_f_id.progenus_number
        type_a=h_id[0] and h_id[0].parent_f_id and h_id[0].parent_f_id.type_animal
        if p_num:
            return True
        elif labo_ref!='1':
            if type_a=="horse":
                cr.execute("SELECT number_next,code from ir_sequence where prefix like 'ch'")
                res=cr.fetchone()
            elif type_a=="dog":
                cr.execute("SELECT number_next,code from ir_sequence where prefix like 'cc'")
                res=cr.fetchone()
        elif labo_ref=='1':
            cr.execute("SELECT number_next,code from ir_sequence where name like 'Progenus Number' ")
            res=cr.fetchone()
        try:
            return ref_c.write(cr,uid,[h_id[0].parent_f_id.id], {'progenus_number': seq_obj.get(cr,uid,res[1]),
                                                                'date_reception':time.strftime('%Y-%m-%d') })
        except:
            raise osv.except_osv('Missed Mal !', 'The child "%s" has no father.' % ( h_id[0].progenus_number,))

        return True
        ##DOG
    _columns={
        'tool':fields.many2one('labo.tool','Equipment', ondelete='cascade'),
        'rk_txt':fields.text('Notice'),
        'stock_id':fields.many2one('stock.reactives', 'Lot'),
        'rk_id': fields.selection(_get_rque, 'Remark', size=64),
       # 'rk_txt': fields.char('Free Remark', size=128),
        'notice': fields.char('Notice', size=128),
        'name':fields.char('Name', size=64, select="1"),
        'date_eff':fields.date('Sample Arrival Date'),
        'num_alpha':fields.char('Num alpha',size=64),
        'num_alpha2':fields.char('Num alpha Plate',size=64),
        'file_setup':fields.many2one('analysis.setup','Set up'),
        'plate_id':fields.many2one('labo.plate','Plate of Extraction'),
        'seq':fields.integer('Sequence litter'),
        'follow_sheet_id':fields.many2one('labo.followsheet','Follow Sheet', select="1"),
        'pedigree':fields.char('Pedigree',size=64),
        'progenus_number':fields.char('Progenus Number',size=64, select="1"),
        'ref_dog':fields.char('Labo ref', size=64),
#        'ueln':fields.char('UELN',size=64, select="1"),
        'origin':fields.char('Origin', size=64, select="1"),
        'date_reception':fields.date('Effective reception date'),
        'stock_id':fields.many2one('stock.reactives', 'Lot'),
        'tatoo':fields.char('Tatoo',size=64, select="2"),
        'date_closing':fields.date('Closing date'),
        'date_limit':fields.date('Limit date'),
        'material':fields.char('Material', size=64),
        'result': fields.char('Result', size=64),
        'sex': fields.selection([('M','M'), ('F','F'),], 'Sex', select="2"),
        'type_animal': fields.selection([('dog','Dog'), ('horse','Horse'),], 'Type of animal', select="2"),
        'race':fields.char('Race', size=64,select="2"),
        'birthdate':fields.date('Birthdate'),
        'ship':fields.char('Chip',size=64,select="2"),
        'state': fields.selection([('ko','zero(0)'), ('ok','Analysis OK(1)'),('no_substance','No substance(2)'),('faulty_substance','Faulty Substance(3)'),('incoming_res','Incoming results(4)'), ('exist','Already existing(5)'),('unrealized','Analysis Unrealized(6)'),('nc','To Reanalyse(7)')], 'State'),
        'state_2': fields.selection([('draft',''),('sent','Sent'),('en_cours','Running'),] , 'Sending State'),
       # 'state': fields.selection([('ko','zero(0)'), ('ok','Analysis OK(1)'),('no_substance','No substance(2)'),('faulty_substance','Faulty Substance(3)'),('incoming_res','Incoming results(4)'), ('exist','Already existing(5)'),('unrealized','Analysis Unrealized(6)')], 'State'),
        'final_c':fields.boolean('Final conformity'),
        'nc_reanalyse':fields.boolean('NC reanalyse'),
        'to_be_invoiced':fields.boolean('To be Invoiced'),
        'nc_gle':fields.boolean('NC General'),
        'parent_m_id':fields.many2one('labo.dog', 'Mother' ),
        'childm_ids': fields.one2many('labo.dog', 'parent_m_id', string='Childs '),
        'allele_ids': fields.one2many('dog.allele', 'dog_id1', string='Alleles '),
        'allele_ids_hist': fields.one2many('dog.allele.history', 'dog_id1', string='Allele Dogs Shifted'),
        'file_h_ids': fields.one2many('file.history', 'dog_id1', 'File History'),
        'doss_id':fields.one2many('doss.dog','dog_id1','File Saint Hubert History'),
        'parent_f_id':fields.many2one('labo.dog','Father'),
        'history_allele_ids':fields.one2many('allele.history','dog_id1','Allele History'),
        'history_s_ids':fields.one2many('setup.history','dog_id1','Setup History'),
        'history_p_ids':fields.one2many('plate.history','dog_id1','Plates History'),
        'labo_id':fields.many2one('labo.labo','Laboratory'),
        'childf_ids': fields.one2many('labo.dog', 'parent_f_id', string='Childs '),
        'v_done':fields.boolean('RBC Done'),
        'v_tag':fields.char('Tag', size=64 ,select="2"),
        'c_done':fields.boolean('Card Done'),
        'done_i':fields.boolean('Import Already Done '),
        'user_id': fields.many2one('res.users', 'User',  ondelete='cascade'),
        'v_done2':fields.boolean('RFC or RCS Done '),
    }



    def fields_view_get(self, cr, user, view_id=None, view_type='form', context=None, toolbar=False):
        req_type = context.get('type_id', False)
        type_view = context.get('type_view', False)
        if type_view=="EMPCHE":
            req_type=type_view
        if view_type=="form":
            if req_type=="EMPDOG_2":
                viewcalled = 'Dog2'
                view_ids = self.pool.get('ir.ui.view').search(cr,user,[('name','=',viewcalled)])
                view_id=view_ids and view_ids[0]
                if view_id:
                    return super(labo_dog, self).fields_view_get( cr, user, view_id , view_type, context, toolbar)
            elif req_type=="EMPCHE":
                viewcalled = 'Che2'
                view_ids = self.pool.get('ir.ui.view').search(cr,user,[('name','=',viewcalled)])
                view_id=view_ids and view_ids[0]
                if view_id:
                    return super(labo_dog, self).fields_view_get( cr, user, view_id , view_type, context, toolbar)
        if view_type=="tree":
            if req_type=="EMPCHE":
                viewcalled = 'emp_tree'
                view_ids = self.pool.get('ir.ui.view').search(cr,user,[('name','=',viewcalled)])
                view_id=view_ids and view_ids[0]
                if view_id:
                    return super(labo_dog, self).fields_view_get( cr, user, view_id , view_type, context, toolbar)
        return super(labo_dog, self).fields_view_get( cr, user, view_id, view_type, context, toolbar)

    def name_search(self, cr, uid, name, args=None, operator='ilike', context=None, limit=80):
        if not args:
            args=[]
        if not context:
            context={}
        if name:
            ids = self.search(cr, uid, [('progenus_number', 'like', name)] + args, limit=limit, context=context)
            if not ids:
                ids = self.search(cr, uid, [('name', operator, name)] + args, limit=limit, context=context)
        else:
            ids = self.search(cr, uid, args, limit=limit, context=context)
        return self.name_get(cr, uid, ids, context)


    def name_get(self, cr, uid, ids, context={}):
        if not len(ids):
            return []
        res = [(r['id'], (r['progenus_number'] or '')+' '+(r['name'] or '')+' ') for r in self.read(cr, uid, ids, ['progenus_number','name'], context)]
        return res

    def onchange_val_child(self, cr, uid, ids,progenus_number, p_f, p_m,context={}):
        if progenus_number or p_f or p_m:
            return {}
        seq_obj = pooler.get_pool(cr.dbname).get('ir.sequence')
        cr.execute("SELECT number_next,code from ir_sequence where name like 'Progenus Number'")
        res_cr=cr.fetchone()
        num_prog=seq_obj.get(cr,uid,res_cr[1])
        return {'value': {'progenus_number': num_prog}}


    def onchange_val(self, cr, uid, ids,progenus_number,context={}):
        if progenus_number:
            return {}
        seq_obj = pooler.get_pool(cr.dbname).get('ir.sequence')
        cr.execute("SELECT number_next,code from ir_sequence where prefix like 'cc'")
        res_cr=cr.fetchone()
        num_prog=seq_obj.get(cr,uid,res_cr[1])
        return {'value': {'progenus_number': num_prog}}


#        if not labo_id:
#            return {}
#        cr.execute("SELECT max(d.progenus_number)  from labo_analysis_type t, labo_analysis_request r, labo_sample s,labo_dog d where r.type_id=t.id and  t.code ilike 'EMPDOG' and s.dog_child=d.id")
#        res1=cr.fetchone()
#        prog_num=",".join([str(x) for x in res1 if x])
#        tmp_dog= self.browse(cr, uid, ids)
#        code=tmp_dog and tmp_dog[0] and tmp_dog[0].labo_id and tmp_dog[0].labo_id.code or ''
#        num_exist=tmp_dog and tmp_dog[0] and tmp_dog[0].progenus_number
        # KEEP PROGENUS NUMBER IMPORTED FROM THE FILE
#        if num_exist:
#            return {}
#        if not len(prog_num):
#            progen_num=code+'00/'+'0001'
#        else:
#            progen_num=code+'00/'+ str(int(prog_num and prog_num[-4:])+1).zfill(4)
#        return {'value': {'progenus_number': progen_num}}
    _defaults = {
    }
labo_dog()

class labo_sample(osv.osv):
    _name = "labo.sample"
    _description = "labo_sample"
    _rec_name='progenus_number'
    _order="progenus_number desc"

    def get_view_context(self, cr, user, context=None):
        return context.get('type_id',0)

    def _get_sequence(self, cr, uid, context):
        type_id = context.get('type_id', 0)
        if type_id=='EMPDOG' or  type_id=='EMPDOG_2' or type_id=='EMPCHE':
            return ''
        return self.pool.get('ir.sequence').get(cr, uid, 'labo.sample')

    def button_prog_simple(self,cr,uid,ids,*a):
        seq_obj = pooler.get_pool(cr.dbname).get('ir.sequence')
        sample_obj = pooler.get_pool(cr.dbname).get('labo.sample')
        sample_id=self.browse(cr,uid,ids)
        cr.execute("SELECT number_next,code from ir_sequence where name like 'Progenus Number' ")
        res=cr.fetchone()
        for i in sample_id:
            p_num=i.progenus_number
            try:
                if not p_num :
                    sample_obj.write(cr,uid,[i.id], {'progenus_number': seq_obj.get(cr,uid,res[1])})
            except:
                return True
        return True
        ##SAMPLES
    _columns = {
    #    'name':fields.char('Name',size=64),
#        'type_id':fields.many2one('labo.analysis.type','Type'),
        'date_mod':fields.date("Modification Date"),
        'num_alpha':fields.char('Num alpha',size=64),
        'case_id':fields.many2many('crm.case','case_request_rel','case_id','sample_id','Cases'),# readonly=True),
        'num_alpha2':fields.char('Num alpha Plate',size=64),
        'done_i':fields.boolean('Import Already Done '),
        'labo_id':fields.many2one('labo.labo', 'Labo'),
        'dog_mother':fields.many2one('labo.dog', 'Mother'),
        'dog_father':fields.many2one('labo.dog', 'Father'),
        'dog_child':fields.many2one('labo.dog', 'Child', domain="[('parent_f_id','=',dog_father),('parent_m_id','=',dog_mother)]"),
        'sample_id':fields.many2one('labo.analysis.request','Request',  ondelete='cascade'), # added new
        'v_done':fields.boolean('Done'),
        'v_tag':fields.char('Tag', size=64 ,select="2"),
        'allele_ids': fields.one2many('dog.allele', 'sample_id', string='Alleles of the animal'),
        'file_h_ids': fields.one2many('file.history', 'sample_id', 'File History'),
        'final_c':fields.boolean('Final conformity'),
        'nc_reanalyse':fields.boolean('NC reanalyse'),
        'nc_gle':fields.boolean('NC General'),
        'follow_sheet_id':fields.many2one('labo.followsheet','Follow Sheet'),
#        'req_id':fields.many2one('labo.analysis.request','Request'),
        'file_setup':fields.many2one('analysis.setup','Set up'),
        'plate_id':fields.many2one('labo.plate','Plate of Extraction'),
        'history_ids':fields.one2many('sample.history','sample_id','Requests History'),
        'history_s_ids':fields.one2many('setup.history','sample_id','Setup History'),
        'history_p_ids':fields.one2many('plate.history','sample_id','Plates History'),
        'allele_ids_hist': fields.one2many('dog.allele.history', 'sample_id', string='Allele Dogs Shifted'),
        'tool':fields.many2one('labo.tool','Equipment', ondelete='cascade'),
        'stock_id':fields.many2one('stock.reactives', 'Lot'),
#        'tool_id':fields.many2one('labo.tool','Tools'),
        'date_limit':fields.date('Limit date'),
        'accredit':fields.boolean('Accredit'),
        'date_reception':fields.date('Labo Reception date'),
        'date_closing':fields.date('Closing date'),
        'date_starting':fields.date('Starting date'),
        'invoice_ids': fields.many2one('account.invoice', 'Analysis Invoice',  ondelete='cascade'),
        'marker': fields.char('Marker', size=64),
        'tatooer_id':fields.many2one('res.partner', 'Tatooer', ondelete='cascade'),
        'owner_id': fields.many2one('res.partner','Owner of animal', ondelete='cascade'),
        'name_animal': fields.char('Name of animal', size=64),
        'result': fields.char('Result', size=64),# select=True),
        'awe2': fields.char('Field Awe', size=64),# select=True),
        'field_awe': fields.char('AWE', size=2),
        'birthdate':fields.date('Birthdate'),
        'progenus_number': fields.char('Progenus number', size=64),
        'sanitel':fields.char('Sanitel', size=64),
        'boucle': fields.integer('Boucle'),
        'p13':fields.char('p136',size=64),
        'p15':fields.char('p154',size=64),
        'p17':fields.char('p171',size=64),
        'genotype':fields.char('Genotype',size=64),
        'material':fields.char('material', size=64),
    #    'sex': fields.selection([('male','Male'), ('female','Female'),], 'Sex', redonly=True),
        'sex': fields.char('Sex',size=7),
      #  'notice': fields.text('Notice'),
        'tube': fields.char('Tube',size=7),
        'breed':fields.char('Breed',size=24),
        'state': fields.selection([('ko','zero(0)'), ('ok','Analysis OK(1)'),('no_substance','No substance(2)'),('faulty_substance','Faulty Substance(3)'),('incoming_res','Incoming results(4)'), ('exist','Already existing(5)'),('unrealized','Analysis Unrealized(6)'),('nc','To Reanalyse(7)')], 'State'),
        'state_2': fields.selection([('draft',''),('sent','Sent'),('en_cours','Running'),] , 'Sending State'),
        'code': fields.char('Code',size=64),
        'microsattelitte':fields.char('microsattelitte', size=64),
        'allele1':fields.integer('Allele1'),
        'allele2':fields.integer('Allele2'),
        'field1':fields.integer('field1',),
        'field2':fields.char('field2', size=64),
        'field3':fields.integer('field3',),
        'field4':fields.char('field4', size=64),
        'nature':fields.char('Nature of sample', size=64),
        'kind': fields.char('kind',size=64),
        'cond_sample':fields.char('Conditions samples',size=64),
        'cond_packing':fields.char('Conditions packing',size=64),
        'notice':fields.char('Notice',size=128),
        'to_be_invoiced':fields.boolean('To be Invoiced'),
        'mission_number':fields.char('Mission number', size=64),
        'lp_file':fields.char('File',size=64),
        'lp_doss':fields.char('Doss',size=64),
        'lp_serv':fields.char('Serv',size=64),
        'preleveur1_id':fields.many2one('res.partner','Eleveur'),
        'preleveur_id':fields.many2one('res.partner','Preleveur'),
        'seq_horse': fields.integer('Sequence'),
#        'allele1_dog':fields.char('Allele dog 1', size=10),
#        'allele2_dog':fields.char('Allele dog 2', size=10),
   #     'marker_dog': fields.char('Marker dog', size=64),
        'user_id': fields.many2one('res.users', 'User',  ondelete='cascade'),
       # 'date_eff':fields.date('Effective reception date'),
        'date_eff':fields.date('Sample Arrival Date'),
#        'preleveur2_id':fields.many2one('res.partner','Preleveur 2', select="1"),
        'res_filiation':fields.selection([('YY','YY'), ('YN','YN'),('NY','NY'),('NN','NN')], 'Filiation'),
        'cont':fields.char('context of view', size=64),
        'identifier_1':fields.char('Identifier 1', size=64),
        'identifier_2':fields.char('Identifier 2', size=64),
        'identifier_3':fields.char('Identifier 3', size=64),
        'misc_1':fields.char('Miscallenous 1', size=64),
        'misc_2':fields.char('Miscallenous 2', size=64),
    }

    _defaults = {
        'field_awe': lambda *a: 'N',
        'awe2': lambda *a: 'A',
        'to_be_invoiced': lambda *a: True,
        'accredit': lambda *a: True,
        'nc_gle': lambda *a: False,
        'nc_reanalyse': lambda *a: False,
        'final_c': lambda *a: False,
       # 'progenus_number': lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid, 'labo.sample'),
     #   'progenus_number': _get_sequence,
        'cont':get_view_context,
        'state_2':lambda *a:'draft'
    }


    def onchange_dog(self, cr, uid, ids,m,context={}):
        cr.execute("Select d.write_date from labo_dog d where d.id=%d"%(m))
        res=cr.fetchone()
        if res and res[0]:
            if res[0][:10] ==time.strftime('%Y-%m-%d'):
                return {'value': {'date_mod': time.strftime('%Y-%m-%d')}}
        return {}

#    def write(self, cr, uid, ids, vals, context=None, check=True, update_check=True):
#        if not context:
#            context={}
#        print vals
#        if 'sample_ids' not in vals:
#            print"::::::::::::"
#            vals.update({'sample_ids':[]})
#            for line in vals['sample_ids']:
#                line[2].update({'sample_id':ids[0]})
#            return  super(labo_sample, self).write(cr, uid,ids, vals, context)
#        else :
#            for line in vals['sample_ids']:
#                if line[2] <> False :
#                    line[2].update({'sample_id':ids[0]})
#            return  super(labo_sample, self).write(cr, uid,ids, vals, context)
##
    def search(self, cr, user, args, offset=0, limit=None, order=None,context=None, count=False):
        is_context=False
        res=[]
        if context and 'type_id' in context:
            is_context =context.get('type_id',False)
        for v_art in args:
            if ('dog_mother' in v_art) and is_context in ('empdog1_2', 'all') :
                val= v_art[2]
                cr.execute("select s.id from labo_dog d, labo_sample s where (s.dog_mother=d.id or s.dog_father=d.id or s.dog_child=d.id) and (d.progenus_number ilike '%%%s%%' or d.name ilike '%%%s%%' ) " %(val, val ,))
                all_ids=cr.fetchall()
                for r in all_ids:
                    res.append(r[0])
                return res
        return super(labo_sample, self).search(cr, user, args, offset, limit,order, context=context, count=count)

#    def create(self, cr, uid, vals, context=None, check=True):
#
#        if  vals.has_key("sample_id"):
##            tmp_sample_lines = vals['sample_ids']
##            vals.update({'sample_ids':[]})
#            samp_id = self.pool.get('labo.analysis.request').browse(self,cr,uid,ids)
##            for line in tmp_sample_lines:
#            vals.update({'sample_id':samp_id})
##            vals.update({'sample_ids':tmp_sample_lines})
#            super(labo_sample, self).write(cr, uid,[samp_id], vals, context)
#        else:
#            samp_id = super(labo_sample, self).create(cr, uid, vals, context)
#        return samp_id

    def running_ko_samples(self, cr, uid, *args):
        print "DANS RUNNING"
        ref_case = pooler.get_pool(cr.dbname).get('crm.case')
        txt_mail="La date limite des echantillons est echue. Les echantillons concernes sont les suivants:"
        cr.execute("select r.name from labo_sample s, labo_analysis_request r where s.sample_id=r.id and s.date_limit = current_date group by r.name ")
        for r in cr.fetchall():
            cr.execute('select distinct(s.sanitel) from labo_analysis_request r, labo_sample s where s.sample_id=r.id and r.name = %s ', (r[0],))
            current_samples=([x[0] for x in cr.fetchall() if x])

            section_id=pooler.get_pool(cr.dbname).get('crm.case.section').search(cr, uid,[('code', '=', 'samples'),])
            print "CURRENT",current_samples
            if current_samples:
                new_id=ref_case.create(cr,uid,{
                'name': "Samples to review",
                'section_id':section_id[0],
                'state': 'open',
                'active':True,
                'description': txt_mail+ ",".join(([str(i) for i in current_samples if i] )) + "soit a la demande suivante:"+r[0]
                })
            else:
                return False
        return True
###
###Following function return the TREE View Depending on the Request type
###

    def fields_view_get(self, cr, user, view_id, view_type='form', context=None, toolbar=False):
        type_analysis=context.get('type_id',0)
        if context.get('type'):
            type=context.get('type')
            req = self.pool.get('labo.analysis.type').browse(cr,user,type)
            type_analysis=req and req.code
        if type_analysis=='empdog1_2':
            if view_type=='form':
                view_ids = self.pool.get('ir.ui.view').search(cr,user,[('name','=','EMPDOG1')])
                view_id=view_ids and view_ids[0]
                return super(labo_sample, self).fields_view_get( cr, user, view_id, view_type, context, toolbar)
            if view_type=='tree':
                view_ids = self.pool.get('ir.ui.view').search(cr,user,[('name','=','EMPDOG2')])
                view_id=view_ids and view_ids[0]
                return super(labo_sample, self).fields_view_get( cr, user, view_id, view_type, context, toolbar)
        if type_analysis=='EMPDOG':
            if view_type=='form':
                view_ids = self.pool.get('ir.ui.view').search(cr,user,[('name','=','EMPDOG1')])
                view_id=view_ids and view_ids[0]
                return super(labo_sample, self).fields_view_get( cr, user, view_id, view_type, context, toolbar)
            if view_type=='tree':
                view_ids = self.pool.get('ir.ui.view').search(cr,user,[('name','=','EMPDOG2')])
                view_id=view_ids and view_ids[0]
                return super(labo_sample, self).fields_view_get( cr, user, view_id, view_type, context, toolbar)
        elif type_analysis=='COLOCHE':
            if view_type=='tree':
                view_ids = self.pool.get('ir.ui.view').search(cr,user,[('name','=','COLOCHE_TS')])
                view_id=view_ids and view_ids[0]
                return super(labo_sample, self).fields_view_get( cr, user, view_id, view_type, context, toolbar)
            if view_type=='form':
                view_ids = self.pool.get('ir.ui.view').search(cr,user,[('name','=','COLOCHE_FS')])
                view_id=view_ids and view_ids[0]
                return super(labo_sample, self).fields_view_get( cr, user, view_id, view_type, context, toolbar)
        elif type_analysis=='all':
            if view_type=='form':
                view_ids = self.pool.get('ir.ui.view').search(cr,user,[('name','=','ALL1')])
                view_id=view_ids and view_ids[0]
                return super(labo_sample, self).fields_view_get( cr, user, view_id, view_type, context, toolbar)
            if view_type=='tree':
                view_ids = self.pool.get('ir.ui.view').search(cr,user,[('name','=','ALL2')])
                view_id=view_ids and view_ids[0]
                return super(labo_sample, self).fields_view_get( cr, user, view_id, view_type, context, toolbar)
        elif type_analysis=='EMPDOG_2':
            if view_type=='form':
                view_ids = self.pool.get('ir.ui.view').search(cr,user,[('name','=','ALONE1')])
                view_id=view_ids and view_ids[0]
                return super(labo_sample, self).fields_view_get( cr, user, view_id, view_type, context, toolbar)
            if view_type=='tree':
                view_ids = self.pool.get('ir.ui.view').search(cr,user,[('name','=','ALONE2')])
                view_id=view_ids and view_ids[0]
                return super(labo_sample, self).fields_view_get( cr, user, view_id, view_type, context, toolbar)
        elif type_analysis=='EMPACBOV':
            if view_type=='form':
                view_ids = self.pool.get('ir.ui.view').search(cr,user,[('name','=','EMPACBOV1')])
                view_id=view_ids and view_ids[0]
                return super(labo_sample, self).fields_view_get( cr, user, view_id, view_type, context, toolbar)
            if view_type=='tree':
                view_ids = self.pool.get('ir.ui.view').search(cr,user,[('name','=','EMPACBOV2')])
                view_id=view_ids and view_ids[0]
                return super(labo_sample, self).fields_view_get( cr, user, view_id, view_type, context, toolbar)
        elif type_analysis=='EMPBOV':
            if view_type=='form':
                view_ids = self.pool.get('ir.ui.view').search(cr,user,[('name','=','EMPBOV1')])
                view_id=view_ids and view_ids[0]
                return super(labo_sample, self).fields_view_get( cr, user, view_id, view_type, context, toolbar)
            if view_type=='tree':
                view_ids = self.pool.get('ir.ui.view').search(cr,user,[('name','=','EMPBOV2')])
                view_id=view_ids and view_ids[0]
                return super(labo_sample, self).fields_view_get( cr, user, view_id, view_type, context, toolbar)
        elif type_analysis=='ACBOV':
            if view_type=='form':
                view_ids = self.pool.get('ir.ui.view').search(cr,user,[('name','=','ACBOV1')])
                view_id=view_ids and view_ids[0]
                return super(labo_sample, self).fields_view_get( cr, user, view_id, view_type, context, toolbar)
            if view_type=='tree':
                view_ids = self.pool.get('ir.ui.view').search(cr,user,[('name','=','ACBOV2')])
                view_id=view_ids and view_ids[0]
                return super(labo_sample, self).fields_view_get( cr, user, view_id, view_type, context, toolbar)
        elif type_analysis=='Scrapie':
            if view_type=='form':
                view_ids = self.pool.get('ir.ui.view').search(cr,user,[('name','=','Scrapie1')])
                view_id=view_ids and view_ids[0]
                return super(labo_sample, self).fields_view_get( cr, user, view_id, view_type, context, toolbar)
            if view_type=='tree':
                view_ids = self.pool.get('ir.ui.view').search(cr,user,[('name','=','Scrapie2')])
                view_id=view_ids and view_ids[0]
                return super(labo_sample, self).fields_view_get( cr, user, view_id, view_type, context, toolbar)
        elif type_analysis=='Id of race':
            if view_type=='form':
                view_ids = self.pool.get('ir.ui.view').search(cr,user,[('name','=','RACE1')])
                view_id=view_ids and view_ids[0]
                return super(labo_sample, self).fields_view_get( cr, user, view_id, view_type, context, toolbar)
            if view_type=='tree':
                view_ids = self.pool.get('ir.ui.view').search(cr,user,[('name','=','RACE2')])
                view_id=view_ids and view_ids[0]
                return super(labo_sample, self).fields_view_get( cr, user, view_id, view_type, context, toolbar)
        elif type_analysis=='Sequence':
            if view_type=='form':
                view_ids = self.pool.get('ir.ui.view').search(cr,user,[('name','=','Sequence1')])
                view_id=view_ids and view_ids[0]
                return super(labo_sample, self).fields_view_get( cr, user, view_id, view_type, context, toolbar)
            if view_type=='tree':
                view_ids = self.pool.get('ir.ui.view').search(cr,user,[('name','=','Sequence2')])
                view_id=view_ids and view_ids[0]
                return super(labo_sample, self).fields_view_get( cr, user, view_id, view_type, context, toolbar)
        elif type_analysis=='EMPCHE':
            if view_type=='form':
                view_ids = self.pool.get('ir.ui.view').search(cr,user,[('name','=','EMPCHE1')])
                view_id=view_ids and view_ids[0]
                return super(labo_sample, self).fields_view_get( cr, user, view_id, view_type, context, toolbar)
            if view_type=='tree':
                view_ids = self.pool.get('ir.ui.view').search(cr,user,[('name','=','EMPCHE2')])
                view_id=view_ids and view_ids[0]
                return super(labo_sample, self).fields_view_get( cr, user, view_id, view_type, context, toolbar)
            return super(labo_sample, self).fields_view_get( cr, user, view_id, view_type, context, toolbar)
        elif type_analysis=='COLODOG':
            if view_type=='tree':
                view_ids = self.pool.get('ir.ui.view').search(cr,user,[('name','=','COLODOG_TS')])
                view_id=view_ids and view_ids[0]
                return super(labo_sample, self).fields_view_get( cr, user, view_id, view_type, context, toolbar)
            if view_type=='form':
                view_ids = self.pool.get('ir.ui.view').search(cr,user,[('name','=','COLODOG_FS')])
                view_id=view_ids and view_ids[0]
                return super(labo_sample, self).fields_view_get( cr, user, view_id, view_type, context, toolbar)
        elif type_analysis=='MULE FOOT':
            if view_type=='tree':
                view_ids = self.pool.get('ir.ui.view').search(cr,user,[('name','=','MULE_FOOT_T')])
                view_id=view_ids and view_ids[0]
                return super(labo_sample, self).fields_view_get( cr, user, view_id, view_type, context, toolbar)
            if view_type=='form':
                view_ids = self.pool.get('ir.ui.view').search(cr,user,[('name','=','MULE_FOOT_F')])
                view_id=view_ids and view_ids[0]
                return super(labo_sample, self).fields_view_get( cr, user, view_id, view_type, context, toolbar)
        elif type_analysis=='IBR':
            if view_type=='tree':
                view_ids = self.pool.get('ir.ui.view').search(cr,user,[('name','=','IBR_TS')])
                view_id=view_ids and view_ids[0]
                return super(labo_sample, self).fields_view_get( cr, user, view_id, view_type, context, toolbar)
            if view_type=='form':
                view_ids = self.pool.get('ir.ui.view').search(cr,user,[('name','=','IBR_FS')])
                view_id=view_ids and view_ids[0]
                return super(labo_sample, self).fields_view_get( cr, user, view_id, view_type, context, toolbar)
        elif type_analysis=='MDR1':
            if view_type=='tree':
                view_ids = self.pool.get('ir.ui.view').search(cr,user,[('name','=','MDR1_TS')])
                view_id=view_ids and view_ids[0]
                return super(labo_sample, self).fields_view_get( cr, user, view_id, view_type, context, toolbar)
            if view_type=='form':
                view_ids = self.pool.get('ir.ui.view').search(cr,user,[('name','=','MDR1_FS')])
                view_id=view_ids and view_ids[0]
                return super(labo_sample, self).fields_view_get( cr, user, view_id, view_type, context, toolbar)
        elif type_analysis=='HYPP':
            if view_type=='tree':
                view_ids = self.pool.get('ir.ui.view').search(cr,user,[('name','=','HYPP')])
                view_id=view_ids and view_ids[0]
                return super(labo_sample, self).fields_view_get( cr, user, view_id, view_type, context, toolbar)
            if view_type=='form':
                view_ids = self.pool.get('ir.ui.view').search(cr,user,[('name','=','HYPP_1')])
                view_id=view_ids and view_ids[0]
                return super(labo_sample, self).fields_view_get( cr, user, view_id, view_type, context, toolbar)
        elif type_analysis=='EMPCAT':
            if view_type=='tree':
                view_ids = self.pool.get('ir.ui.view').search(cr,user,[('name','=','EMPCAT_TS')])
                view_id=view_ids and view_ids[0]
                return super(labo_sample, self).fields_view_get( cr, user, view_id, view_type, context, toolbar)
            if view_type=='form':
                view_ids = self.pool.get('ir.ui.view').search(cr,user,[('name','=','EMPCAT_FS')])
                view_id=view_ids and view_ids[0]
                return super(labo_sample, self).fields_view_get( cr, user, view_id, view_type, context, toolbar)
        elif type_analysis=='Babesia':
            if view_type=='tree':
                view_ids = self.pool.get('ir.ui.view').search(cr,user,[('name','=','Babesia_TS')])
                view_id=view_ids and view_ids[0]
                return super(labo_sample, self).fields_view_get( cr, user, view_id, view_type, context, toolbar)
            if view_type=='form':
                view_ids = self.pool.get('ir.ui.view').search(cr,user,[('name','=','Babesia_FS')])
                view_id=view_ids and view_ids[0]
                return super(labo_sample, self).fields_view_get( cr, user, view_id, view_type, context, toolbar)
        elif type_analysis=='Booroola':
            if view_type=='tree':
                view_ids = self.pool.get('ir.ui.view').search(cr,user,[('name','=','Booroola_TS')])
                view_id=view_ids and view_ids[0]
                return super(labo_sample, self).fields_view_get( cr, user, view_id, view_type, context, toolbar)
            if view_type=='form':
                view_ids = self.pool.get('ir.ui.view').search(cr,user,[('name','=','Booroola_FS')])
                view_id=view_ids and view_ids[0]
                return super(labo_sample, self).fields_view_get( cr, user, view_id, view_type, context, toolbar)
        elif type_analysis=='BVD':
            if view_type=='tree':
                view_ids = self.pool.get('ir.ui.view').search(cr,user,[('name','=','BVD_TS')])
                view_id=view_ids and view_ids[0]
                return super(labo_sample, self).fields_view_get( cr, user, view_id, view_type, context, toolbar)
            if view_type=='form':
                view_ids = self.pool.get('ir.ui.view').search(cr,user,[('name','=','BVD_FS')])
                view_id=view_ids and view_ids[0]
                return super(labo_sample, self).fields_view_get( cr, user, view_id, view_type, context, toolbar)
        elif type_analysis=='caseine':
            if view_type=='tree':
                view_ids = self.pool.get('ir.ui.view').search(cr,user,[('name','=','caseine_TS')])
                view_id=view_ids and view_ids[0]
                return super(labo_sample, self).fields_view_get( cr, user, view_id, view_type, context, toolbar)
            if view_type=='form':
                view_ids = self.pool.get('ir.ui.view').search(cr,user,[('name','=','caseine_FS')])
                view_id=view_ids and view_ids[0]
                return super(labo_sample, self).fields_view_get( cr, user, view_id, view_type, context, toolbar)
        elif type_analysis=='culard':
            if view_type=='tree':
                view_ids = self.pool.get('ir.ui.view').search(cr,user,[('name','=','culard_TS')])
                view_id=view_ids and view_ids[0]
                return super(labo_sample, self).fields_view_get( cr, user, view_id, view_type, context, toolbar)
            if view_type=='form':
                view_ids = self.pool.get('ir.ui.view').search(cr,user,[('name','=','culard_FS')])
                view_id=view_ids and view_ids[0]
                return super(labo_sample, self).fields_view_get( cr, user, view_id, view_type, context, toolbar)
        elif type_analysis=='CVM-BLAD':
            if view_type=='tree':
                view_ids = self.pool.get('ir.ui.view').search(cr,user,[('name','=','CVM_BLAD_TS')])
                view_id=view_ids and view_ids[0]
                return super(labo_sample, self).fields_view_get( cr, user, view_id, view_type, context, toolbar)
            if view_type=='form':
                view_ids = self.pool.get('ir.ui.view').search(cr,user,[('name','=','CVM_BLAD_FS')])
                view_id=view_ids and view_ids[0]
                return super(labo_sample, self).fields_view_get( cr, user, view_id, view_type, context, toolbar)
        elif type_analysis=='EMPPOR':
            if view_type=='tree':
                view_ids = self.pool.get('ir.ui.view').search(cr,user,[('name','=','EMPPOR_TS')])
                view_id=view_ids and view_ids[0]
                return super(labo_sample, self).fields_view_get( cr, user, view_id, view_type, context, toolbar)
            if view_type=='form':
                view_ids = self.pool.get('ir.ui.view').search(cr,user,[('name','=','EMPPOR_FS')])
                view_id=view_ids and view_ids[0]
                return super(labo_sample, self).fields_view_get( cr, user, view_id, view_type, context, toolbar)
        elif type_analysis=='EMPRGENET':
            if view_type=='tree':
                view_ids = self.pool.get('ir.ui.view').search(cr,user,[('name','=','EMPRGENET_TS')])
                view_id=view_ids and view_ids[0]
                return super(labo_sample, self).fields_view_get( cr, user, view_id, view_type, context, toolbar)
            if view_type=='form':
                view_ids = self.pool.get('ir.ui.view').search(cr,user,[('name','=','EMPRGENET_FS')])
                view_id=view_ids and view_ids[0]
                return super(labo_sample, self).fields_view_get( cr, user, view_id, view_type, context, toolbar)
        elif type_analysis=='EXTR':
            if view_type=='tree':
                view_ids = self.pool.get('ir.ui.view').search(cr,user,[('name','=','EXTR_TS')])
                view_id=view_ids and view_ids[0]
                return super(labo_sample, self).fields_view_get( cr, user, view_id, view_type, context, toolbar)
            if view_type=='form':
                view_ids = self.pool.get('ir.ui.view').search(cr,user,[('name','=','EXTR_FS')])
                view_id=view_ids and view_ids[0]
                return super(labo_sample, self).fields_view_get( cr, user, view_id, view_type, context, toolbar)
        elif type_analysis=='IDSPE':
            if view_type=='tree':
                view_ids = self.pool.get('ir.ui.view').search(cr,user,[('name','=','IDSPE_TS')])
                view_id=view_ids and view_ids[0]
                return super(labo_sample, self).fields_view_get( cr, user, view_id, view_type, context, toolbar)
            if view_type=='form':
                view_ids = self.pool.get('ir.ui.view').search(cr,user,[('name','=','IDSPE_FS')])
                view_id=view_ids and view_ids[0]
                return super(labo_sample, self).fields_view_get( cr, user, view_id, view_type, context, toolbar)
        elif type_analysis=='pit-1':
            if view_type=='tree':
                view_ids = self.pool.get('ir.ui.view').search(cr,user,[('name','=','pit_1_TS')])
                view_id=view_ids and view_ids[0]
                return super(labo_sample, self).fields_view_get( cr, user, view_id, view_type, context, toolbar)
            if view_type=='form':
                view_ids = self.pool.get('ir.ui.view').search(cr,user,[('name','=','pit_1_FS')])
                view_id=view_ids and view_ids[0]
                return super(labo_sample, self).fields_view_get( cr, user, view_id, view_type, context, toolbar)
        elif type_analysis=='Facteur Rouge':
            if view_type=='tree':
                view_ids = self.pool.get('ir.ui.view').search(cr,user,[('name','=','Facteur_Rouge_TS')])
                view_id=view_ids and view_ids[0]
                return super(labo_sample, self).fields_view_get( cr, user, view_id, view_type, context, toolbar)
            if view_type=='form':
                view_ids = self.pool.get('ir.ui.view').search(cr,user,[('name','=','Facteur_Rouge_FS')])
                view_id=view_ids and view_ids[0]
                return super(labo_sample, self).fields_view_get( cr, user, view_id, view_type, context, toolbar)
        elif type_analysis=='FCO':
            if view_type=='tree':
                view_ids = self.pool.get('ir.ui.view').search(cr,user,[('name','=','FCO_TS')])
                view_id=view_ids and view_ids[0]
                return super(labo_sample, self).fields_view_get( cr, user, view_id, view_type, context, toolbar)
            if view_type=='form':
                view_ids = self.pool.get('ir.ui.view').search(cr,user,[('name','=','FCO_FS')])
                view_id=view_ids and view_ids[0]
                return super(labo_sample, self).fields_view_get( cr, user, view_id, view_type, context, toolbar)
        elif type_analysis=='FCO':
            if view_type=='tree':
                view_ids = self.pool.get('ir.ui.view').search(cr,user,[('name','=','FCO_TS')])
                view_id=view_ids and view_ids[0]
                return super(labo_sample, self).fields_view_get( cr, user, view_id, view_type, context, toolbar)
            if view_type=='form':
                view_ids = self.pool.get('ir.ui.view').search(cr,user,[('name','=','FCO_FS')])
                view_id=view_ids and view_ids[0]
                return super(labo_sample, self).fields_view_get( cr, user, view_id, view_type, context, toolbar)
        elif type_analysis=='FREE MARTINISME':
            if view_type=='tree':
                view_ids = self.pool.get('ir.ui.view').search(cr,user,[('name','=','FREE_MARTINISME_TS')])
                view_id=view_ids and view_ids[0]
                return super(labo_sample, self).fields_view_get( cr, user, view_id, view_type, context, toolbar)
            if view_type=='form':
                view_ids = self.pool.get('ir.ui.view').search(cr,user,[('name','=','FREE_MARTINISME_FS')])
                view_id=view_ids and view_ids[0]
                return super(labo_sample, self).fields_view_get( cr, user, view_id, view_type, context, toolbar)
        elif type_analysis=='HCM':
            if view_type=='tree':
                view_ids = self.pool.get('ir.ui.view').search(cr,user,[('name','=','HCM_TS')])
                view_id=view_ids and view_ids[0]
                return super(labo_sample, self).fields_view_get( cr, user, view_id, view_type, context, toolbar)
            if view_type=='form':
                view_ids = self.pool.get('ir.ui.view').search(cr,user,[('name','=','HCM_FS')])
                view_id=view_ids and view_ids[0]
                return super(labo_sample, self).fields_view_get( cr, user, view_id, view_type, context, toolbar)
        elif type_analysis=='HYPP':
            if view_type=='tree':
                view_ids = self.pool.get('ir.ui.view').search(cr,user,[('name','=','HYPP_TS')])
                view_id=view_ids and view_ids[0]
                return super(labo_sample, self).fields_view_get( cr, user, view_id, view_type, context, toolbar)
            if view_type=='form':
                view_ids = self.pool.get('ir.ui.view').search(cr,user,[('name','=','HYPP_FS')])
                view_id=view_ids and view_ids[0]
                return super(labo_sample, self).fields_view_get( cr, user, view_id, view_type, context, toolbar)
        elif type_analysis=='IGFBP':
            if view_type=='tree':
                view_ids = self.pool.get('ir.ui.view').search(cr,user,[('name','=','IGFBP_TS')])
                view_id=view_ids and view_ids[0]
                return super(labo_sample, self).fields_view_get( cr, user, view_id, view_type, context, toolbar)
            if view_type=='form':
                view_ids = self.pool.get('ir.ui.view').search(cr,user,[('name','=','IGFBP_FS')])
                view_id=view_ids and view_ids[0]
                return super(labo_sample, self).fields_view_get( cr, user, view_id, view_type, context, toolbar)
        elif type_analysis=='IGF-2':
            if view_type=='tree':
                view_ids = self.pool.get('ir.ui.view').search(cr,user,[('name','=','IGF_2_TS')])
                view_id=view_ids and view_ids[0]
                return super(labo_sample, self).fields_view_get( cr, user, view_id, view_type, context, toolbar)
            if view_type=='form':
                view_ids = self.pool.get('ir.ui.view').search(cr,user,[('name','=','IGF_2_FS')])
                view_id=view_ids and view_ids[0]
                return super(labo_sample, self).fields_view_get( cr, user, view_id, view_type, context, toolbar)
        elif type_analysis=='IGF':
            if view_type=='tree':
                view_ids = self.pool.get('ir.ui.view').search(cr,user,[('name','=','IGF_TS')])
                view_id=view_ids and view_ids[0]
                return super(labo_sample, self).fields_view_get( cr, user, view_id, view_type, context, toolbar)
            if view_type=='form':
                view_ids = self.pool.get('ir.ui.view').search(cr,user,[('name','=','IGF_FS')])
                view_id=view_ids and view_ids[0]
                return super(labo_sample, self).fields_view_get( cr, user, view_id, view_type, context, toolbar)
        elif type_analysis=='K88':
            if view_type=='tree':
                view_ids = self.pool.get('ir.ui.view').search(cr,user,[('name','=','K88_TS')])
                view_id=view_ids and view_ids[0]
                return super(labo_sample, self).fields_view_get( cr, user, view_id, view_type, context, toolbar)
            if view_type=='form':
                view_ids = self.pool.get('ir.ui.view').search(cr,user,[('name','=','K88_FS')])
                view_id=view_ids and view_ids[0]
                return super(labo_sample, self).fields_view_get( cr, user, view_id, view_type, context, toolbar)
        elif type_analysis=='K-caseine':
            if view_type=='tree':
                view_ids = self.pool.get('ir.ui.view').search(cr,user,[('name','=','K_caseine_TS')])
                view_id=view_ids and view_ids[0]
                return super(labo_sample, self).fields_view_get( cr, user, view_id, view_type, context, toolbar)
            if view_type=='form':
                view_ids = self.pool.get('ir.ui.view').search(cr,user,[('name','=','K_caseine_FS')])
                view_id=view_ids and view_ids[0]
                return super(labo_sample, self).fields_view_get( cr, user, view_id, view_type, context, toolbar)
        elif type_analysis=='Lawsonia':
            if view_type=='tree':
                view_ids = self.pool.get('ir.ui.view').search(cr,user,[('name','=','Lawsonia_TS')])
                view_id=view_ids and view_ids[0]
                return super(labo_sample, self).fields_view_get( cr, user, view_id, view_type, context, toolbar)
            if view_type=='form':
                view_ids = self.pool.get('ir.ui.view').search(cr,user,[('name','=','Lawsonia_FS')])
                view_id=view_ids and view_ids[0]
                return super(labo_sample, self).fields_view_get( cr, user, view_id, view_type, context, toolbar)
        elif type_analysis=='M4T4F4':
            if view_type=='tree':
                view_ids = self.pool.get('ir.ui.view').search(cr,user,[('name','=','M4T4F4_TS')])
                view_id=view_ids and view_ids[0]
                return super(labo_sample, self).fields_view_get( cr, user, view_id, view_type, context, toolbar)
            if view_type=='form':
                view_ids = self.pool.get('ir.ui.view').search(cr,user,[('name','=','M4T4F4_FS')])
                view_id=view_ids and view_ids[0]
                return super(labo_sample, self).fields_view_get( cr, user, view_id, view_type, context, toolbar)
        elif type_analysis=='OLWS':
            if view_type=='tree':
                view_ids = self.pool.get('ir.ui.view').search(cr,user,[('name','=','OLWS_TS')])
                view_id=view_ids and view_ids[0]
                return super(labo_sample, self).fields_view_get( cr, user, view_id, view_type, context, toolbar)
            if view_type=='form':
                view_ids = self.pool.get('ir.ui.view').search(cr,user,[('name','=','OLWS_FS')])
                view_id=view_ids and view_ids[0]
                return super(labo_sample, self).fields_view_get( cr, user, view_id, view_type, context, toolbar)
        elif type_analysis=='Paratub':
            if view_type=='tree':
                view_ids = self.pool.get('ir.ui.view').search(cr,user,[('name','=','Paratub_TS')])
                view_id=view_ids and view_ids[0]
                return super(labo_sample, self).fields_view_get( cr, user, view_id, view_type, context, toolbar)
            if view_type=='form':
                view_ids = self.pool.get('ir.ui.view').search(cr,user,[('name','=','Paratub_FS')])
                view_id=view_ids and view_ids[0]
                return super(labo_sample, self).fields_view_get( cr, user, view_id, view_type, context, toolbar)
        elif type_analysis=='PKD':
            if view_type=='tree':
                view_ids = self.pool.get('ir.ui.view').search(cr,user,[('name','=','PKD_TS')])
                view_id=view_ids and view_ids[0]
                return super(labo_sample, self).fields_view_get( cr, user, view_id, view_type, context, toolbar)
            if view_type=='form':
                view_ids = self.pool.get('ir.ui.view').search(cr,user,[('name','=','PKD_FS')])
                view_id=view_ids and view_ids[0]
                return super(labo_sample, self).fields_view_get( cr, user, view_id, view_type, context, toolbar)
        elif type_analysis=='PRRSV':
            if view_type=='tree':
                view_ids = self.pool.get('ir.ui.view').search(cr,user,[('name','=','PRRSV_TS')])
                view_id=view_ids and view_ids[0]
                return super(labo_sample, self).fields_view_get( cr, user, view_id, view_type, context, toolbar)
            if view_type=='form':
                view_ids = self.pool.get('ir.ui.view').search(cr,user,[('name','=','PRRSV_FS')])
                view_id=view_ids and view_ids[0]
                return super(labo_sample, self).fields_view_get( cr, user, view_id, view_type, context, toolbar)
        elif type_analysis=='RIAGH':
            if view_type=='tree':
                view_ids = self.pool.get('ir.ui.view').search(cr,user,[('name','=','RIAGH_TS')])
                view_id=view_ids and view_ids[0]
                return super(labo_sample, self).fields_view_get( cr, user, view_id, view_type, context, toolbar)
            if view_type=='form':
                view_ids = self.pool.get('ir.ui.view').search(cr,user,[('name','=','RIAGH_FS')])
                view_id=view_ids and view_ids[0]
                return super(labo_sample, self).fields_view_get( cr, user, view_id, view_type, context, toolbar)
        elif type_analysis=='RN':
            if view_type=='tree':
                view_ids = self.pool.get('ir.ui.view').search(cr,user,[('name','=','RN_TS')])
                view_id=view_ids and view_ids[0]
                return super(labo_sample, self).fields_view_get( cr, user, view_id, view_type, context, toolbar)
            if view_type=='form':
                view_ids = self.pool.get('ir.ui.view').search(cr,user,[('name','=','RN_FS')])
                view_id=view_ids and view_ids[0]
                return super(labo_sample, self).fields_view_get( cr, user, view_id, view_type, context, toolbar)
        elif type_analysis=='SCID':
            if view_type=='tree':
                view_ids = self.pool.get('ir.ui.view').search(cr,user,[('name','=','SCID_TS')])
                view_id=view_ids and view_ids[0]
                return super(labo_sample, self).fields_view_get( cr, user, view_id, view_type, context, toolbar)
            if view_type=='form':
                view_ids = self.pool.get('ir.ui.view').search(cr,user,[('name','=','SCID_FS')])
                view_id=view_ids and view_ids[0]
                return super(labo_sample, self).fields_view_get( cr, user, view_id, view_type, context, toolbar)
        elif type_analysis=='STRESS':
            if view_type=='tree':
                view_ids = self.pool.get('ir.ui.view').search(cr,user,[('name','=','STRESS_TS')])
                view_id=view_ids and view_ids[0]
                return super(labo_sample, self).fields_view_get( cr, user, view_id, view_type, context, toolbar)
            if view_type=='form':
                view_ids = self.pool.get('ir.ui.view').search(cr,user,[('name','=','STRESS_FS')])
                view_id=view_ids and view_ids[0]
                return super(labo_sample, self).fields_view_get( cr, user, view_id, view_type, context, toolbar)
        elif type_analysis=='TOBIANO':
            if view_type=='tree':
                view_ids = self.pool.get('ir.ui.view').search(cr,user,[('name','=','TOBIANO_TS')])
                view_id=view_ids and view_ids[0]
                return super(labo_sample, self).fields_view_get( cr, user, view_id, view_type, context, toolbar)
            if view_type=='form':
                view_ids = self.pool.get('ir.ui.view').search(cr,user,[('name','=','TOBIANO_FS')])
                view_id=view_ids and view_ids[0]
                return super(labo_sample, self).fields_view_get( cr, user, view_id, view_type, context, toolbar)
        elif type_analysis=='SEXEOIS':
            if view_type=='tree':
                view_ids = self.pool.get('ir.ui.view').search(cr,user,[('name','=','SEXEOIS_TS')])
                view_id=view_ids and view_ids[0]
                return super(labo_sample, self).fields_view_get( cr, user, view_id, view_type, context, toolbar)
            if view_type=='form':
                view_ids = self.pool.get('ir.ui.view').search(cr,user,[('name','=','SEXEOIS_FS')])
                view_id=view_ids and view_ids[0]
                return super(labo_sample, self).fields_view_get( cr, user, view_id, view_type, context, toolbar)
      #  sample_id = context.get('sample_id', 0)
      #  if sample_id :
      #      obj_reqs = self.pool.get('labo.analysis.request').browse(cr,user,sample_id)
      #      viewcalled = 'labo_sample_'+str(obj_reqs.type_id.code)+'_'+view_type
      #      view_ids = self.pool.get('ir.ui.view').search(cr,user,[('name','=',viewcalled)])
      #      if len(view_ids):
      #          view_id = view_ids[0]
      #          return super(labo_sample, self).fields_view_get( cr, user, view_id , view_type, context, toolbar)
        return super(labo_sample, self).fields_view_get( cr, user, view_id, view_type, context, toolbar)



labo_sample()




#class analysis_set_up(osv.osv):
#    _name = "analysis.setup"
#    _description = "Analysis Set up"
#    _columns = {
#        'well':fields.char('Well',size=64),
#        'name':fields.char('Well',size=64),
#        'run_setup': fields.char('Run',size=64),
#        'set_up':fields.many2one('labo.setup', 'Feuille de setup',  ondelete='cascade'),
#        'res': fields.char('Res',size=64),
#        'sample_id1':fields.many2one('labo.sample','Sample' ),
#        }
#    _defaults = {
#        'run_setup': lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid, 'analysis.setup'),
#        }
#analysis_set_up()
class labo_product(osv.osv):
    _inherit = 'product.product'
    _description = "Product progenus"
    _columns = {
        'date_reception':fields.date('Reception date'),
        'opening_date':fields.date('Opening date'),
        'closing_date':fields.date('closing date'),
        'date_expiry':fields.date('Expiry date')
    }

    def fields_view_get(self, cr, user, view_id=None, view_type='form', context=None, toolbar=False):
        sample_id = context.get('isarticleprod', False)
        if sample_id:
            viewcalled = 'labo_article_view_'+view_type
            view_ids = self.pool.get('ir.ui.view').search(cr,user,[('name','=',viewcalled)])
            if len(view_ids):
                view_id = view_ids[0]
                return super(labo_product, self).fields_view_get( cr, user, view_id , view_type, context, toolbar)
        return super(labo_product, self).fields_view_get( cr, user, view_id, view_type, context, toolbar)
labo_product()

class res_domain_partner(osv.osv):
    _name = 'res.domain.partner'
    _columns = {
        'name': fields.char('Domain', size=46, SELECT=1),
        'code': fields.char('Code', size=46, SELECT=1),
        'active': fields.boolean('Active', SELECT=2),
    }
res_domain_partner()

def _get_domain(self, cr, uid, context):
    obj = self.pool.get('res.domain.partner')
    domain_ids= obj.search(cr,uid,[])
    if not len(domain_ids):
        return []
    res = obj.read(cr, uid,domain_ids ,['name','code'], context)
    return [(r['code'], r['name']) for r in res]

class res_partner(osv.osv):
    _inherit='res.partner'
    _description='Partners'
    _columns = {
        'domain_res': fields.selection(_get_domain, 'Domain Activity', size=32),
        'test_h': fields.char('Domain', size=46, SELECT=1),
    }
    #To check: overide search on partner
    def search(self, cr, user, args, offset=0, limit=None, order=None,context=None, count=False):
        request_id = context and context.get('request_id', False) or False
        if request_id:
            partner_ids = []
            req = self.pool.get('labo.analysis.request').browse(cr,user,request_id,context)
            if req.ref_client:
                partner_ids.append(req.ref_client.id)
            for sample in req.sample_ids:
                if sample.preleveur1_id:
                    partner_ids.append(sample.preleveur1_id.id)
                if sample.tatooer_id:
                    partner_ids.append(sample.tatooer_id.id)
            args.append(('id','in',partner_ids))
        return super(res_partner, self).search(cr, user, args, offset, limit,order, context=context, count=count)
    _defaults = {
        'domain_res': lambda *a: '0',
    }
res_partner()

class res_partner_address(osv.osv):
    _inherit='res.partner.address'
    _columns={
        'pobox_no': fields.char('PO Box No.', size=64),
    }
res_partner_address()
class analysis_column(osv.osv):
    def _col_get(self, cr, user, context={}):
        result = []
        cols = self.pool.get('labo.sample')._columns
        for col in cols:
            result.append( (col, cols[col].string) )
        result.sort()
        return result
    _name = "analysis.column"
    _rec_name="field"
    _description = "Analysis Column"
    _columns = {
#        'name': fields.char('Column Name', size=64),
        'field': fields.selection(_col_get, 'Field Name', method=True, required=True, size=32),
        'sequence': fields.integer('Sequence'),
        'view_id': fields.many2one('labo.analysis.view','view',  ondelete='cascade'),
        'required': fields.boolean('Required'),
        'select': fields.boolean('Select'),
        'readonly': fields.boolean('Readonly'),
    }
    _order = "sequence"
analysis_column()

class doss_dog(osv.osv):
    _name = "doss.dog"
    _description="File Saint Hubert history"
    _columns = {
        'name': fields.char('File Name',size=64),
        'dog_id1': fields.many2one('labo.dog', 'Dog'),
    }
doss_dog()

class file_history(osv.osv):
    _name = "file.history"
    _description="File history"
    _columns = {
        'date_f': fields.date('Date'),
        'name': fields.char('File Name',size=64),
        'dog_id1': fields.many2one('labo.dog', 'Dog'),
        'sample_id': fields.many2one('labo.sample', 'Sample'),
    }
    _defaults = {
#        'name': lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid, 'file.history'),
        'date_f': lambda *args: time.strftime('%Y-%m-%d')
    }
file_history()
class allele_history(osv.osv):
    _name = "allele.history"
    _description="Allele history"
    _columns = {
        'date_s': fields.date('Shifting date'),
        'name': fields.char('Reason',size=64),
        'allele': fields.char('Old Allele', size=64),
        'dog_id1': fields.many2one('labo.dog', 'Dog'),
    }
    _defaults = {
        'date_s': lambda *args: time.strftime('%Y-%m-%d')
    }
allele_history()

class dog_allele(osv.osv):
    _name = "dog.allele"
    _description="Dog Allele"
    _rec_name="allele_dog1"
    _columns = {
        'allele_dog1': fields.char('Allele 1',size=64),
        'allele_dog2': fields.char('Allele 2',size=64),
        'marker_dog': fields.char('Marker ',size=64),
        'creation_date': fields.datetime('Creation date'),
        'dog_id1': fields.many2one('labo.dog', 'Dog'),
        'sample_id': fields.many2one('labo.sample', 'Sample'),
    }
    _defaults = {
        'creation_date': lambda *args: time.strftime('%Y-%m-%d %H:%M:%S')
    }
dog_allele()
class dog_allele_history(osv.osv):
    _name = "dog.allele.history"
    _description="Old Dog Allele"
    _rec_name="allele_dog1"
    _columns = {
        'allele_dog1': fields.char('Allele  1',size=64),
        'allele_dog2': fields.char('Allele  2',size=64),
        'marker_dog': fields.char('Marker  ',size=64),
        'creation_date': fields.datetime('Creation date'),
        'dog_id1': fields.many2one('labo.dog', 'Dog'),
        'sample_id': fields.many2one('labo.sample', 'Sample'),
    }
    _defaults = {
        'creation_date': lambda *args: time.strftime('%Y-%m-%d %H:%m:%S')
    }
dog_allele_history()
class setup_history(osv.osv):
    _name = "setup.history"
    _description="Setup history"
    _columns = {
        'name': fields.date('Shifting date',size=64),
        'sample_id': fields.many2one('labo.sample', 'Sample'),
        'dog_id1': fields.many2one('labo.dog', 'Dog'),
        'old_alpha': fields.char('Old number',size=64),
        'setup_id': fields.many2one('analysis.setup', ' New Setup'),
        'setup_id2': fields.many2one('analysis.setup', ' Old Setup'),
    }
    _defaults = {
        'name': lambda *args: time.strftime('%Y-%m-%d')
    }
setup_history()
class plate_history(osv.osv):
    _name = "plate.history"
    _description="Plates history"
    _columns = {
        'name': fields.date('Shifting date',size=64),
        'old_alpha': fields.char('Old number',size=64),
        'sample_id': fields.many2one('labo.sample', 'Sample'),
        'plate_id': fields.many2one('labo.plate', ' New Plate'),
        'plate_id2': fields.many2one('labo.plate', ' Old Plate'),
        'dog_id1': fields.many2one('labo.dog', 'Dog'),
    }
    _defaults = {
        'name': lambda *args: time.strftime('%Y-%m-%d')
    }
plate_history()
class sample_history(osv.osv):
    _name = "sample.history"
    _description="Sample history"
    _columns = {
        'name': fields.date('Shifting date',size=64),
        'sample_id': fields.many2one('labo.sample', 'Sample'),
        'req_id': fields.many2one('labo.analysis.request', ' New Request'),
        'request_id': fields.many2one('labo.analysis.request', ' Old Request'),
#        'request_id': fields.char('Request', size=64),
    }
    _defaults = {
        'name': lambda *args: time.strftime('%Y-%m-%d')
    }
sample_history()

class report_analysis(osv.osv):
    _name = "report.analysis"
    _description = "Analysis per type by month "
    _auto = False
    _columns = {
        'year': fields.char('Date',size=64, select=1),
#        'user_id':fields.many2one('res.users', 'User',select=1),
        'count_t':fields.float('% of success'),
        'code_t':fields.char('Type',size=64, select=1),
    }
    def init(self, cr):
        cr.execute('''
        create or replace view report_analysis  as
                SELECT
                    min (l.id) as id,
                    to_char(l.create_date, 'YYYY-MM') as year,
                    t.code as code_t,
                    (1-count(l.state='ko' or l.nc_reanalyse)::float/count(*)::float)*100 as count_t
                FROM
                    labo_sample l, labo_analysis_request req, labo_analysis_type t
                WHERE
                    req.id=l.sample_id and t.id=req.type_id
                GROUP BY
                    year, code_t
                    ''')

report_analysis()

class report_year_analysis(osv.osv):
    _name = "report.year.analysis"
    _description = "Analysis by type for year"
    _auto = False
    _columns = {
        'year': fields.char('Date',size=64, select=1),
#        'user_id':fields.many2one('res.users', 'User',select=1),
        'count_t':fields.float('% of success'),
        'code_t':fields.char('Type',size=64, select=1),
    }
    def init(self, cr):
        cr.execute('''
        create or replace view report_year_analysis  as
                SELECT
                    min (l.id) as id,
                    to_char(l.create_date, 'YYYY') as year,
                    t.code as code_t,
                    (1-count(l.state='ko' or l.nc_reanalyse)::float/count(*)::float)*100 as count_t
                FROM
                    labo_sample l, labo_analysis_request req, labo_analysis_type t
                WHERE
                    req.id=l.sample_id and t.id=req.type_id
                GROUP BY
                    year, code_t
                    ''')

report_year_analysis()

class report_analysis_substance(osv.osv):
    _name = "report.analysis.substance"
    _description = "Analysis for substance by month "
    _auto = False
    _columns = {
        'year': fields.char('Date',size=64, select=1),
#        'user_id':fields.many2one('res.users', 'User',select=1),
        'count_t':fields.float('% of success'),
        'breed':fields.char('Breed',size=24, select=1),
        'material':fields.char('material', size=64, select=True),
    }
    def init(self, cr):
        cr.execute('''
        create or replace view report_analysis_substance  as
                SELECT
                    min (l.id) as id,
                    to_char(l.create_date, 'YYYY-MM') as year,
                    l.material as material,
                    (1-count(l.state='ko' or l.nc_reanalyse)::float/count(*)::float)*100 as count_t
                FROM
                    labo_sample l, labo_analysis_request req, labo_analysis_type t
                WHERE
                    req.id=l.sample_id and t.id=req.type_id
                GROUP BY
                    year,l.material
                    ''')

report_analysis_substance()


class report_analysis_substance_year(osv.osv):
    _name = "report.analysis.substance.year"
    _description = "Analysis for substance by year"
    _auto = False
    _columns = {
        'year': fields.char('Date',size=64, select=1),
#        'user_id':fields.many2one('res.users', 'User',select=1),
        'count_t':fields.float('% of success'),
        'breed':fields.char('Breed',size=24, select=1),
        'material':fields.char('material', size=64, select=True),
    }
    def init(self, cr):
        cr.execute('''
        create or replace view report_analysis_substance_year  as
                SELECT
                    min (l.id) as id,
                    to_char(l.create_date, 'YYYY') as year,
                    l.material as material,
                    (1-count(l.state='ko' or l.nc_reanalyse)::float/count(*)::float)*100 as count_t
                FROM
                    labo_sample l, labo_analysis_request req, labo_analysis_type t
                WHERE
                    req.id=l.sample_id and t.id=req.type_id
                GROUP BY
                    year,l.material
                    ''')

report_analysis_substance_year()

class report_analysis_accredit(osv.osv):
    _name = "report.analysis.accredit"
    _description = "Analysis accredited by month "
    _auto = False
    _columns = {
        'year': fields.char('Date',size=64, select=1),
        'count_t':fields.float('% of success'),
        'accredit':fields.boolean('Accredit'),
    }
                #    l.accredit as accredit,
    def init(self, cr):
        cr.execute('''
        create or replace view report_analysis_accredit  as
                SELECT
                    min (l.id) as id,
                    to_char(l.create_date, 'YYYY-MM') as year,
                    req.accredit as accredit,
                    (1-count(l.state='ko' or l.nc_reanalyse)::float/count(*)::float)*100 as count_t
                FROM
                    labo_sample l, labo_analysis_request req, labo_analysis_type t
                WHERE
                    req.id=l.sample_id and t.id=req.type_id
                GROUP BY
                    year,req.accredit
                    ''')

report_analysis_accredit()

class report_analysis_accredit_year(osv.osv):
    _name = "report.analysis.accredit.year"
    _description = "Analysis accredited by year "
    _auto = False
    _columns = {
        'year': fields.char('Date',size=64, select=1),
        'count_t':fields.float('% of success'),
        'accredit':fields.boolean('Accredit'),
    }
    def init(self, cr):
        cr.execute('''
        create or replace view report_analysis_accredit_year  as
                SELECT
                    min (l.id) as id,
                    to_char(l.create_date, 'YYYY') as year,
                    req.accredit as accredit,
                    (1-count(l.state='ko' or l.nc_reanalyse)::float/count(*)::float)*100 as count_t
                FROM
                    labo_sample l, labo_analysis_request req, labo_analysis_type t
                WHERE
                    req.id=l.sample_id and t.id=req.type_id
                GROUP BY
                    year,req.accredit
                    ''')

report_analysis_accredit_year()

#class product_product(osv.osv):
#
#product_product()
#class res_partner(osv.osv):
#    _name = 'res.partner.ss'
#    _inherit='res.partner'
#    _description='Partners'
#    _columns = {
#    #    'domain_res': fields.many2one('res.domain.partner', 'Domain Activity', ondelete='cascade', select=2),
#        'test_h': fields.char('Domain', size=46, SELECT=1),
#    }
#res_partner()

class ass_letters_numbers(osv.osv):
    _name = 'letters.numbers'
    _columns = {
        'name': fields.char('Marker', size=64, required=True),
        'name_letter': fields.char('Marker Letters', size=64),
        'name_number': fields.char('Marker Numbers', size=64),
    }
ass_letters_numbers()

class account_tax(osv.osv):
    _name = 'account.tax'
    _inherit='account.tax'
    _columns = {
        'note': fields.text('notes', translate=True),
    }
account_tax()


class labo_rque(osv.osv):
    _name="labo.rque"
    _description="Labo Remark"
    _columns={
        'name':fields.char('Labo Remark', size=170, required=True, select=1),
        'code':fields.char('Remark Code ', size=64, required=True, select=1),
}
labo_rque()
