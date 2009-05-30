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

from osv import osv, fields

class comparison_user(osv.osv):
    _name = 'comparison.user'
    _columns = {
        'name': fields.char('Name', size=64, required=True),
        'email': fields.char('Email', size=64, required=True),
        'password': fields.char('Password', size=64, required=True),
        'active': fields.boolean('Active'),
        'vote_ids': fields.one2many('comparison.vote', 'user_id', "Votes"),
        'factor_ids': fields.one2many('comparison.factor', 'user_id', "Factors",),
        'suggestion_ids': fields.one2many('comparison.ponderation.suggestion', 'user_id', "Ponderation Suggestions",),
    }
    _defaults = {
        'active': lambda *args: 1,
    }
    _sql_constraints = [
        ('email', 'unique(email)', 'The Email is Already Registered!.' ),
        ('name', 'unique(name)', 'The Username Already Exists!.' ),
    ]
    
comparison_user()

class comparison_item(osv.osv):
    _name = "comparison.item"
    _columns = {
        'name': fields.char('Software', size=64, required=True),
        'code': fields.char('Code', size=4, required=True),
        'version': fields.char('Version', size=64, required=True),
        'note': fields.text('Description'),
        'user_id': fields.many2one('comparison.user','User'),
        'result_ids': fields.one2many('comparison.factor.result', 'item_id', "Results"),
        'state': fields.selection([('draft','Draft'),('open','Open')], 'Status', required=True),
        'load_default' : fields.boolean('Load by Default',help="This option if checked, will let the Item display on Evaluation Matrix, by default."),
        'sequence': fields.integer('Sequence'),
    }
    _defaults = {
        'state': lambda *args: 'draft',
        'sequence': lambda *args: 1,
        'load_default': lambda *args: 0,
    }
    _sql_constraints = [
        ('name', 'unique(name)', 'The Item with the same name is already in the List!' )
    ]

    _order = 'sequence,id'

    def create(self, cr, uid, vals, context={}):
        result = super(comparison_item, self).create(cr, uid, vals, context)
        obj_factor = self.pool.get('comparison.factor')
        obj_factor_result = self.pool.get('comparison.factor.result')
        
        for factor_id in obj_factor.search(cr, uid, []):
            obj_factor_result.create(cr, uid, {'factor_id':factor_id,'item_id':[result][0]})
        
        return result
#    
#    def write(self, cr, uid, ids, vals, context=None):
#        if not context:
#            context={}
#        result = super(comparison_item, self).write(cr, uid, ids, vals, context=context)
#        
#        return result
    
comparison_item()


class comparison_factor(osv.osv):
    _name = "comparison.factor"
    
    def _ponderation_compute(self, cr, uid, ids, name, args, context):
        result = {}
        for rec in self.browse(cr, uid, ids, context=context):
            list_pond = []
            pond = rec.ponderation
            if rec.parent_id:
                for child in rec.parent_id.child_ids:
                    list_pond.append(child.ponderation)
            else:
                top_level_ids = self.search(cr, uid, [('parent_id','=',False)])
                for record in self.browse(cr, uid, top_level_ids, context=context):
                    list_pond.append(record.ponderation)
            result[rec.id] = pond / float(sum(list_pond))
        return result
    
    _columns = {
        'name': fields.char('Factor Name', size=128, required=True),
        'parent_id': fields.many2one('comparison.factor','Parent Factor', ondelete='set null'),
        'user_id': fields.many2one('comparison.user','User'),
        'child_ids': fields.one2many('comparison.factor','parent_id','Child Factors'),
        'note': fields.text('Note'),
        'sequence': fields.integer('Sequence'),
        'type': fields.selection([('view','Category'),('criterion','Criteria')], 'Type', required=True),
#        'result': fields.function(_result_compute, method=True, type='float', string="Result"),
        'result_ids': fields.one2many('comparison.factor.result', 'factor_id', "Results",),
        'ponderation': fields.float('Ponderation'),
        'pond_computed': fields.function(_ponderation_compute, digits=(16,3), method=True, type='float', string="Computed Ponderation"),
        'state': fields.selection([('draft','Draft'),('open','Open'),('cancel','Cancel')], 'Status', required=True),
#        'results': fields.one2many('comparison.factor.result', 'factor_id', 'Computed Results', readonly=1)
    }
    _defaults = {
        'state': lambda *args: 'draft',
        'ponderation': lambda *args: 1.0,
        'sequence': lambda *args: 1,
        'type' : lambda *args: 'criterion',
    }
    
    def create(self, cr, uid, vals, context={}):
        result = super(comparison_factor, self).create(cr, uid, vals, context)
        
        obj_item = self.pool.get('comparison.item')
        obj_factor_result = self.pool.get('comparison.factor.result')
        
        for item_id in obj_item.search(cr, uid, []):
            obj_factor_result.create(cr, uid, {'factor_id':[result][0],'item_id':item_id})
        
        return result
    
    def _check_recursion(self, cr, uid, ids):
        level = 100
        while len(ids):
            cr.execute('select distinct parent_id from comparison_factor where id in ('+','.join(map(str,ids))+')')
            ids = filter(None, map(lambda x:x[0], cr.fetchall()))
            if not level:
                return False
            level -= 1
        return True

    def export_csv(self, cr, uid, ids, context={}):
        import csv
        fp = csv.writer(file('/tmp/factors.csv','wb+'))
        val = self.pool.get('comparison.vote.values')
        val_ids = val.search(cr, uid, [])
        fp.writerow(['','Legend',''])
        for v in val.browse(cr, uid, val_ids, context):
            fp.writerow(['',str(v.factor)+' : '+v.name,''])
        fp.writerow(['','',''])
        fp.writerow(['ID','Criterion','Type'])
        def export_line(fp, line):
            md = self.pool.get('ir.model.data')
            ids = md.search(cr, uid, [('module','=','comparison'),('res_id','=',line.id),('model','=','comparison.factor')])
            lid = md.browse(cr, uid, ids[0], context).name
            fp.writerow([lid, line.name, (line.type=='view' or line.child_ids) and 'category' or ''])
            for o in line.child_ids:
                export_line(fp, o)

        ids = self.search(cr, uid, [('parent_id','=',False)])
        for obj in self.browse(cr, uid, ids, context):
            export_line(fp, obj)

        raise osv.except_osv(_('Error !'), _('Your .CSV file has been saved'))
        return True

    _constraints = [
        (_check_recursion, 'Error ! You cannot create recursive Factors.', ['parent_id'])
    ]
    
    _sql_constraints = [
        ('name', 'unique(parent_id,name)', 'The name of the Comparison Factor must be unique!' )
    ]
    
    _order = 'parent_id,sequence,id'
comparison_factor()

class comparison_vote_values(osv.osv):
    _name = 'comparison.vote.values'
    _columns = {
        'name': fields.char('Vote Type', size=64, required=True),
        'factor': fields.float('Factor', required=True),
    }
    _defaults = {
        'factor': lambda *a: 0.0,
    }
    
comparison_vote_values()

class comparison_vote(osv.osv):
    
    def __init__(self, pool, cr=None):
        super(comparison_vote, self).__init__(pool,cr)
        self.reload_ids = []
        
    _name = 'comparison.vote'
    _columns = {
        'user_id': fields.many2one('comparison.user', 'User', ondelete='set null'),
        'factor_id': fields.many2one('comparison.factor', 'Factor', required=True, ondelete='cascade', domain=[('type','<>','view')]),
        'item_id': fields.many2one('comparison.item', 'Item', required=True, ondelete='cascade'),
        'score_id': fields.many2one('comparison.vote.values', 'Value', required=True),
        'note': fields.text('Note'),
        'state': fields.selection([('draft','Draft'),('valid','Valid'),('cancel','Cancel')], 'Status', required=True, readonly=True),
    }
    
    _defaults = {
        'state': lambda *args: 'draft',
    }
    
    _sql_constraints = [
        ('vote_unique', 'unique(user_id,factor_id,item_id)', "You can't vote twice to the same factor of the same item!" )
    ]
    
    def accept_vote(self, cr, uid, ids, context={}):
        self.write(cr, uid, ids, {'state':'valid'})
        return True
    
    def cancel_vote(self, cr, uid, ids, context={}):
        self.write(cr, uid, ids, {'state':'cancel'})
        return True
    
    def vote_create_async(self, cr, uid, args):
        # this will accept the votes in bunch and will calculate parent's score at one call.
        self.reload_ids = []
        if args:
            for vote in args:
                self.create(cr,uid, vote, client_call=True)
            factor_id = int(args[0]['factor_id'])
            factor = self.pool.get('comparison.factor').browse(cr, uid, factor_id) 
            item_obj = self.pool.get('comparison.item').browse(cr, uid, int(args[0]['item_id']))
            # calculating parents until found top level
            while (factor and  factor.parent_id):
                self.compute_parents(cr, uid, factor, item_obj)
                factor = factor.parent_id
        return self.reload_ids

    def compute_parents(self, cr, uid, factor, item):

        if factor.parent_id:
            obj_factor_result = self.pool.get('comparison.factor.result')
            final_score = 0.0

            factor_clause = (','.join([str(x.id) for x in factor.parent_id.child_ids]))

            cr.execute("select sum(cf.ponderation) from comparison_factor as cf where cf.id in (%s) and cf.state!='cancel'"%(factor_clause))
            tot_pond = cr.fetchall()
            
            cr.execute("select cfr.result,cf.ponderation from comparison_factor_result as cfr,comparison_factor as cf where cfr.item_id=%s and cfr.votes > 0.0 and cfr.factor_id = cf.id and cf.id in (%s) and cf.state!='cancel'"%(item.id,factor_clause))
            res = cr.fetchall()

            final_score = 0.0
            
            if res:
                for record in res:
                    final_score += (record[0] * record[1])
    
                final_score = final_score / tot_pond[0][0]   

                parent_result_id = obj_factor_result.search(cr, uid, [('factor_id','=',factor.parent_id.id),('item_id','=',item.id)])
                obj_parent = obj_factor_result.read(cr, uid, parent_result_id,['votes'])
                obj_factor_result.write(cr, uid, parent_result_id[0],{'votes':(obj_parent[0]['votes'] + 1),'result':final_score})
                self.reload_ids.append(parent_result_id[0])
        return True
        
    def create(self, cr, uid, vals, context={}, client_call=False):
        result = super(comparison_vote, self).create(cr, uid, vals, context)
        obj_factor = self.pool.get('comparison.factor')
        obj_factor_result = self.pool.get('comparison.factor.result')
        obj_vote_values = self.pool.get('comparison.vote.values')
        vo = self.browse(cr, uid, result)
        pond_div = 5.0 # ponderation division factor
        
        for obj_vote in self.browse(cr, uid, [result]):
            
            result_id = obj_factor_result.search(cr, uid, [('factor_id','=',obj_vote.factor_id.id),('item_id','=',obj_vote.item_id.id)])
            obj_result = obj_factor_result.read(cr, uid, result_id, ['votes','result'])
            # finding previous score and votes
            votes_old = obj_result[0]['votes']         
            score = (obj_vote.score_id.factor / float(pond_div) ) * 100
            
            if votes_old:
                score = (score + obj_result[0]['result']) /2
                                            
            obj_factor_result.write(cr, uid, result_id, {'votes':(votes_old + 1),'result':score})
            self.reload_ids.append(result_id[0])
            
            if not client_call:
                factor = obj_vote.factor_id
                item_obj = obj_vote.item_id
                while (factor and  factor.parent_id):
                    self.compute_parents(cr, uid, factor, item_obj)
                    factor = factor.parent_id
                
        return result
#    
#    def write(self, cr, uid, ids, vals, context=None):
#        if not context:
#            context={}
#        result = super(comparison_vote, self).write(cr, uid, ids, vals, context=context)
#        
#        return result
        
    
comparison_vote()

class comparison_factor_result(osv.osv):
    _name = "comparison.factor.result"
    _rec_name = 'factor_id'
#    _table = "comparison_factor_result"
#    _auto = False
    
#    def _compute_score(self, cr, uid, ids, name, args, context):
#        if not ids: return {}
#        result = {}
#        print "iiiiiiiiids",ids
#        for obj_factor_result in self.browse(cr, uid, ids):
##            consider maximum vote factor = 5.0
#            pond_div = 5.00
#            result[obj_factor_result.id] = 0.00
#            ponderation_result = 0.00
#            
#            if obj_factor_result.factor_id.type == 'criterion': # type=view cannot be voted ever.
#                
#                ponderation = obj_factor_result.factor_id.ponderation
#                vote_ids = self.pool.get('comparison.vote').search(cr, uid, [('factor_id','=',obj_factor_result.factor_id.id),('item_id','=',obj_factor_result.item_id.id)])
#                votes = []
#                
#                if vote_ids:
#                    for obj_vote in self.pool.get('comparison.vote').browse(cr, uid, vote_ids):
#                        votes.append(obj_vote.score_id.factor * ponderation)
#                    ponderation_result = (ponderation * pond_div) * len(votes)    
#                else:
#    #                votes = [0.00]
#                    ponderation_result = (ponderation * pond_div)        
#                sum_votes = votes and sum(votes) or 0.00
#                
#                result[obj_factor_result.id] = round(((sum_votes * 100)/float(ponderation_result)),2) #+   (' + str(len(votes)) + ' Vote(s))'
#            else:
#                # for type=view, we have to compute its children first and then it should affect its relative parents(not only immediate parents).
#                sum_votes = 0.0
##                child_ids = self.pool.get('comparison.factor').search(cr, uid, [('parent_id','child_of',[obj_factor_result.factor_id.id])])
##                child_ids.remove(obj_factor_result.factor_id.id)
#                voted = False
#                if obj_factor_result.factor_id.child_ids:
#                    child_ids = [x.id for x in obj_factor_result.factor_id.child_ids]
#                    child_factor_ids = self.pool.get('comparison.factor.result').search(cr, uid, [('factor_id','in',child_ids),('item_id','=',obj_factor_result.item_id.id)])
#                    
#                    if child_factor_ids:
#                        child_factors = self.pool.get('comparison.factor.result').read(cr, uid, child_factor_ids)
#                        votes_child = []
#                        pond_child_result = 0.0
#                        
#                        for factor in child_factors:
#                            obj_factor = self.pool.get('comparison.factor').browse(cr, uid, factor['factor_id'][0])
#                            score = factor['result']
#                            if score > 0.0:
#                                votes_child.append(obj_factor.ponderation * pond_div * score/100.00)
#                                pond_child_result += (obj_factor.ponderation * pond_div)
#                                voted = True
#                        
#                        # adding parent into calculation if it has a parent
##                        if obj_factor_result.factor_id.parent_id:
##                            pond_child_result += ponderation_result 
#                        
#                        sum_votes += sum(votes_child)
#                        pond_child_result = pond_child_result or 1.0
#                        result[obj_factor_result.id] = round(((sum_votes * 100)/float(pond_child_result)),2)
#                # Calculate scores of relative parents
##                if obj_factor_result.factor_id.parent_id:
##                    self.write(cr, uid, obj_factor_result.factor_id.parent_id.id, {'votes':obj_factor_result.votes + 1})
#        return result
#    
      
    _columns = {
        'factor_id': fields.many2one('comparison.factor','Factor', ondelete='cascade', required=1, readonly=1,),
        'item_id': fields.many2one('comparison.item','Item', ondelete='cascade', required=1, readonly=1),
#        'result': fields.function(_compute_score, method=True, digits=(16,2), type="float", string='Goodness(%)', readonly=1,),
        'votes': fields.float('Votes', readonly=1),
        'result': fields.float('Goodness(%)', readonly=1, digits=(16,3)),
        # This field must be recomputed each time we add a vote
    }
    
    _defaults = {
        'votes': lambda *a: 0.0,
        'result': lambda *a: 0.0,
    }
    
#    def init(self, cr):
#        cr.execute(""" create or replace view comparison_factor_result as (select (fr.id*10 + it.id ) as id,fr.id as factor_id,it.id as item_id,0.00 as result,(select count(*) from comparison_vote cv where cv.factor_id=fr.id and cv.item_id=it.id) as votes from comparison_factor as fr,comparison_item as it);
#                    """)
#    def unlink(self, cr, uid, ids, context={}):
#        raise osv.except_osv(_('Error !'), _('You cannot delete the vote result. You may have to delete the concerned Item or Factor!'))    
             
comparison_factor_result()


class comparison_ponderation_suggestion(osv.osv):
    _name = 'comparison.ponderation.suggestion'
    _desc = 'Users can suggest new ponderations on criterias'
    
    def accept_suggestion(self, cr, uid, ids, context={}):
#        obj_sugg = self.browse(cr, uid, ids)[0]
#        pool_factor = self.pool.get('comparison.factor')
#        obj_factor = pool_factor.browse(cr, uid, obj_sugg.factor_id.id)
#        obj_user = self.pool.get('comparison.user').browse(cr, uid, obj_sugg.user_id.id)
#        new_pond = (obj_factor.ponderation * obj_sugg.ponderation)
#        note = obj_factor.note or ''
#        factor_id = pool_factor.write(cr, uid, [obj_sugg.factor_id.id],{'ponderation':new_pond, 'note':str(note) + '\n' +'Ponderation Change Suggested by ' + str(obj_user.name) + '(' + obj_user.email + '). Value Changed from ' + str(obj_factor.ponderation) + ' to ' + str(new_pond) +'.' })
        self.write(cr, uid, ids, {'state':'done'})
        return True
    
    def cancel_suggestion(self, cr, uid, ids, context={}):
        obj_sugg = self.browse(cr, uid, ids)[0]
        pool_factor = self.pool.get('comparison.factor')
        obj_factor = pool_factor.browse(cr, uid, obj_sugg.factor_id.id)
        obj_user = self.pool.get('comparison.user').browse(cr, uid, obj_sugg.user_id.id)
#        suggestion = obj_sugg.ponderation or 1.0 # to avoid 0 division
#        new_pond = (obj_factor.ponderation / suggestion)
        if obj_sugg.effect == 'positive':
            new_pond = obj_factor.ponderation - 0.1
        else:
            new_pond = obj_factor.ponderation + 0.1
        
        note = obj_factor.note or ''
        factor_id = pool_factor.write(cr, uid, [obj_sugg.factor_id.id],{'ponderation':new_pond,'note':str(note) + '\n' +'Ponderation Revoked by Website Administrator. Value Changed from ' + str(obj_factor.ponderation) + ' to ' + str(new_pond) +'.' })
        self.write(cr, uid, ids, {'state':'cancel'})
        return True
    
    _columns = {
        'user_id': fields.many2one('comparison.user', 'User', required=True, ondelete='set null'),
        'factor_id': fields.many2one('comparison.factor', 'Factor', required=True, ondelete='cascade'),
        'ponderation': fields.float('Ponderation',required=True),
        'state': fields.selection([('draft','Draft'),('done','Done'),('cancel','Cancel')],'State',readonly=True),
        'note': fields.text('Suggestion'),
        'effect':fields.selection([('positive','Positive'),('negative','Negative')],'Ponderation Effect', help="Select Positive if your suggestion has greater poderation value than the current value, negative otherwise."),
    }
    _defaults = {
        'ponderation': lambda *a: 1.0,
        'state': lambda *a: 'draft',
        'effect': lambda *a: 'positive',
    }
    
    _sql_constraints = [
        ('user_id', 'unique(factor_id,user_id)', 'User can contribute to this factor only Once!!!' )
    ]
    
    def create(self, cr, uid, vals, context={}):
        result = super(comparison_ponderation_suggestion, self).create(cr, uid, vals, context)
        pool_factor = self.pool.get('comparison.factor')
        for obj_sugg in self.browse(cr, uid, [result]):
            obj_factor = pool_factor.browse(cr, uid, obj_sugg.factor_id.id)
            obj_user = self.pool.get('comparison.user').browse(cr, uid, obj_sugg.user_id.id)
            new_pond = obj_sugg.ponderation
            note = obj_factor.note or ''
            pool_factor.write(cr, uid, [obj_sugg.factor_id.id],{'ponderation':new_pond, 'note':str(note) + '\n' +'Ponderation Change Suggested by ' + str(obj_user.name) + '(' + obj_user.email + '). Value Changed from ' + str(obj_factor.ponderation) + ' to ' + str(new_pond) +'.' })
        return result
    
    # Do we need write?user can vote only once(sql constraint). if needed its ready. 
#    def write(self, cr, uid, ids, vals, context=None):
#        if not context:
#            context={}
#        old_ponderation = 1.0    
#        if 'ponderation' in vals:
#            new_ponderation = vals['ponderation']
#            old_ponderation = self.browse(cr, uid, ids)[0].ponderation
#        result = super(comparison_vote, self).write(cr, uid, ids, vals, context=context)
#        pool_factor = self.pool.get('comparison.factor')
#        for obj_sugg in self.browse(cr, uid, ids):
#            obj_factor = pool_factor.browse(cr, uid, obj_sugg.factor_id.id)
#            obj_user = self.pool.get('comparison.user').browse(cr, uid, obj_sugg.user_id.id)
#            new_pond = (obj_factor.ponderation * obj_sugg.ponderation)/float(old_ponderation)
#            note = obj_factor.note or ''
#            pool_factor.write(cr, uid, [obj_sugg.factor_id.id],{'ponderation':new_pond, 'note':str(note) + '\n' +'Ponderation Change Suggested by ' + str(obj_user.name) + '(' + obj_user.email + '). Value Changed from ' + str(obj_factor.ponderation) + ' to ' + str(new_pond) +'.' })
#            
#        return result

comparison_ponderation_suggestion()

class evaluation_pack(osv.osv):
    _name = 'evaluation.pack'
    _description = 'Evaluation Pack for Easy Comparison'
    
    _columns = {
        'name': fields.char('Name', size=64, required=True),
        'item_ids':fields.many2many('comparison.item','pack_items_rel','pack_id','item_id','Items',requierd=True)
    }
evaluation_pack()    

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: