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
        'state' : fields.selection([('draft','Draft'), ('running','Running'), ('done','Done'), ('cancel','Cancel')], 'State')
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
        'accepted_users' : fields.many2many('res.users', 'scenario_step_users', 'user_id', 'scenario_id', 'Users'),
        'tip' : fields.text('Tip'),
        'error' : fields.text('Error'),
        'pre_process_object' : fields.char('Preprocess Object', size=64),
        'pre_process_method' : fields.char('Preprocess Method', size=64),
        'pre_process_args' : fields.text('Preprocess Args'),
        'post_process_object' : fields.char('Postprocess Object', size=64),
        'post_process_method' : fields.char('Postprocess Method', size=64),
        'post_process_args' : fields.text('Postprocess Args'),
        'scenario_id' : fields.many2one('game.scenario', 'Scenario'),
        'step_next_ids':fields.many2many('game.scenario.step','scenario_step_rel', 'next_scenario_id','scenario_id', 'Next Steps'),
        'state' : fields.selection([('draft','Draft'),('running','Running'), ('done','Done'),('cancel','Cancel')], 'State')
        }
    _defaults = {
        'state' : lambda *a : 'running',       
        }
game_scenario_step()

class scenario_objects_proxy(web_services.objects_proxy):
    def execute(self, db, uid, passwd, object, method, *args):    
        security.check(db, uid, passwd)
        service = netsvc.LocalService("object_proxy")
        cr = pooler.get_db_only(db).cursor()
        pool = pooler.get_pool(cr.dbname)        
        step_obj=pool.get('game.scenario.step')
        sce_obj=pool.get('game.scenario')        
        if object in ('game.scenario','game.scenario.step'):
            res = service.execute(db, uid, object, method, *args)
            return res
        if not step_obj:
            res = service.execute(db, uid, object, method, *args)
            return res
        else:
            def _execute_step(step_id):   
				# To do : change state of step             
                # pre method
                pre_res=True
                step=step_obj.browse(cr,uid,step_id)
                pre_object=step.pre_process_object and pool.get(step.pre_process_object) or False
                pre_args=step.pre_process_args and eval(step.pre_process_args) or ()			
					
                if step.pre_process_method and pre_object:
                    pre_res=False
                    try:
                        pre_res=service.execute(db, uid, step.pre_process_object, step.pre_process_method, pre_args)
                    except Exception,e:
                        print e
                        cr.rollback()						
                        #step_obj.write(cr,uid,[step_id],{'error': "Exception on calling pre process :" +str(e),'state':'exception'})
                        cr.commit()
                        raise except_orm('Error!', "Exception on calling pre process :" +str(e))
                # current				
                res=service.execute(db, uid, object, method, *args)                
                # post method
                post_res=True
                post_object=step.post_process_object and pool.get(step.post_process_object) or False
                if pre_res and post_object and step.post_process_method:
                    post_res=False
                    try:
                        post_args=step.pre_process_args and eval(step.pre_process_args) or ()
                        post_args+={'result':res,'model':object},
                        post_res=service.execute(db, uid, step.post_process_object, step.post_process_method, post_args)
                    except Exception,e:
                        print e
                        cr.rollback()
                        #step_obj.write(cr,uid,[step_id],{'error': "Exception on calling post process :" +str(e),'state':'exception'})
                        cr.commit()
                        raise except_orm('Error!', "Exception on calling post process :" +str(e))                
                
                for next_step in step.step_next_ids:                    
                    if next_step.state in ('draft'):                        
                        #step_obj.write(cr,uid,[next_step.id],{'error': '','state':'running'})
                        _execute_step(next_step.id)
                if post_res:                										
                    #step_obj.write(cr,uid,[step_id],{'error': 'successfull done','state':'done'})
                    pass                
                return res
            running_scenario_ids=sce_obj.search(cr,uid,[('state','=','running')],limit=1)
            if len(running_scenario_ids):
                for scenario_id in running_scenario_ids:
                    running_step_ids=step_obj.search(cr,uid,[('state','=','running'),('scenario_id','=',scenario_id),('step_next_ids','<>','False')])
                    for running_step_id in running_step_ids:
                        res=_execute_step(running_step_id)
                    step_ids=step_obj.search(cr,uid,[('scenario_id','=',scenario_id)])
                    done=True
                    for step in step_obj.browse(cr,uid,step_ids):
                        if step.state!='done':
                            done=False
                    if done:
                        sce_obj.write(cr,uid,[scenario_id],{'state':'done'})
            else:
                res=service.execute(db, uid, object, method, *args)            
            return res        
        

                
            
scenario_objects_proxy()
 
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
