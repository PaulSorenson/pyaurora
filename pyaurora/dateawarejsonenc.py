
'''
:mod:`dateawarejsonenc` - encode object to JSON
===============================================

.. moduleauthor:: paul sorenson
'''


import datetime as dt
import json


class DateAwareJSONEncoder(json.JSONEncoder):
    '''
    Subclass of JSONEncoder that can encode dates.
    '''

    def default(self, o):
        try:
            if isinstance(o, dt.datetime):
                return o.isoformat()
            j = json.JSONEncoder.default(self, o)
        except TypeError:
            j =  str(o)
        return j

