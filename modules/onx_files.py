# -*- coding: utf-8 -*-
import os, csv, codecs, cStringIO
from gluon.globals import current

class UTF8Recoder:
    """
    Iterator that reads an encoded stream and reencodes the input to UTF-8
    """
    def __init__(self, f, encoding):
        self.reader = codecs.getreader(encoding)(f)

    def __iter__(self):
        return self

    def next(self):
        return self.reader.next().encode("utf-8")

class UnicodeReader:
    """
    A CSV reader which will iterate over lines in the CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        f = UTF8Recoder(f, encoding)
        self.reader = csv.reader(f, dialect=dialect, **kwds)

    def next(self):
        row = self.reader.next()
        return [unicode(s, "utf-8") for s in row]

    def __iter__(self):
        return self


def csv_defaults(filename):
    try:
        request = current.request
        fname = os.path.join(request.folder, 'static','csv',filename)

        csvfile = open(fname, 'rb')
        return UnicodeReader(csvfile, **{'delimiter':';'})
    except:
        return None
