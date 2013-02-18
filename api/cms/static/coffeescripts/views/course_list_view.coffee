class app.views.CourseListView extends Backbone.View
  template: app.templates.course_table
  tagName: 'div'
  className:'course-list'

  events:
    "click th": "sort_reviews"
    "submit form": "search_by_name"

  render: (search_query) ->
    @$el.html _.template @template
    course_list = []
    console.log search_query
    # if a search query exists, filter the collection results
    render_data = if search_query then \
      @collection.search_by_name(search_query) else @collection.models
    _.each render_data, (course) ->
      course_view = new app.views.CourseView(model: course)
      course_list.push course_view.render()
    course_list_els = _.pluck course_list, 'el'
    @$el.find('tbody').html course_list_els
    @$el.prepend app.templates.course_sort_form
    return @

  initialize: ->
    @listenTo @collection, 'add', @render
    @listenTo @collection, 'sort', @render

  sort_reviews: (e) ->
    e.preventDefault()
    @collection.by = $(e.target).attr 'data-by'
    @collection.sort()

  search_by_name: (e) ->
    e.preventDefault()
    @render $('#search').val()
    # return focus
