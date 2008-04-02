#!/usr/bin/python

from SimpleXMLRPCServer import SimpleXMLRPCServer
import os
import csv
from config import *

server = SimpleXMLRPCServer((SERVER,PORT),allow_none=True)
server.register_introspection_functions()

version_user={
        '4-2-0':['4.2.0',['admin','demo','dhara'] ],
        '4-2-1':['4.2.1',['admin','demo'] ],
        '4-3-0':['4.3.0',['admin','dhara'] ],
        '4-4-0':['4.4.0',['demo','dhara'] ],
    }

profile_user={
        'auction_house':['Auction House',['admin','demo','dhara'] ],
        'main' : ['Main',['admin','demo'] ],
        'service_companies' : ['Service Companies',['admin','dhara'] ],
    }

#contrib = "/home/tiny/translation/contrib"
#publish = "/home/tiny/translation/pu"

def verify_user(user,pwd,lang):
    if user in list_lang[lang] and user in user_info and pwd==user_info[user]:
        return True
    else:
        return False   

def directory_check(directory):
    if os.path.exists(directory):
        return
    os.mkdir(directory)


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
	path = '/'.join([publish,lang,version,profile])
	filename = lang+'-'+revision+'.csv'
	file_content = file(path+'/'+filename,'rb').read()
	return file_content.decode('utf8')

def get_contrib(user,password,lang,version,profile,fname,c=None):
    if not verify_user(user,password,lang):
        return None
    if c:
    	path = '/'.join([publish,lang,version,profile])
    else:
    	path = contrib+'/'+'/'.join([lang,version,profile])
    reader = csv.DictReader(open(path+'/'+fname,'rb'),delimiter=',')
    return map(lambda x:x,reader)


################### Write files for publish and cotrib
    
def publish_contrib(lang,version,profile,filename,content):
    dir_list = [lang,version,profile]
    path = contrib
    for x in dir_list:
        path = path+'/'+x
        directory_check(path)
    outfile = open(path+"/"+filename,'wb')
    UnicodeWriter = csv.writer(outfile,delimiter=',')
    for row in content:
        row[3] = row[3].encode('utf8')
        row[4] = row[4].encode('utf8')
        UnicodeWriter.writerow(row)

def publish_release(user,password,lang,version,profile,filename,content):
    if not verify_user(user,password,lang):
        return None
    dir_list = [lang,version,profile]
    path = publish + '/' +('/'.join(dir_list))
    outfile = open(path+"/"+filename,'wt')
    h_row = {'type': 'type', 'res_id': 'res_id', 'name': 'name', 'value': 'value', 'src': 'src'}
    fieldnames = tuple(h_row.keys())
    outwriter = csv.DictWriter(outfile,fieldnames=fieldnames)
    outwriter.writerow(h_row)
    for row in content:
        row['src'] = row['src'].encode('utf8')
        row['value'] = row['value'].encode('utf8')
        outwriter.writerow(row)
    return True


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