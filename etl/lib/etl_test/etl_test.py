# -*- encoding: utf-8 -*-
##############################################################################
#
#    ETL system- Extract Transfer Load system
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
""" ETL Process.

    The module test ETL component.

"""
from etl import job
from etl import transition
from etl.component import component

class etl_test_exception(Exception):

    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)


class etl_component_test(object):
    def __init__(self,compt):
        self.component=compt
        self.input_data={}
        self.output_data={}
        self.datas=[]
        self.output_channel='main'
        self.test_input=component()
        self.test_output=component()
        self.test_input.generator=self.input_generator_get()
        self.test_output.generator=self.output_generator_get()

    def check_input(self,input_data):
        self.input_data=input_data

    def check_output(self,output_data,channel='main'):
        self.output_data=output_data
        self.output_channel=channel

    def input_generator_get(self):
        for chan in self.input_data:
            for d in self.input_data[chan]:
                yield d,chan

    def output_generator_get(self):
        self.datas={}
        for channel,trans in self.test_output.input_get().items():
            data=[]
            for iterator in trans:
                for d in iterator:
                    data.append(d)
            self.datas[channel]=data
        for chan in self.datas:
            for d in self.datas[chan]:
                yield d,chan


    def output(self):
        tran=transition(self.test_input,self.component)
        tran1=transition(self.component,self.test_output)
        job1=job([self.test_output])
        job1.run()
        if self.output_channel not in self.datas:
            raise etl_test_exception('expected output channel does not has actual data.')
        act_datas=self.datas[self.output_channel]
        if len(act_datas)!=len(self.output_data):
            raise etl_test_exception('lengths of actual output and expected output are different')
        if self.output_data:
            if len(act_datas)!=len(self.output_data):
                raise etl_test_exception('lengths of actual output and expected output are different')
        else:
             return self.datas
        count=0
        while count<len(act_datas):
            exp_r=self.output_data[count]
            act_r=act_datas[count]
            exp_keys=exp_r.keys()
            act_keys=act_r.keys()
            if len(exp_keys)!=len(act_keys):
                raise etl_test_exception('key length of actual output and expected output are different')
            key_count=0

            while key_count<len(act_keys):
                exp_key=exp_keys[key_count]
                act_key=act_keys[key_count]
                if exp_key!=act_key:
                    raise etl_test_exception('keys of actual output and expected output are different.')
                key_count+=1

            value_count=0
            exp_values=exp_r.values()
            act_values=act_r.values()
            while value_count<len(act_values):
                exp_value=exp_values[value_count]
                act_value=act_values[value_count]
                if exp_value!=act_value:
                    raise etl_test_exception('values of actual output and expected output are different')
                value_count+=1
            count+=1

