import time
import os
import StringIO

#
# This should be the indexer
#
def content_index(content, filename=None, content_type=None):
	fname,ext = os.path.splitext(filename)
	result = ''
	if ext == '.doc': #or content_type ?
		(stdin,stdout) = os.popen2('antiword -', 'b')
		stdin.write(content)
		stdin.close()
		result = stdout.read()
	elif ext == '.pdf':
	#		fileHandle = StringIO.StringIO("")
		#fname = os.tempnam(filename)+'.pdf'
		fp = os.tmpfile()
		fp.write(content)
		fp.close()
		fp = os.popen('pdftotext -enc UTF-8 -nopgbrk '+fp.name+' -', 'r')
		result = fp.read()
		fp.close()
	elif ext == '.odt':
		#fname = os.tempnam(filename)
		fp = os.tmpfile()
		fp.write(content)
		fp.close()
		fp = os.popen('python %s/addons/document/webdav/odt2txt.py '%(os.getcwd())+fp.name+' -', 'r')
		result = fp.read()
	elif ext in ('.txt','.py','.patch','.html',) :
		result = content
	return result
