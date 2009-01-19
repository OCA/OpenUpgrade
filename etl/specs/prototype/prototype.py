#csv_in ---> logger
import csv

class component(object):
    def __init__(self,*args, **argv):
        is_start=True
        self.data=[]
        self.job=argv.get('job',False)
        self.trans_out = []
        self.trans_in = []

    def event(self,name):
        return self.output(event=name)
    def start(self):
        self.event('component_start')
        return True
    def stop(self):
        self.event('component_end')
        return True
    def run(self,input_data=[]):
        self.event('component_run')
        data=self.output(input_data)
        return data

    def input(self, rows, transition=None):
        self.event('component_inputflow')
        return self.output(rows)

    def output(self, rows=None, channel=None,event=None):
        self.event('component_outputflow')
        for trans in self.trans_out:
            if (not channel) or (trans.channel_source==channel) or (not trans.channel_source):
                if trans.type=='data_transition' or (trans.type=='trigger_transition' and event==trans.listen_event):
                    yield rows, trans.destination
                else:
                    yield rows,None

class csv_in(component):
    def __init__(self, filename, *args, **argv):
        super(csv_in, self).__init__(*args, **argv)
        self.filename = filename

    def run(self,data=[]):        
        fp = csv.DictReader(file(self.filename))
        data=[]
        for row in fp:
            data.append(row)
        return super(csv_in, self).run(data)

class csv_out(component):
    def __init__(self, filename, *args, **argv):
        super(csv_out, self).__init__(*args, **argv)
        self.filename=filename
        self.fp=None

    def run(self,rows=[]):
        self.fp = file(self.filename, 'wb+')
        return self.input(rows)

    def input(self,rows=[]):
        fieldnames = rows[0].keys()
        fp = csv.DictWriter(self.fp, fieldnames)
        fp.writerow(dict(map(lambda x: (x,x), fieldnames)))
        fp.writerows(rows)        
        return super(csv_out, self).input(rows)

class sort(component):
    def __init__(self, fieldname, *args, **argv):
        self.fieldname = fieldname
        super(sort, self).__init__(*args, **argv)    

    def run(self,rows=[], transition=None):
        self.data=rows
        self.data.sort(lambda x,y: cmp(x[self.fieldname],y[self.fieldname]))
        return super(sort, self).run(self.data)     

    

class logger(component):
    def __init__(self, name, *args, **argv):
        self.name = name
        super(logger, self).__init__(*args, **argv) 
    def run(self,data=[]): 
        res=[]    
        print ' Logger : ',self.name
        for row in data:
            print row
            res.append(row)
        return super(logger, self).run(data)

class transition(object):
    def __init__(self, source, destination,type='data_transition', status='open', channel_source=None, channel_destination=None):
        self.type=type
        self.source = source
        self.source.trans_out.append(self)
        self.destination = destination
        self.destination.trans_in.append(self)
        self.status = 'open'
        self.channel_source = channel_source
        self.channel_destination = channel_destination

class job(object):
    def __init__(self,start_component,components=[]):
        self.components=components
        self.start_component=start_component
        for component in components:
            component.job=self

    def run(self):
        data=None
        start_component=self.start_component        
        def _run(data,component):            
            if not component:
                return            
            res=component.start()        
            if not res:
                raise Exception('not started component')
            try:
                res_list=component.run(data)                
                for out_data,out_component in res_list:                    
                    _run(out_data,out_component)
            except Exception,e:
                raise e
            finally:
                component.stop() 
        _run(data,start_component)    
            


csv_in1= csv_in('partner.csv')
csv_out1= csv_out('partner2.csv')
sort1=sort('name')
log1=logger(name='Read Partner File')
log2=logger(name='After Sort')

tran1=transition(csv_in1,log1)
tran2=transition(csv_in1,sort1)
tran3=transition(sort1,csv_out1)
tran3=transition(sort1,log2)

job1=job(csv_in1,[csv_in1,log1])

job1.run()







