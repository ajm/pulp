SearchApp.directive('result', function(){
  return {
    link: function(scope, elem, attrs){
      $(elem).bind('inview', function(event, visible, tooOrBottomOrBoth){
        if(visible == true){
          scope.result.seen = true;
        }
      });
      /*$(window).on('scroll', function(){
        var $elem = $(elem);

        var $window = $(window);

        var docViewTop = $window.scrollTop();
        var docViewBottom = docViewTop + $window.height();

        var elemTop = $elem.offset().top;
        var elemBottom = elemTop + $elem.height();

        if((elemBottom <= docViewBottom) && (elemTop >= docViewTop)){
          $(elem).css('background-color', 'red');
          scope.result.seen = true;
        }
      });*/

      $(window).trigger('scroll');
    }
  }
});
