
##############################################################################
#
#    ETL system- Extract Transfer Load system
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


from osv import osv,fields


class etl_project(osv.osv):
    _name='etl.project'
    _columns={
              'name' : fields.char('Name',size =64),
              'job_ids' : fields.one2many('etl.job','project_id','Jobs')
    }
etl_project()

class etl_job(osv.osv):
    _name= 'etl.job'
    _description = "ETL Job"
    
    _columns={
              'name':fields.char('Name',size=20,required=True),
              'project_id' : fields.many2one('etl.project','ETL Project',readonly=True),
              'user_id' : fields.many2one("res.users","Responsible",size=64),
              'author' : fields.char('Author',size =50),
              'is_start' : fields.boolean('Starting Job'),
              'notes': fields.text('Notes'),
              'component_ids': fields.one2many("etl.component.item","job_id","Components"),
              'state':fields.selection([("open","open"),("start","start"),("pause","pause"),("stop","stop"),("close","close")],'State',readonly=True),
              'running_process':fields.char("Running Process",size=20),
              'total_process':fields.char("Total Process",size=20)
              }
    
    _defaults = {
                'state': lambda *a: 'open',
                }    
etl_job()

class etl_component_item(osv.osv):
        _name="etl.component.item"
        _description = "Components"
        
        _columns={
                'name':fields.char('Name',size=30,required=True),
                'job_id':fields.many2one("etl.job","Job",required=True),
                'trans_in_ids':fields.one2many("etl.transition","source_id","Source ID"),
                'trans_out_ids':fields.one2many("etl.transition","destination_id","Destination ID")
                  }
etl_component_item()

class etl_transition(osv.osv):
        _name="etl.transition"
        _columns={
                  'name':fields.char('Name',size=30,required=True),
                  "type" :fields.selection([("d_tran","Data Transition"),("t_tran","Trigger Transition")],"Transition Type",required=True),
                  'source_id':fields.many2one("etl.component.item",'Source Component',required=True),
                  'destination_id':fields.many2one("etl.component.item",'Destination Component',required=True),
                  'channel_source':fields.char('Source Channel',size=20),
                  'channel_destination':fields.char('Destination Channel',size=20),
                  'state':fields.selection([("open","open"),("start","start"),("pause","pause"),("stop","stop"),("close","close")],'State',readonly=True), 
                  }
        
        _defaults = {
                'state': lambda *a: 'open',
                }    
etl_transition()
