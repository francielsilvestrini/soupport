
$(function(){
    $(document).ready(function(){

        $('.flash').delay(5000).fadeOut();
		
		$('.onx-form input:visible:enabled:first').focus();

		$('.tooltip-top').tooltip({ placement: 'top' });
    });
});