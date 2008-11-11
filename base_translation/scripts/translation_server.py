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

from SimpleXMLRPCServer import SimpleXMLRPCServer
import os
import csv
from config import *

server = SimpleXMLRPCServer((SERVER,PORT),allow_none=True)
#server.register_introspection_functions()

version_user={
        '4-2-0':['4.2.0',['admin','demo','dhara'] ],
        '4-2-1':['4.2.1',['admin','demo'] ],
        '4-3-0':['4.3.0',['dhara'] ],
        '4-4-0':['4.4.0',['demo','dhara','admin'] ],
    }

profile_user={
        'auction_house':['Auction House',['admin','demo','dhara'] ],
        'main' : ['Main',['admin','demo'] ],
        'service_companies' : ['Service Companies',['admin','dhara'] ],
    }


#contrib = "/home/tiny/translation/contrib"
#publish = "/home/tiny/translation/pu"

################### General Functions

def verify_user(user,pwd,lang):
    if user in list_lang[lang] and user in user_info and pwd==user_info[user]:
        return True
    else:
        return False

def directory_check(dir_list):
    dir = dir_list[0]
    for x in range(1,len(dir_list)):
        dir = dir+'/'+dir_list[x]
        if not os.path.exists(dir):
            os.mkdir(dir)

def file_dict_reader(fname):
    reader = csv.DictReader(open(fname,'rb'),delimiter=',')
    return map(lambda x:x,reader) 

def file_dict_writer(filename,content):
    outfile = open(filename,'w')
    h_row = {'type': 'type', 'res_id': 'res_id', 'name': 'name', 'value': 'value', 'src': 'src'}
    fieldnames = tuple(h_row.keys())
    outwriter = csv.DictWriter(outfile,fieldnames=fieldnames)
    outwriter.writerow(h_row)
    for row in content:
        row['src'] = row['src'].encode('utf8')
        row['value'] = row['value'].encode('utf8')
        outwriter.writerow(row)
                            ############# Need to improve

def file_merger(fname_revision,fname_main=None,content=None):# content will be used when 3 or more files needs to b merged
    if not content:
        main = file_dict_reader(fname_main)
    else:
         main = content
    revision =file_dict_reader(fname_revision)
    diff = filter(lambda x : x not in main, revision)
    for d in diff:
        found = False
        for m in main:
            if d['src']==m['src'] and d['type']==m['type'] and d['name']==m['name']:
                m['value']=d['value']
                found =True
        if not found:
            main.append(d)
    return main

################### List to retrive Language

def version_list(user):
    version=filter(lambda x:user in version_user[x][1],version_user)
    return map(lambda x:(x,version_user[x][0]),version)
               
def profile_list(user):
    profile=filter(lambda x:user in profile_user[x][1],profile_user)
    return map(lambda x:(x,profile_user[x][0]),profile)

def get_lang_list(user=None):
    if user:
        return filter(lambda x:user in list_lang[x],list_lang)
    return os.listdir(publish)
    
def get_publish_revision(lang,version,profile):
    path = '/'.join([publish,lang,version,profile])
    if os.path.exists(path):
        return map(lambda x:(x.split('-')[1].replace('.csv',''),'Revision '+x.split('-')[1].replace('.csv','')),os.listdir(path))
    return None

def get_contrib_revision(user,password,lang,version,profile):
    if not verify_user(user,password,lang):
        return None
    path = '/'.join([contrib,lang,version,profile])
    if os.path.exists(path):
        return map(lambda x:[x,x.split('-')[0],x.split('-')[1].replace('_AT_','@').replace('_DOT_','.'),x.split('-')[2].replace('.csv','')],os.listdir(path))
    return None


################### Get files from publish and contrib

def get_release(lang,version,profile,revision):
    depend_on = filter(lambda x : lang in dependent_language[x],dependent_language)
    main = '/'.join([publish,lang,lang])+'.csv'
    revision = '/'.join([publish,lang,version,profile,lang])+'-'+revision+'.csv'
    if depend_on:
        depend_on_fname = '/'.join([publish,depend_on[0],depend_on[0]])+'.csv'
        content = file_merger(main,fname_main=depend_on_fname)
        return file_merger(revision,content=content)
    return file_merger(revision,fname_main=main)

def get_contrib(user,password,lang,version,profile,fname,c=None):
    if not verify_user(user,password,lang):
        return None
    if c:
        path = '/'.join([publish,lang,version,profile])
    else:
        path = contrib+'/'+'/'.join([lang,version,profile])
    return file_dict_reader(path+'/'+fname)


################### Write files for publish and cotrib
    
def publish_contrib(lang,version,profile,filename,content):
    dir_list = [contrib,lang,version,profile]
    directory_check(dir_list)
    revision = len(os.listdir('/'.join(dir_list)))
    filename = filename +str(revision+1)+'.csv'
    fname = '/'.join([contrib,lang,version,profile,filename])
    file_dict_writer(fname,content)

def publish_release(user,password,lang,version,profile,content):
    if not verify_user(user,password,lang):
        return None
    dir_list = [publish,lang,version,profile]
    directory_check(dir_list)
    revision =len(os.listdir('/'.join(dir_list)))
    filename = '/'.join([publish,lang,version,profile,lang])+'-'+str(revision+1)+'.csv'
    file_dict_writer(filename,content)


server.register_function(verify_user)
server.register_function(version_list)
server.register_function(profile_list)
server.register_function(get_lang_list)
server.register_function(get_publish_revision)
server.register_function(get_contrib_revision)
server.register_function(get_release)
server.register_function(get_contrib)
server.register_function(publish_contrib)
server.register_function(publish_release)
server.serve_forever()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

