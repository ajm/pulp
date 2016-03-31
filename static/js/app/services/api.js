SearchApp.service('Api', function($http, QueryService){
  function parseIterationData(options){
    return {
      selected: _.chain(options.results).where({ bookmarked: true }).map(function(bookmark){ return bookmark.id }).value(),
      participant_id: options.participant_id,
      clicked: _.chain(options.results).where({ clicked: true }).map(function(clicked){ return { id: clicked.id, reading_started: clicked.reading_started.getTime() / 1000, reading_ended: clicked.reading_ended.getTime() / 1000 } }).value(),
      seen: _.chain(options.results).where({ seen: true }).map(function(seen){ return seen.id }).value()
    }
  }

  this.next = function(options){
    var params = parseIterationData(options);

    if(options.exploratory == 0 || options.exploratory == 1){
      params.exploratory = options.exploratory;
    }

    return $http.post('/next', params);
  }

  this.search = function(options){
    var year_range = QueryService.getYearRange();

    return $http.get('/query', { params: { 'q': options.keyword, 'article-count': options.count, 'participant_id': options.participant_id, 'year_from': year_range.from, 'year_to': year_range.to } });
  }

  this.setup = function(options){
    return $http.get('/setup', { params: { participant_id: options.participant_id, 
                                           q: options.q,
                                           article_count: options.article_count,
                                           //task_type: options.task_type, 
                                           exploration_rate: options.exploration_rate
                                           //experiment_id: options.study_type,
                                            } })
  }
  this.end = function(options){
    var params = parseIterationData(options);

    return $http.post('/end', params);
  }

  this.topics = function(options){
    return $http.get('/topics', { params: options });
  }

  this.ratings = function(data){
    return $http.post('/ratings', data);
  }
});
