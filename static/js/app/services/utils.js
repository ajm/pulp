SearchApp.service('Utils', function(){
  this.keywordsToChartData = function(keywords){
    var labels = _.map(keywords, function(keyword){ return keyword.content });
    var values = _.map(keywords, function(keyword){ return Math.round(keyword.weight * 100) });

    return {
      labels: labels,
      values: values
    }
  }
});
