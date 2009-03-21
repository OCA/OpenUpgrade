#!/bin/env python

dict = { 'a' : 'Alpha', 'b' : 'Beta', 'g': 'Gamma' }

report = '''$\\
	$a\t bc $$ \vssd\n
	
	$other
	$other

$\other
	some other string
'''

from string import Template

s = Template(report.decode('string_escape'))

def Do_report(report, dict):
	sections= {}
	main_section = None
	dict2= dict
	if report.startswith('$\\'):
		cur_sec='';
		for line in report.splitlines(True):
			if line.startswith('$\\'):
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
	
	dict2.update(sections)
	return Template(main_section).substitute(dict2)

print Do_report(report,dict)

#eof