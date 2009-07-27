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
from osv import fields, osv
from osv.orm import except_orm
import pooler
import time
from mx import DateTime
import datetime

import netsvc
from service import security

class game_scenario(osv.osv):
    _name="game.scenario"
    _columns = {
        'name':fields.char('Name',size=64, required=True),
        'note':fields.text('Note'),
        'state' : fields.selection([('draft','Draft'), ('running','Running'), ('done','Done'), ('cancel','Cancel')], 'State', required=True)
    }
    _defaults = {
        'state' : lambda *a : 'running',
    }
game_scenario()

class game_scenario_step(osv.osv):
    _name="game.scenario.step"
    _columns = {
        'name':fields.char('Name',size=64, required=True),
        'description' : fields.text('Description'),
        'menu_id' : fields.many2one('ir.ui.menu', 'Menu', required=True),
        'tip' : fields.text('Tip'),
        'error' : fields.text('Error'),
        'pre_process_object' : fields.char('Preprocess Object', size=64),
        'pre_process_method' : fields.char('Preprocess Method', size=64),
        'post_process_object' : fields.char('Postprocess Object', size=64),
        'post_process_method' : fields.char('Postprocess Method', size=64),
        'scenario_id' : fields.many2one('game.scenario', 'Scenario', required=True),
        'step_next_ids':fields.many2many('game.scenario.step','next_step_rel', 'step_id','next_step_id', 'Next Steps'),
        'state' : fields.selection([('draft','Draft'),('running','Running'), ('done','Done'),('cancel','Cancel')], 'State', required=True)
        }
    _defaults = {
        'state' : lambda *a : 'running',
        }
game_scenario_step()

def _execute(cr, uid, object, method, step, type='execute',mode='pre',*args):
    pool = pooler.get_pool(cr.dbname)
    res=False
    if pool.get('game.scenario'):
        if step[mode+'_process_object'] and step[mode+'_process_method']:
            try:
                return getattr(pool.get(step[mode+'_process_object']), step[mode+'_process_method'])(cr, uid,step['id'], object, method,type, *args)
            except Exception,e:
                cr.close()
                raise
        else:
            return True
    return res

def _pre_process(db,uid,passwd,object,method,type='execute',*args):
    security.check(db, uid, passwd)
    pool = pooler.get_pool(db)
    steps=False
    if pool.get('game.scenario'):
        cr = pooler.get_db_only(db).cursor()
        cr.execute('select s.* from game_scenario_step s left join game_scenario g on (s.scenario_id=g.id) where g.state=%s and s.state=%s', ('running', 'running'))
        steps_orig = cr.dictfetchall()
        steps=[]
        for step in steps_orig:
            res = _execute(cr, uid, object, method, step, type,'pre',*args)
            if res:
                steps.append(step)
        cr.close()
    return steps

def _post_process(db,uid,passwd,object,method,steps,type='execute',*args):
    security.check(db, uid, passwd)
    pool = pooler.get_pool(db)
    res=False
    if  pool.get('game.scenario') and steps:
        cr = pooler.get_db_only(db).cursor()
        for step in steps:
           _execute(cr, uid, object, method,step,type, 'post',*args)
        ids = ','.join(map(lambda x: str(x['id']), steps))
        cr.execute('update game_scenario_step set state=%s where id in ('+ids+')', ('done',))
        cr.execute('update game_scenario_step set state=%s where id in (select next_step_id from next_step_rel where step_id in ('+ids+')) and state=%s', ('running','draft'))
        cr.commit()
        cr.close()
    return res


web_services_objects_proxy = netsvc.SERVICES['object'].__class__
class scenario_objects_proxy(web_services_objects_proxy):
    def exec_workflow(self, db, uid, passwd, object, method, id):
        args=id,
        steps=_pre_process(db,uid,passwd,object,method,'execute_wkf',*args)
        res=super(scenario_objects_proxy,self).exec_workflow(db, uid, passwd, object, method, id)
        args+={'result':res},
        _post_process(db,uid,passwd,object,method,steps,'execute_wkf',*args)
        return res

    def execute(self, db, uid, passwd, object, method, *args):
        steps=_pre_process(db,uid,passwd,object,method,'execute',args)
        res=super(scenario_objects_proxy,self).execute(db, uid, passwd, object, method, *args)
        args+={'result':res},
        _post_process(db,uid,passwd,object,method,steps,'execute',*args)
        return res
scenario_objects_proxy()


web_services_wizard = netsvc.SERVICES['wizard'].__class__
class scenario_wizard(web_services_wizard):
    def execute(self,db, uid, passwd, wiz_id, datas, action='init', context=None):
        args=wiz_id,datas,action,context,
        steps=_pre_process(db,uid,passwd,None,None,'wizard',*args)
        if wiz_id==1:
            super(scenario_wizard,self).create(db, uid, passwd, 'base_setup.base_setup', datas)
        res=super(scenario_wizard,self).execute(db, uid,passwd, wiz_id, datas, action, context)
        args+={'result':res},
        res2=_post_process(db,uid,passwd,None, None,steps,'wizard',*args)
        return res
scenario_wizard()


web_services_report_spool = netsvc.SERVICES['report'].__class__
class scenario_report_spool(web_services_report_spool):
    def report(self,db, uid, passwd, object, ids, datas=None, context=None):
        args=ids,datas,context,
        steps=_pre_process(db,uid,passwd,object,None,'report',*args)
        res=super(scenario_report_spool,self).report(db, uid, passwd, object, ids, datas, context)
        _post_process(db,uid,passwd,object, None,steps,'report',*args)
        return res
scenario_report_spool()
