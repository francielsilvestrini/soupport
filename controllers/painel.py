# -*- coding: utf-8 -*-


def index():
	record = db(db.painel.id > 0).select().first()
	form = crud.update(db.painel, record.id)

	return dict(form=form)