# Coffeescript yay!
root = exports ? this
root.app =
  models: {}
  collections: {}
  views: {}
  templates: {}

console.log 'hi'

$ ->
  root.users = new app.collections.Users([
    {name: 'geoff'},
    {name: 'david'},
    {name: 'ceasar'},
    {name: 'nop'}
  ])

  root.courses = new app.collections.Courses([
    {user: 'geoff'},
    {user: 'david'},
    {user: 'ceasar'},
    {user: 'nop'}
  ])

  root.Right = new app.views.RightView(collection: users)
  root.CourseList = new app.views.CourseListView(collection: courses)
  $("#users-table-wrapper").html Right.render().el
  $("#courses-table-wrapper").html CourseList.render().el
