SearchApp.directive('topicsDiagram', function(){
  
  var BAR_HEIGHT = 10;
  var CANVAS_WIDTH = $('#topics-container').width();
  var COLORS = ["#7fdfc6","#ebaf95","#d0fab7","#99a7dd","#cf94a4","#ef8be3","#c58784","#b7c6b5","#e7f9b1","#c3aff1","#84c7b0","#f88bcb","#dffeca","#859dce","#7f8fdf","#eba78e","#f7eedc","#ef8e9e","#c6f6df","#ed86da","#ddd690","#a4d6cd","#af8ea4","#bfa8da","#f7daea","#b3dbc0","#9791d6","#afb8e0","#abebad","#d7b7eb","#ddf9b5","#87ada0","#cb88ed","#9fa9ad","#f6efed","#869588","#e0de94","#97d0a3","#c5acca","#bca4ad","#c6a79c","#c59df4","#afade3","#8ee2e9","#e6edb6","#b7df87","#b6f9a1","#f0c08f","#baba83","#e0aa9d","#f498c0","#8a9ca3","#89a4cc","#b0b790","#d88496","#e29ee4","#90c0ca","#f4be8d","#e2a1a6","#b3a3ce","#a5c49b","#97aac2","#aee1a8","#8a8fb8","#82bdb6","#fdcbae","#faccef","#98e2d7","#cae6af","#ba97a4","#c2a296","#eaf4b6","#f8f0c4","#f9b58d","#f1d8a4","#9a89ce","#a8ddb0","#ea85f6","#9f91e4","#9cb5b3","#d49ccb","#a1dbc2","#93e6c8","#edb0fa","#e5a198","#a4c5f2","#b4e2b5","#add8fc","#f8e3bf","#cef9aa","#e39dda","#e8ee88","#868eaa","#e7babb","#8c87f4","#8ca7c5","#9cedbb","#c7d9f2","#87cac3","#bdd7d5","#a1f7b2","#abedf5","#bd8a96","#d7a5de","#ec8cbd","#82d7c2","#bbb9c9","#beb1fb","#eba5a7","#85f097","#a8f59e","#86e9b9","#cfd4eb","#edeac9","#cf8898","#f199d0","#84e685","#a5e1fc","#c0dbf0","#81fdc6","#93b38d","#a5f9c0","#8ff78e","#dea9c7","#c0a8af","#86c7a9","#aac1e8","#ebfed5","#8996dd","#aeebd4","#cab5c5","#a197ac","#c8f0e8","#b4f6f9","#a1dcdf","#e4edd3","#b38296","#93f4d1","#c6d5bc","#de8fd5","#d7e285","#c6ddf7","#c08481","#c5aac5","#abf992","#9cddd7","#ead7be","#ef9c95","#c78695","#a7aec9","#dc96bc","#efc39f","#b0afbd","#c9808b","#b98fd2","#a48fc0","#8399ef","#958db1","#c4f283","#e4da9f","#cfbcda","#8ce9e4","#b59481","#9ff3ce","#a5f49c","#b4ecd8","#d789d6","#f4fcfc","#c39c9a","#97b6d4","#f1dceb","#fdd5b3","#c599c7","#cd8a9b","#90d693","#90fad8","#c4ccdb","#9ac287","#badedd","#8e95b0","#eb8cfc","#e4efce","#a39acc","#bae388","#a7a8b8","#e68bd0","#cd9080","#f6cefb","#d6ef8c","#faa8f0","#a0d9dc","#ecdbda","#ca998a","#a8a1d1","#d0f7a1","#e1e2c0","#efc4a2","#e3d98c","#ecb5b6","#adbdb8","#e2e9b8","#dcbb83","#c4d9f1","#c7cf91","#c5edb4","#c497ec","#c6efdf","#e188fe","#e9a9d3","#899891","#d6ecf0","#a7b89a","#a3a780","#ee84b8","#e6e2ef","#eab4b3","#8b98f5","#89f4f3","#95f6a2","#92fcd9","#f1da88","#d9bbc7","#b48da6","#bfbcb3","#87cebb","#ae85d7","#b2e18b","#9790f9","#a7af8f","#b7db96","#df9cbc","#ecc0b3","#a7e888","#f2fe99","#8b84d1","#a89dda","#ac81b5","#abfadb","#927fc5","#ddb786","#8896aa","#82d9a3","#dbdab4","#d2f58e","#d9edf4","#de88ef","#cd8d85","#94dfa9","#8196d2","#bc98ae"]
  var color_usage = {};
  var topics_to_color = {};
  var color_iterator = 0;
  var y_pointer = 0;

  var darken_color = function(color, percent) {
    var num = parseInt(color.slice(1),16), amt = Math.round(2.55 * percent), R = (num >> 16) + amt, G = (num >> 8 & 0x00FF) + amt, B = (num & 0x0000FF) + amt;
    return "#" + (0x1000000 + (R<255?R<1?0:R:255)*0x10000 + (G<255?G<1?0:G:255)*0x100 + (B<255?B<1?0:B:255)).toString(16).slice(1);
  }

  var beautiful_color = function(){
    var r = (Math.round(Math.random()* 127) + 127).toString(16);
    var g = (Math.round(Math.random()* 127) + 127).toString(16);
    var b = (Math.round(Math.random()* 127) + 127).toString(16);
    var color = '#' + r + g + b;

    return color;
  }

  var generate_color = function(){
    /*var color = beautiful_color();

    while(color_usage[color]){
      color = beautiful_color();
    }

    return color;*/

    var color = COLORS[color_iterator]
    color_iterator++;

    return color;
  }

  var get_topic_weight_of_article = function(topic, article){
    var topic_in_article = _.find(article.topics, { label: topic });

    if(topic_in_article){
      return topic_in_article.weight;
    }else{
      return 0;
    }
  }

  var show_tooltip = function(title, event){
    var $tooltip = $('#topic-tooltip');

    $tooltip.html(title);

    $tooltip.css({
      left: ( event.clientX - ( $tooltip.outerWidth() + 10 ) ) + 'px',
      top: ( event.clientY + 10 ) + 'px'
    });

    $tooltip.show();
  }

  var hide_tooltip = function(){
    var $tooltip = $('#topic-tooltip');

    $tooltip.hide();
  }

  var create_bar = function(raphael, data, options){
    var bar =
      raphael.rect(0, options.y, 0, options.height)
      .data('topic', data)
      .attr({ 'fill': options.color, 'stroke-width': '0px' })
      .animate({ width: options.width, x: options.x }, 500, '<');

    bar
      .mousemove(function(event){
        show_tooltip(data.label, event);
      })
      .mouseover(function(){
        bar.attr('fill', darken_color(options.color, -10));
      })
      .mouseout(function(){
        hide_tooltip();

        bar.attr('fill', options.color);
      });
  }

  var init_diagram = function(raphael, data, options){
    var all_topics =
      _.chain(data)
        .reduce(function(all, article){ return all.concat(article.topics) }, [])
        .uniq(function(topic){
          return topic.label;
        })
        .map(function(topic){
          if(!topics_to_color[topic.label]){
            topics_to_color[topic.label] = generate_color();
          }

          return topic.label;
        })
        .value();

    all_topics.forEach(function(topic){

      var bar_y = y_pointer;

      data.forEach(function(article){
        var weight_sum = _.sum(article.topics, 'weight');
        var topic_weight = get_topic_weight_of_article(topic, article);
        var bar_width = ( topic_weight / weight_sum ) * CANVAS_WIDTH;

        article.x_pointer = article.x_pointer || 0;

        if(bar_width > 0){
          // render bar
          create_bar(raphael, { label: topic }, { color: topics_to_color[topic], width: bar_width, height: BAR_HEIGHT, x: article.x_pointer, y: bar_y });
        }

        article.x_pointer += bar_width;

        bar_y += BAR_HEIGHT;
      });

    });

    y_pointer += BAR_HEIGHT * data.length;
  }

  return {
    scope: {
      data: '=ngModel'
    },
    link: function(scope, elem, attrs){
      var raphael;

      scope.$watch('data', function(data){
        if(!data){
          return;
        }

        if(!data.append){
          y_pointer = 0;

          $svg = $(elem).find('svg').remove();
          raphael = Raphael(elem[0], CANVAS_WIDTH, 1000);
        }else{
         var $svg = $(elem).find('svg');
         $svg.attr('height', $svg.height() + data.topics.length * BAR_HEIGHT);
        }

        if(data.topics){
          init_diagram(raphael, data.topics, {});
        }
      });
    }
  }
});
