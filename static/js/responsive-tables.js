//Populates responsive table headers
//Author: Angelo Compagnucci <angelo.compagnucci@gmail.com>
jQuery(document).ready(function() {
	set_table_headers();
});

jQuery(window).resize(function() {
	jQuery(".resp-header").remove();
	set_table_headers();
});

function set_table_headers(){
	if (jQuery(document).width() < 700) {
		jQuery("div.resp-table").not("form").children("table").each(function() {
		   	curtable = jQuery(this);
		   	curtable.find("td:empty").html("&nbsp;");
		   	curhead = curtable.find("thead > tr > th");
		   	if (curhead.length > 0) {
		   		tdcount = curtable.find("tbody > tr:eq(0) > td").length
		   		for (index = 1; index <= tdcount; index++){
		   			curth = curhead.eq(index-1).html();
			   		curth = (curth != null) ? curth : '&nbsp;';
			   		curtable.find("tbody > tr > td:nth-of-type("+index+")")
			   			.before('<span class="resp-header">' + curth + '</span>');
		   		}
			}
			else {
				curtable.find("td").css({
				'padding-left': '0',
	        	'width': 'auto',
	        	'left': '3px'
				});
			}
	   	});
	}
}
