
$(function(){
    $(document).ready(function(){

        $('.flash').delay(5000).fadeOut();
        
        $('.onx-form input:visible:enabled:first').focus();

        $('.tooltip-top').tooltip({ placement: 'top' });

        $("a[data-toggle='tooltip']").tooltip({ placement: 'top' });

        $("a[data-action='launchFullscreen']").click(function () {
            if (screenfull.isFullscreen) {
                $(this).removeClass( "btn" ).addClass( "btn btn-inverse" );                
                screenfull.exit();
            } else {
                $(this).removeClass( "btn btn-inverse" ).addClass( "btn" );                
                screenfull.request();
            }
        });


        // Side Bar Toggle
        $('.hide-sidebar').click(function() {
          $('#sidebar').hide('fast', function() {
            $('#content').removeClass('span9');
            $('#content').addClass('span12');
            $('.hide-sidebar').hide();
            $('.show-sidebar').show();
          });
        });

        $('.show-sidebar').click(function() {
            $('#content').removeClass('span12');
            $('#content').addClass('span9');
            $('.show-sidebar').hide();
            $('.hide-sidebar').show();
            $('#sidebar').show('fast');
        });

        var tboby =  $(".web2py_htmltable>table>tbody");
        if(tboby) {
            $(tboby).append('<tr><td class="row-empty">&nbsp;</td></tr>');
            $(tboby).append('<tr><td class="row-empty">&nbsp;</td></tr>');
            $(tboby).append('<tr><td class="row-empty">&nbsp;</td></tr>');
        }
        
    });
});