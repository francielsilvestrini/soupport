# -*- coding: utf-8 -*-

def index():
	return dict()


def todo():
	return dict()
'''
from h5_widgets import TagsInputWidget
def form_test():
	form = SQLFORM.factory(
		Field('tags', 'string', 
			widget=TagsInputWidget(url=URL(c='apptests', f='tag_data.json', host=True)).widget,)
		)
	if form.process().accepted:
		print form.vars.get('tags')

	return dict(form=form)



'''