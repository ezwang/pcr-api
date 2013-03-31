# Coffeescript yay!
root = exports ? this
root.app =
  models: {}
  collections: {}
  views: {}
  templates: {}

$ ->
  root.users = new app.collections.Users([
    {name: 'Geoffrey Verdernikoff', email:'geoff@gmail.com'},
    {name: 'David Xu', email:'david@gmail.com'},
    {name: 'Ceasar Bautista', email:'ceasar@gmail.com'},
    {name: 'Kyle Hardgrave', email:'nop@gmail.com'}
    {name: 'Nop Jia', email:'nop@gmail.com'}
  ])

  root.courses = new app.collections.Courses([
    {user: 'geoff', name: 'Introduction to Computer Programming', department: 'CIS', section: '110', professor: 'Benedict Brown' },
    {user: 'geoff', name: 'Programming Languages and Techniques I', department: 'CIS', section: '120', professor: 'Steve Zdancewic' },
    {user: 'geoff', name: 'Data Structures and Algorithms with Java', department: 'CIS', section: '121', professor: 'Val Tannen' },
    {user: 'david', name: 'Introduction to Computer Architecture', department: 'CIS', section: '240', professor: 'CJ Taylor'},
    {user: 'ceasar', name: 'Automata, Computability, and Complexity', department: 'CIS', section: '262', professor: 'Aaron Roth'},
    {user: 'ceasar', name: 'Introduction to Algorithms', department: 'CIS', section: '320', professor: 'Sanjeev Khanna'},
    {user: 'david', name: 'Operating Systems', department: 'CIS', section: '380', professor: 'Boon Thau Loo'},
    {user: 'geoff', name: 'Computer Organization and Design', department: 'CIS', section: '371', professor: 'Milo K. Martin'},
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
