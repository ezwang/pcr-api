# Coffeescript yay!
$ ->

  root.courses = new app.collections.Courses([
    # {user: 'Geoffrey Verdernikoff', name: 'Introduction to Computer Programming', department: 'CIS', section: '110', professor: 'Benedict Brown' },
    # {user: 'Geoffrey Verdernikoff', name: 'Programming Languages and Techniques I', department: 'CIS', section: '120', professor: 'Steve Zdancewic' },
    # {user: 'Geoffrey Verdernikoff', name: 'Data Structures and Algorithms with Java', department: 'CIS', section: '121', professor: 'Val Tannen' },
    # {user: 'David Xu', name: 'Introduction to Computer Architecture', department: 'CIS', section: '240', professor: 'CJ Taylor'},
    # {user: 'Ceasar Bautista', name: 'Automata, Computability, and Complexity', department: 'CIS', section: '262', professor: 'Aaron Roth'},
    # {user: 'Ceasar Bautista', name: 'Introduction to Algorithms', department: 'CIS', section: '320', professor: 'Sanjeev Khanna'},
    # {user: 'David Xu', name: 'Operating Systems', department: 'CIS', section: '380', professor: 'Boon Thau Loo'},
    # {user: 'Geoffrey Vedernikoff', name: 'Computer Organization and Design', department: 'CIS', section: '371', professor: 'Milo K. Martin'},
  ])


  root.users = new app.collections.Users([
    {
      name: 'Geoffrey Verdernikoff', email:'geoff@gmail.com'
      courses: [
        {user: 'Geoffrey Verdernikoff', name: 'Introduction to Computer Programming', department: 'CIS', section: '110', professor: 'Benedict Brown' },
        {user: 'Geoffrey Verdernikoff', name: 'Programming Languages and Techniques I', department: 'CIS', section: '120', professor: 'Steve Zdancewic' },
        {user: 'Geoffrey Verdernikoff', name: 'Data Structures and Algorithms with Java', department: 'CIS', section: '121', professor: 'Val Tannen' },
        {user: 'Geoffrey Vedernikoff', name: 'Computer Organization and Design', department: 'CIS', section: '371', professor: 'Milo K. Martin'},
      ]
    },
    {
      name: 'David Xu', email:'david@gmail.com'
      courses: [
        {user: 'David Xu', name: 'Introduction to Computer Architecture', department: 'CIS', section: '240', professor: 'CJ Taylor'},
        {user: 'David Xu', name: 'Operating Systems', department: 'CIS', section: '380', professor: 'Boon Thau Loo'},
      ]
    },
    {
      name: 'Ceasar Bautista', email:'ceasar@gmail.com'
      courses: [
        {user: 'Ceasar Bautista', name: 'Automata, Computability, and Complexity', department: 'CIS', section: '262', professor: 'Aaron Roth'},
        {user: 'Ceasar Bautista', name: 'Introduction to Algorithms', department: 'CIS', section: '320', professor: 'Sanjeev Khanna'},
      ]
    },
    {
      name: 'Kyle Hardgrave', email:'nop@gmail.com'
    }
    {
      name: 'Nop Jia', email:'nop@gmail.com'
    }
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
