# -*- encoding: utf-8 -*-
import datetime
import operator
import pooler
import time
from report import report_sxw
from array import array

class langreport(report_sxw.rml_parse):
        def __init__(self, cr, uid, name, context):
                super(langreport, self).__init__(cr, uid, name, context)

                self.localcontext.update({
                    'time':time,
                    'get_data' : self._getData,
                    'get_lang':self._getLang,

                     })
        def _getLang(self,id):
                lid=[]
                lname=[]

                lid.append(pooler.get_pool(self.cr.dbname).get('emp.lang').search(self.cr,self.uid,[('ii_id','=',id),]))
                for i in range (0,len(lid)):
                    lname.append(pooler.get_pool(self.cr.dbname).get('emp.lang').read(self.cr,self.uid,lid[i],))
                res=lname[0]
                return res

        def _getData(self,form):

            name=0
            r=False
            s=False
            w=False
            sort_id=[]
            temp=[]
            emp_id=[]
            emp_name=[]
            count= len(form['lang'])

            if count==0:
                self.cr.execute("select ii_id,name,read,write,speak from emp_lang" )
                temp.append(self.cr.fetchall())

            else:
                for i in range(0,count):
                    name=form['lang'][i][2]['name']
                    r=form['lang'][i][2]['read']
                    w=form['lang'][i][2]['write']
                    s=form['lang'][i][2]['speak']
                    whr= ""
                    whr=whr + "name = %d"%(name)
                    if  r==1:
                        r=True
                        whr=whr+" and read = %s"%r
                    else:
                        r=False
                    if  s==1:
                        s=True
                        whr=whr+" and speak = %s"%s
                    else:
                        s=False
                    if  w==1:
                        w=True
                        whr=whr+" and write = %s"%w
                    else:
                        w=False
                    self.cr.execute("select ii_id,name,read,write,speak from emp_lang where " + whr)
                    temp.append(self.cr.fetchall())

         # This loop is for extracting employee ids
            for i in range(0,len(temp)):
               for j in range(0,len(temp[i])):
                  emp_id.append(temp[i][j][0])

           # This loop is for extracting Unique employee ids
            if count==0:
                sort_id=[]
                for v in emp_id:
                   if not v in sort_id: sort_id.append(v)
            else:
                sort_id.append(list(set([x for x in emp_id if emp_id.count(x)==count])))
                temp=[]
                temp=sort_id[0]
                sort_id=[]
                sort_id=temp
            for i in sort_id:
                emp_name.append(pooler.get_pool(self.cr.dbname).get('hr.employee').read(self.cr,self.uid,i,['name'],))
            return emp_name

report_sxw.report_sxw('report.langreport','hr.employee','addons/hr_skill/report/langreport.rml',parser=langreport,)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

