import time
import os

#
# This should be the indexer
#
def content_index(content, filename=None, content_type=None):
	return ''
	fname,ext = os.path.splitext(filename)
	result = ''
	if ext == '.doc': #or content_type ?
		(stdin,stdout) = os.popen2('antiword -', 'b')
		stdin.write(content)
		stdin.close()
		result = stdout.read()
	elif ext == '.pdf':
		fname = os.tempnam(filename)+'.pdf'
		fp = file(fname,'wb')
		fp.write(content)
		fp.close()
		fp = os.popen('pdftotext -enc UTF-8 '+fname+' -', 'rb')
		result = fp.read()
		print type(result)
		result = result.decode('utf8', "replace").encode('ascii','replace')
		fp.close()
	return result
