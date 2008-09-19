# -*- encoding: utf-8 -*-
import time
import datetime
import offer
from mx import DateTime

from osv import fields
from osv import osv


class dm_campaign_group(osv.osv):
    _name = "dm.campaign.group"
    _columns = {
        'name': fields.char('Campaign group name', size=64, required=True),
        'project_id' : fields.many2one('project.project', 'Project', readonly=True),
        'campaign_ids': fields.one2many('dm.campaign', 'campaign_group_id', 'Campaigns', domain=[('campaign_group_id','=',False)]),
    }
dm_campaign_group()


class dm_campaign_type(osv.osv):
    _name = "dm.campaign.type"

    _columns = {
        'name': fields.char('Description', size=64, required=True),
        'code': fields.char('Code', size=16, required=True),
    }
dm_campaign_type()


class dm_overlay(osv.osv):
    _name = 'dm.overlay'
    _rec_name = 'trademark_id'

    def _overlay_code(self, cr, uid, ids, name, args, context={}):
        result ={}
        for id in ids:

            overlay = self.browse(cr,uid,[id])[0]
            trademark_code = overlay.trademark_id.name or ''
            dealer_code = overlay.dealer_id.ref or ''
            country_code = overlay.country_id.code or ''

            code1='-'.join([trademark_code, dealer_code, country_code])
            result[id]=code1
        return result

    _columns = {
        'code' : fields.function(_overlay_code,string='Code',type="char",method=True,readonly=True),
        'trademark_id' : fields.many2one('dm.trademark', 'Trademark', required=True),
        'dealer_id' : fields.many2one('res.partner', 'Dealer',domain=[('category_id','ilike','Dealer')], context={'category':'Dealer'}, required=True),
        'country_id' : fields.many2one('res.country', 'Country', required=True),
        'bank_account_id' : fields.many2one('account.account', 'Account'),
    }
dm_overlay()


class dm_campaign(osv.osv):
    _name = "dm.campaign"
    _inherits = {'account.analytic.account': 'analytic_account_id'}
    _rec_name = 'name'

    def dtp_making_time_get(self, cr, uid, ids, name, arg, context={}):
        result={}
        for i in ids:
            result[i]=0.0
        return result

    def _campaign_code(self, cr, uid, ids, name, args, context={}):
        result ={}
        for id in ids:
            camp = self.browse(cr,uid,[id])[0]
            offer_code = camp.offer_id and camp.offer_id.code or ''
            trademark_code = camp.trademark_id and camp.trademark_id.code or ''
            dealer_code =camp.dealer_id and camp.dealer_id.ref or ''
            date_start = camp.date_start or ''
            country_code = camp.country_id.code or ''
            date = date_start.split('-')
            year = month = ''
            if len(date)==3:
                year = date[0][2:]
                month = date[1]
            final_date=month+year
            code1='-'.join([offer_code ,dealer_code ,trademark_code ,final_date ,country_code])
            result[id]=code1
        return result

    def po_check(self,cr, uid, ids, *args):
        for pline in self.browse(cr, uid, ids)[0].purchase_line_ids:
            if pline.state == 'requested':
                for po in pline.purchase_order_ids:
                    if po.state == 'confirmed' or po.state == 'approved':
                        pline.write({'state':'ordered'})
            if pline.state == 'ordered':
                for po in pline.purchase_order_ids:
                    if po.shipped :
                        pline.write({'state':'delivered','date_delivery':time.strftime('%Y-%m-%d %H:%M:%S')})
                        if pline.type == 'translation':
                            trans_id = self.pool.get('dm.offer.translation').create(cr, uid,
                                {'offer_id': pline.campaign_id.offer_id.id,
                                 'date': pline.date_delivery,
                                 'language_id': pline.campaign_id.lang_id.id,
                                 'translator_id':  po.partner_id.id,
                                 'notes': pline.notes,
                                 })

        return True

    def _get_campaign_type(self,cr,uid,context={}):
        campaign_type = self.pool.get('dm.campaign.type')
        type_ids = campaign_type.search(cr,uid,[])
        type = campaign_type.browse(cr,uid,type_ids)
        return map(lambda x : [x.code,x.name],type)

    def onchange_lang_currency(self, cr, uid, ids, country_id):
        value = {}
        if country_id:
            country = self.pool.get('res.country').browse(cr,uid,[country_id])[0]
            value['lang_id'] =  country.main_language.id
            value['currency_id'] = country.main_currency.id
        else:
            value['lang_id']=0
            value['currency_id']=0
        return {'value':value}


    _columns = {
        'code1' : fields.function(_campaign_code,string='Code',type="char",size="64",method=True,readonly=True),
        'offer_id' : fields.many2one('dm.offer', 'Offer',domain=[('state','=','open'),('type','in',['new','standart','rewrite'])]),
        'country_id' : fields.many2one('res.country', 'Country',required=True),
        'lang_id' : fields.many2one('res.lang', 'Language'),
        'trademark_id' : fields.many2one('dm.trademark', 'Trademark'),
        'project_id' : fields.many2one('project.project', 'Project', readonly=True),
        'campaign_group_id' : fields.many2one('dm.campaign.group', 'Campaign group'),
        'notes' : fields.text('Notes'),
        'proposition_ids' : fields.one2many('dm.campaign.proposition', 'camp_id', 'Proposition'),
        'campaign_type' : fields.selection(_get_campaign_type,'Type',required=True),
        'analytic_account_id' : fields.many2one('account.analytic.account','Analytic Account', ondelete='cascade'),
        'planning_state' : fields.selection([('pending','Pending'),('inprogress','In Progress'),('done','Done')], 'Planning Status',readonly=True),
        'items_state' : fields.selection([('pending','Pending'),('inprogress','In Progress'),('done','Done')], 'Items Status',readonly=True),
        'translation_state' : fields.selection([('pending','Pending'),('inprogress','In Progress'),('done','Done')], 'Translation Status',readonly=True),
        'manufacturing_state' : fields.selection([('pending','Pending'),('inprogress','In Progress'),('done','Done')], 'Manufacturing Status',readonly=True),
        'customer_file_state' : fields.selection([('pending','Pending'),('inprogress','In Progress'),('done','Done')], 'Customers Files Status',readonly=True),
        'dealer_id' : fields.many2one('res.partner', 'Dealer',domain=[('category_id','ilike','Dealer')], context={'category':'Dealer'}),
        'responsible_id' : fields.many2one('res.users','Responsible'),
        'dtp_making_time' : fields.function(dtp_making_time_get, method=True, type='float', string='Making Time'),
        'deduplicator_id' : fields.many2one('res.partner','Deduplicator',domain=[('category_id','ilike','Deduplicator')], context={'category':'Deduplicator'}),
        'dedup_order_date' : fields.date('Order Date'),
        'dedup_validity_date' : fields.date('Validity Date'),
        'dedup_delivery_date' : fields.date('Delivery Date'),
        'currency_id' : fields.many2one('res.currency','Currency',ondelete='cascade'),
        'manufacturing_costs': fields.float('Manufacturing Costs',digits=(16,2)),
        'manufacturing_product': fields.many2one('product.product','Manufacturing Product'),
        'purchase_line_ids': fields.one2many('dm.campaign.purchase_line', 'campaign_id', 'Purchase Lines'),
        'dtp_dates_ids': fields.one2many('dm.campaign.dtp_dates','campaign_id','DTP Dates'),
        'overlay_id': fields.many2one('dm.overlay', 'Overlay', ondelete='cascade'),
    }

    _defaults = {
        'state': lambda *a: 'draft',
        'manufacturing_state': lambda *a: 'pending',
        'items_state': lambda *a: 'pending',
        'translation_state': lambda *a: 'pending',
        'customer_file_state': lambda *a: 'pending',
        'campaign_type': lambda *a: 'general',
        'responsible_id' : lambda obj, cr, uid, context: uid,
    }

    def state_draft_set(self, cr, uid, ids, *args):
        self.write(cr, uid, ids, {'state':'draft'})
        return True

    def state_close_set(self, cr, uid, ids, *args):
        self.write(cr, uid, ids, {'state':'close'})
        return True

    def state_pending_set(self, cr, uid, ids, *args):
        self.write(cr, uid, ids, {'state':'pending'})
        return True

    def state_open_set(self, cr, uid, ids, *args):
        camp = self.browse(cr,uid,ids)[0]
        if camp.offer_id:
            forbidden_state_ids = [state_id.country_id.id for state_id in camp.offer_id.forbidden_state_ids]
            forbidden_country_ids = [country_id.id for country_id in camp.offer_id.forbidden_country_ids]
            forbidden_country_ids.extend(forbidden_state_ids)
            if camp.offer_id.forbidden_country_ids and camp.country_id.id  in  forbidden_country_ids :
                raise osv.except_osv("Error!!","This offer is not valid in this country")
        if not camp.date_start or not camp.dealer_id or not camp.trademark_id :
            raise osv.except_osv("Error!!","Informations are missing. Check Date Start, Dealer and Trademark")
        super(dm_campaign,self).write(cr, uid, ids, {'state':'open','planning_state':'inprogress'})
        return True

    def write(self, cr, uid, ids, vals, context=None):
        res = super(dm_campaign,self).write(cr, uid, ids, vals, context)
        camp = self.pool.get('dm.campaign').browse(cr,uid,ids)[0]
        c = camp.country_id.id
        if 'date_start' in vals and vals['date_start'] and camp.project_id:
            self.pool.get('project.project').write(cr,uid,[camp.project_id.id],{'date_end':vals['date_start']})
        if camp.offer_id:
            d = camp.offer_id.id
            offers = self.pool.get('dm.offer').browse(cr, uid, d)
            list_off = []
            for off in offers.forbidden_country_ids:
                list_off.append(off.id)
                if c in list_off:
                    raise osv.except_osv("Error!!","You cannot use this offer in this country")

            """ In campaign, if no trademark is given, it gets the 'recommended trademark' from offer """
            if not camp.trademark_id:
                super(osv.osv, self).write(cr, uid, camp.id, {'trademark_id':offers.recommended_trademark.id})
        
        # check if an overlay exists else create it
        overlay = self.pool.get('dm.overlay').search(cr, uid, [('trademark_id','=',camp.trademark_id.id), ('dealer_id','=',camp.dealer_id.id), ('country_id','=',camp.country_id.id)])
        if overlay:
            super(osv.osv, self).write(cr, uid, camp.id, {'overlay_id':overlay[0]}, context)  
        else:
            overlay_ids1 = self.pool.get('dm.overlay').create(cr, uid, {'trademark_id':camp.trademark_id.id, 'dealer_id':camp.dealer_id.id, 'country_id':camp.country_id.id}, context)
            super(osv.osv, self).write(cr, uid, camp.id, {'overlay_id':overlay_ids1}, context)
        
        return res

    def create(self,cr,uid,vals,context={}):
        if context.has_key('campaign_type') and context['campaign_type']=='model':
            vals['campaign_type']='model'

        id_camp = super(dm_campaign,self).create(cr,uid,vals,context)

        # Create dtp_dates from template
        if self.pool.get('dm.campaign').browse(cr, uid, [id_camp])[0].dtp_dates_ids:
            dtp_dates_to_del_ids = self.pool.get('dm.campaign.dtp_dates').search(cr, uid, [('campaign_id','=',id_camp)])
            self.pool.get('dm.campaign.dtp_dates').unlink(cr, uid, dtp_dates_to_del_ids)

        dtp_dates_ids = self.pool.get('dm.campaign.dtp_dates').search(cr, uid, [('template','=',True)])
        for dtp_dates_id in dtp_dates_ids:
            self.pool.get('dm.campaign.dtp_dates').copy(cr, uid, dtp_dates_id, {'campaign_id':id_camp,'template':False})

        data_cam = self.browse(cr, uid, id_camp)
        # Set campaign end date at one year after start date
        if (data_cam.date_start) and (not data_cam.date):
            time_format = "%Y-%m-%d"
            d = time.strptime(data_cam.date_start,time_format)
            d = datetime.date(d[0], d[1], d[2])
            date_end = d + datetime.timedelta(days=365)
            super(dm_campaign,self).write(cr, uid, id_camp, {'date':date_end})

        # Set trademark to offer's trademark only if trademark is null
        if vals['offer_id'] and (not vals['trademark_id']):
            offer_id = self.pool.get('dm.offer').browse(cr, uid, vals['offer_id'])
            super(dm_campaign,self).write(cr, uid, id_camp, {'trademark_id':offer_id.recommended_trademark.id})
        
        # check if an overlay exists else create it
        data_cam1 = self.browse(cr, uid, id_camp)
        overlay = self.pool.get('dm.overlay').search(cr, uid, [('trademark_id','=',data_cam1.trademark_id.id), ('dealer_id','=',data_cam1.dealer_id.id), ('country_id','=',data_cam1.country_id.id)])
        if overlay:
            super(osv.osv, self).write(cr, uid, data_cam1.id, {'overlay_id':overlay[0]}, context)  
        else:
            overlay_ids1 = self.pool.get('dm.overlay').create(cr, uid, {'trademark_id':data_cam1.trademark_id.id, 'dealer_id':data_cam1.dealer_id.id, 'country_id':data_cam1.country_id.id}, context)
            super(osv.osv, self).write(cr, uid, data_cam1.id, {'overlay_id':overlay_ids1}, context)

        return id_camp

    def fields_view_get(self, cr, user, view_id=None, view_type='form', context=None, toolbar=False):
        result = super(dm_campaign,self).fields_view_get(cr, user, view_id, view_type, context, toolbar)
        if context.has_key('campaign_type'):
            if context['campaign_type'] == 'model' :
                if result.has_key('toolbar'):
                    result['toolbar']['action'] =[]
        return result

    def copy_campaign(self,cr, uid, ids, *args):
        camp = self.browse(cr,uid,ids)[0]
        default={}
        default['name']='New campaign from model %s' % camp.name
        default['campaign_type'] = 'recruiting'
        default['responsible_id'] = uid
        self.copy(cr,uid,ids[0],default)
        return True

    def copy(self, cr, uid, id, default=None, context={}):
        cmp_id = super(dm_campaign, self).copy(cr, uid, id, default)
        data = self.browse(cr, uid, cmp_id, context)
        default='Copy of %s' % data.name
        super(dm_campaign, self).write(cr, uid, cmp_id, {'name':default, 'date_start':0, 'date':0})
        return cmp_id

dm_campaign()


class dm_campaign_proposition(osv.osv):
    _name = "dm.campaign.proposition"
    _inherits = {'account.analytic.account': 'analytic_account_id'}

    def write(self, cr, uid, ids, vals, context=None):
        res = super(dm_campaign_proposition,self).write(cr, uid, ids, vals, context)
        camp = self.pool.get('dm.campaign.proposition').browse(cr,uid,ids)[0]
        c = camp.camp_id.id
        id = self.pool.get('dm.campaign').browse(cr, uid, c)
        if not camp.date_start:
            super(osv.osv, self).write(cr, uid, camp.id, {'date_start':id.date_start})
        return res

    def create(self,cr,uid,vals,context={}):
        id = self.pool.get('dm.campaign').browse(cr, uid, vals['camp_id'])
        if not vals['date_start']:
            if id.date_start:
                vals['date_start']=id.date_start
        return super(dm_campaign_proposition, self).create(cr, uid, vals, context)

    def copy(self, cr, uid, id, default=None, context={}):
        """
        Function to duplicate segments only if 'keep_segments' is set to yes else not to duplicate segments
        """
        proposition_id = super(dm_campaign_proposition, self).copy(cr, uid, id, default, context=context)
        data = self.browse(cr, uid, proposition_id, context)
        default='Copy of %s' % data.name
        super(dm_campaign_proposition, self).write(cr, uid, proposition_id, {'name':default, 'date_start':0})
        if data.keep_segments == False:
            l = []
            for i in data.segment_ids:
                 l.append(i.id)
                 self.pool.get('dm.campaign.proposition.segment').unlink(cr,uid,l)
                 super(dm_campaign_proposition, self).write(cr, uid, proposition_id, {'segment_ids':[(6,0,[])]})
            return proposition_id
        return proposition_id

    def _proposition_code(self, cr, uid, ids, name, args, context={}):
        result ={}
        for id in ids:
            pro = self.browse(cr,uid,[id])[0]
            camp_code = pro.camp_id.code1 or ''
            offer_code = pro.camp_id.offer_id and pro.camp_id.offer_id.code or ''
            trademark_code = pro.camp_id.trademark_id and pro.camp_id.trademark_id.name or ''
            dealer_code =pro.camp_id.dealer_id and pro.camp_id.dealer_id.ref or ''
            date_start = pro.date_start or ''
            date = date_start.split('-')
            year = month = ''
            if len(date)==3:
                year = date[0][2:]
                month = date[1]
            country_code = pro.camp_id.country_id.code or ''
            seq = '%%0%sd' % 2 % id
            final_date = month+year
            code1='-'.join([camp_code, seq])
            result[id]=code1
        return result

    def _quantity_ordered_get(self, cr, uid, ids, name, args, context={}):
        result ={}
        for propo in self.browse(cr,uid,ids):
            if not propo.segment_ids:
                result[propo.id]='No segments defined'
                continue
            qty = 0
            numeric=True
            for segment in propo.segment_ids:
                if not segment.quantity_ordered:
                    result[propo.id]='Ordered Quantity missing in a Segment'
                    numeric=False
                    continue
                if segment.quantity_ordered == 'AAA':
                    result[propo.id]='AAA for a Segment'
                    numeric=False
                    continue
                qty += int(segment.quantity_ordered)
            if numeric:
                result[propo.id]=str(qty)
        return result

    def _quantity_delivered_get(self, cr, uid, ids, name, args, context={}):
        result ={}
        for propo in self.browse(cr,uid,ids):
            if not propo.segment_ids:
                result[propo.id]='No segments defined'
                continue
            qty = 0
            for segment in propo.segment_ids:
                if segment.quantity_delivered == 0:
                    result[propo.id]='Delivered Quantity missing in a Segment'
                    numeric=False
                    continue
                qty += segment.quantity_delivered
            result[propo.id]=str(qty)
        return result

    def _quantity_real_get(self, cr, uid, ids, name, args, context={}):
        result ={}
        for propo in self.browse(cr,uid,ids):
            if not propo.segment_ids:
                result[propo.id]='No segments defined'
                continue
            qty = 0
            for segment in propo.segment_ids:
                if segment.quantity_real == 0:
                    result[propo.id]='Real Quantity missing in a Segment'
                    numeric=False
                    continue
                qty += segment.quantity_real
            result[propo.id]=str(qty)
        return result

    def _default_camp_date(self, cr, uid, context={}):
        if 'date1' in context and context['date1']:
            dd = context['date1']
            return dd
        return []

    _columns = {
        'code1' : fields.function(_proposition_code,string='Code',type="char",size="64",method=True,readonly=True),
        'camp_id' : fields.many2one('dm.campaign','Campaign',ondelete = 'cascade',required=True),
        'delay_ids' : fields.one2many('dm.campaign.delay', 'proposition_id', 'Delays', ondelete='cascade'),
        'sale_rate' : fields.float('Sale Rate', digits=(16,2)),
        'proposition_type' : fields.selection([('init','Initial'),('relaunching','Relauching'),('split','Split')],"Type"),
        'initial_proposition_id': fields.many2one('dm.campaign.proposition', 'Initial proposition'),
        'segment_ids' : fields.one2many('dm.campaign.proposition.segment','proposition_id','Segment', ondelete='cascade'),
        'quantity_ordered' : fields.function(_quantity_ordered_get,string='Ordered Quantity',type="char",size="64",method=True,readonly=True),
        'quantity_delivered' : fields.function(_quantity_delivered_get,string='Delivered Quantity',type="char",size="64",method=True,readonly=True),
        'quantity_real' : fields.function(_quantity_real_get,string='Real Quantity',type="char",size="64",method=True,readonly=True),
        'starting_mail_price' : fields.float('Starting Mail Price',digits=(16,2)),
        'customer_pricelist_id':fields.many2one('product.pricelist','Items Pricelist', required=False),
        'forwarding_charges' : fields.float('Forwarding Charges', digits=(16,2)),
        'notes':fields.text('Notes'),
        'analytic_account_id' : fields.many2one('account.analytic.account','Analytic Account', ondelete='cascade'),
        'product_ids' : fields.one2many('dm.product', 'proposition_id', 'Catalogue'),
#        'product_ids' : fields.many2many('dm.product', 'proposition_product_rel', 'proposition_id', 'product_id', 'Catalogue'),
        'payment_methods' : fields.many2many('account.journal','campaign_payment_method_rel','proposition_id','journal_id','Payment Methods',domain=[('type','=','cash')]),
        'keep_segments' : fields.boolean('Keep Segments'),
        'force_sm_price' : fields.boolean('Force Starting Mail Price'),
        'sm_price' : fields.float('Starting Mail Price', digits=(16,2)),
#        'prices_prog_id' : fields.many2one('dm.campaign.proposition.prices_progression', 'Prices Progression'),
        'manufacturing_costs': fields.float('Manufacturing Costs',digits=(16,2)),
    }

    _defaults = {
        'proposition_type' : lambda *a : 'init',
        'date_start' : _default_camp_date,
    }

    def _check(self, cr, uid, ids=False, context={}):
        '''
        Function called by the scheduler to create workitem from the segments of propositions.
        '''
        ids = self.search(cr,uid,[('date_start','=',time.strftime('%Y-%m-%d %H:%M:%S'))])
        for id in ids:
            res = self.browse(cr,uid,[id])[0]
            offer_step_id = self.pool.get('dm.offer.step').search(cr,uid,[('offer_id','=',res.camp_id.offer_id.id),('flow_start','=',True)])
            if offer_step_id :
                for segment in res.segment_ids:
                    vals = {'step_id':offer_step_id[0],'segment_id':segment.id}
                    new_id = self.pool.get('dm.offer.step.workitem').create(cr,uid,vals)
        return True

dm_campaign_proposition()

class dm_campaign_proposition_segment(osv.osv):

    _name = "dm.campaign.proposition.segment"
    _inherits = {'account.analytic.account': 'analytic_account_id'}
    _description = "Segment"

    def _check_char(self, cr, uid, ids):
        segment = self.browse(cr,uid,ids)[0]
        if not segment.quantity_ordered:
            return True
        return segment.quantity_ordered.isdigit() or segment.quantity_ordered=='AAA'

    _columns = {
        'proposition_id' : fields.many2one('dm.campaign.proposition','Proposition', readonly=True, ondelete='cascade'),
        'file_id': fields.many2one('dm.customer.file','File'),
        'quantity_ordered' : fields.char('Ordered Quantity', size=16),
        'quantity_delivered' : fields.integer('Delivered Quantity'),
        'quantity_real' : fields.integer('Real Quantity'),
        'split_id' : fields.many2one('dm.campaign.proposition.segment','Split'),
        'start_census' :fields.integer('Start Census'),
        'end_census' : fields.integer('End Census'),
        'deduplication_level' : fields.integer('Deduplication Level'),
        'active' : fields.boolean('Active'),
        'reuse_id' : fields.many2one('dm.campaign.proposition.segment','Reuse'),
        'analytic_account_id' : fields.many2one('account.analytic.account','Analytic Account', ondelete='cascade'),
        'note' : fields.text('Notes'),
        'manufacturing_costs': fields.float('Manufacturing Costs',digits=(16,2)),
        'segmentation_criteria': fields.text('Segmentation Criteria'),
    }
    _order = 'deduplication_level'

    _default = {
        'quantity_ordered': lambda *a: '0',
    }

    _constraints = [
        (_check_char, "Error ! Quantity of segment can only be integer or 'AAA'", ['quantity_ordered'])
    ]

dm_campaign_proposition_segment()

class dm_campaign_delay(osv.osv):
    _name = "dm.campaign.delay"
    _columns = {
        'name' : fields.char('Name', size=64, required=True),
        'value' : fields.integer('Value'),
        'proposition_id' : fields.many2one('dm.campaign.proposition', 'Proposition')
    }

dm_campaign_delay()


PURCHASE_LINE_TRIGGERS = [
    ('draft','At Draft'),
    ('open','At Open'),
    ('planned','At Planning'),
    ('close','At Close'),
    ('manual','Manual'),
]

PURCHASE_LINE_STATES = [
    ('pending','Pending'),
    ('requested','Quotations Requested'),
    ('ordered','Ordered'),
    ('delivered','Delivered'),
]

PURCHASE_LINE_TYPES = [
    ('manufacturing','Manufacturing'),
    ('items','Items'),
    ('customer_file','Customer Files'),
    ('translation','Translation'),
]

class dm_campaign_purchase_line(osv.osv):
    _name = 'dm.campaign.purchase_line'
    _rec_name = 'product_id'

    def _get_uom_id(self, cr, uid, *args):
        cr.execute('select id from product_uom order by id limit 1')
        res = cr.fetchone()
        return res and res[0] or False

    def quantity_get(self,cr, uid, ids, *args):
        value = {}
        quantity = 0

        pline = self.browse(cr, uid, ids)[0]
        if not pline.campaign_id:
            raise  osv.except_osv('Warning', "You must first save this Purchase Line and the campaign before using this button")

        if pline.type == 'customer_file':
            for propo in pline.campaign_id.proposition_ids:
                for segment in propo.segment_ids:
                    if segment.quantity_ordered:
                        if segment.quantity_ordered != 'AAA':
                            quantity += int(segment.quantity_ordered)
                        else:
                            quantity = 999999
                            break
        elif pline.type == 'manufacturing' or pline.type == 'items':
            for propo in pline.campaign_id.proposition_ids:
                if not propo.segment_ids:
                    raise osv.except_osv('Warning',
                        "There's no segment defined for this commercial proposition: %s" % (propo.name,) )
                for segment in propo.segment_ids:
                    if not segment.quantity_real:
                        raise osv.except_osv('Warning',
                            "There's no real quantity defined for this segment : %s" % (segment.name,) )
                    quantity += int(segment.quantity_real)
        elif pline.type == 'translation':
            for step in pline.campaign_id.offer_id.step_ids:
                if step.doc_number:
                    quantity += step.doc_number

        pline.write({'quantity':quantity})

        return True


    def po_generate(self,cr, uid, ids, *args):
        plines = self.browse(cr, uid ,ids)
        if not plines:
            raise  osv.except_osv('Warning', "There's no purchase lines defined for this campaign")
        for pline in plines:
            if pline.state != 'done':
                if not pline.product_id.seller_ids:
                    raise  osv.except_osv('Warning', "There's no supplier defined for this product : %s" % (pline.product_id.name,) )

                # Create a po / supplier
                for supplier in pline.product_id.seller_ids:
                    partner_id = supplier.id
                    partner = supplier.name

                    address_id = self.pool.get('res.partner').address_get(cr, uid, [partner.id], ['default'])['default']
                    if not address_id:
                        raise osv.except_osv('Warning', "There's no delivery address defined for this partner : %s" % (partner.name,) )
                    pricelist_id = partner.property_product_pricelist_purchase.id
                    if not pricelist_id:
                        raise osv.except_osv('Warning', "There's no purchase pricelist defined for this partner : %s" % (partner.name,) )
                    price = self.pool.get('product.pricelist').price_get(cr, uid, [pricelist_id], pline.product_id.id, pline.quantity, False, {'uom': pline.uom_id.id})[pricelist_id]
                    print "pline.date_planned : ",pline.date_planned
                    newdate = DateTime.strptime(pline.date_planned, '%Y-%m-%d %H:%M:%S') - DateTime.RelativeDateTime(days=pline.product_id.product_tmpl_id.seller_delay or 0.0)
                    print "newdate :",newdate.strftime('%Y-%m-%d %H:%M:%S')

                    if not pline.campaign_id.offer_id:
                        raise osv.except_osv('Warning', "There's no offer defined for this campaign : %s" % (pline.campaign_id.name,) )
                    if not pline.campaign_id.proposition_ids:
                        raise osv.except_osv('Warning', "There's no proposition defined for this campaign : %s" % (pline.campaign_id.name,) )

                    # Get constraints
                    constraints = []
                    if pline.type == 'manufacturing':
                        for step in pline.campaign_id.offer_id.step_ids:
                            for const in step.manufacturing_constraint_ids:
                                if pline.campaign_id.country_id in const.country_ids or not const.country_ids:
                                    constraints.append("---------------------------------------------------------------------------")
                                    constraints.append(const.name)
                                    constraints.append(const.constraint)
                    elif pline.type == 'items':
                        raise osv.except_osv('Warning', "Purchase of items is not yet implemented")
                        for step in pline.campaign_id.offer_id.step_ids:
                            for item in step.product_ids:
                                constraints.append("---------------------------------------------------------------------------")
                                constraints.append(item.product_id.name)
                                constraints.append(item.purchase_constraints)
                    elif pline.type == 'customer_file':
                        raise osv.except_osv('Warning', "Purchase of customers files is not yet implemented")
                    elif pline.type == 'translation':
                        if not pline.campaign_id.lang_id:
                            raise osv.except_osv('Warning', "There's no language defined for this campaign : %s" % (pline.campaign_id.name,) )
                        if pline.notes:
                            constraints.append(pline.notes)
                        else:
                            constraints.append(' ')
                    elif pline.type == False:
                        if pline.notes:
                            constraints.append(pline.notes)
                        else:
                            constraints.append(' ')

                    # Create po
                    purchase_id = self.pool.get('purchase.order').create(cr, uid, {
                        'origin': pline.campaign_id.name,
                        'partner_id': partner.id,
                        'partner_address_id': address_id,
                        'location_id': 1,
                        'pricelist_id': pricelist_id,
                        'notes': "\n".join(constraints),
                        'dm_campaign_purchase_line': pline.id
                    })

                    ''' If Translation Order => Get Number of documents in Offer '''
                    if pline.type == 'translation':
                        if pline.quantity == 0:
                            raise osv.except_osv('Warning',
                                "There's no documents for this offer: %s" % (pline.campaign_id.offer_id.name,) )
                        line = self.pool.get('purchase.order.line').create(cr, uid, {
                           'order_id': purchase_id,
                           'name': pline.campaign_id.name,
                           'product_qty': pline.quantity,
                           'product_id': pline.product_id.id,
                           'product_uom': pline.uom_id.id,
                           'price_unit': price,
                           'date_planned': newdate.strftime('%Y-%m-%d %H:%M:%S'),
                           'taxes_id': [(6, 0, [x.id for x in pline.product_id.product_tmpl_id.supplier_taxes_id])],
                           'account_analytic_id': pline.campaign_id.analytic_account_id,
                        })
                    else:
                        ''' Create po lines for each proposition'''
                        lines = []
                        for propo in pline.campaign_id.proposition_ids:
                            quantity = 0
                            ''' If Customer File Order => Get Ordered Quantity '''
                            ''' If Manufacturing or Items Order => Get Real Quantity '''
                            if pline.type == 'customer_file':
                                for segment in propo.segment_ids:
                                    if segment.quantity_ordered:
                                        if segment.quantity_ordered != 'AAA':
                                            quantity += int(segment.quantity_ordered)
                                        else:
                                            quantity = 999999
                                            break
                            elif pline.type == 'manufacturing' or pline.type == 'items':
                                if not propo.segment_ids:
                                    raise osv.except_osv('Warning',
                                        "There's no segment defined for this commercial proposition: %s" % (propo.name,) )
                                for segment in propo.segment_ids:
                                    if not segment.quantity_real:
                                        raise osv.except_osv('Warning',
                                            "There's no Ordered Quantity defined for the segment %s in proposition %s" % (segment.name,propo.name,) )
                                    quantity += int(segment.quantity_real)
                            print "DEBUG - Segment Quantity : ",quantity

                            line = self.pool.get('purchase.order.line').create(cr, uid, {
                               'order_id': purchase_id,
                               'name': propo.name,
                               'product_qty': quantity,
                               'product_id': pline.product_id.id,
                               'product_uom': pline.uom_id.id,
                               'price_unit': price,
                               'date_planned': newdate.strftime('%Y-%m-%d %H:%M:%S'),
                               'taxes_id': [(6, 0, [x.id for x in pline.product_id.product_tmpl_id.supplier_taxes_id])],
                               'account_analytic_id': propo.analytic_account_id.id,
#                       'move_dest_id': res_id,
                            })
                    self.write(cr, uid, [pline.id], {'state':'requested'})

                    '''
                    # Set campaign supervision states
                    if pline.type == 'translation':
                        pline.campaign_id.write({'translation_state':'inprogress'})
                    elif pline.type == 'manufacturing':
                        pline.campaign_id.write({'manufacturing_state':'inprogress'})
                    elif pline.type == 'items':
                        pline.campaign_id.write({'items_state':'inprogress'})
                    elif pline.type == 'customer_file':
                        pline.campaign_id.write({'customer_file_state':'inprogress'})
                    '''

        return True

    def _default_date(self, cr, uid, context={}):
        if 'date1' in context and context['date1']:
            dd = context['date1']
            newdate =  DateTime.strptime(dd + ' 09:00:00','%Y-%m-%d %H:%M:%S')
            print "From _default_date : ",newdate.strftime('%Y-%m-%d %H:%M:%S')
            return newdate.strftime('%Y-%m-%d %H:%M:%S')
        return []

    _columns = {
        'campaign_id': fields.many2one('dm.campaign', 'Campaign'),
        'product_id' : fields.many2one('product.product', 'Product', required=True, context={'flag':True}),
        'quantity' : fields.integer('Quantity', readonly=False, required=True),
        'uom_id' : fields.many2one('product.uom','UOM', required=True),
        'date_order': fields.datetime('Order date', readonly=True),
        'date_planned': fields.datetime('Scheduled date', required=True),
        'date_delivery': fields.datetime('Delivery date', readonly=True),
        'trigger' : fields.selection(PURCHASE_LINE_TRIGGERS, 'Trigger'),
        'type' : fields.selection(PURCHASE_LINE_TYPES, 'Type'),
        'purchase_order_ids' : fields.one2many('purchase.order','dm_campaign_purchase_line','DM Campaign Purchase Line'),
        'notes': fields.text('Notes'),
        'state' : fields.selection(PURCHASE_LINE_STATES, 'State',readonly=True),
    }

    _defaults = {
#        'date_planned' : _default_date,
        'quantity' : lambda *a : 0,
        'uom_id' : _get_uom_id,
        'trigger': lambda *a : 'manual',
        'state': lambda *a : 'pending',
    }
dm_campaign_purchase_line()


class dm_campaign_proposition_prices_progression(osv.osv):
    _name = 'dm.campaign.proposition.prices_progression'
    _columns = {
        'name' : fields.char('Name', size=64, required=True),
        'fixed_prog' : fields.float('Fixed Prices Progression', digits=(16,2)),
        'percent_prog' : fields.float('Percentage Prices Progression', digits=(16,2)),
    }
dm_campaign_proposition_prices_progression()

class dm_campaign_dtp_dates(osv.osv):
    _name = 'dm.campaign.dtp_dates'
    _columns = {
        'name' : fields.char('Name', size=64, required=True),
        'theorical_date' : fields.date('Theorical Dates'),
        'reviewed_date' : fields.date('Reviewed Dates'),
        'real_date' : fields.date('Real Dates'),
        'planned_date' : fields.date('Planned Dates'),
        'campaign_id' : fields.many2one('dm.campaign','Campaign'),
        'template' : fields.boolean('Set as default for new campaigns'),
    }
    _defaults = {
        'template': lambda *a: False,
    }
dm_campaign_dtp_dates()

class Country(osv.osv):
    _name = 'res.country'
    _inherit = 'res.country'
    _columns = {
                'main_language' : fields.many2one('res.lang','Main Language',ondelete='cascade',),
                'main_currency' : fields.many2one('res.currency','Main Currency',ondelete='cascade'),
    }
Country()

class res_partner(osv.osv):
    _name = "res.partner"
    _inherit="res.partner"

    def _default_category(self, cr, uid, context={}):
        if 'category' in context and context['category']:
            id_cat = self.pool.get('res.partner.category').search(cr,uid,[('name','ilike',context['category'])])[0]
            return [id_cat]
        return []

    _defaults = {
        'category_id': _default_category,
    }
res_partner()

class purchase_order(osv.osv):
    _name = 'purchase.order'
    _inherit = 'purchase.order'
    _columns = {
        'dm_campaign_purchase_line' : fields.many2one('dm.campaign.purchase_line','DM Campaign Purchase Line'),
    }
purchase_order()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
