root = exports ? this

class app.views.CourseListView extends Backbone.View
  template: app.templates.course_table
  tagName: 'div'
  className:'course-list'

  events:
    "click th": "sort_reviews"

  render: ->
    @$el.html _.template @template,
      {headers: @collection.headers, selected: @collection.by}

    course_list = []
    # if a search query exists, filter the collection results
    push_courses = (course) ->
      course_view = new app.views.CourseView(model: course)
      course_list.push course_view.render()

    search_query = $('#search').val()
    @collection.search_by_name(search_query).each push_courses

    course_list_els = _.pluck course_list, 'el'
    @$el.find('tbody').html course_list_els
    return @

  initialize: ->
    @listenTo @collection, 'add', @render
    @listenTo @collection, 'sort', @render
    @listenTo root.search_vent, 'search:by_name', @render

  sort_reviews: (e) ->
    e.preventDefault()
    @collection.by = $(e.target).attr 'data-by'
    @collection.sort()

