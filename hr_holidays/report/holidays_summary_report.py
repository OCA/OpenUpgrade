import datetime
import time

from osv import fields, osv
from report.interface import report_rml
from report.interface import toxml

import pooler


def lengthmonth(year, month):
    if month == 2 and ((year % 4 == 0) and ((year % 100 != 0) or (year % 400 == 0))):
        return 29
    return [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month]

def strToDate(dt):
    dt_date=datetime.date(int(dt[0:4]),int(dt[5:7]),int(dt[8:10]))
    return dt_date

def emp_create_xml(self,cr,uid,dept,holiday_type,row_id,empid,name,som,eom):

    dayDiff=eom-som
    display={}
    display1={}
    if dept==0:
        count=0
        count1=0
        p_id=pooler.get_pool(cr.dbname).get('hr.holidays').search(cr,uid,[('employee_id','=',empid)])

        ids_date = pooler.get_pool(cr.dbname).get('hr.holidays').read(cr,uid,p_id,['date_from','date_to','holiday_status','state'])

        for index in range(1,32):
            diff=index-1
            current=som+datetime.timedelta(diff)

            for item in ids_date:

                if current >= strToDate(item['date_from']) and current <= strToDate(item['date_to']):
                    if item['state'] in holiday_type:
                        display[index]=item['holiday_status'][0]
                        count=count+1
                    else:
                        display[index]=' '
                    break
                else:
                    display[index]=' '

        for index in range(32,63):
            diff=index-1
            current=som+datetime.timedelta(diff)

            for item in ids_date:

                if current >= strToDate(item['date_from']) and current <= strToDate(item['date_to']):
                    if item['state'] in holiday_type:
                        display1[index]=item['holiday_status'][0]
                        count1=count1+1
                    else:
                        display1[index]=' '
                    break
                else:
                    display1[index]=' '

    else:

         for index in range(1,32):
              display[index]=' '
              count=''
         for index in range(32,63):
              display1[index]=' '
              count1=''

    xml = '''
        <time-element index="%d">
            <value>%s</value>
        </time-element>
        '''
    time_xml = ([xml % (index, value) for index,value in display.iteritems()])
    time_xml += ([xml % (index, value) for index,value in display1.iteritems()])

    data_xml=['<info id="%d" number="%d" val="%s" />' % (row_id,x,display[x]) for x in range(1,len(display)+1) ]
    data_xml +=['<info1 id="%d" number="%d" val="%s" />' % (row_id,x,display1[31+x]) for x in range(1,len(display1)+1) ]

    # Computing the xml
    xml = '''
    %s
    <employee row="%d" id="%d" name="%s" sum="%s" sum1="%s">
    %s
    </employee>
    ''' % (data_xml,row_id,dept, toxml(name),count,count1, '\n'.join(time_xml))

    return xml

class report_custom(report_rml):
    def create_xml(self, cr, uid, ids,data, context):
        depts=[]
        done={}
        emp_id={}
        month_dict={}
        month_dict1={}
        width_dict={}
        width_dict1={}
        cr.execute("select name from res_company")
        res=cr.fetchone()[0]
        date_xml=[]
        date_today=time.strftime('%Y-%m-%d %H:%M:%S')
        date_xml +=['<res name="%s" today="%s" />' % (res,date_today)]

        cr.execute("select id,name,color_name from hr_holidays_status order by id")
        legend=cr.fetchall()

        today=datetime.datetime.today()

        som = strToDate(data['form']['date_from'])
        mom=som+datetime.timedelta(30)
        eom = som+datetime.timedelta(61)
        day_diff=mom-som
        day_diff1=eom-mom
        if data['form']['holiday_type']!='both':
            type=data['form']['holiday_type']
            if data['form']['holiday_type']=='Confirmed':
                holiday_type=('confirm')
            else:
                holiday_type=('validate')
        else:
            type="Confirmed and Validated"
            holiday_type=('confirm','validate')
        date_xml.append('<from>%s</from>\n'% (som))
        date_xml.append('<to>%s</to>\n' %(eom))
        date_xml.append('<type>%s</type>'%(type))

        for l in range(0,len(legend)):
            date_xml += ['<legend row="%d" id="%d" name="%s" color="%s" />' % (l+1,legend[l][0],legend[l][1],legend[l][2])]

        date_xml += ['<date month="%s" year="%d" />' % (som.strftime('%B'), som.year),'<days1>']

        month=1
        # Retrieving first set of 31 days.
        cell=1
        date_xml += ['<dayy number="%d" name="%s" cell="%d"/>' % (x, som.replace(day=x).strftime('%a'),x-som.day+1) for x in range(som.day, lengthmonth(som.year, som.month)+1)]
        cell=x-som.day+1
        count=31-cell
        month_dict[month]=som.strftime('%B')
        width_dict[month]=cell
        month=month+1
        if count==0:
            som2=som
            date_xml.append('</days1>')
        else:
            som1=som+datetime.timedelta(cell)

            if count<=lengthmonth(som1.year, som1.month):
                date_xml += ['<dayy number="%d" name="%s" cell="%d"/>' % (x, som1.replace(day=x).strftime('%a'),cell+x) for x in range(1,count+1)]
                month_dict[month]=som1.strftime('%B')
                width_dict[month]=count
                month=month+1
                som2=som1
            else:
                date_xml += ['<dayy number="%d" name="%s" cell="%d"/>' % (x, som1.replace(day=x).strftime('%a'),cell+x) for x in range(1,lengthmonth(som1.year, som1.month)+1)]
                cell=cell+x
                month_dict[month]=som1.strftime('%B')
                width_dict[month]=x
                month=month+1
                count=count -lengthmonth(som1.year, som1.month)
                som2=som1+datetime.timedelta(lengthmonth(som1.year, som1.month))

                date_xml += ['<dayy number="%d" name="%s" cell="%d"/>' % (x, som2.replace(day=x).strftime('%a'),cell+x) for x in range(1,count+1)]
                month_dict[month]=som2.strftime('%B')
                width_dict[month]=x
                month=month+1
            date_xml.append('</days1>')
            count=x
        # First set of 31 days Retrieved,going ahead for the second set of next 31 days.

        date_xml.append('<days2>')

        cell=31
        month=1
        if count==0 or count==lengthmonth(som2.year, som2.month):
            som2=som2+datetime.timedelta(lengthmonth(som2.year, som2.month))
            date_xml += ['<dayy number="%d" name="%s" cell="%d"/>' % (x, som2.replace(day=x).strftime('%a'),cell+x) for x in range(1, lengthmonth(som2.year, som2.month)+1)]
            cell=cell+x
            month_dict1[month]=som2.strftime('%B')
            width_dict1[month]=x
            month=month+1
        else:
            date_xml += ['<dayy number="%d" name="%s" cell="%d"/>' % (x, som2.replace(day=x).strftime('%a'),cell+x-count) for x in range(count+1, lengthmonth(som2.year, som2.month)+1)]
            cell=cell+x-count
            month_dict1[month]=som2.strftime('%B')
            width_dict1[month]=x-count
            month=month+1

        count=62-cell
        if count==0:
            som2=som
            date_xml.append('</days2>')
        else:
            som1=som2+datetime.timedelta(lengthmonth(som2.year, som2.month))

            if count<=lengthmonth(som1.year, som1.month):
                date_xml += ['<dayy number="%d" name="%s" cell="%d"/>' % (x, som1.replace(day=x).strftime('%a'),cell+x) for x in range(1,count+1)]
                month_dict1[month]=som1.strftime('%B')
                width_dict1[month]=x
                month=month+1
                som2=som1
            else:
                date_xml += ['<dayy number="%d" name="%s" cell="%d"/>' % (x, som1.replace(day=x).strftime('%a'),cell+x) for x in range(1,lengthmonth(som1.year, som1.month)+1)]
                month_dict1[month]=som1.strftime('%B')
                width_dict1[month]=x
                month=month+1
                count=count -lengthmonth(som1.year, som1.month)
                cell=cell+x
                som2=som1+datetime.timedelta(lengthmonth(som1.year, som1.month))

                date_xml += ['<dayy number="%d" name="%s" cell="%d"/>' % (x, som2.replace(day=x).strftime('%a'),cell+x) for x in range(1,count+1)]
                month_dict1[month]=som2.strftime('%B')
                width_dict1[month]=x
                month=month+1
            date_xml.append('</days2>')


        date_xml.append('<cols>5.5cm%s,0.8cm</cols>\n' % (',0.7cm' * 31))

        months_xml=[]
        st='<cols_months>5.5cm'
        for m in range(1,len(width_dict)+1):
            st+=',' + str(0.7 *width_dict[m])+'cm'
        st+=',0.8cm</cols_months>\n'
        months_xml.append('<month1>')
        months_xml +=['<months  number="%d" name="%s" />' % (x,month_dict[x]) for x in range(1,len(month_dict)+1) ]
        months_xml.append(st)
        months_xml.append('</month1>')

        st='<cols_months>5.5cm'
        for m in range(1,len(width_dict1)+1):
            st+=',' + str(0.7 *width_dict1[m])+'cm'
        st+=',0.8cm</cols_months>\n'
        months_xml.append('<month2>')
        months_xml +=['<months  number="%d" name="%s" />' % (x,month_dict1[x]) for x in range(1,len(month_dict1)+1) ]
        months_xml.append(st)
        months_xml.append('</month2>')

        emp_xml=''
        row_id=1
        for id in data['form']['depts'][0][2]:
            dept = pooler.get_pool(cr.dbname).get('hr.department').browse(cr, uid, id, context.copy())
            depts.append(dept)

            cr.execute('select user_id from hr_department_user_rel where department_id=%d'%(dept.id))
            result=cr.fetchall()

#            if result!=[]:
#                emp_xml += emp_create_xml(self,cr,uid,1,holiday_type,row_id,dept.id,dept.name,som, eom)
#                row_id = row_id +1
#            else:
#                continue

            if result==[]:
                continue
            dept_done=0
            for d in range(0,len(result)):
                emp_id[d]=pooler.get_pool(cr.dbname).get('hr.employee').search(cr,uid,[('user_id','=',result[d][0])])
                items = pooler.get_pool(cr.dbname).get('hr.employee').read(cr,uid,emp_id[d],['id','name'])

                for item in items:
                    if item['id'] in done:
                        continue
                    else:
                        if dept_done==0:
                            emp_xml += emp_create_xml(self,cr,uid,1,holiday_type,row_id,dept.id,dept.name,som, eom)
                            row_id = row_id +1
                        dept_done=1

                    done[item['id']] = 1

                    emp_xml += emp_create_xml(self,cr,uid,0,holiday_type,row_id,item['id'],item['name'],som, eom)
                    row_id = row_id +1

        # Computing the xml
        xml='''<?xml version="1.0" encoding="UTF-8" ?>
        <report>
        %s
        %s
        %s
        </report>
        ''' % (months_xml,date_xml, emp_xml)

        return xml

report_custom('report.holidays.summary', 'hr.holidays', '', 'addons/hr_holidays/report/holidays_summary.xsl')