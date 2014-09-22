# -*- coding: utf-8 -*-

def index():
	return dict()


def todo():
	return dict()


def firebird():
	d = DAL('firebird://sysdba:masterkey@localhost:P\\ONNIXSISTEMAS\\ERP\\DADOS\\ONNIX.GDB', migrate=False)
	response.view = 'apptests/index.html'    
	return dict(content=d.tables)