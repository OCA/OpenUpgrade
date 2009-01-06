
class TinyException(Exception):

    def __init__(self, message, title=None):

        self.title = title
        self.message = message

    def __unicode__(self):
        return ustr(self.message)
    
    def __str__(self):
        return self.message

class TinyError(TinyException):

    def __init__(self, message, title=_("Error")):
        TinyException.__init__(self, message=message, title=title)

class TinyWarning(TinyException):

    def __init__(self, message, title=_("Warning")):
        TinyException.__init__(self, message=message, title=title)

class TinyMessage(TinyException):

    def __init__(self, message, title=_("Information")):
        TinyException.__init__(self, message=message, title=title)

def error(title, msg, details=None):
    raise TinyError(message=msg, title=title or _("Error"))

def warning(msg, title=None):
    raise TinyWarning(message=msg, title=title or _("Warning"))

def message(msg):
    raise TinyMessage(message=msg)

def to_xml(s):
    return s.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')

# vim: ts=4 sts=4 sw=4 si et

