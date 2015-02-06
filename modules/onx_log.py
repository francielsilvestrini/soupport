# -*- coding: utf-8 -*-
from gluon.globals import current
from onx_utils.OnxUtils import table_default_values

import logging, logging.handlers
class OnxLogHandler(logging.Handler):

    def emit(self, record):
        response = current.response
        if response.get('page_alerts'):
            response.page_alerts.append((
                record.levelname,
                record.msg,
                'warning'))

        db = current.db
        if not 'log' in db.tables:
            return

        try:
            log = db['log']
            defs = table_default_values(log)
            defs['name'] = record.name
            defs['level'] = record.levelname
            defs['module'] = record.module
            defs['func_name'] = record.funcName
            defs['line_no'] = str(record.lineno)
            defs['thread'] = str(record.thread)
            defs['thread_name'] = record.threadName
            defs['process'] = str(record.process)
            defs['message'] = record.msg
            defs['args'] = str(record.args)

            log.insert(**defs)
        except Exception, e:
            pass

def onx_logger():
    request = current.request
    logger = logging.getLogger(request.application)

    handler = OnxLogHandler()
    handler.setLevel(logging.DEBUG)
    logger.handler = []
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    return logger