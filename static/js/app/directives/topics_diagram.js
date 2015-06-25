SearchApp.directive('topicsDiagram', function(){

  var show_tooltip = function(title, event){
    var $tooltip = $('#topic-tooltip');

    $tooltip.html(title);

    $tooltip.css({
      left: ( event.clientX + 10 ) + 'px',
      top: ( event.clientY + 10 ) + 'px'
    });

    $tooltip.show();
  }

  var hide_tooltip = function(){
    var $tooltip = $('#topic-tooltip');

    $tooltip.hide();
  }

  var create_path = function(raphael, data, options){
      var points = [];
      var y = 10;

      data.values.forEach(function(d){
        points.push({ x: (d.weight * 200), y: y });
        y+=20;
      });

      var pointsToStr = _.map(points, function(point){ return point.x + ',' + point.y }).join(' ');

      var path = raphael.path("M0,10R " + pointsToStr + ' 0,' + ( points.length * 20 ));
      path.data('topic', { id: data.id, title: data.title });
      path.attr({ 'stroke': 'rgb(' + options.background_RGB + ')', 'stroke-width': 2, 'fill': 'rgba(' + options.background_RGB + ',.5)' });

      path.mouseover(function(){
        path.attr('stroke-width', 3);
        path.attr('fill', 'rgba(' + options.background_RGB + ',.7)');
        path.attr('cursor', 'pointer');
      });

      path.mousemove(function(event){
        show_tooltip(options.title, event);
      })

      path.mouseout(function(){
        hide_tooltip();

        path.attr('stroke-width', 2);
        path.attr('fill', 'rgba(' + options.background_RGB + ',.5)');
        path.attr('cursor', 'default');
      });

      path.click(function(){
        options.topic_on_click(path.data('topic'));
      });

      if(options.draw_points){
        _.times(20, function(n){
          var point = raphael.circle(points[n].x, points[n].y, 4).attr({ 'stroke': 'rgb(' + options.background_RGB + ')', 'stroke-width': 2, 'fill': 'white' });
          point.data('article', data.values[n]);

          point.click(function(){
            options.article_on_click(point.data('article'));
          })

          point.mouseover(function(){
            point.animate({
              r: 6
            }, 200);

            var pointDim = point.getBBox();

            var indicator = raphael.path('M0,' + pointDim.cy + 'L300,' + pointDim.cy).attr({ 'stroke': 'rgba(255,255,255,.7)' });

            point.data('indicator', indicator);
            point.toFront();
          });

          point.mousemove(function(event){
            show_tooltip(point.data('article').title, event);
          });

          point.mouseout(function(){
            point.animate({
              r: 4
            }, 200)

            point.data('indicator').remove();
            hide_tooltip();
          });
        });
      }

      return path;
  }

  var init_diagram = function(raphael, data, options){
    var colors = ['253,180,92', '70,191,189'];

    data.sort(function(a,b){
        var sumA = _.sum(a.values);
        var sumB = _.sum(b.values);

        return sumB - sumA;
    });

    data.forEach(function(topic, n){
      points = ( n == data.length - 1 ? true : false );
      create_path(raphael, topic, { title: topic.title, background_RGB: colors[n], draw_points: points, topic_on_click: options.topic_on_click, article_on_click: options.article_on_click });
    });
  }

  return {
    scope: {
      data: '=ngModel',
      topic_on_click: '=topicOnClick',
      article_on_click: '=articleOnClick'
    },
    link: function(scope, elem, attrs){
      var raphael = Raphael(elem[0], 300, 2000);

      scope.$watch('data', function(topics){
        if(topics){
          init_diagram(raphael, topics, { topic_on_click: scope.topic_on_click, article_on_click: scope.article_on_click });
        }
      });
    }
  }
});
