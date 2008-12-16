#!/usr/bin/python
# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution	
#    Copyright (C) 2004-2008 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
import csv
import datetime
import time
from datetime import date, timedelta
import psycopg

map_sec = {
'model_id':  lambda x: '',
'group_id': lambda x:'', #should be the last day of x['YEAR,I,4']
'perm_read': lambda x: '',#should be the first day of x['YEAR,I,4']
'perm_create': lambda x: '',
'perm_unlink': lambda x:  '',
'perm_write': lambda x:  '',
'name':lambda x: '',
}
map_headers = {
'model_id': 'model_id',
'group_id': 'group_id', #should be the last day of x['YEAR,I,4']
'perm_read': 'perm_read',#should be the first day of x['YEAR,I,4']
'perm_create': 'perm_create',
'perm_unlink': 'perm_unlink',
'perm_write': 'perm_write',
'name':'name'
}

def import_csv(writer_security, map_sec, map_headers):
    s = "host=localhost dbname=mra user='postgres' port=5432 password='postgres'"
    handle=psycopg.connect(s)
    cr = handle.cursor()
    #cr.execute("select model as model_id,'1' as perm_read,  model as name,'1' as perm_create,'1' as perm_unlink,'1' as perm_write,res_groups.name as group_id from ir_model,res_groups where model like '%cci%' order by model")
    cr.execute("select ir_model.name as model_id,'1' as perm_read,  ir_model.name as name,'1' as perm_create,'1' as perm_unlink,'1' as perm_write,res_groups.name as group_id from ir_model,res_groups  where model like '%cci%' or model like 'account%' or model like 'sale%' or model like 'audittrail%' or model like 'res.partner%' or model like 'meeting%' or model like 'crm%' or model like 'event%' or model like 'res.company' or model like 'res.con%' or model like 'purchase%' \
                or model like 'credit%' or model like 'translation' or model like 'letter%' or model like 'membership' \
                or model like 'product%' or model like 'project%' or model like 'payment%' or model like 'crossovered%' \
                or model like 'hr%' order by model")
    d=[]
    record = {}
#    for key, column_name in map_headers.items():
#        print key
#        record[key] = column_name
    #record1 = ['model_id', 'group_id', 'perm_read', 'perm_create', 'perm_unlink', 'perm_write']
#    print record
    record = {'model_id': 'model_id', 'group_id': 'group_id',  'perm_read': 'perm_read', 'perm_unlink': 'perm_unlink', 'perm_write': 'perm_write', 'perm_create': 'perm_create','name':'name'}
    writer_security.writerow(record)

    for i in cr.fetchall():
#        for j in range(len(i)):
 #           print j
        record = {}
        j=0
        for key,fnct in map_sec.items():
            record[key] =  i[j]
            j=j+1
        writer_security.writerow(record)
if __name__=='__main__':
    writer_security = csv.DictWriter(file('ir.model.access.csv', 'wb'),map_sec.keys())
    import_csv(writer_security, map_sec, map_headers)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
