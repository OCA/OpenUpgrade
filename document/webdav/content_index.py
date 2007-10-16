import time
import os
import commands

#
# This should be the indexer, the result is a UNICODE string
#
def content_index(content, filename=None, content_type=None):
	#
	# Should add a try: except: here, but remove during development
	#
	fname,ext = os.path.splitext(filename)
	result = ''
	if ext == '.doc':
		(stdin,stdout) = os.popen2('antiword -')
		stdin.write(content)
		stdin.close()
		# The default antiword encoding output is latin1
		result = stdout.read().decode('latin1','replace')
	elif ext == '.pdf':
		fname = os.tempnam(filename)+'.pdf'
		fp = file(fname,'wb')
		fp.write(content)
		fp.close()
		fp = os.popen('pdftotext  '+fname+' -', 'r')
		result = fp.read()
		# The default pdftotext encoding is latin1
		result = result.decode('latin1', "replace")
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
		result = ''
	return result
