# runs a sforce SOQL query and saves the results as a csv file.
import sys
import string
import beatbox
import xmltramp

sf = beatbox._tPartnerNS
svc = beatbox.Client()

def buildSoql(sobjectName):
	dr = svc.describeSObjects(sobjectName)
	soql = ""
	for f in dr[sf.fields:]:
		if len(soql) > 0: soql += ','
		soql += str(f[sf.name])
	return "select " + soql + " from " + sobjectName

def printColumnHeaders(queryResult):
	needsComma = 0
	# note that we offset 2 into the records child collection to skip the type and base sObject id elements
	for col in queryResult[sf.records][2:]:
		if needsComma: print ',',
		else: needsComma = 1
		print col._name[1],
	print
		
def export(username, password, objectOrSoql):
	svc.login(username, password)
	if string.find(objectOrSoql, ' ') < 0:
		soql = buildSoql(objectOrSoql)
	else:
		soql = objectOrSoql
	
	qr = svc.query(soql)
	printHeaders = 1
	while True:
		if printHeaders: printColumnHeaders(qr); printHeaders = 0
		for row in qr[sf.records:]:
			needsComma = False
			for col in row[2:]:
				if needsComma: print ',',
				else: needsComma = True
				print str(col),
			print
		if str(qr[sf.done]) == 'true': break
		qr = svc.queryMore(str(qr[sf.queryLocator]))

if __name__ == "__main__":

	if len(sys.argv) != 4:
		print "usage is export.py <username> <password> [<sobjectName> || <soqlQuery>]"
	else:
		export(sys.argv[1], sys.argv[2], sys.argv[3])
