SearchApp.controller('TopicController', function($scope, $routeParams, $location, $sce, Utils){

  $scope.related_articles = [];
  $scope.related_keywords = [];

  for(var i=0; i<10; i++){
    $scope.related_articles.push({
      title: 'Lorem ipsum dolor sit amet',
      abstract: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Aenean euismod, massa ullamcorper pellentesque ultrices, nunc mauris bibendum tortor, ac ultrices urna arcu quis lectus. Quisque ut congue mi, nec dapibus nisl. Pellentesque eu risus sed velit ullamcorper sagittis. Proin posuere congue eros, in tincidunt velit dictum at. Donec posuere sodales tellus, et fringilla lectus scelerisque id. Etiam in feugiat nibh, sit amet sollicitudin erat. Morbi eget velit ac velit sodales aliquam. Suspendisse tempor nisi nec ex consequat cursus.',
      author: 'Lorem ipsum, dolor sit',
      venue: 'arXiv',
      url: 'http://cs.helsinki.fi'
    });

    $scope.related_keywords.push({
      weight: Math.random(),
      content: 'Lorem ipsum'
    });
  }

  $scope.related_keywords = Utils.keywordsToChartData($scope.related_keywords);

  $scope.back = function(){
    $location.path('/');
  }

  $scope.show_full_abstract = function(article){
		article.abstract_synopsis = article.abstract;
		article.full_length_abstract = true;
	}

  function init_articles(){
    $scope.related_articles.forEach(function(article){
  			article.abstract = $sce.trustAsHtml(String(article.abstract).replace(/<[^>]+>/gm, ''));
  			article.title = $sce.trustAsHtml(String(article.title).replace(/<[^>]+>/gm, ''));

        var synopsis = ( String(article.abstract).length > 300 ? String(article.abstract).substring(0, 300) + "..." : String(article.abstract) );

        article.abstract_synopsis = $sce.trustAsHtml(synopsis);
  			article.full_length_abstract = ( String(article.abstract).length == String(article.abstract_synopsis).length );
  	});
  }

  init_articles();

});
