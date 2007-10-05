import time
import os
import commands

#
# This should be the indexer
#
def content_index(content, filename=None, content_type=None):

#	return ''
	fname,ext = os.path.splitext(filename)
	result = ''

	if ext == '.doc': #or content_type ?
		(stdin,stdout) = os.popen2('antiword -')
		stdin.write(content)
		stdin.close()
		result = stdout.read()
	elif ext == '.pdf':
		fname = os.tempnam(filename)+'.pdf'
		fp = file(fname,'wb')
		fp.write(content)
		fp.close()
		fp = os.popen('pdftotext  '+fname+' -', 'r')
		result = fp.read()
		result = result.replace("\x0c","")
#		result = result.decode('utf8', "replace").encode('ascii','replace')
		fp.close()
	elif ext == '.odt':
		print "File name:",filename
		fname = os.tempnam(filename)
		fp = file(fname,'wb')
		fp.write(content)
		fp.close()
		(status,result) = commands.getstatusoutput("pwd")
		static_path = result + "/addons/document/webdav/"
		(status,result) = commands.getstatusoutput("python %sodt2txt.py %s"%(static_path,fname))
	else:
		result = content
	return result
