SearchApp.service('Api', function($http){
  this.next = function(options){
    var params = {
      id: _.chain(options.results).where({ bookmarked: true }).map(function(bookmark){ return bookmark.id }).value(),
      participant_id: options.participant_id
    }

    if(options.exploratory == 0 || options.exploratory == 1){
      params.exploratory = options.exploratory;
    }

    return $http.get('/next', { params: params });
  }

  this.search = function(options){
    return $http.get('/query', { params: { 'q': options.keyword, 'article-count': options.count } });
  }

  this.end = function(){
    return $http.get('/end');
  }
});
