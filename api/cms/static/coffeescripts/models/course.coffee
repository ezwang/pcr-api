root = exports ? this

root.app = if root.app then root.app else
  models: {}
  collections: {}
  views: {}
  templates: {}


course_attrs =
    course_id: 'Default Course Id'
    department: 'default department'
    section: '110'
    name: 'Default Course Name'
    user: undefined  # model
    professor: 'professory dude'
    status: 'In Progress'  # in progress, Finished, Approved

class root.app.models.Course extends Backbone.RelationalModel

  STATUSES: ['In Progress', 'Finished', 'Approved']

  defaults: ->
    course_attrs

  initialize: ->
    @set 'reviews', Math.round(Math.random() * 100)
    if root.courses
      root.courses.add(@) # add it to the root collection

  activate: ->

  clear: ->
    @destroy()
    @view.remove()

  matches_at: (search_query, search_type) ->
    if search_type == 'user'
      console.log('searching by user')
      return @get(search_type).get('name').indexOf search_query
    else return @get(search_type).indexOf search_query

root.app.models.Course.setup() # required for coffeescript

class root.app.collections.Courses extends Backbone.Collection
  model: root.app.models.Course
  comparator: (model) ->
    sort_by = model.get @by
    if @by == 'user' # return custom comparator
      sort_by = model.get(@by).id
    else return sort_by
  initialize: ->
    @by = "name"

    # set it to all keys except those that contain "id"
    @headers = _.filter(_.keys(course_attrs), (input) ->
      input.indexOf('id') == -1
    )

  # sort_by_type
  search_by_type: (search_term='', search_type='name') ->
    return (@filter (course) =>
      course.matches_at(search_term, search_type) != -1)
