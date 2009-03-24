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
import time
import netsvc
import pooler
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
    _cache={}
    _columns={
              'name' : fields.char('Name', size=64, required=True), 
              'tranformer_line_ids' : fields.one2many('etl.transformer.line', 'tranformer_id', 'ETL Transformer'), 
    }
    def get_instance(self, cr, uid, id, context={}):
        if (cr.dbname, uid, id) not in self._cache:
            self._cache[(cr.dbname, uid, id)]=self.create_instance(cr, uid, id, context)
        return self._cache[(cr.dbname, uid, id)]
        
    def create_instance(self, cr, uid, id, context):
        trans = self.browse(cr, uid, id)
        val = etl.transformer(trans.tranformer_line_ids)
        return val
    
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
              'code' : fields.char('Code', size=24), 
     }
etl_connector_type()


class etl_connector(osv.osv):
    _name='etl.connector'
    _cache={}
    def _get_connector_type(self, cr, uid, context={}):
            c_obj = self.pool.get('etl.connector.type')
            type_ids = c_obj.search(cr, uid, [])
            result = c_obj.read(cr, uid, type_ids, ['code', 'name'], context)
            return [(r['code'], r['name']) for r in result]
        
    _columns={
              'name' : fields.char('Connector Name', size=64, required=True), 
              'type' : fields.selection(_get_connector_type, 'Connector Type', size=64, required=True), 
    }
    def onchange_type(self, cr, uid, ids, type):
        return {'value':{}}

    def get_instance(self, cr, uid, id, context={}):
        if (cr.dbname, uid, id) not in self._cache:
            self._cache[(cr.dbname, uid, id)]=self.create_instance(cr, uid, id, context)
        return self._cache[(cr.dbname, uid, id)]
    def create_instance(self, cr, uid, ids, context={}):
        # logic for super create_instance
        return False
    
etl_connector()


class etl_component_type(osv.osv):
    _name='etl.component.type'
    _description = "ETL Component Type"
    
    _columns={
              'name' : fields.char('Name', size=64, required=True), 
              'code' : fields.char('Code', size=24), 
              
    }
etl_component_type()


class etl_component(osv.osv):
    _name='etl.component'
    _description = "ETL Component"
    _cache={}    
    _columns={
            'name' : fields.char('Name', size=64, required=True), 
            'type_id' : fields.many2one('etl.component.type', 'Component Type', required=True), 
            'transformer_id' :  fields.many2one('etl.transformer', 'Transformer'), 
            'trans_in_ids' : fields.one2many('etl.transition', 'destination_component_id', 'Source ID'), 
            'trans_out_ids' : fields.one2many('etl.transition', 'source_component_id', 'Destination ID'), 
     }
    
    def action_start(self, key, signal_data={}, data={}):
        print 'component is started...', key, signal_data, data
        return True
  

    def action_end(self, key, signal_data={}, data={}):
        print 'component is end...', key, data    
        return True
    
    def get_instance(self, cr, uid, id, context={}):       
        if (cr.dbname, uid, id) not in self._cache:
            comp =self.create_instance(cr, uid, id, context)
            data={'dbname':cr.dbname, 'uid':uid, 'component_id':id}
            comp.signal_connect(comp, 'start', self.action_start, data)
            comp.signal_connect(comp, 'end', self.action_end, data)
            self._cache[(cr.dbname, uid, id)] = comp
            self._post_process(cr, uid, id, context)
        return self._cache[(cr.dbname, uid, id)]

    def _post_process(self, cr, uid, id, context={}):
        obj_transition=self.pool.get('etl.transition')
        cmp=self.browse(cr, uid, id, context=context)          
        for tran_in in cmp.trans_in_ids: 
            if tran_in.state=='open':           
                obj_transition.get_instance(cr, uid, tran_in.id, context)                                
        for tran_out in cmp.trans_out_ids:
            if tran_out.state=='open':
                obj_transition.get_instance(cr, uid, tran_out.id, context)                

    def create_instance(self, cr, uid, id, context={}):        
        return None
        
etl_component()


class etl_transition(osv.osv):
    _name = 'etl.transition'
    _description = "This defines  ETL job's transition"
    _cache={}
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
              'state' : fields.selection([('open', 'Open'), ('close', 'Close')], 'State', readonly=True), 
     }
    
    _defaults = {
            'state': lambda *a: 'open', 
     }
    
    def get_instance(self, cr, uid, id, context={}):        
        if (cr.dbname, uid, id) not in self._cache:
            self._cache[(cr.dbname, uid, id)]=self.create_instance(cr, uid, id, context)
        return self._cache[(cr.dbname, uid, id)]

    def create_instance(self, cr, uid, id, context={}):
        obj_component=self.pool.get('etl.component')
        trans=self.browse(cr, uid, id)
        cmp_in = obj_component.get_instance(cr, uid, trans.source_component_id.id, context)
        cmp_out = obj_component.get_instance(cr, uid, trans.destination_component_id.id, context) 
        if (cr, uid, id) in self._cache:
            return self._cache[(cr.dbname, uid, id)]              
        val=etl.transition(cmp_in, cmp_out, channel_source=trans.channel_source, channel_destination=trans.channel_destination, type=trans.type)
        return val

    def action_open_transition(self, cr, uid, ids, context={}):
        return self.write(cr, uid, ids, {'state':'open'})

    def action_close_transition(self, cr, uid, ids, context={}):
        return self.write(cr, uid, ids, {'state':'close'})
    
etl_transition()


class etl_job(osv.osv):
    _name= 'etl.job'
    _cache={}
    
    def __process_calc(self, cr, uid, ids, field_names, arg, context={}, query=''):
        res = {}
        mapping = {
            'running_process': "where p.state='start' ", 
            'total_process': "", 
        }
        for id in ids:
            res[id] = {}
            cr.execute(("SELECT count(p.id) from etl_job_process p inner join etl_job j on (j.id = p.job_id) " +\
                    ' , '.join(map(lambda x: mapping[x], field_names)) +
                    "and j.id =%d ") % (id,))
            ret = map(lambda x: int(x[0]), cr.fetchall())
            res[id][field_names[0]]= ret[0]
        return res
    
    
    _columns={
              'name' : fields.char('Name', size=24, required=True), 
              'project_id' : fields.many2one('etl.project', 'ETL Project'), 
              'user_id' : fields.many2one('res.users', 'Responsible', size=64), 
              'author' : fields.char('Author', size =50), 
              'is_start' : fields.boolean('Starting Job'), 
              'notes' : fields.text('Notes'), 
              'component_ids' : fields.many2many('etl.component', 'rel_etl_job_component', 'component_id', 'job_id' , 'Components'), 
              'state' : fields.selection([('draft', 'Draft'), ('open', 'Open'), ('close', 'Close')], 'State', readonly=True), 
              'running_process' : fields.function(__process_calc, method=True, type='integer', string='Running Processes' , multi='running_process'), 
              'total_process' : fields.function(__process_calc, method=True, type='integer', string='Total Processes' , multi='total_process'), 
     }
    
    _defaults = {
                'state': lambda *a: 'draft', 
     }    
    def get_instance(self, cr, uid, id, context={}):
        if (cr.dbname, uid, id) not in self._cache:
            self._cache[(cr.dbname, uid, id)]=self.create_instance(cr, uid, id, context)
        return self._cache[(cr.dbname, uid, id)]

    def create_instance(self, cr, uid, id, context={}):        
        obj_component=self.pool.get('etl.component')   
        res = self.read(cr, uid, id, ['component_ids'])
        output_cmps=[]
        for cmp_id in res['component_ids']:
            output_cmps.append(obj_component.get_instance(cr, uid, cmp_id, context))
        job=etl.job(output_cmps)
        return job
    
    def action_open_job(self, cr, uid, ids, context={}):
        return self.write(cr, uid, ids, {'state':'open'})
    def action_close_job(self, cr, uid, ids, context={}):
        return self.write(cr, uid, ids, {'state':'close'})
    
    def action_launch_process(self, cr, uid, ids, context={}):
        obj_process=self.pool.get('etl.job.process')
        for id in ids:                    
            process_id=obj_process.create(cr, uid, {'name':self.pool.get('ir.sequence').get(cr, uid, 'etl.job.process'), 'job_id':id})
            wf_service = netsvc.LocalService("workflow")
            wf_service.trg_validate(uid, 'etl.job.process', process_id, 'action_open', cr)
        return True
        
etl_job()


class etl_job_process(osv.osv):
    _name = 'etl.job.process'
    _description = "This defines  ETL Job Process"
    _cache={}
    
    def _get_computation_time(self, cr, uid, ids, name, args, context=None):
        res = {}
        for id in ids:
            res[id] = {}
            pro_obj = self.browse(cr, uid, id)
            if pro_obj.start_date and pro_obj.end_date:
                d1 = time.strptime (pro_obj.start_date, '%Y-%m-%d %H:%M:%S')
                d2 = time.strptime (pro_obj.end_date, '%Y-%m-%d %H:%M:%S')
                time_difference = time.mktime(d2) - time.mktime(d1)
                res[id] = time_difference
        return res
    
    _columns = {
              'name' : fields.char('Name', size=64, required=True, readonly=True), 
              'job_id' : fields.many2one('etl.job', 'Job', readonly=True, required=True), 
              'start_date' : fields.datetime('Start Date', readonly=True), 
              'end_date' : fields.datetime('End Date', readonly=True), 
              'schedule_date' : fields.datetime('Scheduled Date'), 
              'compute_time' : fields.function(_get_computation_time, method=True, string= 'Computation Time', help="The total computation time to run process in Seconds"), 
              'input_records' : fields.integer('Total Input Records', readonly=True), 
              'output_records' : fields.integer('Total Output Records', readonly=True), 
              'state' : fields.selection([('draft', 'Draft'), ('open', 'Open'), ('start', 'Started'), ('pause', 'Paused'), ('stop', 'Stop'), ('exception', 'Exception'), ('cancel', 'Cancel'), ('end', 'Done')], 'State', readonly=True), 
              'component_ids' : fields.one2many('etl.job.process.component', 'job_process_id', 'Components'), 
              'log_ids' :  fields.one2many('etl.job.log', 'job_process_id', 'Logs'), 
              'statistics' : fields.boolean('Statistics Details?'), 
              'log' : fields.boolean('Log Details?'), 
              'error_msg' : fields.char('Error Message', size= 64), 
    }
    
    _defaults = {
            'name': lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid, 'etl.job.process'), 
            'state': lambda *a: 'draft', 
    }
    
    def action_hook_component(self, cr, uid, process, component):
        cid = self.pool.get('etl.job.process.component').create(cr, uid, {'name' : component, 'start_date' :time.strftime('%Y-%m-%d %H:%M:%S'), 'state' : 'start', 'job_process_id' : process})
        cr.commit()
        return cid
    
    
    def action_start(self, key, signal_data={}, data={}):
        print 'job is started...', key, data
        cr = pooler.get_db(data['dbname']).cursor()
        uid = data['uid']
        process=self.browse(cr, uid, data['process_id'], context={})
        self.write(cr, uid, process.id, {'state':'start', 'start_date':time.strftime('%Y-%m-%d %H:%M:%S')})
        cr.commit()
        if process.statistics:
            components = []
            for comp in  process.job_id.component_ids:
                components.append(comp)
                for trans in comp.trans_in_ids + comp.trans_out_ids:
                    components.append(trans.source_component_id)
                    components.append(trans.destination_component_id)
            comps = []
            for comp in  components:
                comps.append(comp.id)
                for trans in comp.trans_in_ids + comp.trans_out_ids:
                    comps.append(trans.source_component_id.id)
                    comps.append(trans.destination_component_id.id)
            comps = list(set(comps))
            for c_id in comps:
                 self.action_hook_component(cr, uid, process.id, c_id)
            cr.commit()
        return True
  
    def action_restart(self, key, signal_data={}, data={}):
        print 'job is restarted...', key, data
        return True

    def action_pause(self, key, signal_data={}, data={}):
        print 'job is pause...', key, data
        return True

    def action_stop(self, key, signal_data={}, data={}):                    
        print 'job is stop...', key, data
        return True

    def action_end(self, key, signal_data={}, data={}):
        cr = pooler.get_db(data['dbname']).cursor()
        print 'job is end...', key, data    
        self.write(cr, data['uid'], data['process_id'], {'state':'end', 'end_date':time.strftime('%Y-%m-%d %H:%M:%S')})
        cr.commit()
        return True

    def get_job_instance(self, cr, uid, process_id, context={}):
        obj_job=self.pool.get('etl.job')
        process=self.browse(cr, uid, process_id, context=context)       
        if (cr, uid, process.id) not in self._cache:
            job=obj_job.get_instance(cr, uid, process.job_id.id, context)             
            data={'dbname':cr.dbname, 'uid':uid, 'process_id':process.id}
            job.signal_connect(job, 'start', self.action_start, data)
            job.signal_connect(job, 'pause', self.action_pause, data)
            job.signal_connect(job, 'stop', self.action_stop, data)
            job.signal_connect(job, 'end', self.action_end, data)
            self._cache[(cr.dbname, uid, process.id)]=job
        return self._cache[(cr.dbname, uid, process.id)]

    def action_open_process(self, cr, uid, ids, context={}):
        for process in self.browse(cr, uid, ids, context=context):
            self.write(cr, uid, process.id, {'state':'open'})

    def action_start_process(self, cr, uid, ids, context={}):
        for process in self.browse(cr, uid, ids, context=context):
            try:
                job=self.get_job_instance(cr, uid, process.id, context)            
                job.pickle_file=tools.config['root_path']+'/save_job.p'
                if process.state in ('open'):
                    job.run()
                elif process.state in ('pause', 'exception'):
                    self.write(cr, uid, process.id, {'state':'start', 'start_date':time.strftime('%Y-%m-%d %H:%M:%S')}) 
                    job.signal('restart')
                else:
                    raise osv.except_osv(_('Error !'), _('Cannot start process in %s state !'%process.state))          
            except Exception, e:
                self.write(cr, uid, [process.id], {'state' : 'exception', 'error_msg' : e})
                cr.commit()
        return True
    
    def action_restart_process(self, cr, uid, ids, context={}):
        for process in self.browse(cr, uid, ids, context=context):
            try:
                if process.state in ('pause', 'exception'):
                    self.write(cr, uid, process.id, {'state':'start', 'start_date':time.strftime('%Y-%m-%d %H:%M:%S')}) 
                    job.signal('restart')
                else:
                    raise osv.except_osv(_('Error !'), _('Cannot restart process in %s state !'%process.state))          
            except Exception, e:
               self.write(cr, uid, [process.id], {'state' : 'exception'})
               cr.commit()
        return True
            
            
    def action_pause_process(self, cr, uid, ids, context={}):        
        for process in self.browse(cr, uid, ids, context=context):
            job=self.get_job_instance(cr, uid, process.id, context) 
            job.signal('pause')
            self.write(cr, uid, process.id, {'state':'pause'})
    
    def test_process(self, cr, uid, ids, context={}):
        for process in self.browse(cr, uid, ids, context=context):
            print process.state
            if process.state == 'end':
                return True
            else:
                return False
            

    def action_stop_process(self, cr, uid, ids, context={}):        
        for process in self.browse(cr, uid, ids, context=context):
            job=self.get_job_instance(cr, uid, process.id, context) 
            job.signal('stop')
            self.write(cr, uid, process.id, {'state':'stop'})
    
    def action_cancel_process(self, cr, uid, ids, context={}):        
        for process in self.browse(cr, uid, ids, context=context):
            job=self.get_job_instance(cr, uid, process.id, context) 
            job.signal('stop')
            self.write(cr, uid, process.id, {'state':'stop'})


    def action_cancel_draft(self, cr, uid, ids, *args):
        if not len(ids):
            return False
        self.pool.get('etl.job.process').write(cr, uid, ids, {'state':'draft', 'component_ids':[(6, 0, [])]})
        return True

    def run_scheduler(self, cr, uid, automatic=False, use_new_cursor=False, context=None):
        if not context:
            context={}
        self._start_job_process(cr, uid, use_new_cursor=use_new_cursor, context=context)
        return True
        
etl_job_process()


class etl_job_process_component(osv.osv):
    _name = 'etl.job.process.component'
    _description = "This defines components in  ETL Job Process"
    _cache={}
    
    def _get_computation_time(self, cr, uid, ids, name, args, context=None):
        res = {}
        for id in ids:
            res[id] = {}
            pro_obj = self.browse(cr, uid, id)
            if pro_obj.start_date and pro_obj.end_date:
                d1 = time.strptime (pro_obj.start_date, '%Y-%m-%d %H:%M:%S')
                d2 = time.strptime (pro_obj.end_date, '%Y-%m-%d %H:%M:%S')
                time_difference = time.mktime(d2) - time.mktime(d1)
                res[id] = time_difference
        return res
    
    _columns = {
              'name' : fields.many2one('etl.component' , 'Component', required=True), 
              'component_ids' : fields.many2many('etl.component', 'rel_etl_job_process_component', 'component_id', 'process_id', 'Components'), 
              'start_date' : fields.datetime('Start Date'), 
              'end_date' : fields.datetime('End Date'), 
              'compute_time' : fields.function(_get_computation_time, method=True, string= 'Computation Time', help="The total computation time to run process in Seconds"), 
              'records_in' : fields.integer('Input Records'), 
              'seconds_par_record' : fields.integer('MilliSeconds per Record'), 
              'records_out' : fields.integer('Output Records'), 
              'signal' : fields.char('Signal', size=64), 
              'state' : fields.selection([('draft', 'Not Started'), ('open', 'Open'), ('start', 'Started'), ('pause', 'Paused'), ('stop', 'Stop'), ('end', 'Finished'), ('cancel', 'Canceld')], 'State', readonly=True), 
              'job_process_id' : fields.many2one('etl.job.process', 'Job Process'), 
    }
    
    _defaults = {
            'state': lambda *a: 'draft', 
    }
      
etl_job_process_component()

class etl_job_log(osv.osv):
    _name = 'etl.job.log'
    _description = "Logs"
    _cache={}
    
    _columns = {
              'name' : fields.char('Name', size=64), 
              'date_time' : fields.datetime('Date/Time'), 
              'desc' : fields.text('Description'), 
              'job_process_id' : fields.many2one('etl.job.process', 'Job Process'), 
    }
    
etl_job_log()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
