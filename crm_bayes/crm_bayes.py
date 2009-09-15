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
import tools
import copy

try:
    from reverend.thomas import Bayes
except:
    import netsvc
    netsvc.Logger().notifyChannel('reverend:', netsvc.LOG_WARNING, "python-reverend package currently not install!")
result =[]
file_path= tools.config['addons_path'] +"/crm_bayes/"

class crm_bayes_group(osv.osv):
    _name = 'crm.bayes.group'
    _description = 'Crm Bayes Group'
    _columns = {  
          'name': fields.char('Group Name',size=64,required=1),
          'bayes_category_ids': fields.one2many('crm.bayes.categories','group_id','Category'),
          'train_data': fields.binary('Trained Data'),
          'active': fields.boolean("Active"),
    }
    
    def action_reset(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'train_data':''})
        cat_obj = self.pool.get('crm.bayes.categories')
        
        cat_ids = cat_obj.search(cr, uid,[('group_id','=',ids[0])])
        
        for id in cat_ids:
            cat_obj.write(cr, uid, id, {'train_messages':0,'guess_messages':0,'automate_test' :0})
            
        case_obj = self.pool.get('crm.case')
        case_ids = case_obj.search(cr, uid, [])
        for rec in case_obj.read(cr, uid, case_ids, ['category_id','state_bayes']):
            if rec['category_id']:
                if rec['category_id'][0] in cat_ids and  rec['state_bayes'] == 'trained' :
                    case_obj.write(cr, uid, rec['id'], {'state_bayes':'untrained'})
        return True
         
crm_bayes_group()

class crm_bayes_categories(osv.osv):
    _name = "crm.bayes.categories"
    _description = 'Crm Bayes Categories'
    _columns = {
        'seq': fields.integer("Seq"),
        'name': fields.char('Name', size=64 , required=1),
        'train_messages': fields.integer('Training Message', readonly = True),
        'guess_messages': fields.integer('Guessed Message', readonly = True),
        'automate_test': fields.float('% Automated', readonly = True),
        'group_id': fields.many2one('crm.bayes.group',ondelete='cascade'),
    }
    
    def create(self, cr, uid, vals, context={}):
        cr.execute("select seq from crm_bayes_categories where group_id = %d order by seq " % vals['group_id'])
        rec = cr.dictfetchall()
        if len(rec):
            vals['seq'] = rec[len(rec)-1]['seq'] + 1
        else:
            vals['seq'] = 1
        res = super(crm_bayes_categories, self).create(cr, uid, vals, context)
        return res
    
    def search(self, cr, uid, args, offset=0, limit=None, order=None,
            context=None, count=False):
        if context is None:
            context = {}
        if context.get('from_wiz',False) and context.get('group_id',False):
            args += [('group_id','=',context['group_id'])]
        return super(crm_bayes_categories, self).search(cr, uid, args, offset, limit,
                order, context=context, count=count)

crm_bayes_categories()

class crm_bayes_test_guess(osv.osv_memory):
    _name = 'crm.bayes.test.guess'
    _columns = {
        'name' : fields.text('Message',required=1),
    }
    
    def action_guess(self, cr, uid, ids, context=None):
        guesser = Bayes()
        group_obj = self.pool.get('crm.bayes.group')
        if result:
            for res in range(0, len(result)):
                result.pop(0)
        data = ""
        for rec in group_obj.browse(cr, uid, context['active_ids']):
            if rec['train_data']:
                data += rec['train_data']
        result_lang=[]
        if data:
            myfile = file("/tmp/crm_bayes.bay", 'w')
            myfile.write(data)
            myfile.close()
            guesser.load('/tmp/crm_bayes.bay')
            message = self.read(cr, uid, ids, ['name'])
            result_lang = guesser.guess(message[0]['name'])
            
        cat_obj = self.pool.get('crm.bayes.categories')
        cat_id = cat_obj.search(cr, uid, [])
        for re in cat_obj.read(cr, uid, cat_id, ['name']):
            flag = False
            for r in result_lang:
                if r[0] == re['name']:
                    result.append(r)
                    flag = True
                    break
            if not flag:
                result.append((re['name'],0))
        context_new = {}
        context_new.update({'from_wiz':True})
        context_new.update({'group_id':context.get('active_id',False)})
        return {
            'context': context_new,
            'view_type': 'form', 
            "view_mode": 'form', 
            'res_model': 'crm.bayes.test.train', 
            'type': 'ir.actions.act_window', 
            'target':'new', 
         }
crm_bayes_test_guess()

class crm_bayes_test_train(osv.osv_memory):
    _name = 'crm.bayes.test.train'
    
    def _default_statistics(self, cr, uid, context={}):
        text=""
        if result :
            for re in result:
                text += str(re[0]) +"\t" + str(round(re[1] * 100,2))  +"%" +"\n"
        return text
    
    _columns = {
        'name': fields.text('statistics',readonly=True),
        'category_id': fields.many2one('crm.bayes.categories','Real Category'),
    }
    _defaults = {
        'name': _default_statistics,
    }
    
    def action_train(self, cr, uid, ids, context=None):
        cat_obj = self.pool.get('crm.bayes.categories')
        group_obj = self.pool.get('crm.bayes.group')
        message_obj = self.pool.get('crm.bayes.test.guess')
        for id in ids:
            cat_id = self.read(cr, uid, id, ['category_id','name'])         
            cat_id = cat_id[0]['category_id']
            if  result :
                max_list = max(result, key=lambda k: k[1])
                if max_list[1] > 0 and not cat_id:
                    cat_id = cat_obj.search(cr, uid, [('name','=',max_list[0])])[0]
                    cat_guess_msg = cat_obj.read(cr, uid, cat_id, ['guess_messages'])
                    cat_obj.write(cr, uid, cat_id, {'guess_messages' :cat_guess_msg['guess_messages'] + 1})

                    self.write(cr, uid, ids, {'category_id':cat_id})
            if cat_id :
                cat_rec = cat_obj.read(cr, uid, cat_id, [])
                guesser = Bayes()
                data = ""
                for rec in group_obj.browse(cr, uid, [cat_rec['group_id'][0]]):
                    if rec['train_data']:
                        data += rec['train_data']
                if data :
                    myfile = file(file_path+"crm_bayes.bay", 'w')
                    myfile.write(data)
                    myfile.close()
                    guesser.load(file_path+"crm_bayes.bay")
                    
                guesser.train(cat_rec['name'], message_obj.read(cr, uid, id)[0]['name'])
                guesser.save(file_path+"crm_bayes.bay")
                myfile = file(file_path+"crm_bayes.bay", 'r')
                data=""
                for fi in myfile.readlines():
                    data += fi 
                group_obj.write(cr, uid, cat_rec['group_id'][0], {'train_data': data})
                percantage = (int(cat_rec['guess_messages'])) *100  / (int(cat_rec['train_messages']) + int(cat_rec['guess_messages']) + 1)
                cat_obj.write(cr, uid, cat_id, {'train_messages':int(cat_rec['train_messages']) + 1, 'guess_messages':int(cat_rec['guess_messages']), 'automate_test':percantage })
            
            else :
                raise osv.except_osv(_('Error !'),_('Please Select Category! '))
        return {
            'view_type': 'form', 
            "view_mode": 'form', 
            'res_model': 'crm.bayes.train.message', 
            'type': 'ir.actions.act_window', 
            'target':'new', 
         }
    
crm_bayes_test_train()


class crm_bayes_train_message(osv.osv_memory):
    _name = 'crm.bayes.train.message'
    _columns = {
    }
    
    def action_ok(self, cr, uid, ids, context=None):
        return {}
        
crm_bayes_train_message()

class crm_case_rule(osv.osv):
    _name = "crm.case.rule"
    _inherit = "crm.case.rule"
    _columns = {
        'action': fields.selection([('perform action and assign category','Perform Action and assign category'),('perform action only','Perform Action Only'),("don't perform statistic test","Don't Perform Statistic Test")], 'Action', size=32,required=1),
        'group_id': fields.many2one('crm.bayes.group','Statistic Group'),
        'category_id': fields.many2one('crm.bayes.categories','Statistic Category'),
        'main_category_rate': fields.float('Main Category Min Rate', help = 'Perform the action only if the probability to be the main category if bigger than this rate'),
        'sec_category_rate': fields.float('Second Category Max Rate',help = 'Perform the ation only if the probability of the second category is lower than this rate'),
    }
    _defaults = {
        'action': lambda *a: "don't perform statistic test",
    }
crm_case_rule()

class crm_case(osv.osv):
    _name = "crm.case"
    _inherit= "crm.case"
    _description = "Case"
    _columns = {
        'category_id': fields.many2one('crm.bayes.categories','Statistic Category'),
        'state_bayes': fields.selection([('trained','Trained',),('untrained','Untrained')], 'Status', size=16, readonly=True),
    }
    _defaults = {
        'state_bayes': lambda *a: 'untrained',
    }
    def perform_action(self, cr, uid, ids, context=None):
        cases = self.browse(cr, uid, ids)
        for case in cases:
            if not case.email_from :
                raise osv.except_osv(_('Error!'),_("No E-Mail ID Found  for Partner Email!"))
            if case.user_id and case.user_id.address_id and case.user_id.address_id.email:
                emailfrom = case.user_id.address_id.email
            else:
                emailfrom = case.section_id.reply_to
            if not emailfrom:
                raise osv.except_osv(_('Error!'),_("No E-Mail ID Found for your Company address or missing reply address in section!"))
        self._action(cr,uid, cases, 'open')
        return True
    
    def guess_message(self,cr,uid,ids,context={}):
        cases = self.browse(cr, uid, ids)
        result_lang=[]
        if cases.description :
            guesser = Bayes()
            group_obj = self.pool.get('crm.bayes.group')
            data = ""
            for rec in group_obj.browse(cr, uid, group_obj.search(cr,uid,[('active','=',True)])):
                if rec['train_data']:
                    data += rec['train_data']
            if data :
                myfile = file("/tmp/crm_bayes.bay", 'w')
                myfile.write(data)
                myfile.close()
                guesser.load('/tmp/crm_bayes.bay')
                result_lang = guesser.guess(cases.description)
        guess_re = []
        for le in result_lang:
            guess_re.append((le[0],le[1]*100))
        return guess_re

    def _action(self, cr, uid, cases, state_to, scrit=None, context={}):
        super(crm_case, self)._action(cr, uid, cases, state_to, scrit=None, context={})
        if not scrit:
            scrit = []
        action_ids = self.pool.get('crm.case.rule').search(cr, uid, scrit)
        actions = self.pool.get('crm.case.rule').browse(cr, uid, action_ids, context)
        category={}
        cat_obj = self.pool.get('crm.bayes.categories')
        cat_rec = cat_obj.read(cr, uid, cat_obj.search(cr, uid, []),['name'])
        for cat in cat_rec:
            category[cat['name']] = cat['id']
        for case in cases:
            result_perform = self.guess_message(cr, uid, case.id, context)
            for action in actions:
                if action.action == "perform action only"  and action.category_id == case.category_id :
                    if result_perform:
                        res = max(result_perform, key=lambda k: k[1])
                        if res[1] >= action.main_category_rate:
                            self.write(cr, uid, case.id, {'category_id':category[res[0]]})
                            break
                        elif action.sec_category_rate :
                            sec_result = copy.deepcopy(result_perform)
                            sec_result.pop(sec_result.index (max (result_perform, key=lambda k: k[1])))
                            if sec_result:
                                re = max(sec_result, key=lambda k: k[1])
                                if re[1] <= action.main_category_rate and re[1] >= action.sec_category_rate:
                                    self.write(cr, uid, case.id, {'category_id':category[re[0]]})
                                    break
                elif action.action == "perform action and assign category" and action.category_id == case.category_id:
                    if result_perform :
                        max_list = max(result_perform, key=lambda k: k[1])
                        self.write(cr, uid, case.id, {'category_id':category[max_list[0]]})
                        break
        for case in cases:
            for action in actions:
                cate = self.read(cr, uid, case.id, ['category_id'])
                if action.action == "don't perform statistic test":
                    continue
                if cate['category_id']  and case.email_from :
                    if action.category_id.name == cate['category_id'][1]:
                        emails = []
                        emails.append(case.email_from)
                        if len(emails) and action.act_mail_body:
                            body = action.act_mail_body
                            if case.user_id and case.user_id.address_id and case.user_id.address_id.email:
                                emailfrom = case.user_id.address_id.email
                            else:
                                emailfrom = case.section_id.reply_to
                            name = '[%d] %s' % (case.id, case.name.encode('utf8'))
                            reply_to = case.section_id.reply_to or False
                            if reply_to: reply_to = reply_to.encode('utf8')
                            if emailfrom:
                                tools.email_send(emailfrom, emails, name, body, reply_to=reply_to, tinycrm=str(case.id))
                                break
        return True
    
    def trained(self, cr, uid, ids, context=None):
        for id in ids:
            record = self.read(cr, uid, id, ['category_id','description'])
            if record['description']:
                group_obj = self.pool.get('crm.bayes.group')
                cat_obj = self.pool.get('crm.bayes.categories')
                
                cat_rec = cat_obj.read(cr, uid, record['category_id'][0], [])
                guesser = Bayes()
                data =""
                for rec in group_obj.browse(cr, uid, [cat_rec['group_id'][0]]):
                    if rec['train_data']:
                        data += rec['train_data']
                if data :
                    myfile = file(file_path+"crm_bayes.bay", 'w')
                    myfile.write(data)
                    myfile.close()
                    guesser.load(file_path+"crm_bayes.bay")
                guesser.train(cat_rec['name'], record['description'])
                guesser.save(file_path+"crm_bayes.bay")
                myfile = file(file_path+"crm_bayes.bay", 'r')
                data=""
                for fi in myfile.readlines():
                    data += fi
                group_obj.write(cr, uid, cat_rec['group_id'][0], {'train_data': data})
                percantage = 0
                if cat_rec.get('guess_messages',  False):
                    percantage = (int(cat_rec['guess_messages'])) *100  / (int(cat_rec['train_messages']) + int(cat_rec['guess_messages']) + 1)
    
                cat_obj.write(cr, uid, record['category_id'][0], {'train_messages':int(cat_rec['train_messages']) + 1, 'automate_test':percantage })
                self.write(cr, uid, id, {'state_bayes':'trained'})
        return True
        
    def untrained(self, cr, uid, ids, context=None):
        for id in ids:
            record = self.read(cr, uid, id, ['category_id','description'])
            if record['description']:
                group_obj = self.pool.get('crm.bayes.group')
                cat_obj = self.pool.get('crm.bayes.categories')
                
                cat_rec = cat_obj.read(cr, uid, record['category_id'][0],[])
                guesser = Bayes()
                data = ""
                for rec in group_obj.browse(cr, uid, [cat_rec['group_id'][0]]):
                    if rec['train_data']:
                        data += rec['train_data']
                if data :
                    myfile = file(file_path+"crm_bayes.bay", 'w')
                    myfile.write(data)
                    myfile.close()
                    guesser.load(file_path+"crm_bayes.bay")
                guesser.untrain(cat_rec['name'],record['description'])
                guesser.save(file_path+"crm_bayes.bay")
                myfile = file(file_path+"crm_bayes.bay", 'r')
                data= ""
                for fi in myfile.readlines():
                    data += fi
                group_obj.write(cr, uid, cat_rec['group_id'][0], {'train_data': data})
                percantage = 0
                if cat_rec.get('guess_messages',  False):
                    percantage = (int(cat_rec['guess_messages'])) *100  / (int(cat_rec['train_messages']) + int(cat_rec['guess_messages']) - 1)
                    
                cat_obj.write(cr, uid, record['category_id'][0], {'train_messages':int(cat_rec['train_messages']) - 1, 'automate_test':percantage })
                self.write(cr, uid, id, {'state_bayes':'untrained'})
        return True    
    
crm_case()

class report_crm_bayes_statistic(osv.osv):
    _name = "report.crm.bayes.statistic"
    _description = "Bayes Statistic Report"
    _auto = False
    _columns = {
        'name': fields.char('Year', size=4),
        'month': fields.char('Month',size =4),
        'section_id': fields.many2one('crm.case.section', 'Section'),
        'total_case': fields.integer('Total Case'),
        'category_id': fields.many2one('crm.bayes.categories','Statistic Category'),
        'state_bayes': fields.char('Statistic Status',size=64),
        'group_id' : fields.many2one('crm.bayes.group','Group')
    }
    def init(self, cr):
        cr.execute("""
            create or replace view report_crm_bayes_statistic as (
            select 
                min(c.id) as id,
                count(c.section_id) as total_case ,
                c.section_id as section_id,
                c.category_id as category_id,
                c.state_bayes as state_bayes,
                to_char(c.create_date, 'MM') as month,  
                to_char(c.create_date, 'YYYY') as name, 
                ct.group_id as group_id
            from 
                crm_case c,crm_bayes_categories ct 
            where ct.id = c.category_id 
            group by c.section_id,c.category_id,c.state_bayes,to_char(c.create_date, 'MM'),to_char(c.create_date, 'YYYY'),ct.group_id
            )""")
report_crm_bayes_statistic()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
