SearchApp.factory('QueryService', function($location){
  var year_range = { from: 1993, to: 2100 };
  var query = ''

  var service = {
    setYearRange: setYearRange,
    getYearRange: getYearRange,
    getQuery: getQuery,
    setQuery: setQuery
  };

  function setYearRange(range){
    year_range = { from: range.from || year_range.from, to: range.to || year_range.to };
  }

  function getYearRange(){
    return year_range;
  }

  function setQuery(q){
    query = q;
  }

  function getQuery(){
    return query;
  }

  return service;
});
