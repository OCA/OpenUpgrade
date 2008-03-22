from SimpleXMLRPCServer import SimpleXMLRPCServer
import os
import csv

server = SimpleXMLRPCServer(("192.168.0.4",8000),allow_none=True)
server.register_introspection_functions()

user_info={
        'admin':'admin',
        'dhara':'dhara'
    }
list_lang={
        'zh_CN': ['admin'],
        'zh_TW': ['admin'],
        'cs_CZ': ['admin'],
        'de_DE': ['admin'],
        'es_AR': ['admin','dhara'],
        'es_ES': ['admin','dhara'],
        'fr_FR': ['admin','dhara'],
        'fr_CH': ['admin','dhara'],
        'en_EN': ['admin','dhara'],
        'hu_HU': ['dhara'],
        'it_IT': ['dhara'],
        'pt_BR': ['dhara','admin'],
        'pt_PT': ['dhara'],
        'nl_NL': ['dhara'],
        'ro_RO': [],
        'ru_RU': [],
        'sv_SE': [],
    }

def verify_user(user,pwd,lang):
    if user in list_lang[lang] and user in user_info and pwd==user_info[user]:
        return True
    else:
        return False   

contrib = "/home/tiny/translation/contrib"
publish = "/home/tiny/translation/publish"

def file_name(filename):
    if filename.find('AT')>0:
        return filename.split('-')[0]
    else: 
        return filename.replace('.csv','')

def get_contrib_list():
    return os.listdir(contrib)


def get_release(filename):
    file_content = file(publish+"/"+filename,'rb').read()
    return file_content.decode('utf8')
    
def publish_contrib(filecontent,filename):
    outfile = open(contrib+"/"+filename,'wb')
    UnicodeWriter = csv.writer(outfile,delimiter=',')
    for row in filecontent:
        row[3] = row[3].encode('utf8')
        row[4] = row[4].encode('utf8')
        UnicodeWriter.writerow(row)

def get_publish_list(user=None):
    if user:
        return filter(lambda lang : user in list_lang[lang.replace('.csv','')] ,list_lang)
    return os.listdir(publish)


# Is not finished yet
def publish_release(user,password,publish,filename):
    outfile = open(publish+"/"+filename,'wb')
    UnicodeWriter = csv.writer(outfile,delimiter=',')
    for row in filecontent:
        row[3] = row[3].encode('utf8')
        row[4] = row[4].encode('utf8')
        UnicodeWriter.writerow(row)

def get_contrib(filename,user,pwd,lang):
    if verify_user(user,pwd,lang):
        reader = csv.DictReader(open(contrib+"/"+filename,'rb'),delimiter=',')
        return map(lambda x:x,reader)
    else:
        return False

     
server.register_function(get_contrib_list)
server.register_function(get_publish_list)
server.register_function(publish_release)
server.register_function(get_release)
server.register_function(publish_contrib)
server.register_function(get_contrib)


server.serve_forever()