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
        ('email', 'unique(email)', 'The email of the item must be unique' )
    ]
comparison_user()

class comparison_item(osv.osv):
    _name = "comparison.item"
    _columns = {
        'name': fields.char('Software', size=64, required=True),
        'version': fields.char('Version', size=64, required=True),
        'name': fields.text('Description'),
        'user_id': fields.many2one('comparison.user','User'),
        'state': fields.selection([('draft','Draft'),('open','Open')], 'Status', required=True),
    }
    _defaults = {
        'state': lambda *args: 'draft',
        'ponderation': lambda *args: 1.0,
    }
    _sql_constraints = [
        ('name', 'unique(parent_id,name)', 'The name of the item must be unique' )
    ]
    _order = 'parent_id,name asc'
comparison_item()


class comparison_factor(osv.osv):
    _name = "comparison.factor"
    _columns = {
        'name': fields.char('Item Name', size=64, required=True),
        'parent_id': fields.many2one('comparison.factor','Parent Item', ondelete='set null'),
        'user_id': fields.many2one('comparison.user','User'),
        'child_ids': fields.one2many('comparison.factor','parent_id','Child Items'),
        'note': fields.text('Note'),
        'ponderation': fields.float('Ponderation'),
        'state': fields.selection([('draft','Draft'),('open','Open'),('cancel','Cancel')], 'Status', required=True),
        'results': fields.one2many('comparison.factor.result', 'factor_id', 'Computed Results')
    }
    _defaults = {
        'state': lambda *args: 'draft',
        'ponderation': lambda *args: 1.0,
    }
    _sql_constraints = [
        ('name', 'unique(parent_id,name)', 'The name of the item must be unique' )
    ]
    _order = 'parent_id,name asc'
comparison_factor()

class comparison_factor_result(osv.osv):
    _name = "comparison.factor.result"
    _rec_name = 'factor_id'
    _columns = {
        'factor_id': fields.many2one('comparison.factor','Factor', ondelete='set null'),
        'item_id': fields.many2one('comparison.item','Item', ondelete='set null'),
        'result': fields.float('Result') # May be a fields.function store=True ?
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
idea_vote()

class comparison_vote(osv.osv):
    _name = 'comparison.vote'
    _columns = {
        'user_id': fields.many2one('comparison.user', 'User', required=True, ondelete='cascade'),
        'factor_id': fields.many2one('comparison.factor', 'Factor', required=True, ondelete='cascade'),
        'item_id': fields.many2one('comparison.item', 'Item', required=True, ondelete='cascade'),
        'score_id': fields.many2one('comparison.vote.value', 'Value', required=True)
        'ponderation': fields.float('Ponderation'),
        'note': fields.text('Note')
    }
    _defaults = {
        'ponderation': lambda *a: 1.0,
    }
    # TODO: overwrite create/write
comparison_vote()

