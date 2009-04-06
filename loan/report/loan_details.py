import time
import datetime
from report import report_sxw
from osv import osv
from datetime import date
import pooler

import mx.DateTime
from mx.DateTime import RelativeDateTime, now, DateTime, localtime

class loan_details(report_sxw.rml_parse):
    s=0.0
    _capital=0.0
    _interest=0.0
    _subtotal=0.0

    def __init__(self, cr, uid, name, context):

        super(loan_details, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'amount_total' : self.__amount_total__,
            'ending_date' : self.__ending_date__,
            'get_capital': self.__get_capital__,
            'get_interest':self.__get_interest__,
            'get_subtotal':self.__get_subtotal__,
        })

    def __amount_total__(self,install):

        self._capital = self._capital + install.capital
        self._interest = self._interest + install.interest
        self._subtotal= self._subtotal + install.capital + install.interest

        self.s = self.s + install.total
        return self.s

    def __get_capital__(self,install):

        return self._capital

    def __get_interest__(self,install):

        return self._interest

    def __get_subtotal__(self,install):

        return self._subtotal

    def __ending_date__(self):
        loan_pool = pooler.get_pool(self.cr.dbname).get('account.loan')
        loan = loan_pool.browse(self.cr,self.uid,self.ids);

        start_date = loan[0].approve_date
        total_inst = loan[0].total_installment

        i = 366
        j = 12
        if j == total_inst:
            end_date = mx.DateTime.strptime(start_date, '%Y-%m-%d') + RelativeDateTime(days=i)
        else:
            while j < total_inst:
                j = j + 12
                i = i + 365
                end_date = mx.DateTime.strptime(start_date, '%Y-%m-%d') + RelativeDateTime(days=i)

        return end_date.date
  #end if

report_sxw.report_sxw('report.account.loan', 'account.loan', 'addons/loan/report/loan_info.rml', parser=loan_details)
