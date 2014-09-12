# -*- coding: utf-8 -*-
from gluon.sqlhtml import StringWidget, MultipleOptionsWidget
from gluon.html import INPUT, SCRIPT, DIV, URL
from gluon.globals import current


class TagsInputWidget(StringWidget):

	def __init__(self, url):
		self.url = url

	def widget(self, field, value):
		files = [
			URL('static','assets/typeahead.js/typeahead.css'),
  			URL('static','assets/bootstrap-tags/bootstrap-tagsinput.css'),]
  		for f in files:
  			if not f in current.response.header_files:
  				current.response.header_files.append(f)

		files = [
			URL('static','assets/typeahead.js/bloodhound.min.js'),
  			URL('static','assets/typeahead.js/typeahead.jquery.min.js'),
  			URL('static','assets/typeahead.js/typeahead.bundle.min.js'),
  			URL('static','assets/bootstrap-tags/bootstrap-tagsinput.min.js')]
  		for f in files:
  			if not f in current.response.files:
  				current.response.files.append(f)

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