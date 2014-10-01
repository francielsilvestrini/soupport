
$(function(){
    $(document).ready(function(){

        $('.flash').delay(5000).fadeOut();
        
        $('.onx-form input:visible:enabled:first').focus();

        $('.tooltip-top').tooltip({ placement: 'top' });

        $("a[data-action='launchFullscreen']").click(function () {
            if (screenfull.isFullscreen) {
                $(this).removeClass( "btn" ).addClass( "btn btn-inverse" );                
                screenfull.exit();
            } else {
                $(this).removeClass( "btn btn-inverse" ).addClass( "btn" );                
                screenfull.request();
            }
        });     
    });
});