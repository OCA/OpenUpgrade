#!/bin/env python
# Copyright (C) 2009 By P. Christeas

from string import Template
from textwrap import wrap

def posprint_report(report, pdict,context={}):
	""" Format a pos print report using values from pdict 
	"""
	sections= {}
	main_section = None
	dict2= pdict
	dyndicts = []
	if report.startswith('$\\'):
		cur_sec='';
		for line in report.splitlines(True):
			if line.startswith('$\\+'):
				(sec,exp)=line[3:].strip().split(' ',1)
				dyndicts.append((sec,exp))
			elif line.startswith('$\\'):
				#current line
				cur_args=line[2:].strip().split(' ')
				cur_sec=cur_args[0]
				if len(cur_sec):
					sections[cur_sec]= ''
				else:
					main_section=''
				#TODO: process args[1..]
			else:
				if len(cur_sec):
					sections[cur_sec]+=line.decode('string_escape')
				else:
					main_section +=line.decode('string_escape')
		
	else:
		main_section = report.decode('string_escape')
	
	ctx2 = context
	ctx2['wrap']=wrap
	ctx2.update(pdict)
	ctx2.update(sections)
	# Evaluate expressions into the sections
	for d,e in dyndicts:
		re = eval(e, ctx2)
		ctx2[d] = re
		sections[d]= re
		
	dict2.update(sections)
	return Template(main_section).substitute(dict2)
