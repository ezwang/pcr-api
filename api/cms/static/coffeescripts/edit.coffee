# Coffeescript yay!
root = exports ? this
$ ->
  temp_data = []
  _.each [1..20], (item) ->
    temp_data.push
      course: item
      review: 'review: ' + Math.random(192830)

  temp_course_data = []
  _.each [1..20], (item) ->
    temp_course_data.push
      user_id: item
      course_id: item
      name: 'course_name:' + Math.random(122743)
      department: 'cis'
      professor: 'hi prof'
      section: '110'



  root.reviews = new app.collections.Reviews(temp_data)
  root.courses = new app.collections.Courses(temp_course_data)

  console.log root.reviews

  String::capitalize = ->
    @charAt(0).toUpperCase() + @[1..]

  root.review_filter_vent = _.extend {}, Backbone.Events
  root.ReviewTableView = new app.views.ReviewTableView collection:reviews
  root.ReviewSummaryView = new app.views.ReviewSummaryView
  root.ReviewFilterView = new app.views.ReviewFilterView collection: courses

  $("#review-table-wrapper").html ReviewTableView.render().el
  $("#review-summary-wrapper").html ReviewSummaryView.render().el
  $("#review-filter-wrapper").html ReviewFilterView.render().el
