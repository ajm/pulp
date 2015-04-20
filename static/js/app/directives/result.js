SearchApp.directive('result', function(){
  return {
    link: function(scope, elem, attrs){
      $(window).on('scroll', function(){
        var $elem = $(elem);
        var $window = $(window);

        var docViewTop = $window.scrollTop();
        var docViewBottom = docViewTop + $window.height();

        var elemTop = $elem.offset().top;
        var elemBottom = elemTop + $elem.height();

        if(!scope.result.seen && (elemBottom <= docViewBottom) && (elemTop >= docViewTop)){
          scope.result.seen = true;
        }
      });

      $(window).trigger('scroll');
    }
  }
});
