#!/bin/env python

dict = { 'a' : 'Alpha', 'b' : 'Beta', 'g': 'Gamma',
	'd' : 'Delta but some text must be wrapped' }

report = '''$\\
	$a\t bc $$ \vssd\n
	
	$other
	$other

The original d: $d

D wrapped: $dw0
and : $dw1

$\other
	some other string

$\\+dw wrap(d,12)
$\\+dw0 dw[0]
$\\+dw1 dw[1]
'''

from report_engine import posprint_report

print posprint_report(report,dict)

#eof