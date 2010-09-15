#!/usr/bin/python

#Initialise nextvs file

vsid_file = open('/etc/vservers/nextvs','w')
id = 11
pickle.dump(id,vsid_file)
vsid_file.close()


