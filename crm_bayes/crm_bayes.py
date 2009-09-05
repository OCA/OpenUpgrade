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

from osv import fields, osv
import string
from reverend.thomas import Bayes

result =[]
class crm_bayes_group(osv.osv):
    _name = 'crm.bayes.group'
    _description = 'Crm Bayes Group'
    _columns = {  
              'name':fields.char('Group Name',size=64,required=1),
              'bayes_category_ids' : fields.one2many('crm.bayes.categories','group_id','Category'),
              'train_data' : fields.binary('Trained Data')
              }
    def action_reset(self, cr, uid, ids, conect=None):
        group_obj = self.pool.get('crm.bayes.group')
        for rec in group_obj.search(cr,uid,[]):
            group_obj.write(cr,uid,rec,{'train_data':""})
        return True
         
crm_bayes_group()

class crm_bayes_categories(osv.osv):
    _name = "crm.bayes.categories"
    _description = 'Crm Bayes Categories'
    _columns = {
            'name':fields.char('Name', size=64 , required=1),
            'train_messages':fields.integer('Training Message', readonly = True),
            'guess_messages':fields.integer('Guessed Message', readonly = True),
            'automate_test' : fields.float('% Automated', readonly = True),
            'group_id' : fields.many2one('crm.bayes.group'),
              }
crm_bayes_categories()

class crm_bayes_test_guess(osv.osv_memory):
    _name='crm.bayes.test.guess'
    _columns = {
            'name' : fields.text('Message',required=1),
            }
    def action_guess(self, cr, uid, ids, context=None):
        guesser = Bayes()
        group_obj = self.pool.get('crm.bayes.group')
        if result:
            for res in range(0, len(result)):
                result.pop(0)
        data =""
        for rec in group_obj.browse(cr,uid,group_obj.search(cr,uid,[])):
            if rec['train_data']:
                data += str(rec['train_data'])
        result_lang=[]
        if data:
            myfile = file("/tmp/crm_bayes.bay", 'w')
            myfile.write(data)
            myfile.close()
            guesser.load('/tmp/crm_bayes.bay')
            message = self.read(cr,uid,ids,['name'])
            result_lang = guesser.guess(message[0]['name'])
        result.append(result_lang)
        return {
                'view_type': 'form', 
                "view_mode": 'form', 
                'res_model': 'crm.bayes.test.train', 
                'type': 'ir.actions.act_window', 
                'target':'new', 
         }
crm_bayes_test_guess()


class crm_bayes_test_train(osv.osv_memory):
    _name='crm.bayes.test.train'
    def _default_statistics(self, cr, uid, context={}):
        text=""
        if result :
            for re in result[0]:
                text += str(re[0]) +"\t" + str(round(re[1] * 100,2))  +"%" +"\n"
        return text
    _columns = {
            'name' : fields.text('statistics',readonly=True),
            'category_id' : fields.many2one('crm.bayes.categories','Real Category'),
            }
    _defaults = {
        'name':_default_statistics  ,
            }
    def action_train(self, cr, uid, ids, conect=None):
        cat_obj = self.pool.get('crm.bayes.categories')
        cat_id = self.read(cr,uid,ids[0],['category_id'])['category_id']
        if  result[0] and not cat_id:        
            max = float(result[0][0][1])
            max_list = result[0][0]
            for le in result[0]:
                if float(le[1]) > max :
                    max = float(le[1])
                    max_list =le
            cat_id = cat_obj.search(cr,uid,[('name','=',max_list[0])])[0]
            self.write(cr,uid,ids,{'category_id':cat_id})
        if cat_id :
            group_obj = self.pool.get('crm.bayes.group')
            message_obj = self.pool.get('crm.bayes.test.guess')
            cat_rec = cat_obj.read(cr,uid,cat_id,[])
            guesser = Bayes()
            data =""
            for rec in group_obj.browse(cr,uid,group_obj.search(cr,uid,[])):
                if rec['train_data']:
                    data += str(rec['train_data'])
            if data :
                myfile = file("/tmp/crm_bayes.bay", 'w')
                myfile.write(data)
                myfile.close()
                guesser.load('/tmp/crm_bayes.bay')
            guesser.train(cat_rec['name'],message_obj.read(cr,uid,ids)[0]['name'])
            guesser.save('/tmp/crm_bayes.bay')
            myfile = file("/tmp/crm_bayes.bay", 'r')
            data=""
            for fi in myfile.readlines():
                data += fi
            data1 =  group_obj.read(cr,uid,cat_rec['group_id'][0])['train_data']
            if data1 :
                data += data1
            group_obj.write(cr,uid,cat_rec['group_id'][0],{'train_data': data})
            percantage =   (int(cat_rec['guess_messages']) +  1) *100  / (int(cat_rec['train_messages']) + int(cat_rec['guess_messages']) + 2)
            cat_obj.write(cr,uid,cat_id,{'train_messages':int(cat_rec['train_messages']) + 1,'guess_messages':int(cat_rec['guess_messages']) + 1,'automate_test':percantage })
        else :
            raise osv.except_osv(_('Error !'),_('Please Select Category! '))
        return True
crm_bayes_test_train()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
