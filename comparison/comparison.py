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
    }
    _defaults = {
        'active': lambda *args: 1,
    }
    _sql_constraints = [
        ('email', 'unique(email)', 'The email of the User must be unique.' )
    ]
    
comparison_user()

class comparison_item(osv.osv):
    _name = "comparison.item"
    _columns = {
        'name': fields.char('Software', size=64, required=True),
        'version': fields.char('Version', size=64, required=True),
        'note': fields.text('Description'),
        'user_id': fields.many2one('comparison.user','User'),
        'state': fields.selection([('draft','Draft'),('open','Open')], 'Status', required=True),
    }
    _defaults = {
        'state': lambda *args: 'draft',
#        'ponderation': lambda *args: 1.0,
    }
    _sql_constraints = [
        ('name', 'unique(name)', 'The name of the item must be unique' )
    ]
#    _order = 'parent_id,name asc'
    
comparison_item()


class comparison_factor(osv.osv):
    _name = "comparison.factor"
    def _result_compute(self, cr, uid, ids, name, args, context):
        result = {}
        for rec in self.browse(cr, uid, ids, context=context):
            r = ''
            for res in rec.result_ids:
                r+='%s (%.2f), ' % (res.item_id.name, res.vote)
            result[rec.id] = r
        return result
    _columns = {
        'name': fields.char('Item Name', size=64, required=True),
        'parent_id': fields.many2one('comparison.factor','Parent Item', ondelete='set null'),
        'user_id': fields.many2one('comparison.user','User'),
        'child_ids': fields.one2many('comparison.factor','parent_id','Child Items'),
        'note': fields.text('Note'),
        'sequence': fields.integer('Sequence'),
        'type': fields.selection([('view','View'),('criterion','criterion')], 'Type'),
        'result': fields.function(_result_compute, method=True, type='char', string="Result"),
        'result_ids': fields.one2many('comparison.factor.result', 'factor_id', "Results"),
        'ponderation': fields.float('Ponderation'),
        'state': fields.selection([('draft','Draft'),('open','Open'),('cancel','Cancel')], 'Status', required=True),
        'results': fields.one2many('comparison.factor.result', 'factor_id', 'Computed Results', readonly=1)
    }
    _defaults = {
        'state': lambda *args: 'draft',
        'ponderation': lambda *args: 1.0,
        'sequence': lambda *args: 1,
    }
    _sql_constraints = [
        ('name', 'unique(parent_id,name)', 'The name of the item must be unique' )
    ]
    _order = 'parent_id,sequence'
comparison_factor()

class comparison_factor_result(osv.osv):
    _name = "comparison.factor.result"
    _rec_name = 'factor_id'
    
#    def create(self, cr, uid, vals, context={}):
#        result = super(comparison_factor_result, self).create(cr, uid, vals, context)
#         
#        record = self.browse(cr, uid, result)
#        print "REC",record
#        exist_ids = self.search(cr, uid, [])
#        for records in self.browse(cr, uid, exist_ids):
#            if (record.factor_id.parent_id):
#                if not ((record.factor_id.parent_id.id == records.id) and (records.item_id.id == vals['item_id'])):
#                    res = self.create(cr, uid, {'factor_id':record.factor_id.parent_id.id,'item_id':vals['item_id']})
#
#        return result    
    
    def _compute_score(self, cr, uid, ids, name, args, context):
        if not ids: return {}
        result = {}

        for obj_factor_result in self.browse(cr, uid, ids):
#            consider max factor = 5.0
            result[obj_factor_result.id] = 0.00
            root_ids =  self.pool.get('comparison.factor').search(cr, uid, [('parent_id','child_of',[obj_factor_result.id])])
            pond_div = 5.00
            ponderation_result = 0.00
            
            if not root_ids:
                continue
            
            for obj_factor in self.pool.get('comparison.factor').browse(cr, uid, root_ids):
                
                vote_ids = self.pool.get('comparison.vote').search(cr, uid, [])
                
                ponderation = obj_factor.ponderation
                
                votes = []
                
                if vote_ids:
                    for obj_vote in self.pool.get('comparison.vote').browse(cr, uid, vote_ids):
                        if obj_vote.factor_id.id == obj_factor.id and obj_vote.item_id.id == obj_factor_result.item_id.id:
                            votes.append(obj_vote.score_id.factor * ponderation)
                            ponderation_result += (ponderation * pond_div)
                else:
                    votes = [0.00]
                if not ponderation_result:
                    ponderation_result = 1     
                
                result[obj_factor_result.id] = sum(votes)/float(ponderation_result)
                
                        
        return result
    
    _columns = {
        'factor_id': fields.many2one('comparison.factor','Factor', ondelete='set null',required=1, readonly=1),
        'item_id': fields.many2one('comparison.item','Item', ondelete='set null', required=1, readonly=1),
        'result': fields.function(_compute_score, digits=(16,2), method=True, string='Score', readonly=1),
        # This field must be recomputed each time we add a vote
    }
    
comparison_factor_result()

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
    _name = 'comparison.vote'
    _columns = {
        'user_id': fields.many2one('comparison.user', 'User', required=True, ondelete='cascade'),
        'factor_id': fields.many2one('comparison.factor', 'Factor', required=True, ondelete='cascade'),
        'item_id': fields.many2one('comparison.item', 'Item', required=True, ondelete='cascade'),
        'score_id': fields.many2one('comparison.vote.values', 'Value', required=True),
#        'ponderation': fields.float('Ponderation'), do we need it here?
        'note': fields.text('Note'),
    }
#    _defaults = {
#        'ponderation': lambda *a: 1.0,
#    }

    def create(self, cr, uid, vals, context={}):
        result = super(comparison_vote, self).create(cr, uid, vals, context)
        
        flag = False
        result_ids = self.pool.get('comparison.factor.result').search(cr, uid, [])
               
        for score in  self.pool.get('comparison.factor.result').browse(cr, uid, result_ids):
            print "score",score    
            if score.item_id.id  == vals['item_id'] and score.factor_id.id == vals['factor_id']:
                self.pool.get('comparison.factor.result').write(cr, uid, [score.id], {}, context=context)
                return result
            else:
                flag = True
        
        if flag:
            self.pool.get('comparison.factor.result').create(cr, uid,{'factor_id':vals['factor_id'],'item_id':vals['item_id']}, context)
            
        return result
    
    def write(self, cr, uid, ids, vals, context=None):
        if not context:
            context={}
        result = super(comparison_vote, self).write(cr, uid, ids, vals, context=context)
        
        obj_vote = self.browse(cr, uid, ids[0])
        flag = False
        result_ids = self.pool.get('comparison.factor.result').search(cr, uid, [])
               
        for score in  self.pool.get('comparison.factor.result').browse(cr, uid, result_ids):
            print score    
            if score.item_id.id  == obj_vote.item_id.id and score.factor_id.id == obj_vote.factor_id.id:
                self.pool.get('comparison.factor.result').write(cr, uid, [score.id], {}, context=context)
                return result
            else:
                flag = True
                
        if flag:
            self.pool.get('comparison.factor.result').create(cr, uid,{'factor_id':obj_vote.factor_id.id,'item_id':obj_vote.item_id.id}, context)        
        
        return result
    
    # TODO: overwrite create/write
    
comparison_vote()


class comparison_ponderation_suggestion(osv.osv):
    _name = 'comparison.ponderation.suggestion'
    _desc = 'Users can suggest new ponderations on criterions'
    _columns = {
        'user_id': fields.many2one('comparison.user', 'User', required=True, ondelete='cascade'),
        'factor_id': fields.many2one('comparison.factor', 'Factor', required=True, ondelete='cascade'),
        'ponderation': fields.float('Ponderation'),
        'state': fields.selection([('draft','Draft'),('done','Done'),('cancel','Cancel')],'State'),
        'note': fields.text('Note')
    }
    _defaults = {
        'ponderation': lambda *a: 1.0,
        'state': lambda *a: 'draft',
    }
    # TODO: overwrite create/write
comparison_ponderation_suggestion()


