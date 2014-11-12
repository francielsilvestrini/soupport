# -*- coding: utf-8 -*-

from onx_model import ModelBase
from h5_widgets import TagsInputWidget


def tag_represent(value):
    if value:
        rep = [A(SPAN(name, _class='label label-info'), SPAN(' '),
            _href='javascript:void(0);', _class='tag') for name in value.split(',')]
    else:
        rep = []
    return DIV(rep)


class TagsModel(ModelBase):
    name = 'tags'

    def define_tables(self):
        db.define_table('tag',
            Field('name', 'string', label=T('Name')),
            migrate="tag.table",
            format='%(name)s')
        db.tag.name.requires = [IS_NOT_EMPTY(),IS_NOT_IN_DB(db, 'tag.name')]    


    def make_field_tags(self, db):
        field_tags = Field('tags', 'string', 
            label=T('Tags'),
            widget=TagsInputWidget(url=URL(c='tags', f='tag_data.json', host=True)).widget,
            represent=lambda value,row: tag_represent(value)
            )

        return field_tags