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


  temp_course_data = [
    {course_id: 1, user: 'Geoffrey Verdernikoff', name: 'Introduction to Computer Programming', department: 'CIS', section: '110', professor: 'Benedict Brown'},
    {course_id: 2, user: 'Geoffrey Verdernikoff', name: 'Programming Languages and Techniques I', department: 'CIS', section: '120', professor: 'Steve Zdancewic' },
    {course_id: 3, user: 'Geoffrey Verdernikoff', name: 'Data Structures and Algorithms with Java', department: 'CIS', section: '121', professor: 'Val Tannen' },
    {course_id: 4, user: 'Geoffrey Vedernikoff', name: 'Computer Organization and Design', department: 'CIS', section: '371', professor: 'Milo K. Martin'},
    {course_id: 5, user: 'David Xu', name: 'Introduction to Computer Architecture', department: 'CIS', section: '240', professor: 'CJ Taylor'},
    {course_id: 6, user: 'David Xu', name: 'Operating Systems', department: 'CIS', section: '380', professor: 'Boon Thau Loo'},
    {course_id: 7, user: 'Ceasar Bautista', name: 'Automata, Computability, and Complexity', department: 'CIS', section: '262', professor: 'Aaron Roth'},
    {course_id: 8, user: 'Ceasar Bautista', name: 'Introduction to Algorithms', department: 'CIS', section: '320', professor: 'Sanjeev Khanna'},

  ]

  temp_data = [
    {
      course: 1,
      review: "this course wasn't so great"
    },
    {
      course: 1,
      review: "this course was awesome"
    },
    {
      course: 3,
      review: "i would rate this course a 3"
    }
  ]


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

