#!/bin/env python

dict = { 'a' : 'Alpha', 'b' : 'Beta', 'g': 'Gamma',
	'd' : 'Delta but some text must be wrapped' }

report = '''$\\
	$a\t bc $$ \vssd\n
	
	$other
	$other

$\other
	some other string
'''

from report_engine import posprint_report

print posprint_report(report,dict)

#eof