from turbogears import expose
from turbogears import controllers
import cherrypy

from erpcomparator import rpc
from erpcomparator import common

class Graph(controllers.Controller):
    
    @expose(template="erpcomparator.subcontrollers.templates.graph")
    def index(self):
        
        proxy_item = rpc.RPCProxy('comparison.item')
        item_ids = proxy_item.search([])
        
        res = proxy_item.read(item_ids, ['name'])
        titles = []
        
        for r in res:
            title = {}
            title['name'] = r['name']
            title['id'] = r['id']
            titles += [title]
        
        root = []
        
        proxy_factor = rpc.RPCProxy('comparison.factor')
        factors = proxy_factor.search([('parent_id', '=', False)])
        root_factors = proxy_factor.read(factors, ['name'])
        
        for r in root_factors:
            root += [r]
        
        return dict(titles=titles, root_factor=root)

    @expose('json')
    def radar(self, **kw):
        
        item_ids = kw.get('ids')
        item_ids = item_ids and eval(str(item_ids))
        
        factor_name = kw.get('factor_name')
        factor_name = factor_name.replace('@', '&')
        
        proxy_factor = rpc.RPCProxy('comparison.factor')
        parent_list = proxy_factor.search([('name', '=', factor_name)])
        child_ids = proxy_factor.read(parent_list, ['child_ids'])
        child_ids = child_ids[0].get('child_ids')
        
        child_list = proxy_factor.read(child_ids, ['name'])
        
        child_name = []
        for ch in child_list:
            child_name += [ch['name']]

        elem = []
        elements = {}
        elements["elements"] = [] #Required
        elements["title"] = {}   #Optional
        elements["radar_axis"] = {} #Required
        elements["tooltip"] = {} #Depend On Choice
        elements["bg_colour"] = "#ffffff" #Optional
        
        ChartColors = ['#c4a000', '#ce5c00', '#8f5902', '#4e9a06', '#204a87', '#5c3566', '#a40000', '#babdb6', '#2e3436'];
        proxy_item = rpc.RPCProxy('comparison.item')
        item_name = proxy_item.read(item_ids, ['name'])
        
        proxy_res = rpc.RPCProxy('comparison.factor.result')
        rids = proxy_res.search([('factor_id', 'in', child_ids)])            
        factor_res = proxy_res.read(rids)
        
        value = []
        
        for item in item_name:
            val = []
            for factor in factor_res:
                if factor.get('item_id')[1] == item['name']:
                    val += [factor.get('result')]
            
            value += [val]
        
        for n, j in enumerate(item_name):
            if n%2==0:
                elem.append({'type': 'line_hollow', 
                             "values": value[n],
                             "halo_size": 2,
                             "width": 1,
                             "dot-size": 2,
                             "colour": ChartColors[n],
                             "tip": "",
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
                              "tip": "",
                              "text": str(j['name']),
                              "font-size": 12,
                              "loop": True})
                
            elements["elements"] = elem
        
        elements["title"] = {"text":"Comparison Chart","style": "{font-size: 15px; color: #50284A; text-align: center;}"}
        elements["radar_axis"] = {
                                  "max":100.0,
                                  "colour": "#DAD5E0",
                                  "grid-colour":"#DAD5E0",
                                  "labels": {
                                             "labels": [],
                                             "colour": "#9F819F"
                                             },
                                  "spoke-labels": {
                                                   "labels": [ch for ch in child_name],
                                                   "colour": "#5c3566"
                                                   }
                                  }
       
        elements["tooltip"] = {"mouse": 1}
        elements["bgcolor"] = "#ffffff"
        
        return elements