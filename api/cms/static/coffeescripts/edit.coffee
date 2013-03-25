# Coffeescript yay!
root = exports ? this
root.app =
  models: {}
  collections: {}
  views: {}
  templates: {}

$ ->
  root.reviews = new app.collections.Reviews([
    {course:'12343', review:'This is a samply review Ojw ohago wjeoia orugha oewijfa oweifoawu hgoai jfowa iuwhg oaiewjfoauwhge lauhl aij lawiue liuahg irj aowiejf o'},
    {course:'12343', review:'This is a samply review Ojw ohago wjeoia orugha oewijfa oweifoawu hgoai jfowa iuwhg oaiewjfoauwhge lauhl aij lawiue liuahg irj aowiejf o'},
    {course:'12343', review:'This is a samply review Ojw ohago wjeoia orugha oewijfa oweifoawu hgoai jfowa iuwhg oaiewjfoauwhge lauhl aij lawiue liuahg irj aowiejf o'},
    {course:'12343', review:'This is a samply review Ojw ohago wjeoia orugha oewijfa oweifoawu hgoai jfowa iuwhg oaiewjfoauwhge lauhl aij lawiue liuahg irj aowiejf o'},
    {course:'12343', review:'This is a samply review Ojw ohago wjeoia orugha oewijfa oweifoawu hgoai jfowa iuwhg oaiewjfoauwhge lauhl aij lawiue liuahg irj aowiejf o'},
    {course:'12343', review:'This is a samply review Ojw ohago wjeoia orugha oewijfa oweifoawu hgoai jfowa iuwhg oaiewjfoauwhge lauhl aij lawiue liuahg irj aowiejf o'},
    {course:'12343', review:'This is a samply review Ojw ohago wjeoia orugha oewijfa oweifoawu hgoai jfowa iuwhg oaiewjfoauwhge lauhl aij lawiue liuahg irj aowiejf o'},
    {course:'12343', review:'This is a samply review Ojw ohago wjeoia orugha oewijfa oweifoawu hgoai jfowa iuwhg oaiewjfoauwhge lauhl aij lawiue liuahg irj aowiejf o'},
    {course:'12343', review:'This is a samply review Ojw ohago wjeoia orugha oewijfa oweifoawu hgoai jfowa iuwhg oaiewjfoauwhge lauhl aij lawiue liuahg irj aowiejf o'},
  ])

  String::capitalize = ->
    @charAt(0).toUpperCase() + @[1..]

  # root.create_vent = _.extend {}, Backbone.Events
  # root.search_vent = _.extend {}, Backbone.Events
  # root.match_vent = _.extend {}, Backbone.Events
  root.ReviewTableView = new app.views.ReviewTableView collection:reviews
  root.ReviewSummaryView = new app.views.ReviewSummaryView
  root.ReviewFilterView = new app.views.ReviewFilterView
  # root.CourseList = new app.views.CourseListView collection: courses
  # root.SearchCourses = new app.views.SearchView
  # root.UserNew = new app.views.UserNewView
  $("#review-table-wrapper").html ReviewTableView.render().el
  $("#review-summary-wrapper").html ReviewSummaryView.render().el
  $("#review-filter-wrapper").html ReviewFilterView.render().el
  # $("#summary-wrapper").html ReviewTableView.render().el
  # $("#users-table-wrapper").append UserNew.render().el
  # $("#courses-table-wrapper").html CourseList.render().el
  # $("#search-wrapper").html SearchCourses.render().el
