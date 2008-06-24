##############################################################################
#
# Copyright (c) 2004 TINY SPRL. (http://tiny.be) All Rights Reserved.
#                    Fabien Pinckaers <fp@tiny.Be>
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

import time, os
import netsvc
import pooler,tools
import sys
import report

def graph_get(cr, uid, graph, offer_id):
	import pydotdm
	offer_obj = pooler.get_pool(cr.dbname).get('dm.offer')
	#offer = self.pool.get('dm.offer').browse(cr, uid, offer_id)
	#offer = offer_obj.browse(cr, uid, offer_id)
	offer = offer_obj.browse(cr, uid, offer_id)[0]
	print "Offer : ",offer
	print "Offer step_ids : ",offer.step_ids
	for step in offer.step_ids:
		args = {
			#'label': step.type + "\\n32"
			'label': step.type
		}
		print "DEBUG Graph",step.id
		print step.type
		graph.add_node(pydot.Node(step.id, **args))
			
		for transition in step.outgoing_transition_ids:
			args = {
				'label': transition.condition
			}
			if step.split_mode=='and':
				args['arrowtail']='box'
			elif step.split_mode=='xor':
				args['arrowtail']='inv'
			graph.add_edge(pydot.Edge( transition.step_from.id ,transition.step_to.id, fontsize=10, **args))
	print graph.write_dot("/tmp/debug.dot")
	print dir(graph)
	return True


#
# TODO: pas clean: concurrent !!!
#

class report_graph_instance(object):
	def __init__(self, cr, uid, ids, data):
		logger = netsvc.Logger()
		try:
			import pydotdm
		except Exception,e:
			logger.notifyChannel('workflow', netsvc.LOG_WARNING,
					'Import Error for pydot, you will not be able to render workflows\n'
					'Consider Installing PyDot or dependencies: http://dkbza.org/pydot.html')
			raise e
		offer_id = ids
		self.done = False

		graph = pydotdm.Dot(fontsize=16, label="Test")
		graph.set('size', '10.7,7.3')
		graph.set('center', '1')
		graph.set('ratio', 'auto')
		graph.set('rotate', '90')
		graph.set('rankdir', 'LR')
		graph_get(cr, uid, graph, offer_id)

		ps_string = graph.create_ps(prog='dot')
		if os.name == "nt":
			prog = 'ps2pdf.bat'
		else:
			prog = 'ps2pdf'
		args = (prog, '-', '-')
		try:
			input, output = tools.exec_command_pipe(*args)
		except:
			return
		input.write(ps_string)
		input.close()
		self.result = output.read()
		output.close()
		self.done = True

	def is_done(self):
		return self.done

	def get(self):
		if self.done:
			return self.result
		else:
			return None

class report_graph(report.interface.report_int):
	def __init__(self, name, table):
		report.interface.report_int.__init__(self, name)
		self.table = table

	def result(self):
		if self.obj.is_done():
			return (True, self.obj.get(), 'pdf')
		else:
			return (False, False, False)

	def create(self, cr, uid, ids, data, context={}):
		self.obj = report_graph_instance(cr, uid, ids, data)
		return (self.obj.get(), 'pdf')

report_graph('report.dm.offer.graph', 'dm.offer')
