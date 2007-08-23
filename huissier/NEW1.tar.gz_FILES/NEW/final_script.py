import csv;
import traceback;
import sys;
import time;
import os;
import string;
import errno
import psycopg 
import shutil
import StringIO

class import_module:
    def __init__(self):
        self.filename=''
        self.filelist=['huissier_db.xml','res.lang.csv','res.partner.csv','res.partner.address.csv','account.invoice.csv','account.invoice.line.csv','huissier.vignettes.csv']
    def do_copy(self,source, dest):
        if os.path.islink(source):
            dest = os.path.join(os.path.dirname(dest), os.path.basename(source))
            try:
                do_create_link(os.readlink(source), dest)
            except (IOError, os.error), (errno, strerror):
                return (strerror, errno)
        elif os.path.isdir(source):
            try:
                os.mkdir(dest)
            except (IOError, os.error), (errno, strerror):
                pass     # don't return if directory exists
            else:
   
                pass
            for f in os.listdir(source):
                do_copy(os.path.join(source, f), os.path.join(dest, f))
        elif source == dest:
            raise IOError, (0, "Source and destination are the same file")
        else:
            shutil.copy2(source, dest)
    def copy(self,path, file, destdir, check_fileexists = 1):
        fullpath = os.path.join(path, file)
        if destdir[0] != os.sep:
            destdir = os.path.join(path, destdir)
        if os.path.isdir(destdir):
            fulldestdir = os.path.join(destdir, file)
            if os.path.exists(fulldestdir) and check_fileexists:
                return os.path.basename(fulldestdir)
        else:
            if os.path.exists(destdir) and check_fileexists:
                return os.path.basename(destdir)
            fulldestdir = destdir
        try:
            self.do_copy(fullpath, fulldestdir)
        except (IOError, os.error), (errno, strerror):
            return (strerror, errno)
    def read_file(self,name,delimiter='|'):
	name= 'data/'+name
	csv_file=open(name,'r')
	input=StringIO.StringIO(csv_file.read())
	reader = csv.reader(input, delimiter=delimiter)
	fields = reader.next()
	datas=[]
	for line in reader:
		datas.append(line)
	csv_file.close()
	return fields,datas
#function
    def make_huissier_csv(self):
    			pt_f=open('huissier.vignettes.csv', 'w')
			numb={}
			err_file=open('import_country_errors.txt','w');
			partner_fields,partner_datas=self.read_file('hussier_vignettes_export.csv')
			pt_fields=['acquis','invoice_id:id','price','etude_id:id','state','last','income_account_id:id','first','date_creation','quantity']
			pt_f.write(','.join(pt_fields)+"\n")
			pt_w=csv.DictWriter(pt_f, pt_fields, extrasaction='ignore',delimiter=',')

			partners=[]
			par=[]
			par_dict={}			
			length = len(partner_datas)
			count=0
			try:
				for data in partner_datas:
				    try:
					line={}
					rec={}
					i=0
					for field in partner_fields:
						rec[field]=data[i]
						i+=1			
					line['acquis']=rec['acquis']
					line['invoice_id:id']='huissier_db.'+rec['invoice_id'] or ''
					line['price']=rec['price']
					line['etude_id:id']='huissier_db.'+rec['etude_id']
					line['state']=rec['state']
					line['last']=rec['last']
					if not rec['income_account_id']:
						 line['income_account_id:id']=''				  
					elif int(rec['income_account_id'])== 66:
						line['income_account_id:id']='Vignettes'	
					line['first']=rec['first']
					line['date_creation']=rec['date_creation']
					line['quantity']=rec['quantity']
					pt_w.writerow(line)
					
				    except Exception,e :
				    	print >> err_file,'----------Record Data--------- Starts ==>321' +str(e)				    	
				    	print line['name']
			except Exception,e:
			            print "Exception Found..@@@@@@@@@@@@@@." + str(e)
			    
			           

    def make_invoice_csv(self):
    			pt_f=open('account.invoice.csv', 'w')
			numb={}
			err_file=open('import_country_errors.txt','w');
			partner_fields,partner_datas=self.read_file('account_incoive_export.csv')
			pt_fields=['id','number','address_invoice_id:id','partner_id:id','state','type','account_id:id','currency_id:id','company_id:id','date_invoice','name','address_contact_id:id','invoice_line/name','invoice_line/price_unit','invoice_line/quantity','invoice_line/account_id']
			pt_f.write(','.join(pt_fields)+"\n")
			pt_w=csv.DictWriter(pt_f, pt_fields, extrasaction='ignore',delimiter=',')

			partners=[]
			par=[]
			par_dict={}
			length = len(partner_datas)
			
			count=0
			try:
				for data in partner_datas:
				
				    try:
					line={}
					rec={}
					i=0
					for field in partner_fields:
						rec[field]=data[i]
						i+=1
					line['id']=rec['id']
				        line['number']=rec['number']
				        if rec['address_invoice_id']:
						line['address_invoice_id:id']='huissier_db.'+ rec['address_invoice_id']
					else:
						
						line['address_invoice_id:id']='huissier_db.address_unknown'
						print "*********",line['address_invoice_id:id']
					if rec['partner_id']:
						line['partner_id:id']='huissier_db.' + rec['partner_id']
					else:
						line['partner_id:id']='huissier_db.partner_unknown'
				        line['state']=rec['state']
					line['type']=rec['type']
						
					
					if rec['account_id']:
						line['account_id:id']='account.a_recv'
					else:
						line['account_id:id']='huissier_db.account_unknown'
					
					line['company_id:id']='base.main_company'
					line['currency_id:id']='base.rateEUR'
					line['date_invoice']=rec['date_invoice']	
					line['name']= rec['name']
					if rec['address_contact_id']:		
						line['address_contact_id:id']='huissier_db.'+ rec['address_contact_id']
					line['invoice_line/name']=rec['invoice_line_name']			
					line['invoice_line/price_unit']= rec['invoice_line_price_unit']		
					line['invoice_line/quantity']=rec['invoice_line_quantity']		
					if not rec['invoice_line_account_id']:
						line['invoice_line/account_id']='unknown'
					elif int(rec['invoice_line_account_id'])== 64:
						line['invoice_line/account_id']='Frais de salle'
					elif int(rec['invoice_line_account_id'])== 65:
						line['invoice_line/account_id']='Frais de voirie'	
					elif int(rec['invoice_line_account_id'])== 66:
						line['invoice_line/account_id']='Vignettes'	
					elif int(rec['invoice_line_account_id'])== 67:
						line['invoice_line/account_id']='Frais de garde '				
					
					pt_w.writerow(line)
					
				    except Exception,e :
				    	print >> err_file,'----------Record Data--------- Starts ==>321' +str(e)
				    	
			except Exception,e:
			            print "Exception Found..@@@@@@@@@@@@@@2." + str(e)
			           
			            
			            

			
			f=open('account.invoice.line.csv', 'w')
			partner_fields,partner_datas=self.read_file('account_incoive_line_export.csv')
			

			fields=['invoice_id:id','name','price_unit','quantity','account_id']
			f.write(','.join(fields)+"\n")
			w=csv.DictWriter(f, fields, extrasaction='ignore',delimiter=',')
			try:
				for data in partner_datas:
				    try:
					rec={}
					i=0
					
					for field in partner_fields:
						rec[field]=data[i]
						i+=1
						
					if rec['invoice_id']:
						line['invoice_id:id']='huissier_db.'+rec['invoice_id']
					line['name']=rec['name'] 
					line['price_unit']=rec['price_unit']	
					line['quantity']=rec['quantity']
					if not rec['account_id']:
						line['account_id']='unknown'	
					elif int(rec['account_id'])== 64:
						line['account_id']='Frais de salle'
					elif int(rec['account_id'])== 65:
						line['account_id']='Frais de voirie'	
					elif int(rec['account_id'])== 66:
						line['account_id']='Vignettes'	
					elif int(rec['account_id'])== 67:
						line['account_id']='Frais de garde'				
							
					w.writerow(line)
					
				    except Exception,e:
			           		print "Exception Found.*************.123" + str(e)
			           		
			except Exception,e:
			            print "Exception Found..%%%%%%%%%%%%%%%.ddd" + str(e)
			
			f.close()
			pt_f.close()

    
    def make_partner_csv(self):   			

			pt_f=open('res.partner.csv', 'w')
			numb={}
			err_file=open('import_country_errors.txt','w');
			partner_fields,partner_datas=self.read_file('res_partner_export.csv')
			pt_fields=['id','lang','website','name','comment','active','vat', 'address/name', 'address/street', 'address/zip', 'address/city', 'address/email', 'address/phone','address/type','address/fax']
			pt_f.write(','.join(pt_fields)+"\n")
			pt_w=csv.DictWriter(pt_f, pt_fields, extrasaction='ignore',delimiter=',')

			partners=[]
			par=[]
			par_dict={}
			
			length = len(partner_datas)			
			count=0
			try:
				for data in partner_datas:
				    try:
					line={}
					rec={}
					i=0
					for field in partner_fields:
						rec[field]=data[i]
						i+=1
					line['id']=rec['id']
				        line['lang']=rec['lang'] or 'en'
					line['website']=rec['website']
					
					p=str(rec['name']).strip()		
			
					
					if p in par:
						if p== 'unknown':
							continue
						else:
													
							if par_dict.has_key(p):
								count=par_dict[p]
								count=count+1
							par_dict[p]=count							
							line['name']=p + str(count)
							
					else:
						line['name']=p
						
					
						
					par.append(p)
					
					partners.append(line['name'])	
						
					line['comment']=rec['comment']	
					line['active']=rec['active']		
					line['address/name']= rec['address_name'] 	
					line['address/street']=   rec['address_street'] 			
					line['address/zip']=rec['address_zip']		
					line['address/city']=rec['address_city']				
					line['address/email']=rec['address_email']	
					line['address/phone']=rec['address_phone']			
					line['address/type']=rec['address_type']
					line['address/fax']=rec['address_fax']					
					pt_w.writerow(line)
					
				    except Exception,e :
				    	print >> err_file,'----------Record Data--------- Starts ==>3' +str(e)
				    	print "Record Processed",c
				    	print line['name']
			except Exception,e:
			            print "Exception Found..@@@@@@@@@@@@@@2." + str(e)
			           

			
			f=open('res.partner.address.csv', 'w')
			partner_fields,partner_datas=self.read_file('res_partner_address_export.csv')
			
			fields=['partner_id:id','name','street', 'zip', 'city','email', 'phone','type','fax']
			f.write(','.join(fields)+"\n")
			w=csv.DictWriter(f, fields, extrasaction='ignore',delimiter=',')
			temp= '\"'
			try:
				for data in partner_datas:
				    try:
					rec={}
					i=0
					
					for field in partner_fields:
						rec[field]=data[i]
						i+=1
						
					if rec['partner_id']:
						line['partner_id:id']='huissier_db.'+rec['partner_id']
					line['name']=rec['p_name'] 
					line['street']= rec['street'] 	
					line['zip']=rec['zip']		
					line['city']=rec['city']		
					line['email']=rec['email']	
					line['phone']=rec['phone']
					line['type']=rec['type'] 
					line['fax']=rec['fax'] 
					w.writerow(line)
					
				    except Exception,e:
			           		print "Exception Found.*************." + str(e)
			           		#print >>err_file,'----------Record Data--------- Starts ==>ERROR==>' + str(e)
			except Exception,e:
			            print "Exception Found..%%%%%%%%%%%%%%%." + str(e)
			
			f.close()
			pt_f.close()
   

    def _import(self):
        list1=[]
        self.make_partner_csv()
        self.make_invoice_csv()
        self.make_huissier_csv()
        tabcount=0
        terp_dict={
        	"name" : "Huissier Data",
    		"version" : "1.0",
    		"author" : "Tiny",
    		"category" : "Data Module",
    		"depends" : ["base","Huissier"],
    		"init_xml" : [],
    		"demo_xml" : [],
    		"active": False,
		"installable": True,
        	}
        try:
            module_name='huissier_db'
            temp=raw_input("Enter modulename (huissier_db)===>");
            if temp:
                module_name=temp
            source='/home/tinyadmin/Desktop/NEW'
            DIRNAME = '/home/tinyadmin/Desktop/myauction/server/bin/addons/' + module_name
            print DIRNAME

            flename1=['__init__.py','__terp__.py']
   		
            try:
                os.makedirs(DIRNAME)
                for i in range(len(flename1)):
                    print DIRNAME +'/'+ flename1[i]
                    f=open(DIRNAME +'/'+ flename1[i],"w")
                    f.close()

            except OSError, err:
                if err.errno == errno.EEXIST:
                    if os.path.isdir(DIRNAME):
                        print "directory already exists"
                    else:
                        print "file already exists, but not a directory"
                        raise # re-raise the exception
                else:
                    raise       
            
	          
            for i in range(len(self.filelist)):                     
            	terp_dict["init_xml"].append(str(self.filelist[i]))
                    
            for i in range(len(self.filelist)):
                self.copy(source,self.filelist[i],DIRNAME,1)           
            tp=open(DIRNAME + '/' +'__terp__.py','w')
            print >> tp,terp_dict            
      
	    

        except Exception,e:
            print "Exception Found..." + str(e)


obj = import_module()
obj._import()

