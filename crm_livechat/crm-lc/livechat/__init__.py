# -*- encoding: utf-8 -*-
def ustr(value):
    """This method is similar to the builtin `str` method, except
    it will return Unicode string.

    @param value: the value to convert

    @rtype: unicode
    @return: unicode string
    """

    if isinstance(value, unicode):
        return value

    if hasattr(value, '__unicode__'):
        return unicode(value)

    if not isinstance(value, str):
        value = str(value)

    return unicode(value, 'utf-8')

__builtins__['ustr'] = ustr
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

