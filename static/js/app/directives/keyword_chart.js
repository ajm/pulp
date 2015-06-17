SearchApp.directive('keywordChart', function(){
  return {
    scope: {
      data: '=ngModel'
    },
    link: function(scope, elem, attrs){
      //var colors = ['#F7464A', '#46BFBD', '#FDB45C', '#949FB1', '#4D5360', '#886655', '#D4556A', '#706D97', '#588C73', '#B5512F']

      var data = {
        labels: scope.data.labels,
        datasets: [{
          fillColor: "rgba(0,151,207,0.2)",
          strokeColor: "rgba(0,151,207,1)",
          pointColor: "rgba(0,151,207,1)",
          pointStrokeColor: "#fff",
          pointHighlightFill: "#fff",
          pointHighlightStroke: "rgba(0,151,207,1)",
          data: scope.data.values
        }]
      }

      new Chart($(elem)[0].getContext('2d')).Radar(data, {
        scaleOverride: true,
        scaleSteps: 10,
        scaleStepWidth : 10,
        scaleStartValue : 0
      });
    }
  }
});
