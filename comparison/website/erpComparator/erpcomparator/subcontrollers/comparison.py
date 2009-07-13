
import xml.dom.minidom

from turbojson import jsonify
from turbogears import expose
from turbogears import controllers
from turbogears import url as tg_url
from turbogears import config
import cherrypy
import math

from erpcomparator import rpc
from erpcomparator import tools
from erpcomparator import common
from erpcomparator.tinyres import TinyResource

class Comparison(controllers.Controller, TinyResource):
    
    @expose(template="erpcomparator.subcontrollers.templates.comparison")
    def default(self, args=None, **kw):
        
#        lang_proxy = rpc.RPCProxy('res.lang')
#        if(kw.get('lang_code')):
#            language = kw['lang_code']
#            context = rpc.session.context
#              
#            context['lang'] = language
#            lang_id = lang_proxy.search([])
#            lang_data = lang_proxy.read(lang_id, [], rpc.session.context)
#            cherrypy.session['language'] = context['lang']
#            cherrypy.session['lang_data'] = lang_data
#        else:
#            search_lang = lang_proxy.search([])
#            lang_data = lang_proxy.read(search_lang, [], rpc.session.context)
#            language  = 'en_US'
#            context = rpc.session.context
#            context['lang'] = language
#        
#        if(cherrypy.session.has_key('language')):
#             cherrypy.session['language']
#             cherrypy.session['lang_data']
#        else:
#            cherrypy.session['language'] = context['lang']
#            cherrypy.session['lang_data'] = lang_data
#      
        selected_items = kw.get('ids', [])
        selected_items = selected_items and eval(str(selected_items))
        
        if args and not selected_items:
            pack_proxy = rpc.RPCProxy('evaluation.pack')
            packs = pack_proxy.search([('name', '=', args)], 0, 0, 0, rpc.session.context)
            item_ids = pack_proxy.read(packs, ['item_ids'], rpc.session.context)
            selected_items = item_ids[0].get('item_ids')
        
        user_info = cherrypy.session.get('login_info', '')
        
        context = rpc.session.context
        model = 'comparison.factor'
        proxy = rpc.RPCProxy(model)
        
        domain = [('parent_id', '=', False)]
        ids = proxy.search(domain, 0, 0, 0, context)
        
        view = proxy.fields_view_get(False, 'tree', context)
        fields = proxy.fields_get(False, context)
        
        field_parent = view.get("field_parent") or 'child_ids'
        
        dom = xml.dom.minidom.parseString(view['arch'].encode('utf-8'))
        
        root = dom.childNodes[0]
        attrs = tools.node_attributes(root)
        
        self.head = []
        self.parse(root, fields)
        
        self.headers = []
        
        add_factor = {}
        add_factor['name'] = "add_factor"
        add_factor['type'] = "image"
        add_factor['string'] = ''
        add_factor['colspan'] = 2
        
        sh_graph = {}
        sh_graph['name'] = 'show_graph'
        sh_graph['type'] = 'image'
        sh_graph['string'] = ''
        sh_graph['colspan'] = -1
        
        incr = {}
        incr['name'] = 'incr'
        incr['type'] = 'image'
        incr['string'] = ''
        incr['colspan'] = -1
        
        decr = {}
        decr['name'] = 'decr'
        decr['type'] = 'image'
        decr['string'] = ''
        decr['colspan'] = -1
        
        self.headers += [self.head[0]]
        self.headers += [add_factor]
        self.headers += [sh_graph]
        self.headers += [self.head[1]]
        self.headers += [incr]
        self.headers += [decr]
        
        fields = []
     
        item_model = 'comparison.item'
        proxy_item = rpc.RPCProxy(item_model)
        item_ids = proxy_item.search([], 0, 0, 0, context)
        
        res = proxy_item.read(item_ids, ['name', 'code', 'load_default'])
        
        titles = []
        ses_id = []
        for r in res:
            title = {}
            title['sel'] = False
            if selected_items:
                ses_id = selected_items
                item = {}
                for s in selected_items:
                    if r['id'] == s:
                        item['id'] = r['id']
                        item['type'] = 'url'
                        item['string'] = r['name']
                        item['name'] = r['name']
                        item['code'] = r['code']
                        
                        title['sel'] = True
                        title['load'] = r['load_default']
                        
                        self.headers += [item]
            
            elif r['load_default']:
                item = {}
                item['id'] = r['id']
                item['type'] = 'url'
                item['string'] = r['name']
                item['name'] = r['name']
                item['code'] = r['code']
                self.headers += [item]
                ses_id.append(r['id'])
            cherrypy.session['selected_items'] = ses_id
            title['name'] = r['name']
            title['id'] = r['id']
            title['code'] = r['code']
            title['load'] = r['load_default']
            titles += [title]
            
        sel_ids=[]
        for t in titles:
            if t['load'] or t['sel']:
                sel_ids += [t['id']]
        
#        cherrypy.response.simple_cookie['selected_items'] = sel_ids
        
        for field in self.headers:
            if field['name'] == 'name' or field['name'] == 'ponderation':
                fields += [field['name']]
        
        fields = jsonify.encode(fields)
        icon_name = self.headers[0].get('icon')
#        if kw.has_key('all'):
#            self.url = '/comparison/data'
#            self.url_params = dict(model=model, 
#                                    ids=ids,
#                                    fields=ustr(fields), 
#                                    domain=ustr(domain), 
##                                    context=ustr(context), 
#                                    field_parent=field_parent,
#                                    icon_name=icon_name,all = kw.get('all'))
#        else:
        self.url = '/comparison/data'
        self.url_params = dict(model=model, 
                                ids=ids,
                                fields=ustr(fields), 
                                domain=ustr(domain), 
                                context=ustr(context), 
                                field_parent=field_parent,
                                icon_name=icon_name)
        
        def _jsonify(obj):
            for k, v in obj.items():
                if isinstance(v, dict):
                    obj[k] = _jsonify(v)
            
            return jsonify.encode(obj)
        
        self.url_params = _jsonify(self.url_params)
        self.headers = jsonify.encode(self.headers)
        return dict(headers=self.headers, url_params=self.url_params, url=self.url, titles=titles, selected_items=selected_items)
    
    def check_data(self):
        criterions = None
        feedbacks = None
        
        model = 'comparison.factor'
        proxy = rpc.RPCProxy(model)
        criterions = proxy.search([])
        
        criterions = len(criterions)
                
        vproxy = rpc.RPCProxy('comparison.vote')
        feedbacks = vproxy.search([])
        feedbacks = len(feedbacks)
        
        user_info = cherrypy.session.get('login_info', None)
        
        return criterions, feedbacks, user_info
    
    @expose(template="erpcomparator.subcontrollers.templates.new_factor")
    def add_factor(self, **kw):
        
        user_info = cherrypy.session.get('login_info', '')
        
        id = kw.get('id')
        error = ''
        p_name = 'No Parent'
        child_type = 'view'
        model = "comparison.factor"
        
        proxy = rpc.RPCProxy(model)
        res = proxy.read([id], ['name', 'parent_id', 'child_ids'], rpc.session.context)
            
        parent = res[0].get('name')
        p_id = id
        
        count = range(0, 21)
        count = [c/float(10) for c in count]
        
        if not user_info:
            return dict(error="You are not logged in...", count=count, parent_id=p_id, parent_name=parent)
        else:
            return dict(error=error, count=count, parent_id=p_id, parent_name=parent)
    
    @expose('json')
    def voting(self, **kw):
        
        id = kw.get('id')
        pond_val = kw.get('pond_val')
        
        value = None
        
        user_info = cherrypy.session.get('login_info', '')
        
        if not user_info:
            return dict(value=value, error="You are not logged in...")
        
        model = "comparison.factor"
        proxy = rpc.RPCProxy(model)
        res = proxy.read([id], ['name', 'ponderation'], rpc.session.context)
        name = res[0]['name']
        pond = res[0]['ponderation']
        
        smodel = "comparison.ponderation.suggestion" 
        sproxy = rpc.RPCProxy(smodel)
        
        if pond_val == 'incr':
            if pond > 0.0:
                pond = pond + 0.1
                effect = 'positive'
        else:
            if pond > 0.0:
                pond = pond - 0.1
                effect = 'negative'
        
        user_proxy = rpc.RPCProxy('comparison.user')
        user_id = user_proxy.search([('name', '=', user_info)])
        user_id = user_id[0]
        
        try:
            value = sproxy.create({'factor_id': id, 'user_id': user_id, 'ponderation': pond, 'effect':effect})
        except Exception, e:
            return dict(value=value, error=str(e))
        
        return dict(value=value, error="")
        
    @expose(template="erpcomparator.subcontrollers.templates.item_voting")
    def item_voting(self, **kw):
        
        user_info = cherrypy.session.get('login_info', '')
        
        id = kw.get('id')
        item = kw.get('header')
        
        iproxy = rpc.RPCProxy('comparison.item')
        item_id = iproxy.search([('name', '=', item)], 0, 0, 0, rpc.session.context)[0]
        
        fmodel = "comparison.factor"
        proxy = rpc.RPCProxy(fmodel)
        fres = proxy.read([id], [], rpc.session.context)
        
        factor_id = fres[0]['name']
        child_ids =  fres[0]['child_ids']
        
        child = []
        for ch in child_ids:
            chid = {}
            chd = proxy.read([ch], [], rpc.session.context)
            chid['name'] = chd[0]['name']
            chid['id'] = ch
            chid['type'] = chd[0]['type']
            if chid['type'] == 'criterion':
                child += [chid]
        
        vproxy = rpc.RPCProxy('comparison.vote.values')
        val = vproxy.search([], 0, 0, 0, rpc.session.context)
        value_name = vproxy.read(val, ['name'], rpc.session.context)
        
        if not user_info:
            return dict(item_id=item_id, item=item, child=child, factor_id=factor_id, value_name=value_name, id=id, error="You are not logged in...")
        else:
            return dict(item_id=item_id, item=item, child=child, factor_id=factor_id, value_name=value_name, id=id, error="")
    
    @expose('json')
    def update_item_voting(self, **kw):
        
        user_info = cherrypy.session.get('login_info', '')
        
        if not user_info:
            return dict(error="You are not logged in...")
        
        vals = kw.get('_terp_values', '')
        vals = vals.split('!')
        vals = [v.split('|') for v in vals]
        vals = [(x.split(','), y.split(','), z.split(','), w.split(',')) for x, y, z, w in vals]
        vals = [dict(v) for v in vals]
        
        list = []
        
        user_proxy = rpc.RPCProxy('comparison.user')
        user_id = user_proxy.search([('name', '=', user_info)])
        
        for v in vals:
            items = {}
            if v.get('score_id') != '0' and user_id:
                items['score_id'] = v.get('score_id')
                items['factor_id'] = v.get('id')
                items['item_id'] = v.get('item_id')
                items['note'] = str(v.get('note'))
                items['user_id'] = user_id[0]
            
                list += [items]
                
        vproxy = rpc.RPCProxy('comparison.vote.values')
        
        vid = vproxy.search([], 0, 0, 0, rpc.session.context)
        value_name = vproxy.read(vid, ['name'], rpc.session.context)
                
        smodel = "comparison.vote"
        sproxy = rpc.RPCProxy(smodel)
        
        res = None
        
        try:
            res = sproxy.vote_create_async(list)
        except Exception, e:
            return dict(error=str(e))
        
        return dict(res=res, show_header_footer=False, error="")
    
    @expose('json')
    def data(self, model, ids=[], fields=[], field_parent=None, icon_name=None, domain=[], context={}, sort_by=None, sort_order="asc",
             factor_id=None, ponderation=None, parent_id=None, parent_name=None, ftype='',all = None):

        ids = ids or []
        
        if isinstance(ids, basestring):
            ids = [int(id) for id in ids.split(',')]
            
        res = None
        user_info = cherrypy.session.get('login_info', '')
        if parent_id:
            
            if not user_info:
                return dict(error="You are not logged in...")
            
            user_proxy = rpc.RPCProxy('comparison.user')
            user_id = user_proxy.search([('name', '=', user_info)])
            
            new_fact_proxy = rpc.RPCProxy(model)
            try:
                res = new_fact_proxy.create({'name': factor_id, 'parent_id': parent_id, 'user_id': user_id[0], 
                                         'ponderation': ponderation, 'type': ftype})
                ids = [res]
            
            except Exception, e:
                return dict(error=str(e))

        if isinstance(fields, basestring):
            fields = eval(fields)

        if isinstance(domain, basestring):
            domain = eval(domain)
            
        if isinstance(context, basestring):
            context = eval(context)

        if field_parent and field_parent not in fields:
            fields.append(field_parent)

        proxy = rpc.RPCProxy(model)
        
        ctx = context or {}
        ctx.update(rpc.session.context.copy())
        if icon_name:
            fields.append(icon_name)
        
        if not fields:
            fields = ['name', 'ponderation', 'child_ids']
        
        fact_proxy = rpc.RPCProxy('comparison.factor')      
        fields_info = proxy.fields_get(fields, ctx)
        result = proxy.read(ids, fields, ctx)
        prx = rpc.RPCProxy('comparison.factor.result')
        rids = prx.search([('factor_id', 'in', ids)], 0, 0, 0, ctx)            
        factor_res = prx.read(rids, [], ctx)
        
        c_ids = fact_proxy.search([('type', '!=', 'view'), ('id', 'in', ids)], 0, 0, 0, ctx)
        p_ids = fact_proxy.search([('type', '!=', 'view'), ('parent_id', 'in', ids)], 0, 0, 0, ctx)
        parent_ids = fact_proxy.read(p_ids, ['parent_id'], ctx)
        child_ids = fact_proxy.read(c_ids, ['id'], ctx)
        
        if sort_by:
            result.sort(lambda a,b: self.sort_callback(a, b, sort_by, sort_order))

        # formate the data
        for field in fields:

            if fields_info[field]['type'] in ('float', 'integer'):
                for x in result:
                    if x[field]:
                        x[field] = '%s'%(x[field])

            if fields_info[field]['type'] in ('date',):
                for x in result:
                    if x[field]:
                        date = time.strptime(x[field], DT_FORMAT)
                        x[field] = time.strftime('%x', date)

            if fields_info[field]['type'] in ('datetime',):
                for x in result:
                    if x[field]:
                        date = time.strptime(x[field], DHM_FORMAT)
                        x[field] = time.strftime('%x %H:%M:%S', date)

            if fields_info[field]['type'] in ('one2one', 'many2one'):
                for x in result:
                    if x[field]:
                        x[field] = x[field][1]

            if fields_info[field]['type'] in ('selection'):
                for x in result:
                    if x[field]:
                        x[field] = dict(fields_info[field]['selection']).get(x[field], '')

        records = []

        for item in result:
         
            # empty string instead of bool and None
            for k, v in item.items():
                if v==None or (v==False and type(v)==bool):
                    item[k] = ''
                    
            record = {}
            for i, j in item.items():
                for r in factor_res:
                    if j == r.get('factor_id')[1]:
                        if r.get('votes') > 0.0:
                            item[r.get('item_id')[1]] = '%d%%' % math.floor(r.get('result'))
                        else:
                            item[r.get('item_id')[1]] = "No Vote"
                        if r.get('factor_id')[0] in [v.get('parent_id')[0] for v in parent_ids]:
                            item[r.get('item_id')[1]] += '|' + "open_item_vote(%s, '%s');" % (r.get('factor_id')[0], r.get('item_id')[1]) + '|' + r.get('factor_id')[1]
                        if r.get('factor_id')[0] in [v1.get('id') for v1 in child_ids]:
                            item[r.get('item_id')[1]] += '-' + r.get('factor_id')[1]
                        else:
                            item['add_factor'] = '/static/images/treegrid/gtk-edit.png'
                            item['show_graph'] = '/static/images/treegrid/graph.png'
            
                    item['incr'] = '/static/images/increase.png'
                    item['decr'] = '/static/images/decrease.png'
            
                    
            if res:
                record['id'] = res
            else:
                record['id'] = item.pop('id') or id
                
            record['target'] = None

            if item['ponderation']:
                item['ponderation'] = '%.2f' % float(item['ponderation'] or ponderation) + '@'
            else:
                item['ponderation'] = '0.00'
                    
            if icon_name and item.get(icon_name):
                icon = item.pop(icon_name)
                record['icon'] = icons.get_icon(icon)

                if icon == 'STOCK_OPEN':
                    record['action'] = None

            record['children'] = []
            
            if item['child_ids']:
                record['children'] = item.pop('child_ids') or None

            if field_parent and field_parent in item:
                record['children'] = item.pop(field_parent) or None
            
            record['items'] = item
            records += [record]
            
        return dict(records=records)
    
    def parse(self, root, fields=None):
        for node in root.childNodes:

            if not node.nodeType==node.ELEMENT_NODE:
                continue

            attrs = tools.node_attributes(node)

            field = fields.get(attrs['name'])
            field.update(attrs)
            
            if field['name'] == 'name' or field['name'] == 'ponderation':
                if field['name'] == 'ponderation':
                    field['type'] = 'url'
                    field['colspan'] = 3
                    
                self.head += [field]