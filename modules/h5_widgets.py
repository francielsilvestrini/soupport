# -*- coding: utf-8 -*-
from gluon.sqlhtml import StringWidget, MultipleOptionsWidget
from gluon.html import INPUT, SCRIPT, DIV, URL
from gluon.globals import current


class TagsInputWidget(StringWidget):

    def __init__(self, url):
        self.url = url


    def widget_files(self):
        session = current.session

        session.page.header_files['typeahead.css'] = URL('static','assets/typeahead.js/typeahead.css')
        session.page.header_files['bootstrap-tagsinput.css'] = URL('static','assets/bootstrap-tags/bootstrap-tagsinput.css')

        session.page.footer_files['bloodhound.min.js'] = URL('static','assets/typeahead.js/bloodhound.min.js')
        session.page.footer_files['typeahead.jquery.min.js'] = URL('static','assets/typeahead.js/typeahead.jquery.min.js')
        session.page.footer_files['typeahead.bundle.min.js'] = URL('static','assets/typeahead.js/typeahead.bundle.min.js')
        session.page.footer_files['bootstrap-tagsinput.min.js'] = URL('static','assets/bootstrap-tags/bootstrap-tagsinput.min.js')
        return

    def widget(self, field, value):
        self.widget_files()

        wgt_default = StringWidget.widget(field, value, **{
            '_data-role':'tagsinput', '_placeholder':current.T('Add Tag')})
        wgt_id = wgt_default.attributes.get('_id', 'no_id')
        wgt_value = wgt_default.attributes.get('_value', '')

        js = '''
            jQuery(document).ready(function(){
                var tagnames = new Bloodhound({
                    datumTokenizer: Bloodhound.tokenizers.obj.whitespace('name'),
                    queryTokenizer: Bloodhound.tokenizers.whitespace,
                    prefetch: {
                        url: '%(url_tags_json)s',
                        filter: function(list) {
                            return $.map(list, function(tagname) {
                                return { name: tagname }; 
                            });
                        }
                    }
                });
                tagnames.clearPrefetchCache();
                tagnames.initialize(true);

                $('#%(wgt_id)s').tagsinput({
                    typeaheadjs: {
                        name: 'tagnames',
                        displayKey: 'name',
                        valueKey: 'name',
                        source: tagnames.ttAdapter()
                    }
                });

                $('form').submit(function() {
                    var value = $('#%(wgt_id)s').val();
                    $('#%(wgt_id)s').val(value);
                    return true;
                });
            });
            ''' % {'wgt_id':wgt_id, 'url_tags_json':self.url}
        jq_script=SCRIPT(js, _type="text/javascript")

        wrapper = DIV(_class="TagsInputWidget") 
        wrapper.components.extend([wgt_default, jq_script])
        return wrapper


from gluon.sqlhtml import TextWidget
class NicEditorWidget(TextWidget):

    def widget_files(self):
        current.session.page.footer_files['nicEditComplete.js'] = URL('static','assets/nicEdit/nicEditComplete.js')
        return

    def widget(self, field, value, **attributes):
        self.widget_files()

        wgt_default = TextWidget.widget(field, value, **attributes)
        wgt_id = wgt_default.attributes.get('_id', 'no_id')

        js = '''
            jQuery(document).ready(function(){
                var wysiwygfield = new nicEditor({
                    fullPanel : true,
                    iconsPath :"%(iconsPath)s",
                    uploadURI :"%(uploadURI)s",
                })
                wysiwygfield.panelInstance("%(field_name)s");
                jQuery('input[type=submit]').click(function(){
                    wysiwygfield.panelInstance("%(field_name)s");});
            }); 
            ''' % {
                'field_name':wgt_id,
                'iconsPath':URL(c='static', f='assets/nicEdit/nicEditorIcons.gif'),
                'uploadURI':URL(c='uploads', f='editor', args=[wgt_id]),
            }
        jq_script=SCRIPT(js, _type="text/javascript")

        wrapper = DIV(_class="NicEditorWidget") 
        wrapper.components.extend([wgt_default, jq_script])
        return wrapper


from gluon.sqlhtml import OptionsWidget
class LookupWidget(OptionsWidget):

    def widget_files(self):
        current.session.page.header_files['select2.css'] = URL('static','assets/select2-3.5.1/select2.css')
        current.session.page.footer_files['select2.min.js'] = URL('static','assets/select2-3.5.1/select2.min.js')
        return

    def widget(self, field, value, **attributes):
        self.widget_files()
        
        attributes['_style'] = 'width: 316px; height: 20px; margin-bottom: 14px;'
        wgt_default = OptionsWidget.widget(field, value, **attributes)
        wgt_id = wgt_default.attributes.get('_id', 'no_id')

        js = '''
            jQuery(document).ready(function(){
                jQuery('#%(field_name)s').select2();
            }); 
            ''' % {'field_name':wgt_id}
        jq_script=SCRIPT(js, _type="text/javascript")

        wrapper = DIV(_class="LookupWidget") 
        wrapper.components.extend([wgt_default, jq_script])
        return wrapper


class MaskWidget(StringWidget):  

    def __init__(self, mask):
        self.mask = mask
        return

    def widget_files(self):
        current.session.page.footer_files['jquery.mask.min.js'] = URL('static','assets/mask/jquery.mask.min.js')
        return

    def widget(self, field, value, **attributes):
        self.widget_files()
        
        wgt_default = StringWidget.widget(field, value, **attributes)
        wgt_id = wgt_default.attributes.get('_id', 'no_id')

        js = '''
            jQuery(document).ready(function(){
                jQuery('#%(field_name)s').each( function(){ 
                    jQuery(this).mask('%(mask)s'); 
                });  
            }); 
            ''' % dict(field_name=wgt_id, mask=self.mask)
        jq_script=SCRIPT(js, _type="text/javascript")

        wrapper = DIV(_class="MaskWidget") 
        wrapper.components.extend([wgt_default, jq_script])
        return wrapper


class H5ColorWidget(StringWidget):  
    def widget(self, field, value, **attr):
        attr['_type'] = 'color'
        return StringWidget.widget(field, value, **attr)


class H5EmailWidget(StringWidget):  
    def widget(self, field, value, **attr):
        attr['_type'] = 'email'
        return StringWidget.widget(field, value, **attr)

'''
color
date
datetime
datetime-local
email
month
number
range
search
tel
time
url
week        
'''