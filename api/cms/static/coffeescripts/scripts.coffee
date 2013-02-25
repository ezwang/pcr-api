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
    {user: 'nop', name: 'middle'}
  ])

  String::capitalize = ->
    @charAt(0).toUpperCase() + @[1..]

  root.search_vent = _.extend {}, Backbone.Events
  root.UserList = new app.views.UserListView collection: users
  root.CourseList = new app.views.CourseListView collection: courses
  root.SearchCourses = new app.views.SearchView
  $("#users-table-wrapper").html UserList.render().el
  $("#courses-table-wrapper").html CourseList.render().el
  $("#search-wrapper").html SearchCourses.render().el
