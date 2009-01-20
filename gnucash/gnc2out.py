#!/bin/env python

from optparse import OptionParser
import sys
import gnccontent
from xml import sax
import gzip

print "Starting import.."

parser = OptionParser()
parser.add_option("-q", "--quiet",
                  action="store_false", dest="verbose", default=True,
                  help="don't print the data to stdout")

parser.add_option("-u", "--no-gunzip",
                  action="store_false", dest="gunzip", default=True,
                  help="read a plain xml file rather than a compressed one")

(options, args) = parser.parse_args()


if not len(args):
	sys.stderr.write ("Must have at least one argument, a GNC file\n")
	exit(1)

print "Parsing %s"%args[0]

gcfile = args[0]
if options.gunzip:
	sys.stderr.write("Opening %s as gziped xml\n"%gcfile)
	f = gzip.open(gcfile)
else:
	sys.stderr.write("Opening %s as plain xml\n"%gcfile)
	f = open(gcfile, "rb")

try:
	handler = gnccontent.GCContent();
	if not options.verbose:
		handler.outh.go_quiet()
	sax.parse(f,handler)
except sax._exceptions.SAXParseException as exc:
	sys.stderr.write("Parse exception: %s at %d,%d\n" % (exc.getMessage(), exc.getLineNumber(),exc.getColumnNumber()))
finally:
	f.close()

#eof