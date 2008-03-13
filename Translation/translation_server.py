from SimpleXMLRPCServer import SimpleXMLRPCServer
import os
import csv

server = SimpleXMLRPCServer(("192.168.0.4",8000),allow_none=True)
server.register_introspection_functions()

user_info={'admin':('admin', ['fr_FR','pt_PT']),'dhara':('dhara', ['nl_NL'])}

def verify_user(user,pwd,lang):
    if user in user_info and pwd==user_info[user][0] and lang in user_info[user][1]:
        return True
    else:
        return False   

contrib = "/home/tiny/translation/contrib"
publish = "/home/tiny/translation/publish"


def get_contrib_list():
    return os.listdir(contrib)

def get_publish_list():
    return os.listdir(publish)

def publish_release(filecontent,filename):
    outfile = open(publish+"/"+filename,'wb')
    UnicodeWriter = csv.writer(outfile,delimiter=',')
    for row in filecontent:
        row[3] = row[3].encode('utf8')
        row[4] = row[4].encode('utf8')
        UnicodeWriter.writerow(row)

def get_release(filename):
    file_content = file(contrib+"/"+filename,'rb').read()
    return file_content.decode('utf8')

def publish_contrib(filecontent,filename):
    outfile = open(contrib+"/"+filename,'wb')
    UnicodeWriter = csv.writer(outfile,delimiter=',')
    for row in filecontent:
        row[3] = row[3].encode('utf8')
        row[4] = row[4].encode('utf8')
        UnicodeWriter.writerow(row)


def get_contrib(filename,user,pwd,lang):
    print filename,user,pwd,lang
    result = verify_user(user,pwd,lang)
    if verify_user(user,pwd,lang):
        file_content = file(contrib+"/"+filename,'rb').read()
        return file_content.decode('utf8')
    else:
        return False
#        return "Bad User name or Passsword or you are not authorised for this language"  



     
server.register_function(get_contrib_list)
server.register_function(get_publish_list)
server.register_function(publish_release)
server.register_function(get_release)
server.register_function(publish_contrib)
server.register_function(get_contrib)


server.serve_forever()