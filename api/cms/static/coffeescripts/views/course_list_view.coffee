root = exports ? @

class app.views.CourseListView extends Backbone.View
  template: app.templates.course_table
  tagName: 'div'
  className:'course-list'
  selectedUser: undefined

  events:
    "click th": "sort_reviews"

  # data resulting from user selection
  render: (search_data = {}) ->
    console.log search_data
    data = if @selectedUser then @collection.where({user:@selectedUser}) else []
    console.log(@collection.headers)
    console.log(data)

    @$el.html _.template @template,
      {headers: @collection.headers, selected: @collection.by}

    course_list = []

    # if a search query exists, filter the collection results
    # extra class to be added (selected)
    push_courses = (course) =>
      course_view = new app.views.CourseView(model: course, selected_user: @selectedUser)
      course_list.push course_view.render()

    search_query = $('#course-search').val()
    search_results = @collection.search_by_type(search_query, search_data.search_type)
    # everything searched in the data
    _(_.intersection(data, search_results)).each (item) -> push_courses item
    # everything that's left
    _(_.difference(search_results, data)).each (item) -> push_courses item

    # _(data).each push_courses
    # @collection.search_by_name(search_query, data).each push_courses
    # _(_.difference(@collection.models, data)).each push_courses
    #search_query = $('#course-search').val()
    #@collection.search_by_name(search_query).each push_courses

    course_list_els = _.pluck course_list, 'el'
    @$el.find('tbody').html course_list_els
    return @

  initialize: ->
    @listenTo @collection, 'add', @render
    @listenTo @collection, 'sort', @render
    @listenTo root.match_vent, 'select_user', @filter_by_user
    @listenTo root.search_vent, 'course:search_by', @render

  sort_reviews: (e) ->
    e.preventDefault()
    @collection.by = $(e.target).attr 'data-by'
    @collection.sort()

  filter_by_user: (data) ->
    @selectedUser = data.user
    # console.log('hier')
    # console.log(@selectedUser)
    @render()

