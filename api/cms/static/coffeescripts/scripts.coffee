# Coffeescript yay!
root = exports ? this
root.app =
  models: {}
  collections: {}
  views: {}
  templates: {}

$ ->
  root.users = new app.collections.Users([
    {name: 'geoff'},
    {name: 'david'},
    {name: 'ceasar'},
    {name: 'nop'}
  ])

  root.courses = new app.collections.Courses([
    {user: 'geoff', name: 'course1'},
    {user: 'david', name: 'new'},
    {user: 'ceasar', name: 'old'},
    {user: 'nop', name: 'middle'}
  ])


  root.search_vent = _.extend {}, Backbone.Events
  root.UserList = new app.views.UserListView collection: users
  root.CourseList = new app.views.CourseListView collection: courses
  root.SearchCourses = new app.views.SearchView
  $("#users-table-wrapper").html UserList.render().el
  $("#courses-table-wrapper").html CourseList.render().el
  $("#search-wrapper").html SearchCourses.render().el
