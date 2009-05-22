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
import os

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
    def get_instance(self, cr, uid, id, context={}, data={}):
        if (cr.dbname, uid, data.get('process_id', False), id) not in self._cache:
            self._cache[(cr.dbname, uid, data.get('process_id', False), id)]=self.create_instance(cr, uid, id, context, data)
        return self._cache[(cr.dbname, uid, data.get('process_id', False), id)]

    def create_instance(self, cr, uid, id, context, data={}):
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
              'code' : fields.char('Code', size=24, required=True),
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
              'uri' : fields.char('URL', size=124, help="Enter Real Path"),
              'host' : fields.char('Host', size=64),
              'port' : fields.char('Port', size=64),
              'uid' : fields.char('User  ID', size=64),
              'passwd' : fields.char('Password', size=64),

    }

    def get_instance(self, cr, uid, id, context={}, data={}):
        if (cr.dbname, uid, data.get('process_id', False), id) not in self._cache:
            self._cache[(cr.dbname, uid, data.get('process_id', False), id)]=self.create_instance(cr, uid, id, context, data)
        return self._cache[(cr.dbname, uid, data.get('process_id', False), id)]

    def create_instance(self, cr, uid, ids, context={}, data={}):
        # logic for super create_instance
        return False

    def search(self,cr, user, args, offset=0, limit=None, order=None, context=None, count=False):
        if not context:
            context = {}
        if 'comp_type' in context and context['comp_type']:
            cmptype_data = self.pool.get('etl.component.type').browse(cr, user, [context['comp_type']])
            connector_type = cmptype_data[0].connector_type_id.code or False
            if connector_type:
                args.append(('type', '=', connector_type))
        res=super(etl_connector, self).search(cr, user, args, offset, limit, order, context, count)
        return res

etl_connector()


class etl_component_type(osv.osv):
    _name='etl.component.type'
    _description = "ETL Component Type"

    _columns={
              'name' : fields.char('Name', size=64, required=True),
              'code' : fields.char('Code', size=24, required=True),
              'connector_type_id' :  fields.many2one('etl.connector.type', 'Connector Type'),
              'added' : fields.boolean('Added to Component view', readonly=True),
              'field_ids' : fields.many2many('ir.model.fields','comp_field_rel', 'field_id', 'comp_id', 'Component fields',  domain="[('model','ilike','etl.%')]"),
    }
    
    def add_type_view(self, cr, uid , id, context={}):
        type= self.browse(cr, uid, id)[0]
        if type.added:
            return
        fields = type.field_ids
        if not len(type.field_ids):
            return
        from xml import dom, xpath
        from lxml import etree
        cr.execute("select id, arch from ir_ui_view where name = 'view.etl.component.form'")
        result = cr.dictfetchall()[0]
        mydom = dom.minidom.parseString(result['arch'].encode('utf-8'))
        child_node=mydom.childNodes[0].childNodes
        for i in range(1,len(child_node)):
            for node in child_node[i].childNodes:
                if node.localName=='page' and node.getAttribute('string')=='Property':
                    groupnode = mydom.createElement('group')
                    groupnode.setAttribute('col', "4")
                    groupnode.setAttribute('colspan', "4")
                    groupnode.setAttribute('attrs', "{'invisible':[('type_id','!=',%s)]}" % type.id)
                    node.appendChild(groupnode)
                    for field in fields:
                        newnode = mydom.createElement('field')
                        newnode.setAttribute('name', field.name)
                        newnode.setAttribute('attrs', "{'invisible':[('type_id','!=',%s)]}" % (type.id))
                        if field.ttype in ['one2many', 'text']:
                            newnode.setAttribute('colspan', "4")
                            newnode.setAttribute('nolabel', "1")
                            sepnode = mydom.createElement('separator')
                            sepnode.setAttribute('colspan', "4")
                            sepnode.setAttribute('string',  field.field_description)
                            groupnode.appendChild(sepnode)
                        groupnode.appendChild(newnode)
        result['arch']=mydom.toxml()
        self.pool.get('ir.ui.view').write(cr, uid, result['id'], {'arch' : result['arch']})
        return self.write(cr, uid, id, {'added' : True})

etl_component_type()


class etl_job(osv.osv):
    _name= 'etl.job'
    _description = "ETL Job"
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
              'notes' : fields.text('Notes'),
              'component_ids' : fields.one2many('etl.component','job_id','Components'),
              'state' : fields.selection([('draft', 'Draft'), ('open', 'Open'), ('close', 'Close')], 'State', readonly=True),
              'running_process' : fields.function(__process_calc, method=True, type='integer', string='Running Processes' , multi='running_process'),
              'total_process' : fields.function(__process_calc, method=True, type='integer', string='Total Processes' , multi='total_process'),
     }

    _defaults = {
                'state': lambda *a: 'draft',
     }

    def action_set_to_draft(self, cr, uid , id, context={}):
        self.write(cr, uid , id, {'state': 'draft'})
        return True
    
    def action_start_process(self, db, uid , ids, obj, context={}):
        import pooler
        db, pool = pooler.get_db_and_pool(db)
        cr = db.cursor()
        return obj.action_start_process(cr, uid , ids, context)
    
    def action_run_all_processes(self, cr, uid , id, context={}):
        import threading
        job = self.browse(cr, uid , id)[0]
        process_obj = self.pool.get('etl.job.process')
        cr.execute("select id from etl_job_process where job_id = %s and state='open'" % (id[0],))
        process_ids = map(lambda x:x[0],cr.fetchall())
        thread1 = threading.Thread( target=self.action_start_process , args=(cr.dbname, uid, process_ids, process_obj, context))
        thread1.start()
        return True
    
    def get_instance(self, cr, uid, id, context={}, data={}):
        if (cr.dbname, uid, data.get('process_id', False), id) not in self._cache:
            self._cache[(cr.dbname, uid, data.get('process_id', False), id)]=self.create_instance(cr, uid, id, context, data)
        job = self._cache[(cr.dbname, uid, data.get('process_id', False), id)]
        if context.get('action_start_job', False):
            job.signal_connect({'id':id, 'instance':job}, 'start', context['action_start_job'], data)
        if context.get('action_restart_job', False):
            job.signal_connect({'id':id, 'instance':job}, 'restart', context['action_restart_job'], data)
        if context.get('action_stop_job', False):
            job.signal_connect({'id':id, 'instance':job}, 'stop', context['action_stop_job'], data)
        if context.get('action_end_job', False):
            job.signal_connect({'id':id, 'instance':job}, 'end', context['action_end_job'], data)
        if context.get('action_pause_job', False):

            job.signal_connect({'id':id, 'instance':job}, 'pause', context['action_pause_job'], data)
        return self._cache[(cr.dbname, uid, data.get('process_id', False), id)]

    def create_instance(self, cr, uid, id, context={}, data={}):
        obj_component=self.pool.get('etl.component')
        res = self.read(cr, uid, id, ['component_ids', 'name'])
        components=[]
        component_instance = []
        for comp in  obj_component.browse(cr, uid, res['component_ids']):
            components.append(comp)
            for trans in comp.trans_in_ids + comp.trans_out_ids:
                components.append(trans.source_component_id)
                components.append(trans.destination_component_id)
        comps = []
        for comp in components:
            comps.append(comp.id)
            for trans in comp.trans_in_ids + comp.trans_out_ids:
                comps.append(trans.source_component_id.id)
                comps.append(trans.destination_component_id.id)
        comps = list(set(comps))
        for cmp_id in comps:
            component_instance.append(obj_component.get_instance(cr, uid, cmp_id, context, data))
        job=etl.job(component_instance, res['name'])
        return job

    def action_open_job(self, cr, uid, ids, context={}):
        return self.write(cr, uid, ids, {'state':'open'})
    def action_close_job(self, cr, uid, ids, context={}):
        return self.write(cr, uid, ids, {'state':'close'})

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
              'job_id' : fields.many2one('etl.job', 'Job', required=True),
              'start_date' : fields.datetime('Start Date', readonly=True),
              'end_date' : fields.datetime('End Date', readonly=True),
              'schedule_date' : fields.datetime('Scheduled Date', states={'done':[('readonly', True)]}),
              'compute_time' : fields.function(_get_computation_time, method=True, string= 'Computation Time', help="The total computation time to run process in Seconds"),
              'input_records' : fields.integer('Total Input Records', readonly=True),
              'output_records' : fields.integer('Total Output Records', readonly=True),
              'state' : fields.selection([('draft', 'Draft'), ('open', 'Open'), ('start', 'Started'), ('pause', 'Paused'), ('stop', 'Stop'), ('exception', 'Exception'), ('cancel', 'Cancel'), ('end', 'Done')], 'State', readonly=True),
              'component_ids' : fields.one2many('etl.job.process.statistics', 'job_process_id', 'Statics', readonly=True),
              'log_ids' :  fields.one2many('etl.job.process.log', 'job_process_id', 'Logs', readonly=True),
              'statistics' : fields.boolean('Statistics Details', states={'draft':[('readonly', False)], 'open':[('readonly', False)] }),
              'log' : fields.boolean('Log Details', states={'draft':[('readonly', False)], 'open':[('readonly', False)] }),
              'error_msg' : fields.text('Error Message', readonly=True),
    }

    _defaults = {
            'name': lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid, 'etl.job.process'),
            'state': lambda *a: 'draft',
    }


    def action_start_component(self, key, signal_data={}, data={}):
        cr = pooler.get_db(data['dbname']).cursor()
        pool = pooler.get_pool(cr.dbname)
        uid = data['uid']
        process_obj = pool.get('etl.job.process')
        process = process_obj.browse(cr, uid, data['process_id'], context={})
        if process.statistics:
            cid = pool.get('etl.job.process.statistics').create(cr, uid, {'name' : key['id'], 'signal':'start', 'start_date' :time.strftime('%Y-%m-%d %H:%M:%S'), 'state' : 'start', 'job_process_id' : data['process_id']})
        if process.log:
            lid = pool.get('etl.job.process.log').create(cr, uid, {'date_time' :time.strftime('%Y-%m-%d %H:%M:%S'), 'desc' : str(key['instance'])+ str(key['id'])+'component is started...' })
        cr.commit()
        return True


    def action_end_component(self, key, signal_data={}, data={}):
        cr = pooler.get_db(data['dbname']).cursor()
        pool = pooler.get_pool(cr.dbname)
        uid = data['uid']
        process_obj = pool.get('etl.job.process')
        process = process_obj.browse(cr, uid, data['process_id'], context={})
        if process.statistics:
            comp_obj = pool.get('etl.job.process.statistics')
            comp_ids = comp_obj.search(cr, uid, [('job_process_id', '=', data['process_id']), ('name', '=', key['id'])])
            cid = comp_obj.write(cr, uid, comp_ids, {'end_date' :time.strftime('%Y-%m-%d %H:%M:%S'),'signal':'end',  'state' : 'end'})
        if process.log:
            lid = pool.get('etl.job.process.log').create(cr, uid, {'date_time' :time.strftime('%Y-%m-%d %H:%M:%S'), 'desc' : 'Component' + str(key['instance'])+ str(key['id'])+' is ended...' , 'job_process_id': data['process_id']})
        cr.commit()
        return True


    def action_start_transition(self, key, signal_data={}, data={}):
        cr = pooler.get_db(data['dbname']).cursor()
        pool = pooler.get_pool(cr.dbname)
        uid = data['uid']
        process_obj = pool.get('etl.job.process')
        process = process_obj.browse(cr, uid, data['process_id'], context={})
        if process.log:
            lid = pool.get('etl.job.process.log').create(cr, uid, {'date_time' :time.strftime('%Y-%m-%d %H:%M:%S'), 'desc' : 'Transition'+ str(key['instance'])+ str(key['id'])+' is started...' , 'job_process_id': data['process_id']})
        cr.commit()
        return True

    def action_end_transition(self, key, signal_data={}, data={}):
        cr = pooler.get_db(data['dbname']).cursor()
        pool = pooler.get_pool(cr.dbname)
        uid = data['uid']
        process_obj = pool.get('etl.job.process')
        process = process_obj.browse(cr, uid, data['process_id'], context={})
        if process.log:
            lid = pool.get('etl.job.process.log').create(cr, uid, {'date_time' :time.strftime('%Y-%m-%d %H:%M:%S'), 'desc' : 'Transition'+ str(key['instance'])+ str(key['id'])+' is ended...' , 'job_process_id': data['process_id']})
        cr.commit()
        return True

    def action_stop_component(self, key, signal_data={}, data={}):
        return True

    def action_no_input_component(self, key, signal_data={}, data={}):
        return True

    def action_send_output_component(self, key, signal_data={}, data={}):
        cr = pooler.get_db(data['dbname']).cursor()
        pool = pooler.get_pool(cr.dbname)
        uid = data['uid']
        process_obj = pool.get('etl.job.process')
        process = process_obj.browse(cr, uid, data['process_id'], context={})
        if process.statistics:
            comp_obj = pool.get('etl.job.process.statistics')
            comp_ids = comp_obj.search(cr, uid, [('job_process_id', '=', data['process_id']), ('name', '=', key['id'])])
            if comp_ids:
                cr.execute('select records_out from etl_job_process_statistics where id  in (' + ','.join([str(id) for id in comp_ids]) + ')')
                count =cr.fetchone()[0] or 0
                count = count+1
                comp_obj.write(cr, uid, comp_ids, {'records_out' : count,'signal':'start_output'})
                cr.commit()
        return True

    def action_get_input_component(self, key, signal_data={}, data={}):
        cr = pooler.get_db(data['dbname']).cursor()
        pool = pooler.get_pool(cr.dbname)
        uid = data['uid']
        process_obj = pool.get('etl.job.process')
        process = process_obj.browse(cr, uid, data['process_id'], context={})
        if process.statistics:
            comp_obj = pool.get('etl.job.process.statistics')
            comp_ids = comp_obj.search(cr, uid, [('job_process_id', '=', data['process_id']), ('name', '=', key['id'])])
            if comp_ids:
                cr.execute('select records_in from etl_job_process_statistics where id  in (' + ','.join([str(id) for id in comp_ids]) + ')')
                count =cr.fetchone()[0] or 0
                count = count+1
                comp_obj.write(cr, uid, comp_ids, {'records_in' : count,'signal':'start_input'})
                cr.commit()
        return True

    def action_start_job(self, key, signal_data={}, data={}):
        cr = pooler.get_db(data['dbname']).cursor()
        uid = data['uid']
        process=self.browse(cr, uid, data['process_id'], context={})
        self.write(cr, uid, process.id, {'state':'start', 'start_date':time.strftime('%Y-%m-%d %H:%M:%S')})
        cr.commit()
        return True

    def action_restart_job(self, key, signal_data={}, data={}):
        return True

    def action_pause_job(self, key, signal_data={}, data={}):
        return True

    def action_stop_job(self, key, signal_data={}, data={}):
        return True

    def action_end_job(self, key, signal_data={}, data={}):
        cr = pooler.get_db(data['dbname']).cursor()
        self.write(cr, data['uid'], data['process_id'], {'state':'end', 'end_date':time.strftime('%Y-%m-%d %H:%M:%S')})
        cr.commit()
        return True

    def get_job_instance(self, cr, uid, process_id, context={}, data={}):
        obj_job=self.pool.get('etl.job')
        context = {}
        process=self.browse(cr, uid, process_id, context)
        context.update({
                        'action_start_component':self.action_start_component,
                        'action_end_component':self.action_end_component,
                        'action_get_input_component':self.action_get_input_component,
                        'action_send_output_component':self.action_send_output_component,
                        'action_no_input_component':self.action_no_input_component,
                        'action_stop_component':self.action_stop_component,
                        'action_start_job':self.action_start_job,
                        'action_end_job':self.action_end_job,
                        'action_stop_job':self.action_stop_job,
                        'action_restart_job':self.action_restart_job,
                        'action_pause_job':self.action_pause_job,
                        'action_start_transition':self.action_start_transition,
                        'action_end_transition':self.action_end_transition,
                        })
        if (cr.dbname, uid, process.id) not in self._cache:
            job=obj_job.get_instance(cr, uid, process.job_id.id, context, data)
            self._cache[(cr.dbname, uid, process.id)]=job
        return self._cache[(cr.dbname, uid, process.id)]

    def action_open_process(self, cr, uid, ids, context={}):
        for process in self.browse(cr, uid, ids, context):
            self.write(cr, uid, process.id, {'state':'open'})
            
    def action_start_process(self, cr, uid, ids, context={}, data={}):
        for process in self.browse(cr, uid, ids, context):
            data.update({'dbname':cr.dbname, 'uid':uid, 'process_id':process.id})
            job=self.get_job_instance(cr, uid, process.id, context, data)
            job.pickle_file=tools.config['root_path']+'/save_job.p'
            if process.state in ('open', 'exception'):
                try:
                    job.run()
                except Exception, e:
                    print 'Exception: ', e
                    self.write(cr, uid, process.id, {'state':'exception'})
            elif process.state in ('pause'):
                self.write(cr, uid, process.id, {'state':'start', 'start_date':time.strftime('%Y-%m-%d %H:%M:%S')})
                job.signal('restart')
            else:
                raise osv.except_osv(_('Error !'), _('Cannot start process in %s state !'%process.state))
        return True

    def action_restart_process(self, cr, uid, ids, context={}, data={}):
        for process in self.browse(cr, uid, ids, context):
            data.update({'dbname':cr.dbname, 'uid':uid, 'process_id':process.id})
            job=self.get_job_instance(cr, uid, process.id, context, data)
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


    def action_pause_process(self, cr, uid, ids, context={}, data={}):
        for process in self.browse(cr, uid, ids, context):
            data.update({'dbname':cr.dbname, 'uid':uid, 'process_id':process.id})
            job=self.get_job_instance(cr, uid, process.id, context, data)
            job.signal('pause')
            self.write(cr, uid, process.id, {'state':'pause'})

    def test_process(self, cr, uid, ids, context={}):
        for process in self.browse(cr, uid, ids, context):
            if process.state == 'end':
                return True
            else:
                return False


    def action_stop_process(self, cr, uid, ids, context={}, data={}):
        for process in self.browse(cr, uid, ids, context):
            data.update({'dbname':cr.dbname, 'uid':uid, 'process_id':process.id})
            job=self.get_job_instance(cr, uid, process.id, context, data)
            job.signal('stop')
            self.write(cr, uid, process.id, {'state':'stop'})

    def action_cancel_process(self, cr, uid, ids, context={}, data={}):
        for process in self.browse(cr, uid, ids, context):
            data.update({'dbname':cr.dbname, 'uid':uid, 'process_id':process.id})
            job=self.get_job_instance(cr, uid, process.id, context, data)
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

class etl_component(osv.osv):
    _name='etl.component'
    _description = "ETL Component"
    _cache={}

    def _get_type(self,cr,uid,context={}):
        type_name=context.get('type_id',False)
        if type_name:
            obj_type=self.pool.get('etl.component.type')
            cmp_ids=obj_type.search(cr, uid, [('name','=',type_name)])
            return len(cmp_ids) and cmp_ids[0] or False
        return False

    _columns={
            'name' : fields.char('Name', size=64, required=True),
            'type_id' : fields.many2one('etl.component.type', 'Component Type', required=True),
            'connector_id' :  fields.many2one('etl.connector', 'Connector'),
            'transformer_id' :  fields.many2one('etl.transformer', 'Transformer'),
            'trans_in_ids' : fields.one2many('etl.transition', 'destination_component_id', 'Source ID'),
            'trans_out_ids' : fields.one2many('etl.transition', 'source_component_id', 'Destination ID'),
            'job_id' :  fields.many2one('etl.job', 'Job'),
            'row_limit':  fields.integer('Limit'),
            'encoding':  fields.char('Encoding',size=64),

     }
    _defaults = {
        'type_id':_get_type,
    }


    def get_instance(self, cr, uid, id, context={}, data={}):
        if (cr.dbname, uid, data.get('process_id', False), id) not in self._cache:
            self._cache[(cr.dbname, uid, data.get('process_id', False), id)] = self.create_instance(cr, uid, id, context, data)
            self._post_process(cr, uid, id, context, data)
        comp = self._cache[(cr.dbname, uid, data.get('process_id', False), id)]
        if context.get('action_start_component', False):
            comp.signal_connect({'id':id, 'instance':comp}, 'start', context['action_start_component'], data)
        if context.get('action_end_component', False):
            comp.signal_connect({'id':id, 'instance':comp}, 'end', context['action_end_component'], data)
        if context.get('action_get_input_component', False):
            comp.signal_connect({'id':id, 'instance':comp}, 'start_input', context['action_get_input_component'], data)
        if context.get('action_send_output_component', False):
            comp.signal_connect({'id':id, 'instance':comp}, 'start_output', context['action_send_output_component'], data)
        if context.get('action_no_input_component', False):
            comp.signal_connect({'id':id, 'instance':comp}, 'no_input', context['action_no_input_component'], data)
        if context.get('action_stop_component', False):
            comp.signal_connect({'id':id, 'instance':comp}, 'stop', context['action_stop_component'], data)

        return self._cache[(cr.dbname, uid, data.get('process_id', False), id)]

    def _post_process(self, cr, uid, id, context={}, data={}):
        obj_transition=self.pool.get('etl.transition')
        cmp=self.browse(cr, uid, id, context)
        for tran_in in cmp.trans_in_ids:
            if tran_in.state=='open':
                obj_transition.get_instance(cr, uid, tran_in.id, context, data)
        for tran_out in cmp.trans_out_ids:
            if tran_out.state=='open':
                obj_transition.get_instance(cr, uid, tran_out.id, context, data)

    def create_instance(self, cr, uid, id, context={}, data={}):
        return True

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
              'name' : fields.char('Name', size=64),
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

    def get_instance(self, cr, uid, id, context={}, data={}):
        if (cr.dbname, uid, data.get('process_id', False), id) not in self._cache:
            self._cache[(cr.dbname, uid, data.get('process_id', False), id)]  =self.create_instance(cr, uid, id, context, data)
        val = self._cache[(cr.dbname, uid, data.get('process_id', False), id)]
        if context.get('action_start_transition', False):
            val.signal_connect({'id':id, 'instance':val}, 'start', context['action_start_transition'], data)
        if context.get('action_end_transtiton', False):
            val.signal_connect({'id':id, 'instance':val}, 'end', context['action_end_transtiton'], data)
        return self._cache[(cr.dbname, uid, data.get('process_id', False), id)]

    def create_instance(self, cr, uid, id, context={}, data={}):
        obj_component=self.pool.get('etl.component')
        trans=self.browse(cr, uid, id)
        cmp_in = obj_component.get_instance(cr, uid, trans.source_component_id.id, context, data)
        cmp_out = obj_component.get_instance(cr, uid, trans.destination_component_id.id, context, data)
        if (cr.dbname, uid, data.get('process_id', False), id) in self._cache:
            return self._cache[(cr.dbname, uid, data.get('process_id', False), id)]
        val=etl.transition(cmp_in, cmp_out, channel_source=trans.channel_source or 'main',\
                           channel_destination=trans.channel_destination or 'main', type=trans.type)
        return val

    def action_open_transition(self, cr, uid, ids, context={}):
        return self.write(cr, uid, ids, {'state':'open'})

    def action_close_transition(self, cr, uid, ids, context={}):
        return self.write(cr, uid, ids, {'state':'close'})

etl_transition()


class etl_job_process_statistics(osv.osv):
    _name = 'etl.job.process.statistics'
    _description = "This defines Statitics of  ETL Job Process"
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

etl_job_process_statistics()

class etl_job_process_log(osv.osv):
    _name = 'etl.job.process.log'
    _description = "Job Process Logs"
    _cache={}

    _columns = {
              'date_time' : fields.datetime('Date/Time'),
              'desc' : fields.text('Description'),
              'job_process_id' : fields.many2one('etl.job.process', 'Job Process'),
    }

etl_job_process_log()



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

