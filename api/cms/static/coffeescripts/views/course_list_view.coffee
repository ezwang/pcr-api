class app.views.CourseListView extends Backbone.View
  template: app.templates.course_table
  tagName: 'table'
  className:'table table-striped'
  id: 'course-table'

  render: ->
    @$el.html _.template @template
    course_list = []
    @collection.each (course) ->
      course_view = new app.views.CourseView(model: course)
      course_list.push course_view.render()
    course_list_els = _.pluck course_list, 'el'
    @$el.find('tbody').html course_list_els
    return @

  events: ''

  initialize: ->
    @listenTo @collection, 'add', @render


