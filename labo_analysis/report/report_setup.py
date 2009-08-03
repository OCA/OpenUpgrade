import netsvc
import pooler
import time
from report import report_sxw
from osv import osv

class report_setup(report_sxw.rml_parse):

    sample_l=[]
    type_v=''

    def __init__(self, cr, uid, name, context):
        super( report_setup, self).__init__(cr, uid, name, context)
        self.localcontext.update({
                'time': time,
                'get_well':self.get_well,
                'get_well2':self.get_well2,
                'get_setup': self.get_setup,
                'find_run':self.find_run,
        })

    def get_setup(self,objects):
#===============================================================================
#        print "objects: ",objects
#        print "objects.context: ",objects.context
#        print "objects.parents: ",objects.parents
#===============================================================================
        type_view=objects and objects[0].sample_id and objects[0].sample_id.type_id and objects[0].sample_id.type_id.code
        self.type_v=type_view
        setup_l=[]
        set_list=[]
        for sample_id  in objects:
            if sample_id.file_setup and sample_id.file_setup.set_up and type_view!="EMPCHE" and type_view!="EMPDOG" and type_view!='EMPDOG_2':
                set_list.append(sample_id.file_setup.set_up.id)
                setup_l.append(sample_id.id)
           # elif type_view=="EMPCHE" and type_view=="EMPDOG" and type_view=='EMPDOG_2':
            else:
                if sample_id.dog_child and sample_id.dog_child.file_setup and  sample_id.dog_child.file_setup.set_up:
                    set_list.append( sample_id.dog_child.file_setup.set_up.id)
                if sample_id.dog_mother and sample_id.dog_mother.file_setup and  sample_id.dog_mother.file_setup.set_up:
                    set_list.append( sample_id.dog_mother.file_setup.set_up.id)
                if sample_id.dog_father and sample_id.dog_father.file_setup and  sample_id.dog_father.file_setup.set_up:
                    set_list.append( sample_id.dog_father.file_setup.set_up.id)
        self.sample_l=setup_l
        self.set_list=dict([i,0] for i in set_list if i ).keys()
        if type_view=="EMPDOG_2" or type_view=="EMPDOG" or type_view=="EMPCHE":
#            self.cr.execute('select distinct(st.name), st.id,st.date_s, t.code from labo_analysis_type t,labo_analysis_request r,labo_sample l, labo_dog d,labo_setup st, analysis_setup s where st.id=s.set_up and t.id=r.type_id and l.sample_id = r.id and d.file_setup=s.id and l.id in ('+','.join(map(str,setup_l))+') and (l.dog_mother=d.id or l.dog_father=d.id or l.dog_child=d.id)')
#            self.cr.execute("select distinct(st.name), st.id,st.date_s, t.code from labo_analysis_type t,labo_analysis_request r,labo_sample l,"\
 #                           "labo_dog d,labo_setup st, analysis_setup s where st.id=s.set_up and t.id=r.type_id and l.sample_id = r.id "\
  #                          "and d.file_setup=s.id and st.id in ("+",".join(map(str,self.set_list))+") and (l.dog_mother=d.id or l.dog_father=d.id or l.dog_child=d.id)")
            self.cr.execute("select distinct(st.name), st.id,st.date_s, t.code from labo_analysis_type t,labo_analysis_request r,labo_sample l,"\
                            "labo_dog d,labo_setup st, analysis_setup s where st.id=s.set_up and t.id=r.type_id and l.sample_id = r.id "\
                            "and d.file_setup=s.id and st.id in ("+",".join(map(str,self.set_list))+") and (l.dog_mother=d.id or l.dog_father=d.id or l.dog_child=d.id)")
        else:
          #  self.cr.execute('select distinct(st.name), st.id,st.date_s, t.code from labo_analysis_type t,labo_analysis_request r,labo_sample l, labo_setup st, analysis_setup s where st.id=s.set_up and t.id=r.type_id and l.sample_id = r.id and l.file_setup=s.id and l.id in ('+','.join(map(str,setup_l))+')')
            self.cr.execute('select distinct(st.name), st.id,st.date_s, t.code from labo_analysis_type t,labo_analysis_request r,labo_sample l, labo_setup st,'\
                            'analysis_setup s where st.id=s.set_up and t.id=r.type_id and l.sample_id = r.id and l.file_setup=s.id '\
                            'and st.id in ('+','.join(map(str,self.set_list))+')')
        res = self.cr.fetchall()
        setup_l=[]
        for r in res:
            setup_l.append(r)
        return setup_l


    def find_run(self, o, val):
        if self.type_v=="EMPDOG_2" or self.type_v=="EMPDOG" or self.type_v=="EMPCHE":
            self.cr.execute("select distinct(at.run_setup) from labo_dog d, labo_analysis_type t,labo_analysis_request r,analysis_setup at, labo_sample s, labo_setup ls where at.set_up=ls.id and ls.id in ("+",".join(map(str,self.set_list))+")  and s.sample_id = r.id and at.set_up=ls.id and t.id=r.type_id and at.well in ("+",".join(map(str,val))+") and (s.dog_mother=d.id or s.dog_father=d.id or s.dog_child=d.id)")
           # self.cr.execute("select distinct(at.run_setup) from labo_dog d, labo_analysis_type t,labo_analysis_request r,analysis_setup at, labo_sample s, labo_setup ls where at.set_up=ls.id and s.id in ("+",".join(map(str,self.sample_l))+")  and s.sample_id = r.id and at.set_up=ls.id and t.id=r.type_id and at.well in ("+",".join(map(str,val))+") and (s.dog_mother=d.id or s.dog_father=d.id or s.dog_child=d.id)")
        else:
           # self.cr.execute("select distinct(at.run_setup) from labo_analysis_type t,labo_analysis_request r,analysis_setup at, labo_sample s, labo_setup ls where at.set_up=ls.id and s.id in ("+",".join(map(str,self.sample_l))+") and s.sample_id = r.id and at.set_up=ls.id and t.id=r.type_id and at.well in ("+",".join(map(str,val))+") ")
            self.cr.execute("select distinct(at.run_setup) from labo_analysis_type t,labo_analysis_request r,analysis_setup at, labo_sample s, labo_setup ls where at.set_up=ls.id and ls.id in ("+",".join(map(str,self.set_list))+") and s.sample_id = r.id and at.set_up=ls.id and t.id=r.type_id and at.well in ("+",".join(map(str,val))+") ")
        req_ids = self.cr.fetchone()
        return req_ids and req_ids[0] or False


    def get_well2(self, o,i):
        a=b=c=d=""
        aff=""
        if self.type_v=="EMPDOG_2" or self.type_v=="EMPDOG" or self.type_v=="EMPCHE":
            self.cr.execute("SELECT r.name, d.progenus_number from labo_analysis_type t, labo_analysis_request r,labo_setup ls, labo_sample s, labo_dog d, analysis_setup e where s.id in ("+",".join(map(str,self.sample_l))+") and e.set_up=ls.id and d.file_setup=e.id and e.well=%d and ls.id=%d and r.type_id=t.id and s.sample_id=r.id and (s.dog_mother=d.id or s.dog_father=d.id or s.dog_child=d.id) order by s.create_date desc "%(i,o))
        else:
            self.cr.execute("SELECT r.name, s.progenus_number from labo_analysis_type t, labo_analysis_request r,labo_setup ls, labo_sample s, analysis_setup e where s.id in ("+",".join(map(str,self.sample_l))+") and e.set_up=ls.id and s.file_setup=e.id and e.well=%d and ls.id=%d and r.type_id=t.id and s.sample_id=r.id order by s.create_date desc "%(i,o))
    #    self.cr.execute("SELECT f.name, s.progenus_number from labo_analysis_type t, labo_analysis_request r, labo_followsheet f,labo_setup ls, labo_sample s, analysis_setup e where s.id in ("+",".join(map(str,self.sample_l))+") and e.set_up=ls.id and s.file_setup=e.id and e.well=%d and ls.id=%d and s.follow_sheet_id=f.id and r.type_id=t.id and s.sample_id=r.id "%(i,o))
        req_ids = self.cr.fetchone()
        a= req_ids and str(req_ids[1]) or ""
        c=req_ids and req_ids[0] or ""
        if i==97:
            return req_ids and req_ids[1]
        if i>97  :
            if self.type_v=="EMPDOG_2" or self.type_v=="EMPDOG" or self.type_v=="EMPCHE":
                self.cr.execute("SELECT r.name, d.progenus_number from labo_dog d,labo_analysis_type t, labo_analysis_request r,labo_setup ls, labo_sample s, analysis_setup e where s.id in ("+",".join(map(str,self.sample_l))+") and e.set_up=ls.id and s.file_setup=e.id and e.well=%d and ls.id=%d and r.type_id=t.id and s.sample_id=r.id and (s.dog_mother=d.id or s.dog_father=d.id or s.dog_child=d.id) order by s.create_date desc"%(i-1,o))
            else:
                self.cr.execute("SELECT r.name, s.progenus_number from labo_analysis_type t, labo_analysis_request r,labo_setup ls, labo_sample s, analysis_setup e where s.id in ("+",".join(map(str,self.sample_l))+") and e.set_up=ls.id and s.file_setup=e.id and e.well=%d and ls.id=%d and r.type_id=t.id and s.sample_id=r.id order by s.create_date desc"%(i-1,o))
        #    self.cr.execute("SELECT f.name, s.progenus_number from labo_analysis_type t, labo_analysis_request r, labo_followsheet f,labo_setup ls, labo_sample s, analysis_setup e where s.id in ("+",".join(map(str,self.sample_l))+") and e.set_up=ls.id and s.file_setup=e.id and e.well=%d and ls.id=%d and s.follow_sheet_id=f.id and r.type_id=t.id and s.sample_id=r.id "%((i-1),o))
            req_ids1= self.cr.fetchone()
            b=req_ids1 and str(req_ids1[0]) or ""
            d=req_ids1 and req_ids1[1] or ""


        if b==c:
            aff=req_ids and req_ids[1]
        else:
            aff=(req_ids and str(req_ids[1]) or "")  + '\n'+ c
        return aff
    def get_well(self, o,i):
        a=b=c=d=""
        aff=""
        if self.type_v=="EMPDOG_2" or self.type_v=="EMPDOG" or self.type_v=="EMPCHE":
           #If follow
       #     self.cr.execute("SELECT f.name, d.progenus_number from labo_analysis_type t, labo_analysis_request r,labo_dog d, labo_followsheet f,"\
       #                         "labo_setup ls, labo_sample s, analysis_setup e where (d.follow_sheet_id=f.id)and e.set_up=ls.id and d.file_setup=e.id "\
       #                         "and e.well=%d and ls.id=%d and r.type_id=t.id and s.sample_id=r.id "\
       #                         "and (s.dog_mother=d.id or s.dog_father=d.id or s.dog_child=d.id) order by s.create_date desc"%(i,o))
            #If rapp
                self.cr.execute("SELECT r.name, d.progenus_number from labo_analysis_type t, labo_analysis_request r,labo_dog d,labo_setup ls, labo_sample s, "\
                                "analysis_setup e where ls.id in ("+",".join(map(str,self.set_list))+") and e.set_up=ls.id and d.file_setup=e.id and e.well=%d  "\
                                "and ls.id=%d and r.type_id=t.id and s.sample_id=r.id and (s.dog_mother=d.id or s.dog_father=d.id or s.dog_child=d.id) "\
                                "order by s.create_date desc "%(i,o))
         #   self.cr.execute("SELECT f.name, d.progenus_number from labo_analysis_type t, labo_analysis_request r,labo_dog d, labo_followsheet f, "\
         #                       "labo_setup ls, labo_sample s, analysis_setup e where d.follow_sheet_id=f.id "\
         #                       "and e.set_up=ls.id and d.file_setup=e.id and e.well=%d and ls.id=%d and r.type_id=t.id and s.sample_id=r.id "\
         #                       "and (s.dog_mother=d.id or s.dog_father=d.id or s.dog_child=d.id) order by s.create_date desc "%(i,o))
        else:
           # if followsheet
#            self.cr.execute("SELECT f.name, s.progenus_number from labo_analysis_type t, labo_analysis_request r,labo_setup ls,"\
#                            "labo_sample s, analysis_setup e, labo_followsheet f where e.set_up=ls.id and s.file_setup=e.id and e.well=%d and ls.id=%d "\
#                            "and r.type_id=t.id  and s.sample_id=r.id and s.follow_sheet_id=f.id order by s.create_date desc "%(i,o))
            #if rapp
            self.cr.execute("SELECT r.name, s.progenus_number from labo_analysis_type t, labo_analysis_request r,labo_setup ls, "\
                                "labo_sample s, analysis_setup e where ls.id in ("+",".join(map(str,self.set_list))+") and e.set_up=ls.id "\
                                "and s.file_setup=e.id and e.well=%d and ls.id=%d and r.type_id=t.id and s.sample_id=r.id order by s.create_date desc "%(i,o))
        req_ids = self.cr.fetchone()
        a= req_ids and str(req_ids[1]) or ""
        c=req_ids and req_ids[0] or ""
      #  if i==1:
      #      return req_ids and req_ids[1] or None
        if  i>=1  :
            if self.type_v=="EMPDOG_2" or self.type_v=="EMPDOG" or self.type_v=="EMPCHE":
               #if follow to return
              #  self.cr.execute("SELECT f.name, d.progenus_number from labo_analysis_type t, labo_analysis_request r,labo_dog d, labo_followsheet f,"\
              #                  "labo_setup ls, labo_sample s, analysis_setup e where (d.follow_sheet_id=f.id)and e.set_up=ls.id and d.file_setup=e.id "\
              #                  "and e.well=%d and ls.id=%d and r.type_id=t.id and s.sample_id=r.id "\
              #                  "and (s.dog_mother=d.id or s.dog_father=d.id or s.dog_child=d.id) order by s.create_date desc"%(i-1,o))
                #IF rapp nbr
                self.cr.execute("SELECT r.name, d.progenus_number from labo_analysis_type t, labo_analysis_request r,labo_dog d,labo_setup ls, labo_sample s, "\
                                "analysis_setup e where ls.id in ("+",".join(map(str,self.set_list))+") and e.set_up=ls.id and d.file_setup=e.id and e.well=%d  "\
                                "and ls.id=%d and r.type_id=t.id and s.sample_id=r.id and (s.dog_mother=d.id or s.dog_father=d.id or s.dog_child=d.id) "\
                                "order by s.create_date desc "%(i-1,o))
#                print ("SELECT r.name, d.progenus_number from labo_analysis_type t, labo_analysis_request r,labo_dog d,labo_setup ls, labo_sample s, "\
#                                "analysis_setup e where ls.id in ("+",".join(map(str,self.set_list))+") and e.set_up=ls.id and d.file_setup=e.id and e.well=%d  "\
#                                "and ls.id=%d and r.type_id=t.id and s.sample_id=r.id and (s.dog_mother=d.id or s.dog_father=d.id or s.dog_child=d.id) "\
#                                "order by s.create_date desc "%(i-1,o))
            else:
              # if followsheet to return
             #   self.cr.execute("SELECT f.name, s.progenus_number from analysis_setup e, labo_setup ls, labo_analysis_type t, labo_analysis_request r, "\
             #                   "labo_sample s,labo_followsheet f  where e.well=%d and e.set_up=ls.id  and r.type_id=t.id and s.sample_id=r.id and ls.id=%d "\
             #                   "and s.file_setup=e.id  and s.follow_sheet_id=f.id order by s.create_date desc "%(i-1,o))
                # if report number to return
                self.cr.execute("SELECT r.name, s.progenus_number from labo_analysis_type t, labo_analysis_request r, labo_setup ls, labo_sample s, "\
                                "analysis_setup e where ls.id in ("+",".join(map(str,self.set_list))+") "\
                                "and e.set_up=ls.id and s.file_setup=e.id and e.well=%d and ls.id=%d and r.type_id=t.id and s.sample_id=r.id  "\
                                "order by s.create_date desc "%(i-1,o))
            req_ids1= self.cr.fetchone()
            b=req_ids1 and str(req_ids1[0]) or ""
            d=req_ids1 and req_ids1[1] or ""
        if b==c:
            aff=req_ids and req_ids[1]
        else:
            aff=(req_ids and str(req_ids[1]) or "")  + '\n' + c
        return aff

report_sxw.report_sxw('report.setup','labo.sample','addons/labo_analysis/report/report_setup.rml',parser=report_setup,header_rml="labo_analysis/report/report_header_setup.rml")
report_sxw.report_sxw('report.setup1','labo.sample','addons/labo_analysis/report/report_setup1.rml',parser=report_setup)#,header_rml="labo_analysis/report/rml_header.rml")
