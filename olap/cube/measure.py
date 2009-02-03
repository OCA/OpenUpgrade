
import sqlalchemy
import common
import copy

from agregator import agregator
import axis_map


class measure(object):
	def __init__(self, name):
		self.name = name
		self.object = False
	def validate(self, cube):
		for measure in cube.measure_ids:
			if measure.name==self.name:
				self.object = measure
		if not self.object:
			raise 'This measure does not exist !'
		return True

	def run(self, metadata):
		table = common.table_get(metadata, self.object.cube_id.table_id)
		col = common.col_get(sqlalchemy.Table(self.object.table_name,metadata), self.object.value_column)
		col_agregated = agregator[self.object.agregator](col)
		return [ {
			'value': [(['measures',self.name], self.name, False)],
			'query': {
				'column': [col_agregated]
			},
			'axis_mapping': axis_map.column_fixed(0),
			'delta': 0
		} ]

	def children(self, level, metadata):
		raise 'Not yet implemented !'

	def __repr__(self):
		res= '\t\t<olap.measure %s>\n' % (self.name,)
		return res

# vim: ts=4 sts=4 sw=4 si et
