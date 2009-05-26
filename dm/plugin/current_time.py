import time

__description__ = '''This plugin returns the current time'''
__args__ = []
def current_time(cr,uid,**args):
    return time.strftime('%Y-%m-%d %H:%M:%S')
