# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2004-2008 Tiny SPRL (http://tiny.be) All Rights Reserved.
#
# $Id$
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
###############################################################################
from osv import fields, osv
from osv.orm import except_orm
import pooler
import time
from mx import DateTime
import datetime

import netsvc
from service import security
from service import web_services

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

#def _execute_service(db,uid,passwd,object,method,type,*args):
#    res=False
#    if type=='execute':
#        service = netsvc.LocalService("object_proxy")
#        res = service.execute(db, uid, object, method, *args)
#    elif type=='execute_wkf':
#        service = netsvc.LocalService("object_proxy")
#        res = service.exec_workflow(db, uid, object, method, id)
#    elif type=='wizard':
#        wiz = netsvc.LocalService('wizard.'+self.wiz_name[wiz_id])
#        res=wiz.execute(db, uid, self.wiz_datas[wiz_id], action, context)
#    elif type=='report':
#        cr = pooler.get_db(db).cursor()
#        obj = netsvc.LocalService('report.'+object)
#        res = obj.create(cr, uid, ids, datas, context)
#        cr.close()
#    return res
#def _execute(db,uid,passwd,object,method,type,*args):        
#    pool = pooler.get_pool(db)
#    res=False
#    if pool.get('game.scenario'):
#        cr = pooler.get_db_only(db).cursor()
#        cr.execute('select s.* from game_scenario_step s left join game_scenario g on (s.scenario_id=g.id) where g.state=%s and s.state=%s', ('running', 'running'))
#        steps_orig = cr.dictfetchall()            
#        new_args=()
#        def check(step, mode='pre'):
#            if step[mode+'_process_object'] and step[mode+'_process_method']:
#                try:
#                    return getattr(pool.get(step[mode+'_process_object']), step[mode+'_process_method'])(cr, uid, object, method, *new_args)
#                except Exception,e:
#                    cr.close()
#                    raise
#            else:
#                return True
#        steps = filter(check, steps_orig)
#        cr.close()
#        res=_execute_service(db,uid,passwd,object,method,type,args)
#        if steps:
#            new_args+={'result':res},
#            cr = pooler.get_db_only(db).cursor()
#            for step in steps:
#                check(step, 'post')
#            ids = ','.join(map(lambda x: str(x['id']), steps))
#            cr.execute('update game_scenario_step set state=%s where id in ('+ids+')', ('done',))
#            cr.execute('update game_scenario_step set state=%s where id in (select next_step_id from next_step_rel where step_id in ('+ids+')) and state=%s', ('running','draft'))
#            cr.commit()
#            cr.close()
#    else:
#        res=_execute_service(db,uid,passwd,object,method,type,args)
#    return res
class scenario_objects_proxy(web_services.objects_proxy):
    def exec_workflow(self, db, uid, passwd, object, method, id):
        security.check(db, uid, passwd)
        service = netsvc.LocalService("object_proxy")
        res = service.exec_workflow(db, uid, object, method, id)
        return res

    def execute(self, db, uid, passwd, object, method, *args):
        security.check(db, uid, passwd)
        service = netsvc.LocalService("object_proxy")
        pool = pooler.get_pool(db)
        if pool.get('game.scenario'):
            cr = pooler.get_db_only(db).cursor()
            cr.execute('select s.* from game_scenario_step s left join game_scenario g on (s.scenario_id=g.id) where g.state=%s and s.state=%s', ('running', 'running'))
            steps_orig = cr.dictfetchall()            
            new_args =()
            def check(step, mode='pre'):
                if step[mode+'_process_object'] and step[mode+'_process_method']:
                    try:
                        return getattr(pool.get(step[mode+'_process_object']), step[mode+'_process_method'])(cr, uid, object, method, *new_args)
                    except Exception,e:
                        cr.close()
                        raise
                else:
                    return True
            steps = filter(check, steps_orig)
            cr.close()
#            if steps_orig and not steps:
#                raise Exception("%s -- %s\n\n%s"%('warning', 'Warning !', steps_orig[0]['error']))
            res = service.execute(db, uid, object, method, *args)
            if steps:
                new_args+={'result':res},
                cr = pooler.get_db_only(db).cursor()
                for step in steps:
                    check(step, 'post')
                ids = ','.join(map(lambda x: str(x['id']), steps))
                cr.execute('update game_scenario_step set state=%s where id in ('+ids+')', ('done',))
                cr.execute('update game_scenario_step set state=%s where id in (select next_step_id from next_step_rel where step_id in ('+ids+')) and state=%s', ('running','draft'))
                cr.commit()
                cr.close()
        else:
            res = service.execute(db, uid, object, method, *args)
        return res
scenario_objects_proxy()


class scenario_wizard(web_services.wizard):
    def _execute(self, db, uid, wiz_id, datas, action, context):
        self.wiz_datas[wiz_id].update(datas)
        wiz = netsvc.LocalService('wizard.'+self.wiz_name[wiz_id])
        return wiz.execute(db, uid, self.wiz_datas[wiz_id], action, context)
scenario_wizard()

class scenario_report_spool(web_services.report_spool):
    def _report(self,db, uid, passwd, object, ids, datas=None, context=None):        
        cr = pooler.get_db(db).cursor()
        obj = netsvc.LocalService('report.'+object)
        res = obj.create(cr, uid, ids, datas, context)
        cr.close()
        return res
scenario_report_spool()



#
#1. Call pre_... of running steps of running scenario (state=running)
#  2. If 1 raise exception:
#        Raise Exception
#    If 1 return False: continue on 3 but not 4.
#    If 1 return True: continue on 3 and 4.
#  3. Call the normal method of the service
#  4. Call post_... method
#    Set state to done
#    Set state of next_step_ids to running
#  5. If no more steps in the scenario, set state of scenario as done.


#         res=pre method of pre model
#         exception :
#            raise exception
#        if not res:
#            res = service.execute(db, uid, object, method, *args)
#        else:
#            run current
#            run post method of post model
