SearchApp.directive('rate', function(){
  return {
    scope: {
      rating: '=ngModel'
    },
    template: '<ul class="list-inline star-list"><li data-pos="1"><i class="fa fa-star"></i></li><li data-pos="2"><i class="fa fa-star"></i></li><li data-pos="3"><i class="fa fa-star"></i></li><li data-pos="4"><i class="fa fa-star"></i></li><li data-pos="5"><i class="fa fa-star"></i></li></ul><p class="text-muted rating-helper"></p>',
    link: function(scope, elem, attrs){

      var highlight_stars = function(end){
        $(elem).find('.star-list .fa-star').removeClass('active');

        for(var i=1; i<=end; i++){
          $(elem).find('.star-list li[data-pos=' + i + '] .fa-star').addClass('active');
        }
      }

      var helper_text = function(value){
        if(value == 1){
          return 'This article wasn\'t at all relative to me.';
        }else if(value > 1 && value < 5){
          return 'This article was quite relative to me.';
        }else{
          return 'This article was very relative to me.';
        }
      }

      scope.$watch('rating', function(value){
        highlight_stars(value);
        $(elem).find('.rating-helper').html(helper_text(value));
      });

      $(elem).find('.star-list li')
        .on('mouseover', function(){
          var star_pos = parseInt($(this).data('pos'));

          $(elem).find('.rating-helper').html(helper_text(star_pos));

          highlight_stars(star_pos);
        })
        .on('click', function(){
          var star_pos = parseInt($(this).data('pos'));

          scope.$apply(function(){
            scope.rating = star_pos;
          });
        })
        .on('mouseout', function(){
          highlight_stars(scope.rating);
        });
    }
  }
});
