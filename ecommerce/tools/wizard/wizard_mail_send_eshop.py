
import wizard
import netsvc
import pooler
import time
import mx.DateTime
import datetime
import binascii
import base64
import os
from osv import osv
import tools

import smtplib;
import mimetypes;
from optparse import OptionParser;
from email.Message import Message;
from email.MIMEBase import MIMEBase;
from email.MIMEMultipart import MIMEMultipart;
from email.MIMEText import MIMEText;
from email.Header import Header
import smtplib
from email.Utils import COMMASPACE, formatdate
from email import Encoders
sent_dict={}
not_sent=[]

mail_send_form = '''<?xml version="1.0"?>
<form string="Mail to Customer">
    <field name = "partner_id"/>
    <newline/>
    <field name="subject"/>
    <newline/>
    <field name="message"/>
    <newline/>
    <field name ="attachment"/>
</form>'''

mail_send_fields = {
    'partner_id': {'string':'Customer','type': 'many2many', 'relation': 'res.partner','domain':"[('category_id','in',[1])]"},
    'subject': {'string':'Subject', 'type':'char', 'size':64, 'required':True},
    'message': {'string':'Message', 'type':'text', 'required':True},
    'attachment':{'string' : 'Attachment', 'type':'binary'}
}
   
     
mail_server_not_specify_form='''<?xml version="1.0"?>
<form string="SMTP Mail Server Error!">
    <separator string="Required Mail-Server!!!" colspan="4"/>
    <label string="Mail-Server Configuration Required" colspan="4"/>
    <field name="subject"/>
</form>''';

finished_form='''<?xml version="1.0"?>
<form string="Mail send ">
    <label string="Operation Completed " colspan="4"/>
    <field name ="mailsent" width="300"/>
    <field name ="mailnotsent" width="300"/>
    
</form>''';

finished_fields = {
                    'mailsent': {'string':'Mail Sent to', 'type':'text'},
                    'mailnotsent': {'string':'Mail Not sent', 'type':'text'}

                   }

partial_finish_form='''<?xml version="1.0"?>
<form string="Partial Operation Completed">
    <label string="Some of Contacts might not have email address\nCheck Requests" colspan="4"/>
</form>''';

not_partner_form = '''<?xml version="1.0"?>
<form string="Partner Adress is not Include">
    <label string="Some of Contacts might not have email address\nCheck Requests" colspan="4"/>
</form>''';




class wiz_send_email_eshop(wizard.interface):
 
    def _send_reminder(self, cr, uid, data, context):
            atch=data['form']['attachment']
            partner = data['form']['partner_id'][0][2]
         
            flag_success = True
            if partner:
                res = pooler.get_pool(cr.dbname).get('res.partner').browse(cr,uid,partner)
                for partner in res:
                    if partner.address and not partner.address[0].email:
                            not_sent.append(partner.name)
                    for adr in partner.address:
                        print ":::::::::::EEEEEEEEEEEEEEEEEEEEEEEEEeee",partner.name,adr.email
                        if adr.email:
                            print ":::::::::::EEEEEEEEEEEEEEEEEEEEEEEEEeee",partner.name,adr.email
                            sent_dict[partner.name]=adr.email
                            name = adr.name or partner.name
                            to = '%s <%s>' % (name, adr.email)
                           
                            mail_config_ids = pooler.get_pool(cr.dbname).get('smtp.mail.config').search(cr,uid,[])
                            print 'mail_config_ids',mail_config_ids
                            if not len(mail_config_ids):
                                    return 'mailservernotgivan'
                            else:
                                    mail_config_id = mail_config_ids[0]
                                    msg=data['form']['message']
                                    sub=data['form']['subject']
                                    atch=data['form']['attachment']
                        
                            send_ret = self._send_mail(cr,uid,mail_config_id,to,msg,sub,atch)
            return 'finished';
        
    def get_mail_dtl(self, cr, uid, data, context):
            dtl = len(sent_dict)
            cust_get_mail = []
            cust_not_get_mail=[]
            mail_value = ''
            not_mail = ''
            for items in sent_dict:
                cust_get_mail.append(items) 
                mail_value = mail_value+ ','+items
                
            for items_not in not_sent:
                cust_not_get_mail.append(items_not)
                not_mail = not_mail+ ','+items_not
            return {'mailsent':str(mail_value),'mailnotsent':str(not_mail)}

    def _send_mail(self,cr,uid,smtp_server_id,mail_to,body_message='',subject='',attachment=''):
            COMMASPACE = ','
            mail_pool = pooler.get_pool(cr.dbname).get('smtp.mail.config');
            print "smtp_server_id::::::::",smtp_server_id
            mail_data = mail_pool.read(cr, uid, [smtp_server_id])[0];
            print "mail data:::::::::",mail_data
     
            s = smtplib.SMTP()
            s.debuglevel = 5;
            con=s.connect(str(mail_data['server_name']),str(mail_data['port']))
            print "Connect :::: ",con,":::",s;
            print "str(mail_data['user_name'])",str(mail_data['user_name']),":::",str(mail_data['password'])
        
            s.login(str(mail_data['user_name']),str(mail_data['password']));
            outer = MIMEMultipart()
            outer['Subject'] = subject;
            outer['To'] =mail_to;
             
            mail_from= 'priteshmodi.eiffel@yahoo.co.in'
            outer['From'] = mail_from;

            if attachment:   
                temp_id=1
                file_name1 = "Report"+str(temp_id)+".pdf";
                temp_id+=1
                fp = file(file_name1,'wb+');
                content = base64.decodestring(attachment);
                fp.write(content);
                fp.close();
                outer.attach(MIMEText('Weekly report', 'plain', 'koi8-r'))
                fp = open(file_name1,'rb')
                img = MIMEBase('application', 'octet-stream')
                img.set_payload(fp.read())
                Encoders.encode_base64(img)
                fp.close()
                outer.attach(img)
          
            s.sendmail(mail_from,mail_to,outer.as_string());
            s.close();
            return True
  
    def create_request(self,cr,uid,message):
        admin_user_id = (pooler.get_pool(cr.dbname).get('res.users').search(cr,uid,[['name','=','Administrator']]))[0];
        req_dict = {
                    'act_from':uid,
                    'act_to' : admin_user_id,
                    'name' : 'Email Addres not found  !!!!',
                    'body' : message,
                    'priority' : '2',
                    'date_sent' : time.strftime('%Y-%m-%d'),
                    };
       
        request_id = pooler.get_pool(cr.dbname).get('res.request').create(cr,uid,req_dict);
        pooler.get_pool(cr.dbname).get('res.request').request_send(cr,uid,[request_id],None);

    states = {

            'init': {
                         'actions': [],
                         'result': {'type':'form', 'arch':mail_send_form, 'fields':mail_send_fields, 'state':[('end','Cancel'),('connect','Send Mail')]}
               
                     },
                     
            'connect': {
                         'actions': [],
                        'result': {'type':'choice', 'next_state': _send_reminder},
                     },
       
            'finished':{
                        'actions': [get_mail_dtl],
                        'result': {'type':'form', 'arch': finished_form, 'fields':finished_fields,'state':[('end','OK')]}
                          },
            'partial_finish':{
                           'actions': [],
                        'result': {'type':'form', 'arch': partial_finish_form, 'fields':{},'state':[('end','OK')]}
                          },
            'mailservernotgivan': {
                            'actions': [],
                            'result': {'type':'form', 'arch':mail_server_not_specify_form, 'fields':{}, 'state':[('end','OK')]}
                            },
             
            'not_partner' :{
                             'actions' : [],
                             'result' :{'type':'form','arch':not_partner_form,'fields':{}, 'state':[('end','OK')]}
                             }
          }
  
  
wiz_send_email_eshop('customer.send.mail.eshop') 


