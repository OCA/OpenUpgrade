#!/usr/bin/python2.5
#
# ODMS server script
#

import os
import pickle

def newvs():

	#Get new vs id
	vsid_file = open('/etc/vservers/nextvs','r')
	vsid = pickle.load(vsid_file)
	print "DEBUG - ODMS create vs - VSID type",type(vsid)
	print "DEBUG - ODMS create vs - VSID",vsid
	vsid_file.close()

	# Create new vserver
	cmd = "dupvserver --ip 10.1.0."+str(vsid)+" --from vs-base --to vs-customer-"+str(vsid)+" >> /var/log/openerp/odms.log 2>&1"
	print "DEBUG - ODMS create vs - cmd",cmd
	res = os.system(cmd)
	print "DEBUG - ODMS create vs - res",res

	# Set new VS context
	file = "/etc/vservers/vs-customer-"+str(vsid)+"/context"
	vscontext_file = open(file,'w')
	r = vscontext_file.write(str(vsid)+"\n")
	vscontext_file.close()

	# Set next vsid 
	nextvsid = vsid+1
	vsid_file = open('/etc/vservers/nextvs','w')
	pickle.dump(nextvsid,vsid_file)
	vsid_file.close()

	# Start Vserver
	scmd = "vserver vs-customer-"+str(vsid)+" start"
	sres = os.system(scmd)

	print "DEBUG - ODMS start vs - sres",sres

	# return vsid
	if (res == 0):
		return vsid
	return False


def newweb(vserv_id, url):

	# TODO : Not limited to 100
	ipt_rule = 'iptables -t nat -A PREROUTING -d 78.24.129.70 -p tcp -m tcp --dport 80'+vserv_id+'-j DNAT --to-destination 10.1.0.'+vserv_id+':8080'

	os.system(ipt_rule)

	return True

