import time
import os
import StringIO

#
# This should be the indexer
#
def content_index(content, filename=None, content_type=None):
#	return ''
	fname,ext = os.path.splitext(filename)
	result = ''
	if ext == '.doc': #or content_type ?
		(stdin,stdout) = os.popen2('antiword -', 'b')
		stdin.write(content)
		stdin.close()
		result = stdout.read()
	elif ext == '.pdf':
#		fileHandle = StringIO.StringIO("")
		fname = os.tempnam(filename)+'.pdf'
		fp = file(fname,'wb')
		fp.write(content)
		fp.close()
		fp = os.popen('pdftotext -enc UTF-8 -nopgbrk '+fname+' -', 'r')
		result = fp.read()
		fp.close()
	elif ext == '.odt':
		print "File name:",filename
		fname = os.tempnam(filename)
		fp = file(fname,'wb')
		fp.write(content)
		fp.close()
		fp = os.popen('python %s/addons/document/webdav/odt2txt.py '%(os.getcwd())+fname+' -', 'r')
		result = fp.read()
	elif ext in ('.png','.jpg','.jpeg'):
		result=''
	else:
		result = content
	return result