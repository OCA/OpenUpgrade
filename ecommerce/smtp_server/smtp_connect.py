
from osv import fields,osv
import pooler
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.Utils import COMMASPACE, formatdate

class smtp_mail_config(osv.osv):
    _description='Mail Server Config'
    _name = "smtp.mail.config"
    _columns = {
                'name':fields.char('Name', size=128, required=True),
                'server_name': fields.char('SMTP Server Name', size=128, required=True),
                'port': fields.integer('SMTP Port', size=64,required=True),
                'user_name':fields.char('User Name',size=128,required=True),
                'password': fields.char('Password',size=128,required=True,invisible=True),
                'from_add': fields.char('Email From',size=255,required=True),
                'ssl_name':fields.boolean('SSL Server')
     }

    def __init__(self, pool):
        super(smtp_mail_config,self).__init__(pool);
        self.smtpserver = None;
        self.email = None;
 
    def connect(self, cr, uid, id=False):
        server = False
        
        if id:
            server = self.read(cr, uid, [id])[0]
        else:
            return False
        if server:
            self.smtpserver = smtplib.SMTP(str(server['server_name']), server['port']);
            self.smtpserver.set_debuglevel(1)

            if server['istls']:
                self.smtpserver.ehlo(str(server['user_name']))
                self.smtpserver.starttls()
                self.smtpserver.ehlo(str(server['user_name']))
            self.smtpserver.login(str(server['user_name']), str(server['password']));

            self.email = server['from_add']
            return True;
        return False
  
    def close(self):
        try:
            self.smtpserver.close()
        except Exception,e:
            return False
        return True
    
    def sendmail(self, cr, uid, to, subject='', body=''):

        msg = MIMEMultipart()
        msg['From'] = self.email
        msg['To'] = to
        msg['Date'] = formatdate(localtime=True)
        msg['Subject'] = subject

        part1 = MIMEText(body);
        part1.set_type("text/html");
        msg.attach(part1)
        try:
            self.smtpserver.sendmail(self.email, to, msg.as_string())
        except Exception,e:
            return False
        return True

smtp_mail_config()


