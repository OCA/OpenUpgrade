
from turbogears import expose
from turbogears import controllers

import cherrypy
import urllib

from erpcomparator import rpc
from erpcomparator import common
from erpcomparator.tinyres import TinyResource

class Graph(controllers.Controller, TinyResource):
    
    @expose(template="erpcomparator.subcontrollers.templates.graph")
    def index(self, **kw):
        
      
        ctx = rpc.session.context.copy()
        ctx.update(ctx or {})

        
        proxy_factor = rpc.RPCProxy('comparison.factor')
        
        view_factor_id = kw.get('view_id', [])
        parent_name = kw.get('parent_name')
        
        sel_factor_id = []
        if parent_name:
            parent_name = parent_name.replace('@', '&')
            sel_factor_id = proxy_factor.search([('name', '=', parent_name)], 0, 0, 0, ctx)
        
        proxy_item = rpc.RPCProxy('comparison.item')
        item_ids = proxy_item.search([], 0, 0, 0, ctx)
        res = proxy_item.read(item_ids, ['name'], ctx)
 
        titles = []
        factors = []
        
        summary = {}
        parent_child = []
        
        selected_items = []
        
        if cherrypy.session.has_key('selected_items'):
            selected_items = cherrypy.session['selected_items']
            selected_items = selected_items and eval(str(selected_items))
        for r in res:
            title = {}
            title['sel'] = False
            if selected_items:
                for s in selected_items:
                    if r['id'] == s:
                        title['sel'] = True
            
            title['name'] = r['name']
            title['id'] = r['id']
            titles += [title]
        
#        if view_factor_id:
#            view_factors = proxy_factor.search([('id', '=', [view_factor_id])])
#        else:
        factors = proxy_factor.search([('parent_id', '=', False)], 0, 0, 0, ctx)
        parents = proxy_factor.read(factors, ['id', 'name'], ctx)
      
        for pch in parents:
            fact = proxy_factor.search([('id', '=', [pch['id']])], 0, 0, 0, ctx)
            parent_child += proxy_factor.read(fact, ['child_ids'], ctx)
        
        all_child = []
        
        for ch in parent_child:
            pname = proxy_factor.read(ch['id'], ['name'], ctx)
            if ch.get('child_ids'):
                for c in ch['child_ids']:
                    child = {}
                    level2 = proxy_factor.read(c, ['name'], ctx)
                    child['name'] = pname.get('name') + '/' + level2.get('name')
                    child['id'] = level2.get('id')
                    all_child += [child]
        
        view_name = None
        
        if view_factor_id:
            view = {}
            view_id = proxy_factor.read([view_factor_id], ['name'], ctx)
            view_name = view_id[0].get('name')
            view['id'] = view_id[0].get('id')
            view['name'] = view_name
            all_child += [view]
            
        return dict(titles=titles, parents=parents, view_name=view_name, all_child=all_child, selected_items=selected_items)

    @expose('json')
    def radar(self, **kw):
        
        item_ids = kw.get('ids')
        item_ids = item_ids and eval(str(item_ids))
        
       
        ctx = rpc.session.context.copy()
        ctx.update(ctx or {})
        
        parent_name = kw.get('factor_name')
        parent_name = parent_name.replace('@', '&')
        proxy_factor = rpc.RPCProxy('comparison.factor')
        
        child_name = []
        child_ids = []
        
        if parent_name == 'Summary':
            list = proxy_factor.search([('parent_id', '=', False)], 0, 0, 0, ctx)
            ch_ids = proxy_factor.read(list, [], ctx)
            for ch in ch_ids:
                cname = {}                
                cname['name'] = ch['name'][:18]
                                
                child_ids += [ch['id']]
                child_name += [cname]
                
        else :
            if '/' in parent_name:
                parent_name = parent_name.rsplit('/')[1]
            parent_list = proxy_factor.search([('name', '=', parent_name)], 0, 0, 0, ctx)
            
            child_ids = proxy_factor.read(parent_list, ['child_ids'], ctx)
            child_ids = child_ids[0].get('child_ids')
            child_list = proxy_factor.read(child_ids, ['name'], ctx)
            for ch in child_list:
                cname = {}
                cname['name'] = ch['name'][:18]
                child_name += [cname]

        elem = []
        elements = {}
        elements["elements"] = [] #Required
        elements["title"] = {}   #Optional
        elements["radar_axis"] = {} #Required
        elements["tooltip"] = {"mouse": 2, "stroke": 1, "colour": "#000000", "background": "#ffffff"} #Depend On Choice
        elements["bg_colour"] = "#ffffff" #Optional
        
        ChartColors = ['#c4a000', '#ce5c00', '#8f5902', '#4e9a06', '#204a87', '#5c3566', '#a40000', '#babdb6', '#2e3436'];
        proxy_item = rpc.RPCProxy('comparison.item')
        item_name = proxy_item.read(item_ids, ['name'])
        
        proxy_res = rpc.RPCProxy('comparison.factor.result')
        rids = proxy_res.search([('factor_id', 'in', child_ids)], 0, 0, 0, ctx)            
        factor_res = proxy_res.read(rids, [], ctx)
        
        value = []
        
        lables = [i['name'] for i in child_name]
        for item in item_name:
            val = [0]  * len(lables)
            for factor in factor_res:
                if factor.get('item_id')[1] == item['name']:
                    val[lables.index(factor.get('factor_id')[1][:18])] = factor.get('result')/10.0
            value += [val]
            
        for n, j in enumerate(item_name):
        
            if n%2==0:
                elem.append({'type': 'line_hollow', 
                             "values": value[n],
                             "halo_size": 2,
                             "width": 1,
                             "dot-size": 2,
                             "colour": ChartColors[n],
                             "text": str(j['name']),
                             "font-size": 12,
                             "loop": True})
            else:
                elem.append({"type": "line_dot",
                              "values": value[n],
                              "halo_size": 2,
                              "width": 1,
                              "dot-size": 2,
                              "colour": ChartColors[n],
                              "text": str(j['name']),
                              "font-size": 12,
                              "loop": True})
                
            elements["elements"] = elem
        elements["title"] = {"text": parent_name, "style": "{font-size: 15px; color: #50284A; text-align: left; font-weight: bold;}"}
        elements["radar_axis"] = {
                                  "max":10,
                                  "colour": "#DAD5E0",
                                  "grid-colour":"#DAD5E0",
                                  "labels": {
                                             "labels": [],
                                             "colour": "#9F819F"
                                             },
                                  "spoke-labels": {
                                                   "labels": [ch['name'] for ch in child_name],
                                                   "colour": "#5c3566"
                                                   }
                                  }
       
#        elements["tooltip"] = {"mouse": 1}
        elements["bgcolor"] = "#ffffff"
        
        return elements