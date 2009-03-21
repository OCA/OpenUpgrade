#!/bin/env python

dict = { 'a' : 'Alpha', 'b' : 'Beta', 'g': 'Gamma' }

report = '''

	$a\t bc $$ \vssd\n
'''

from string import Template

s = Template(report.decode('string_escape'))


print s.substitute(dict)

#eof