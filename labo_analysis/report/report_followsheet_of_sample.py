import netsvc
import pooler
import time
from report import report_sxw
import pooler

class report_followsheet_of_sample(report_sxw.rml_parse):
    req_l=[]
    ait=[]
    bl=[]
    follow_id=[]
    ati=[]
    type_v=''
    def __init__(self, cr, uid, name, context):
        super(report_followsheet_of_sample, self).__init__(cr, uid, name, context)
        self.localcontext.update({
                    'time': time,
                    'get_begining_date':self.get_begining_date,
                    'get_date_closed':self.get_date_closed,
                    'get_date_closed_c':self.get_date_closed_c,
                    'get_report_type':self.get_report_type,
                    'get_report_type_c':self.get_report_type_c,
                    'ct':self.ct,
                    'ct_c':self.ct_c,
                    'get_followsheet': self.get_followsheet,
                    'get_followsheet_2': self.get_followsheet_2,
                    'get_request':self.get_request,
                    'get_request_c':self.get_request_c,
                    'get_urgent':self.get_urgent,
                    'get_urgent_c':self.get_urgent_c,
                    'get_code':self.get_code,
                    'get_code_c':self.get_code_c,
                    'get_material':self.get_material,
                    'get_material_c':self.get_material_c,
                    'get_notice':self.get_notice,
                    'get_notice_c':self.get_notice_c,
                    'get_res':self.get_res,
                    'get_res_c':self.get_res_c,
                    'get_date_limit':self.get_date_limit,
                    'get_date_limit_c':self.get_date_limit_c,
                    'get_setup':self.get_setup,
                    'get_request_name':self.get_request_name,
                    'get_request_name_c':self.get_request_name_c,
                    'get_begining_date_c':self.get_begining_date_c,
             })



    def get_request(self,o):
        s_ids=[]
        self.cr.execute('select l.id from labo_sample l, labo_followsheet f,labo_analysis_request r where f.id=l.follow_sheet_id and r.id in  ('+','.join(map(str,self.req_l))+')  and r.id=l.sample_id and f.id =%d order by l.progenus_number '%(o))
        res=self.cr.fetchall()
        for r in res:
            s_ids.append(r[0])
        return s_ids

    def get_request_c(self,o):
        s_ids=[]
        c= ','.join(map(str,self.list_r))
        self.cr.execute('select d.id from labo_sample l, labo_followsheet f,labo_analysis_request r , labo_dog d '\
                        'where f.id=d.follow_sheet_id and f.id =  %d  '\
                        'and r.id=l.sample_id  and (d.id=l.dog_child or d.id=l.dog_father '\
                        'or d.id=l.dog_mother ) and d.done_i is null and r.id=%d order by d.progenus_number asc'%(o,int(c)))
     #   self.cr.execute('select d.id from labo_sample l, labo_followsheet f,labo_analysis_request r , labo_dog d '\
     #                   'where f.id=d.follow_sheet_id and f.id in  ('+','.join(map(str,self.req_l))+')  '\
     #                   'and r.id=l.sample_id  and (d.id=l.dog_child or d.id=l.dog_father '\
     #                   'or d.id=l.dog_mother ) and d.done_i is null and r.id=%d order by d.progenus_number'%(int(c)))
        res=self.cr.fetchall()
        for r in res:
            s_ids.append(r[0])
        s_ids=dict([i,0] for i in s_ids if i ).keys()
        s_ids.sort()
        return s_ids

    def get_followsheet_2(self,objects):
        follow_r=[]
        list_r=[]
        list_r.append(objects and objects[0] and objects[0].id)
        self.list_r=list_r
        b=[]
        a=[]
        st=[]
        l_prog=[]
        ati=[]
        for req in objects:
            for r in req.sample_ids:
                if r.dog_child and r.dog_child.follow_sheet_id:
                    follow_r.append(r.dog_child.follow_sheet_id.id)
                if r.dog_mother and r.dog_mother.follow_sheet_id:
                    follow_r.append(r.dog_mother.follow_sheet_id.id)
                if r.dog_father and r.dog_father.follow_sheet_id:
                    follow_r.append(r.dog_father.follow_sheet_id.id)
        self.bl=b
        follow_r=dict([i,0] for i in follow_r if i).keys()
        self.req_l=follow_r
        self.cr.execute("select distinct(st.name),st.id, st.date_f from labo_analysis_type t,labo_analysis_request r,labo_sample l,"\
                        "labo_dog d,labo_followsheet st where st.id=d.follow_sheet_id and t.id=r.type_id and l.sample_id = r.id "\
                        "and st.id in ("+",".join(map(str,follow_r))+") and (l.dog_mother=d.id or l.dog_father=d.id "\
                        "or l.dog_child=d.id) and d.done_i is null")
        res = self.cr.fetchall()
        follow_s=[]
        for r in res:
            follow_s.append(r)
            st.append(r[1])
        return follow_s


    def get_followsheet(self,objects):
        follow_r=[]
        b=[]
        a=[]
        st=[]
        ati=[]
        for req in objects:
            follow_r.append(req.id)
            for r in req.sample_ids:
                self.cr.execute('select st.id from  labo_analysis_request r,labo_sample l, labo_followsheet st where st.id=l.follow_sheet_id and l.sample_id = r.id and r.id =%d  and l.id =%d '%(req.id, r.id))
                res=self.cr.fetchone()
                if res and res[0]:
                    b.append(r.id)
        self.bl=b
        self.req_l=follow_r
        self.cr.execute('select  distinct(st.name), st.id,st.date_f from labo_analysis_request r,labo_sample l, labo_followsheet st where st.id=l.follow_sheet_id and l.sample_id = r.id and r.id in ('+','.join(map(str,follow_r))+') ')
        res = self.cr.fetchall()
        follow_s=[]
        for r in res:
            follow_s.append(r)
            st.append(r[1])
            ati.append(r[0])
        self.follow_id=st
        self.ati=ati
        return follow_s

    def get_begining_date(self,i,e):
        self.cr.execute('select l.date_starting from labo_analysis_request r, labo_sample l, labo_followsheet f where l.follow_sheet_id=f.id and r.id=l.sample_id and f.id=%d and l.id = %d '%(i,e))
    #    self.cr.execute('select r.date_reception from labo_analysis_request r, labo_sample l, labo_followsheet f where l.sample_id=r.id and f.id=l.follow_sheet_id and f.id=%d and l.id = %d'%(o,e))
        req_ids = self.cr.fetchone()
        return req_ids and req_ids[0] or False

    def get_setup(self,i,e):
        self.cr.execute('select ls.name from labo_analysis_request r, labo_sample l,analysis_setup st,labo_setup ls, labo_followsheet f where l.follow_sheet_id=f.id and ls.id=st.set_up and st.id=l.file_setup  and r.id=l.sample_id and f.id=%d and l.id = %d '%(i,e))
        res=self.cr.fetchone()
        return res and res[0] or False


    def get_material(self, i, e):
        self.cr.execute('select l.material,l.tube from labo_analysis_request r, labo_sample l, labo_followsheet f where l.follow_sheet_id=f.id and r.id=l.sample_id and f.id=%d and l.id = %d '%(i,e))
        res=self.cr.fetchone()
        return res and res[0] or False

    def get_res(self, i, e):
        self.cr.execute('select l.result from labo_analysis_request r, labo_sample l, labo_followsheet f where l.follow_sheet_id=f.id and r.id=l.sample_id and f.id=%d and l.id = %d '%(i,e))
        res=self.cr.fetchone()
        return res and res[0] or False

    def get_date_limit(self, i, e):
        self.cr.execute('select l.date_limit from labo_analysis_request r, labo_sample l, labo_followsheet f where l.follow_sheet_id=f.id and r.id=l.sample_id and f.id=%d and l.id = %d '%(i,e))
        res=self.cr.fetchone()
        return res and res[0] or False

    def get_code(self, i, e):
        self.cr.execute('select l.progenus_number from labo_analysis_request r, labo_sample l, labo_followsheet f where l.follow_sheet_id=f.id and r.id=l.sample_id and f.id=%d and l.id = %d '%(i,e))
        res=self.cr.fetchone()
        return res and res[0] or False


    def get_notice(self, i, e):
        self.cr.execute('select l.notice from labo_analysis_request r, labo_sample l, labo_followsheet f where l.follow_sheet_id=f.id and r.id=l.sample_id and f.id=%d and l.id = %d '%(i,e))
        res=self.cr.fetchone()
        return res and res[0] or False

    def get_date_closed(self,i,e):
        self.cr.execute('select l.date_closing from labo_analysis_request r, labo_sample l, labo_followsheet f where l.follow_sheet_id=f.id and r.id=l.sample_id and f.id=%d and l.id = %d '%(i,e))
    #    self.cr.execute('select r.date_closed from labo_analysis_request r, labo_sample l, labo_followsheet f where l.sample_id=r.id and f.id=l.follow_sheet_id and f.id=%d and l.id = %d'%(o,e))
        req_ids = self.cr.fetchone()
        return req_ids and req_ids[0] or False

    def get_urgent_c(self,o, e):
        c= ','.join(map(str,self.list_r))
        self.cr.execute('select r.urgent from labo_analysis_request r, labo_sample l, labo_followsheet f , labo_dog d '\
                'where l.sample_id=r.id and f.id=d.follow_sheet_id and f.id=%d  and r.id =%d and d.id = %d and '\
                '(l.dog_child=d.id or l.dog_father=d.id or d.id=l.dog_mother)'%(o,int(c),e))
        req_ids = self.cr.fetchone()
        return req_ids and req_ids[0] and 'X' or False

    def get_urgent(self,o, e):
        self.cr.execute('select r.urgent from labo_analysis_request r, labo_sample l, labo_followsheet f where l.sample_id=r.id and f.id=l.follow_sheet_id and f.id=%d and l.id = %d'%(o,e))
        req_ids = self.cr.fetchone()
        return req_ids and req_ids[0] and 'X' or False

    def get_report_type(self,o,e):
        self.cr.execute('select t.code,r.name from labo_analysis_request r, labo_analysis_type t,labo_sample l, labo_followsheet f where r.type_id=t.id and l.sample_id=r.id and f.id=l.follow_sheet_id and f.id=%d and l.id = %d'%(o,e))
#        self.cr.execute('select r.name from labo_analysis_request r where r.id in ('+','.join(map(str,self.req_l))+') ')
        req_ids = self.cr.fetchone()
        typ_name=req_ids and req_ids[0] or False
        req_name=req_ids and req_ids[1] or False
        return str(typ_name + '/'+ req_name)

    def get_report_type_c(self,o,e):
        c= ','.join(map(str,self.list_r))
        self.cr.execute('select t.code,r.name from labo_analysis_request r, labo_analysis_type t,labo_sample l, labo_followsheet f, labo_dog d '\
                        'where r.type_id=t.id and l.sample_id=r.id and f.id=d.follow_sheet_id and f.id=%d and d.id = %d '\
                        'and (d.id=l.dog_child or d.id=l.dog_father '\
                        'or d.id=l.dog_mother )  and d.done_i is null and r.id =%d '%(o,e,int(c)))
        req_ids = self.cr.fetchone()
        typ_name=req_ids and req_ids[0] or ''
        req_name=req_ids and req_ids[1] or ''
        return str(typ_name + '/'+ req_name)
    def get_request_name(self,p,o):
#        self.cr.execute('select l.progenus_number from labo_analysis_request r, labo_sample l, labo_followsheet f '\
#                        'where l.follow_sheet_id=f.id and r.id=l.sample_id and f.id=%d and l.id = %d '%(p,o))
#        res=self.cr.fetchone()
#        prog_num=res and res[0] or ''
#        file_n=''
#        if prog_num:
#            self.cr.execute("select fh.name from file_history fh, labo_sample l where l.progenus_number='%s' and "\
#                        "fh.sample_id=l.id and fh.name like '%%.txt' order by fh.create_date desc"%prog_num)
#            req_ids = self.cr.fetchone()
#            if req_ids and req_ids[0]:
#                file_n=req_ids[0].split(' ')
#                file_n=file_n[0]
#        return file_n  or ""

        self.cr.execute("select fh.name from file_history fh, labo_sample l, labo_followsheet f where l.id='%s' and "\
                        "fh.sample_id=l.id and fh.name like '%%.txt' and l.follow_sheet_id=f.id and f.id=%s order by fh.create_date desc"%(o, p))
        req_ids = self.cr.fetchone()
        return req_ids and req_ids[0] and req_ids[0].split(' ')[0] or None
       # return req_ids and req_ids[0]  or ""

    def ct(self,p,o):
#        self.cr.execute('select l.progenus_number from labo_analysis_request r, labo_sample l, labo_followsheet f '\
#                        'where l.follow_sheet_id=f.id and r.id=l.sample_id and f.id=%d and l.id = %d '%(p,o))
#        res=self.cr.fetchone()
#        prog_num=res and res[0] or False
        self.cr.execute("select distinct(ls.name), s.create_date from analysis_setup st, labo_setup ls,"\
                         "labo_analysis_request req, labo_sample s, labo_followsheet f where s.file_setup=st.id "\
                         "and req.id=s.sample_id and s.id = %d and f.id= %d and (s.state not like 'ko' or s.nc_reanalyse='f') "\
                         "and st.set_up=ls.id and f.id=s.follow_sheet_id order by create_date desc"%(o,p))
        req_ids = self.cr.fetchone()
        return req_ids and req_ids[0]  or ""

    def get_begining_date_c(self,i,e):
        c= ','.join(map(str,self.list_r))
        h_1=[]
#        print ('select d.date_reception from labo_analysis_request r, labo_sample l, labo_followsheet f , labo_dog d '\
#                        ' where d.follow_sheet_id=f.id and r.id=l.sample_id and f.id=%d and d.id = %d and (d.id=l.dog_child or d.id=l.dog_father '\
#                        'or d.id=l.dog_mother ) and d.done_i is null and r.id =%d'%(i,e, int(c)))
        self.cr.execute('select d.date_reception from  labo_dog d where d.id = %d and d.done_i is null '%(e))
#        self.cr.execute('select d.date_reception from labo_analysis_request r, labo_sample l, labo_followsheet f , labo_dog d '\
#                        ' where d.follow_sheet_id=f.id and r.id=l.sample_id and f.id=%d and d.id = %d and (d.id=l.dog_child or d.id=l.dog_father '\
#                        'or d.id=l.dog_mother ) and d.done_i is null and r.id =%d'%(i,e, int(c)))
        req_ids = self.cr.fetchone()
        return req_ids and req_ids[0] or None

    def get_material_c(self, i, e):
        c= ','.join(map(str,self.list_r))
        h_m=[]
        self.cr.execute('select d.material from labo_analysis_request r, labo_sample l, labo_followsheet f, labo_dog d '\
                        ' where d.follow_sheet_id=f.id and r.id=l.sample_id and f.id=%d and d.id = %d and (d.id=l.dog_child or d.id=l.dog_father '\
                        'or d.id=l.dog_mother ) and d.done_i is null and r.id =%d '%(i,e, int(c)))
        req_ids = self.cr.fetchone()
        return req_ids and req_ids[0] or None

    def get_res_c(self, i, e):
        h_r=[]
        c= ','.join(map(str,self.list_r))
        self.cr.execute('select d.result from labo_analysis_request r, labo_sample l, labo_followsheet f , labo_dog d '\
                        'where d.follow_sheet_id=f.id and r.id=l.sample_id and f.id=%d and d.id = %d and (d.id=l.dog_child or d.id=l.dog_father '\
                        'or d.id=l.dog_mother ) and d.done_i is null and r.id =%d '%(i,e, int(c)))
        req_ids = self.cr.fetchone()
        return req_ids and req_ids[0] or None

    def get_date_limit_c(self, i, e):
        c= ','.join(map(str,self.list_r))
        self.cr.execute('select d.date_limit from labo_analysis_request r, labo_sample l, labo_followsheet f , labo_dog d '\
                        'where d.follow_sheet_id=f.id and r.id=l.sample_id and f.id=%d and d.id = %d and (d.id=l.dog_child or d.id=l.dog_father '\
                        'or d.id=l.dog_mother ) and  d.done_i is null and r.id=%d'%(i,e,int(c)))
        req_ids = self.cr.fetchone()
        return req_ids and req_ids[0] or None

    def get_code_c(self, i, e):
        c= ','.join(map(str,self.list_r))
        h_r=[]
        self.cr.execute('select d.progenus_number from labo_analysis_request r, labo_sample l, labo_followsheet f , labo_dog d '\
                        'where d.follow_sheet_id=f.id and r.id=l.sample_id and f.id=%d and d.id = %d and (d.id=l.dog_child or d.id=l.dog_father '\
                        'or d.id=l.dog_mother ) and d.done_i is null and r.id =%d'%(i,e, int(c)))
        req_ids = self.cr.fetchone()
        return req_ids and req_ids[0] or None

    def get_notice_c(self, i, e):
        c= ','.join(map(str,self.list_r))
        h_r=[]
        self.cr.execute('select d.notice from labo_analysis_request r, labo_sample l, labo_followsheet f , labo_dog d '\
                        'where d.follow_sheet_id=f.id and r.id=l.sample_id and f.id=%d and d.id = %d and (d.id=l.dog_child or d.id=l.dog_father '\
                        'or d.id=l.dog_mother ) and d.done_i is null and r.id =%d'%(i,e, int(c)))
        req_ids = self.cr.fetchone()
        return req_ids and req_ids[0] or None

    def get_date_closed_c(self,i,e):
        c= ','.join(map(str,self.list_r))
        self.cr.execute('select d.date_closing from labo_analysis_request r, labo_sample l, labo_followsheet f , labo_dog d '\
                        'where d.follow_sheet_id=f.id and r.id=l.sample_id and f.id=%d and d.id = %d and (d.id=l.dog_child or d.id=l.dog_father '\
                        'or d.id=l.dog_mother ) and d.done_i is null and r.id =%d'%(i,e, int(c)))
        req_ids = self.cr.fetchone()
        return req_ids and req_ids[0] or None

    def ct_c(self,p,o):
        c= ','.join(map(str,self.list_r))
        self.cr.execute ("select distinct(ls.name) from labo_analysis_request req, labo_sample s, analysis_setup st, labo_setup ls, labo_dog d, "\
                        "labo_followsheet f where d.file_setup=st.id  "\
                        "and d.id = %d and req.id=s.sample_id and d.follow_sheet_id=f.id and f.id =%d and st.set_up=ls.id and "\
                        "d.done_i is null and req.id =%d"%(o, p, int(c)))
        req_ids = self.cr.fetchone()
        return req_ids and req_ids[0] or None

    def get_request_name_c(self,p,o):
#        self.cr.execute("select  distinct(fh.name), fh.create_date from file_history fh,  labo_dog d, labo_followsheet f where d.id =452 
#and  f.id=d.follow_sheet_id and f.id=3 and d.done_i is null and fh.name like '%.txt' group by fh.name , fh.create_date  order by fh.create_date desc
        self.cr.execute("select f.name from file_history f, labo_dog d, labo_followsheet lf where  d.id = %d and lf.id=d.follow_sheet_id and "\
                        "f.dog_id1=d.id and d.done_i is null order by f.create_date"%(o))
        req_ids = self.cr.fetchone()
        name_file= req_ids and req_ids[0] and req_ids[0].split(' ')[0] or None
        if name_file and len(name_file) >20:
            return name_file[:20]+'...'
        return name_file

report_sxw.report_sxw('report.List_followsheet', 'labo.analysis.request', 'addons/labo_analysis/report/report_followsheet_of_sample.rml',parser=report_followsheet_of_sample,header=False)
report_sxw.report_sxw('report.List_followsheet3', 'labo.analysis.request', 'addons/labo_analysis/report/report_followsheet_of_sample3.rml',parser=report_followsheet_of_sample,header=False)


