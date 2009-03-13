#!/usr/bin/python
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
import etl
import tools
from osv import osv, fields

class etl_project(osv.osv):
    _name='etl.project'
    _columns={
              'name' : fields.char('Name', size =64), 
              'job_ids' : fields.one2many('etl.job', 'project_id', 'Jobs')
    }
etl_project()

class etl_channel(osv.osv):
    _name='etl.channel'
    _columns={
              'name' : fields.char('Channel Name', size=64, required=True), 
              'code' : fields.char('Code', size=24, required=True), 
              'type' : fields.selection([('logger', 'Logger'), ('transition', 'Transition')], 'Type', required=True), 
              }
etl_channel()

class etl_transformer(osv.osv):
    _name='etl.transformer'
        
    _columns={
              'name' : fields.char('Name', size=64, required=True), 
              'tranformer_line_ids' : fields.one2many('etl.transformer.line', 'tranformer_id', 'ETL Transformer'), 
              }
    
    def create_instance(self, cr, uid, ids, context, component=None):
        trans = self.browse(cr, uid, ids)
        val = etl.transformer(trans.tranformer_line_ids) 
        context['components'][component]['transformer'] = val
        return None
    
etl_transformer()


class etl_transformer_line(osv.osv):
    _name='etl.transformer.line'
        
    _columns={
              'name' : fields.char('Name', size=64, required=True), 
              'tranformer_id' : fields.many2one('etl.transformer', 'ETL Transformer'), 
              'type' : fields.selection([('integer', 'INTEGER'), ('string', 'STRING'), ('date', 'DATE'), ('datetime', 'DATETIME'), ('time', 'TIME'), ('float', 'FLOAT'), ('long', 'LONG'), ('complex', 'COMPLEX'), ('boolean', 'BOOLEAN')], 'Type'), 
              }
    
etl_transformer_line()

class etl_connector_type(osv.osv):
    _name='etl.connector.type'
    
    _columns={
              'name' : fields.char('Name', size=64, required=True), 
              'code' : fields.char('Code', size=24, required=True), 
              'args'  : fields.text('Arguments'), 
              }
etl_connector_type()


class etl_connector(osv.osv):
    _name='etl.connector'
    
    def _get_connector_type(self, cr, uid, context={}):
            c_obj = self.pool.get('etl.connector.type')
            type_ids = c_obj.search(cr, uid, [])
            result = c_obj.read(cr, uid, type_ids, ['code', 'name'], context)
            return [(r['code'], r['name']) for r in result]
        
    _columns={
              'name' : fields.char('Connector Name', size=64, required=True), 
              'type' : fields.selection(_get_connector_type, 'Connector Type', size=64, required=True), 
              }
    
    def create_instance(self, cr, uid, ids, context , component= None):
        # logic for super create_instance
        return None
    
etl_connector()

class etl_connector_localfile(osv.osv):
    _name='etl.connector'
    _inherit='etl.connector'
        
    _columns={
              'uri' : fields.char('URL Path', size=124), 
              'bufsize' : fields.integer('Buffer Size'), 
              }
    
    def create_instance(self, cr, uid, ids , context, component= None):
        obj_connector=self.pool.get('etl.connector')
        for con in obj_connector.browse(cr, uid, [ids]):
            if con.type == 'localfile':
                val =  etl.connector.localfile(tools.config['addons_path']+con.uri, con.bufsize, encoding='utf-8')
                context['components'][component]['connector'] = val
        return super(etl_connector_localfile, self).create_instance(cr, uid, ids, context, component)
  
etl_connector_localfile()

class etl_connector_openobject(osv.osv):
    _name='etl.connector'
    _inherit='etl.connector'
    
    _columns={
              'uri' : fields.char('URL Path', size=64), 
              'db' : fields.char('Database', size=64), 
              'login' : fields.char('Login Name', size=64), 
              'passwd' : fields.char('Password', size=64), 
              'obj' : fields.char('Object', size=64), 
              'con_type' : fields.char('Connection Type', size=64), 
              }
    
    
    def onchange_type(self, cr, uid, ids, type):
        val={}
        if type and type=='openobject_connector':
            val['obj']= '/xmlrpc/object'
            val['con_type']= 'xmlrpc'
        if type and type=='localfile':
            val['obj']= ''
            val['con_type']= ''
        if type and type=='sql_connector':
            val['con_type']= 'postgres'
            val['obj']= ''
        return {'value':val}
        
    def create_instance(self, cr, uid, ids , context, component= None):
        obj_connector=self.pool.get('etl.connector')
        for con in obj_connector.browse(cr, uid, [ids]):
            if con.type == 'openobject_connector':
                val = etl.connector.openobject_connector(con.uri, cr.dbname, con.login, con.passwd, con.obj, con.con_type)
                context['components'][component]['connector'] = val
        return super(etl_connector_openobject, self).create_instance(cr, uid, ids, context, component)
        
etl_connector_openobject()

class etl_connector_sql(osv.osv):
    _name='etl.connector'
    _inherit='etl.connector'
    
    _columns={
              'host' : fields.char('Host', size=64), 
              'port' : fields.char('Port', size=64), 
              'db' : fields.char('Database', size=64), 
              'uid' : fields.char('User  ID', size=64), 
              'passwd' : fields.char('Password', size=64), 
              'con_type' : fields.char('Connection Type', size=64), 
              'sslmode' : fields.boolean('Allow SSL Mode'), 
              }
    
    def create_instance(self, cr, uid, ids , context, component= None):
        obj_connector=self.pool.get('etl.connector')
        for con in obj_connector.browse(cr, uid, [ids]):
            if con.type == 'sql_connector':
                if con.sslmode: sslmode = 'allow'
                val = connector.sql_connector(con.host, con.port, con.db, con.uid, con.passwd, sshmode , con.con_type)
                context['components'][component]['connector'] = val
        return super(etl_connector_sql, self).create_instance(cr, uid, ids, context, component)
        
etl_connector_sql()

class etl_component_type(osv.osv):
    _name='etl.component.type'
    _description = "ETL Component Type"
    
    _columns={
              'name' : fields.char('Name', size=64, required=True), 
              'code' : fields.char('Code', size=24, required=True), 
              'args'  : fields.text('Arguments'), 
              }
etl_component_type()


class etl_component(osv.osv):
    _name='etl.component'
    _description = "ETL Component"
    
    _columns={
            'name' : fields.char('Name', size=64, required=True), 
            'type' : fields.many2one('etl.component.type', 'Component Type', required=True), 
            'trans_in_ids' : fields.one2many('etl.transition', 'destination_component_id', 'Source ID'), 
            'trans_out_ids' : fields.one2many('etl.transition', 'source_component_id', 'Destination ID'), 
              }
    
    def create_instance(self, cr, uid, ids, context):
        obj_component=self.pool.get('etl.component')
        obj_trans=self.pool.get('etl.transition')
        cmp = obj_component.browse(cr, uid, ids)
        
        if not ids in context['components']:
            context['components'][ids] = {'instance':False}
            
        context['components'][cmp.id]['transitions'] = {}
        if cmp.trans_in_ids:
            for tran_in in cmp.trans_in_ids:
                obj_trans.create_instance(cr, uid, tran_in.id, context, cmp.id)
                
        if cmp.trans_out_ids:
            for tran_out in cmp.trans_out_ids:
                obj_trans.create_instance(cr, uid, tran_out.id, context, cmp.id)
        
        return None
        
etl_component()

class etl_component_control_data_count(osv.osv):
    _name='etl.component'
    _inherit = 'etl.component'
    
    def create_instance(self, cr, uid, ids, context={}):
            obj_component=self.pool.get('etl.component')
            for cmp in obj_component.browse(cr, uid, [ids]):
                if cmp.type.name == 'control.data_count':
                    context['components'][ids] = {}
                    context['components'][ids]['instance'] = etl.component.control.data_count()
            return super(etl_component_control_data_count, self).create_instance(cr, uid, ids, context)
    
etl_component_control_data_count()

class etl_component_transform_sort(osv.osv):
    _name='etl.component'
    _inherit = 'etl.component'
    
    def create_instance(self, cr, uid, ids, context={}):
            obj_component=self.pool.get('etl.component')
            for cmp in obj_component.browse(cr, uid, [ids]):
                if cmp.type.name == 'transform.sort':
                    context['components'][ids] = {}
                    context['components'][ids]['instance'] = etl.component.transform.sort('name')
            return super(etl_component_transform_sort, self).create_instance(cr, uid, ids, context)
    
etl_component_transform_sort()

class etl_component_field(osv.osv):
    _name='etl.component.field'
    _columns={
              'source_field' : fields.char('Source Field', size=124), 
              'dest_field' : fields.char('Destination Field', size=124), 
              'component_id' : fields.many2one('etl.component', 'Model'), 
              }

etl_component_field()

class etl_component_vcard_in(osv.osv):
    _name='etl.component'
    _inherit = 'etl.component'
    _description = "ETL Component"

    _columns={
            'connector_id' :  fields.many2one('etl.connector', 'Connector', domain="[('type','=',localfile)]"), 
              }
    
    def create_instance(self, cr, uid, ids, context={}):
            obj_component=self.pool.get('etl.component')
            for cmp in obj_component.browse(cr, uid, [ids]):
                if cmp.type.name == 'input.vcard_in':
                    context['components'][ids] = {}
                    context['components'][ids]['transformer'] = None
                    
                    if cmp.connector_id:
                        obj_connector = self.pool.get('etl.connector')
                        obj_connector.create_instance(cr, uid, cmp.connector_id.id, context, cmp.id)
                        conn_instance = context['components'][ids]['connector']
                        
                        val = etl.component.input.vcard_in(conn_instance, 'component.input.csv_in')
                        context['components'][ids]['instance'] = val
            return super(etl_component_vcard_in, self).create_instance(cr, uid, ids, context)
        
etl_component_vcard_in()

class etl_component_transform_map(osv.osv):
    _name = 'etl.component'
    _inherit = 'etl.component'
    
    _columns={
            'name' : fields.char('Name', size=24, required=True), 
            'transformer_id' :  fields.many2one('etl.transformer', 'Transformer'), 
            'field_ids' : fields.one2many('etl.component.field', 'component_id', 'fields'), 
            'preprocess' : fields.text('Preprocess'), 
              }
    
    def create_instance(self, cr, uid, ids, context={}):
        obj_component=self.pool.get('etl.component')
        
        for cmp in obj_component.browse(cr, uid, [ids]):
            if cmp.type.name == 'transform.map':
                context['components'][ids] = {}
                context['components'][ids]['transformer'] = None
                
                if cmp.transformer_id:
                    obj_transformer = self.pool.get('etl.transformer')
                    obj_transformer.create_instance(cr, uid, cmp.transformer_id.id, context, cmp.id)
                
                trans_instance = context['components'][ids]['transformer']
                
                field_obj = self.pool.get('etl.component.field')
                field_ids = field_obj.search(cr, uid, [('component_id', '=', cmp.id)])
                field_data = field_obj.read(cr, uid, field_ids, ['source_field','dest_field'])
                map_criteria = {}
                map_criteria['main'] = {}
                for data in field_data:
                    map_criteria['main'][data['source_field']] = data['dest_field']
                val = etl.component.transform.map(map_criteria, cmp.preprocess, 'component.transfer.map', trans_instance) 
                context['components'][ids]['instance'] = val
            
        return super(etl_component_transform_map, self).create_instance(cr, uid, ids, context)
        
    
etl_component_transform_map()

class etl_component_csv_out(osv.osv):
    _name='etl.component'
    _inherit = 'etl.component'
    _description = "ETL Component"
         
    def create_instance(self, cr, uid, ids, context={}):
        obj_component=self.pool.get('etl.component')
        
        for cmp in obj_component.browse(cr, uid, [ids]):
            if cmp.type.name == 'output.csv_out':
                context['components'][ids] = {}
                context['components'][ids]['connector'] = None
                context['components'][ids]['transformer'] = None
                if cmp.connector_id:
                    obj_connector=self.pool.get('etl.connector')
                    obj_connector.create_instance(cr, uid, cmp.connector_id.id , context, cmp.id)
                    
                if cmp.transformer_id:
                    obj_transformer = self.pool.get('etl.transformer')
                    obj_transformer.create_instance(cr, uid, cmp.transformer_id.id, context, cmp.id)
                
                conn_instance = context['components'][ids]['connector']
                trans_instance = context['components'][ids]['transformer']
                
                val = etl.component.output.csv_out(conn_instance, 'component.output.csv_out', trans_instance, cmp.row_limit, cmp.csv_params) 
                context['components'][ids]['instance'] = val
            
        return super(etl_component_csv_out, self).create_instance(cr, uid, ids, context)
        
        
etl_component_csv_out()

class etl_component_csv_in(osv.osv):
    _name='etl.component'
    _inherit = 'etl.component'
    _description = "ETL Component"

    _columns={
            'connector_id' :  fields.many2one('etl.connector', 'Connector', domain="[('type','=','localfile')]"), 
            'transformer_id' :  fields.many2one('etl.transformer', 'Transformer'), 
            'row_limit' : fields.integer('Limit'), 
            'csv_params' : fields.char('CSV Parameters', size=64), 
              }
    _defaults={
               'csv_params':lambda *x:'{}'
               }
    
         
    def create_instance(self, cr, uid, ids, context={}):
        obj_component=self.pool.get('etl.component')
        
        for cmp in obj_component.browse(cr, uid, [ids]):
            if cmp.type.name == 'input.csv_in':
                context['components'][ids] = {}
                context['components'][ids]['connector'] = None
                context['components'][ids]['transformer'] = None
                
                if cmp.connector_id:
                    obj_connector=self.pool.get('etl.connector')
                    obj_connector.create_instance(cr, uid, cmp.connector_id.id , context, cmp.id)
                    
                if cmp.transformer_id:
                    obj_transformer = self.pool.get('etl.transformer')
                    obj_transformer.create_instance(cr, uid, cmp.transformer_id.id, context, cmp.id)
                
                conn_instance = context['components'][ids]['connector']
                trans_instance = context['components'][ids]['transformer']
                
                val =etl.component.input.csv_in(conn_instance, 'component.input.csv_in', trans_instance, cmp.row_limit, cmp.csv_params or {})
                context['components'][ids]['instance'] = val
    
        return super(etl_component_csv_in, self).create_instance(cr, uid, ids, context)
        
etl_component_csv_in()


class etl_component_transform_logger(osv.osv):
    _name='etl.component'
    _inherit = 'etl.component'
    _description = "ETL Component"

    _columns={
            'output_id' :  fields.many2one('etl.connector', 'Connector', domain="[('type','=',sys)]"), 
            }
        
    def create_instance(self, cr, uid, ids , context={}):
        obj_component=self.pool.get('etl.component')
        
        for cmp in obj_component.browse(cr, uid, [ids]):
            if cmp.type.name == 'transform.logger':
                context['components'][ids] = {}
                val = etl.component.transform.logger(cmp.name)
                context['components'][ids]['instance'] = val
        
        return super(etl_component_transform_logger, self).create_instance(cr, uid, ids, context)
        
etl_component_transform_logger()
#
#class etl_component_input_data(osv.osv):
#    _name='etl.component'
#    _inherit = 'etl.component'
#
#    _columns={
#              'data_ids' : fields.one2many('etl.component.data.line', 'component_id', 'Datas'), 
#              'transformer_id' :  fields.many2one('etl.transformer', 'Transformer'), 
#              }
#    
#etl_component_input_data()
#
#
#class etl_component_input_data_line(osv.osv):
#    _name='etl.component.data.line'
#    _columns={
#              'field' : fields.char('Field', size=124), 
#              'value' : fields.char('Value', size=124), 
#              'component_id' : fields.many2one('etl.component', 'Model'), 
#              }
#
#etl_component_input_data_line()

class etl_component_open_object_out(osv.osv):
    _name='etl.component'
    _inherit = 'etl.component'
    _description="This is for open object out"

    _columns={
              'field_ids' : fields.one2many('etl.component.field', 'component_id', 'Fields'), 
              'model_id' : fields.many2one('ir.model', 'Model'), 
              'connector_id' : fields.many2one('etl.connector', 'Connector'), 
              'transformer_id' : fields.many2one('etl.transformer', 'Transformer'), 
              }
    
    def create_instance(self, cr, uid, ids, context={}):
        obj_component=self.pool.get('etl.component')
        
        for cmp in obj_component.browse(cr, uid, [ids]):
            if cmp.type.name == 'output.openobject_out':
                context['components'][ids] = {}
                context['components'][ids]['connector'] = None
                context['components'][ids]['transformer'] = None
                
                if cmp.connector_id:
                    obj_connector=self.pool.get('etl.connector')
                    obj_connector.create_instance(cr, uid, cmp.connector_id.id , context, cmp.id)
                    
                if cmp.transformer_id:
                    obj_transformer = self.pool.get('etl.transformer')
                    obj_transformer.create_instance(cr, uid, cmp.transformer_id.id, context, cmp.id)
                
                conn_instance = context['components'][ids]['connector']
                trans_instance = context['components'][ids]['transformer']
                
                field_obj = self.pool.get('etl.component.field')
                field_ids = field_obj.search(cr, uid, [('component_id','=',cmp.id)])
                field_data = field_obj.read(cr, uid, field_ids, ['source_field','dest_field'])
                field_ids = {}
                for data in field_data:
                    field_ids[data['source_field']] = data['dest_field']
                val = etl.component.output.openobject_out(conn_instance, cmp.model_id.model, field_ids, 'component.output.openobject_out', trans_instance)
                context['components'][ids]['instance'] = val
    
        return super(etl_component_open_object_out, self).create_instance(cr, uid, ids, context)
            
etl_component_open_object_out()

class etl_component_control_sleep(osv.osv):
    _name='etl.component'
    _inherit = 'etl.component'
    _description = "ETL Component"

#    _columns={
#            'delay' :  fields.float('Delay'), 
#              }
    
    def create_instance(self, cr, uid, ids, context={}):
            obj_component=self.pool.get('etl.component')
            context['components'][ids] = {}
            for cmp in obj_component.browse(cr, uid, [ids]):
                if cmp.type.name == 'control.sleep':
                    context['components'][ids]['instance'] = etl.component.control.sleep()
            return super(etl_component_control_sleep, self).create_instance(cr, uid, ids, context)
        
etl_component_control_sleep()

class etl_job(osv.osv):
    _name= 'etl.job'
    _columns={
              'name' : fields.char('Name', size=24, required=True), 
              'project_id' : fields.many2one('etl.project', 'ETL Project', readonly=True), 
              'user_id' : fields.many2one('res.users', 'Responsible', size=64), 
              'author' : fields.char('Author', size =50), 
              'is_start' : fields.boolean('Starting Job'), 
              'notes' : fields.text('Notes'), 
              'component_ids' : fields.many2many('etl.component', 'rel_job_component', 'component_id', 'job_id' , 'Components'), 
              'state' : fields.selection([('draft', 'Draft'), ('open', 'Open'), ('start', 'Started'), ('pause', 'Pause'), ('stop', 'Stop'), ('close', 'Close')], 'State', readonly=True), 
              'running_process' : fields.integer('Running Processes'), 
              'total_process' : fields.integer('Total Processes')
              }
    
    _defaults = {
                'state': lambda *a: 'draft', 
                }    
    
    def create_instance(self, cr, uid, ids, context={}):
        context['components'] = {}
        obj_component=self.pool.get('etl.component')
        
        for cmp in obj_component.browse(cr, uid, ids):
            obj_component.create_instance(cr, uid, cmp.id, context)
        return None
    
    def action_launch_process(self, cr, uid, ids, context={}):
        obj_component=self.pool.get('etl.component')
        component_ids = self.read(cr, uid, ids, ['component_ids'])[0]['component_ids']
        self.create_instance(cr, uid, component_ids, context)
        para = []
        for cmp in component_ids:
           para.append(context['components'][cmp]['instance'])
        job1=etl.job(para)
        job1.run()
        return 
        
etl_job()


class etl_job_process(osv.osv):
    _name = 'etl.job.process'
    _description = "This defines  ETL Job Process"
    
    _columns = {
              'name' : fields.char('Name', size=64, required=True), 
              'job_id' : fields.many2one('etl.job', 'Job', required=True), 
              'component_ids' : fields.many2many('etl.component', 'rel_job_process_component', ' component_id', 'process_id', 'Components', required=True), 
              'start_date' : fields.datetime('Start Date', readonly=True), 
              'end_date' : fields.datetime('End Date', readonly=True), 
              'compute_time' : fields.float('Computation Time'), 
              'input_records' : fields.integer('Total Input Records'), 
              'output_records' : fields.integer('Total Output Records'), 
              'state' : fields.selection([('draft', 'Draft'), ('open', 'Open'), ('start', 'Started'), ('pause', 'Paused'), ('stop', 'Stop'), ('close', 'Closed')], 'State', readonly=True), 
              }
    
    _defaults = {
            'state': lambda *a: 'draft', 
            }
    
etl_job_process()

class etl_transition(osv.osv):
    _name = 'etl.transition'
    _description = "This defines  ETL job's transition"
    
    def _get_channels(self, cr, uid, context={}):
        c_obj = self.pool.get('etl.channel')
        ch_ids = c_obj.search(cr, uid, [('type', '=', 'transition')])
        result = c_obj.read(cr, uid, ch_ids, ['code', 'name'], context)
        return [(r['code'], r['name']) for r in result]
    
    _columns = {
              'name' : fields.char('Name', size=64, required=True), 
              'type' : fields.selection([('data', 'Data Transition'), ('trigger', 'Trigger Transition')], 'Transition Type', required=True), 
              'source_component_id' : fields.many2one('etl.component', 'Source Component', required=True), 
              'destination_component_id' : fields.many2one('etl.component', 'Destination Component', required=True), 
              'channel_source' : fields.selection(_get_channels, 'Source Channel'), 
              'channel_destination' : fields.selection(_get_channels, 'Destination Channel'), 
              'state' : fields.selection([('open', 'Open'), ('start', 'Start'), ('pause', 'Pause'), ('stop', 'Stop'), ('close', 'Close')], 'State', readonly=True), 
              }
    
    _defaults = {
            'state': lambda *a: 'open', 
            }
    
    
    def create_instance(self, cr, uid, ids, context={}, component=None):
        obj_trans=self.pool.get('etl.transition')
        for trans in obj_trans.browse(cr, uid, [ids]):
            source = trans.source_component_id.id
            destination = trans.destination_component_id.id
            if not (source in context['components']):
                obj_component=self.pool.get('etl.component')
                obj_component.create_instance(cr, uid, source, context)
                context['components'][source]['transitions'] = {}
            
            elif not (destination in context['components']):
                obj_component=self.pool.get('etl.component')
                obj_component.create_instance(cr, uid, destination, context)
                context['components'][destination]['transitions'] = {}
                
            else:
                cmp_in = context['components'][source]['instance']
                cmp_out = context['components'][destination]['instance']
                trans_instance = etl.transition(cmp_in, cmp_out)
                context['components'][source]['transitions'][trans.id] = trans_instance
                context['components'][destination]['transitions'][trans.id] = trans_instance
        return None
    
etl_transition()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
