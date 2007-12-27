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

def emp_create_xml(self,cr,uid, empid, som, eom):

    cr.execute('select name from hr_employee where id=%d'%(empid))
    emp = cr.fetchall()

    p_id=pooler.get_pool(cr.dbname).get('hr.holidays').search(cr,uid,[('employee_id','=',empid)])

    ids_date = pooler.get_pool(cr.dbname).get('hr.holidays').read(cr,uid,p_id,['date_from','date_to','holiday_status','state'])
    display={}
    dayDiff=eom-som

    for index in range(1,dayDiff.days+2):
        diff=index-1
        current=som+datetime.timedelta(diff)

        for item in ids_date:
            if current >= strToDate(item['date_from']) and current < strToDate(item['date_to']):
                display[index]=item['holiday_status'][0]
                break
            else:
                display[index]=' '

    month = {}
    xml = '''
    <time-element index="%d">
        <value>%s</value>
    </time-element>
    '''

    time_xml = ([xml % (index, value) for index,value in display.iteritems()])
    data_xml=['<info id="%d" number="%d" val="%s" />' % (empid,x,display[x]) for x in range(1,len(display)+1) ]

    # Computing the xml
    xml = '''
    %s
    <employee id="%d" name="%s">
    %s
    </employee>
    ''' % (data_xml,empid, toxml(emp[0][0]), '\n'.join(time_xml))

    return xml

class report_custom(report_rml):
    def create_xml(self, cr, uid, ids, data, context):

        # Computing the dates (start of month: som, and end of month: eom)
        cr.execute("select id,name from hr_holidays_status")
        legend=cr.fetchall()

        today=datetime.datetime.today()

        first_date=data['form']['date_from']
        last_date=data['form']['date_to']

        som = strToDate(first_date)
        eom = strToDate(last_date)

        day_diff=eom-som

        date_xml=[]
        for l in range(0,len(legend)):
            date_xml += ['<legend id="%d" name="%s" />' % (legend[l][0],legend[l][1])]

        date_xml += ['<date month="%s" year="%d" />' % (som.strftime('%B'), som.year),'<days>']

        cell=1
        date_xml += ['<dayy number="%d" name="%s" cell="%d"/>' % (x, som.replace(day=x).strftime('%a'),x-som.day+1) for x in range(som.day, lengthmonth(som.year, som.month)+1)]
        cell=x-som.day+1
        day_diff1=day_diff.days+som.day-lengthmonth(som.year, som.month)

        width_dict={}
        month_dict={}

        i=1
        j=1
        year=som.year
        month=som.month
        month_dict[j]=som.strftime('%B')
        width_dict[j]=lengthmonth(som.year, som.month)-som.day+1

        while day_diff1>0:
            if month+i<=12:
                if day_diff1>=30:
                    som1=datetime.date(year,month+i,1)
                    date_xml += ['<dayy number="%d" name="%s" cell="%d"/>' % (x, som1.replace(day=x).strftime('%a'),cell+x) for x in range(1, lengthmonth(year,i+month)+1)]
                    i=i+1
                    j=j+1
                    month_dict[j]=som1.strftime('%B')
                    cell=cell+x
                    width_dict[j]=x
#                    print "in  if if som1",som1,"i",i,"date_xml",date_xml,"x",x
#                    print ""
                else:
                    som1=datetime.date(year,month+i,1)
                    date_xml += ['<dayy number="%d" name="%s" cell="%d"/>' % (x, som1.replace(day=x).strftime('%a'),cell+x) for x in range(1, eom.day+1)]
                    i=i+1
                    j=j+1
                    month_dict[j]=som1.strftime('%B')
                    cell=cell+x
                    width_dict[j]=x
#                    print "in  if else  som1",som1,"i",i,"date_xml",date_xml,"x",x
#                    print ""
                day_diff1=day_diff1-x
#                print "now day_diff1 is..frst.",day_diff1
            else:
                years=year+1
                year=years
                month=0
                i=1
                if day_diff1>=30:
                    som1=datetime.date(years,i,1)
                    date_xml += ['<dayy number="%d" name="%s" cell="%d"/>' % (x, som1.replace(day=x).strftime('%a'),cell+x) for x in range(1, lengthmonth(years,i)+1)]
                    i=i+1
                    j=j+1
                    month_dict[j]=som1.strftime('%B')
                    cell=cell+x
                    width_dict[j]=x
#                    print "in else if som1",som1,"i",i,"date_xml",date_xml,"x",x
#                    print ""
                else:
                    som1=datetime.date(years,i,1)
                    i=i+1
                    j=j+1
                    month_dict[j]=som1.strftime('%B')
                    date_xml += ['<dayy number="%d" name="%s" cell="%d"/>' % (x, som1.replace(day=x).strftime('%a'),cell+x) for x in range(1, eom.day+1)]
                    cell=cell+x
                    width_dict[j]=x
#                    print "in else else som1",som1,"i",i,"date_xml",date_xml,"x",x
#                    print ""
                day_diff1=day_diff1-x
#                print "now day_diff1 is..scnd.",day_diff1

#        print "data...",date_xml
        date_xml.append('</days>')
#        date_xml.append('<cols>3.5cm%s</cols>\n' % (',0.7cm' * (day_diff.days+1)))
        date_xml.append('<cols>3.5cm%s</cols>\n' % (',0.7cm' * (day_diff.days+1)))

        st='<cols_months>3.5cm'
        for m in range(1,len(width_dict)+1):
            st+=',' + str(0.7 *width_dict[m])+'cm'
        st+='</cols_months>\n'

        months_xml =['<months  number="%d" name="%s" />' % (x,month_dict[x]) for x in range(1,len(month_dict)+1) ]
        months_xml.append(st)

        cr.execute("select id from hr_employee")
        emp = cr.fetchall()

        emp_xml=''
        for eid in range(1,len(emp)+1):
            emp_xml += emp_create_xml(self,cr,uid,eid, som, eom)

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