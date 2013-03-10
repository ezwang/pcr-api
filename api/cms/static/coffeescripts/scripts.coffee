# Coffeescript yay!
root = exports ? this
root.app =
  models: {}
  collections: {}
  views: {}
  templates: {}

$ ->
  root.users = new app.collections.Users([
    {name: 'geoff', email:'1@gmail.com'},
    {name: 'david', email:'2@gmail.com'},
    {name: 'ceasar', email:'3@gmail.com'},
    {name: 'nop', email:'4@gmail.com'}
  ])

  root.courses = new app.collections.Courses([
    {user: 'geoff', name: 'course1'},
    {user: 'david', name: 'new'},
    {user: 'ceasar', name: 'old'},
    {user: 'ceasar', name: 'oldf'},
    {user: 'david', name: 'old34'},
    {user: 'geoff', name: 'oldr4'},
    {user: 'nop', name: 'old23'},
    {user: 'ceasar', name: 'ol2 '},
    {user: 'nop', name: 'middle'}
  ])

  String::capitalize = ->
    @charAt(0).toUpperCase() + @[1..]

  root.create_vent = _.extend {}, Backbone.Events
  root.search_vent = _.extend {}, Backbone.Events
  root.match_vent = _.extend {}, Backbone.Events
  root.UserList = new app.views.UserListView collection: users
  root.CourseList = new app.views.CourseListView collection: courses
  root.SearchCourses = new app.views.SearchView
  root.UserNew = new app.views.UserNewView
  $("#users-table-wrapper").html UserList.render().el
  $("#users-table-wrapper").append UserNew.render().el
  $("#courses-table-wrapper").html CourseList.render().el
  $("#search-wrapper").html SearchCourses.render().el
