##############################################################################
#
# Copyright (c) 2004-2006 TINY SPRL. (http://tiny.be) All Rights Reserved.
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
#
##############################################################################

import string
import time
import tools
from osv import fields,osv,orm

#class ir_model_fields(osv.osv):
#	_inherit = 'ir.model.fields'
#	def _get_models(self, cr, uid, model_name, level=1):
#		if not level:
#			return []
#		result = [model_name]
#		print model_name
#		for field,data in self.pool.get(model_name).fields_get(cr, uid).items():
#			if data.get('relation', False):
#				result += self._get_models(cr, uid, data['relation'], level-1)
#		return result
#	def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None):
#		if context and ('model_id' in context):
#			model_name = self.pool.get("ir.model").browse(cr, uid, context['model_id'], context).model
#			models = self._get_models(cr, uid, model_name, context.get('model_level',2))
#			models = map(lambda x: self.pool.get('ir.model').search(cr, uid, [('model','=',x)])[0], models)
#			args.append(('model_id','in',models))
#			print args
#		return super(ir_model_fields, self).search(cr, uid, args, offset, limit, order, context)
#ir_model_fields()

class report_creator(osv.osv):
	_name = "base_report_creator.report"
	_description = "Report"

	def fields_view_get(self, cr, user, view_id=None, view_type='form', context=None, toolbar=False):
		if (not context) or 'report_id' not in context:
			return super(report_creator, self).fields_view_get(cr, user, view_id, view_type, context, toolbar)
		report = self.browse(cr, user, context['report_id'])
		fields = {}
		i = 0
		for f in report.field_ids:
			fields['field'+str(i)] = {
				'string': f.field_id.field_description,
				'type': f.field_id.ttype,
				'select': 1,
				'relation': f.field_id.relation,
			}
			i+=1
		arch = '<?xml version="1.0" encoding="utf-8"?>\n'
		if view_type=='graph':
			arch +='<graph string="%s" type="%s" orientation="%s">' % (report.name, report.view_graph_type,report.view_graph_orientation)
			for val in ('x','y'):
				i = 0
				for f in report.field_ids:
					if f.graph_mode==val:
						arch += '<field name="%s" select="1"/>' % ('field'+str(i),)
					i+=1
		else:
			arch += '<%s string="%s">\n' % (view_type, report.name)
			i = 0
			for f in report.field_ids:
				arch += '<field name="%s" select="1"/>' % ('field'+str(i),)
				i+=1
		arch += '</%s>' % (view_type,)
		result = {
			'arch': arch,
			'fields': fields
		}
		result['toolbar'] = {
			'print': [],
			'action': [],
			'relate': []
		}
		return result

	def read(self, cr, user, ids, fields=None, context=None, load='_classic_read'):
		if (not context) or 'report_id' not in context:
			return super(report_creator, self).read(cr, user, ids, fields, context, load)
		ctx = context or {}
		wp = [self._id_get(cr, user, context['report_id'], context)+(' in (%s)' % (','.join(map(lambda x: "'"+str(x)+"'",ids))))]
		report = self._sql_query_get(cr, user, [context['report_id']], 'sql_query', None, ctx, where_plus = wp)
		sql_query = report[context['report_id']]
		cr.execute(sql_query)
		return cr.dictfetchall()

	def search(self, cr, user, args, offset=0, limit=None, order=None, context=None, count=False):
		if (not context) or 'report_id' not in context:
			return super(report_creator, self).search(cr, user, args, offset, limit, order, context, count)
		ctx = context or {}
		ctx['getid'] = True

		report = self._sql_query_get(cr, user, [context['report_id']], 'sql_query', None, ctx)
		query = report[context['report_id']]
		cr.execute(query)
		result = cr.fetchall()
		return map(lambda x: x[0], result)

	# To be implemented
	def _path_get(self,cr, uid, models, filter_ids=[]):
		ret_str = """	sale_order_line
	left join sale_order on (sale_order_line.order_id=sale_order.id)
	left join res_partner on (res_partner.id=sale_order.partner_id)"""
		where_list = []
		for filter_id in filter_ids:
			where_list.append(filter_id.expression)
		if where_list:
			ret_str+="\nwhere\n\t"+" and\n\t".join(where_list)
		return ret_str

	def _id_get(self, cr, uid, id, context):
		return 'min(sale_order_line.id)'

	def _sql_query_get(self, cr, uid, ids, prop, unknow_none, context, where_plus=[]):
		result = {}
		for obj in self.browse(cr, uid, ids):
			fields = [ self._id_get(cr, uid, ids[0], context)+' as id' ]
			groupby = []
			i = 0
			for f in obj.field_ids:
				t = self.pool.get(f.field_id.model_id.model)._table
				if f.group_method == 'group':
					fields.append('\t'+t+'.'+f.field_id.name+' as field'+str(i))
					groupby.append(t+'.'+f.field_id.name)
				else:
					fields.append('\t'+f.group_method+'('+t+'.'+f.field_id.name+')'+' as field'+str(i))
				i+=1

			models = self._path_get(cr, uid, obj.model_ids, obj.filter_ids)
			result[obj.id] = """select
%s
from
%s
			""" % (',\n'.join(fields), models)
			if groupby:
				result[obj.id] += "group by\n\t"+', '.join(groupby)
			if where_plus:
				result[obj.id] += "\nhaving \n\t"+"\n\t and ".join(where_plus)
		return result
	_columns = {
		'name': fields.char('Report Name',size=64, required=True),
		'type': fields.selection([('list','Rows And Columns Report'),('sum','Summation Report')], 'Report Type',required=True),
		'active': fields.boolean('Active'),
		'view_type1': fields.selection([('tree','Tree'),('graph','Graph'),('calendar','Calendar')], 'First View', required=True),
		'view_type2': fields.selection([('','/'),('tree','Tree'),('graph','Graph'),('calendar','Calendar')], 'Second View'),
		'view_type3': fields.selection([('','/'),('tree','Tree'),('graph','Graph'),('calendar','Calendar')], 'Third View'),
		'view_graph_type': fields.selection([('pie','Pie Chart'),('bar','Bar Chart')], 'Graph Type', required=True),
		'view_graph_orientation': fields.selection([('horz','Horizontal'),('vert','Vertical')], 'Graph Orientation', required=True),
		'model_ids': fields.many2many('ir.model', 'base_report_creator_report_model_rel', 'report_id','model_id', 'Reported Objects'),
		'field_ids': fields.one2many('base_report_creator.report.fields', 'report_id', 'Fields to Display'),
		'filter_ids': fields.one2many('base_report_creator.report.filter', 'report_id', 'Filters'),
		'state': fields.selection([('draft','Draft'),('valid','Valid')], 'State', required=True),
		'sql_query': fields.function(_sql_query_get, method=True, type="text", string='SQL Query', store=True),
		'group_ids': fields.many2many('res.groups', 'base_report_creator_group_rel','report_id','group_id','Authorized Groups'),
	}
	_defaults = {
		'type': lambda *args: 'list',
		'state': lambda *args: 'draft',
		'active': lambda *args: True,
		'view_type1': lambda *args: 'tree',
		'view_type2': lambda *args: 'graph',
		'view_graph_type': lambda *args: 'bar',
		'view_graph_orientation': lambda *args: 'horz',
	}
report_creator()

class report_creator_field(osv.osv):
	_name = "base_report_creator.report.fields"
	_description = "Display Fields"
	_rec_name = 'field_id'
	_order = "sequence,id"
	_columns = {
		'sequence': fields.integer('Sequence'),
		'field_id': fields.many2one('ir.model.fields', 'Field'),
		'report_id': fields.many2one('base_report_creator.report','Report', on_delete='cascade'),
		'group_method': fields.selection([('group','Grouped'),('sum','Sum'),('min','Minimum'),('max','Maximum'),('avg','Average')], 'Grouping Method', required=True),
		'graph_mode': fields.selection([('','/'),('x','X Axis'),('y','Y Axis')], 'Graph Mode'),
		'calendar_mode': fields.selection([('','/'),('date_start','Starting Date'),('date_end','Ending Date'),('date_delay','Delay'),('color','Uniq Colors')], 'Calendar Mode'),
	}
	_defaults = {
		'group_method': lambda *args: 'group',
		'graph_mode': lambda *args: '',
	}
report_creator_field()

class report_creator_filter(osv.osv):
	_name = "base_report_creator.report.filter"
	_description = "Report Filters"
	_columns = {
		'name': fields.char('Filter Name',size=64, required=True),
		'expression': fields.text('Value', required=True),
		'report_id': fields.many2one('base_report_creator.report','Report', on_delete='cascade'),
	}
report_creator_filter()
