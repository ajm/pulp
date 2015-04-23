SearchApp.directive('result', function(){
  return {
    link: function(scope, elem, attrs){
      var header_height = 220;
      var items_on_screen = 7;

      $(window).on('resize', function(){
        var result_height = ( $(window).height() - header_height ) / items_on_screen;
        $(elem).css('height', result_height + 'px');
      });

      $(window).trigger('resize');
    }
  }
});
