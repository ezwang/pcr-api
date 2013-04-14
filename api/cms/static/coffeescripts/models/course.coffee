root = exports ? this

root.app = if root.app then root.app else
  models: {}
  collections: {}
  views: {}
  templates: {}

class root.app.models.Course extends Backbone.RelationalModel

  defaults: ->
    user: undefined # model
    course_id: 'Default Course Id'
    name: 'Default Course Name'
    department: 'default department'
    professor: 'professory dude'
    section: '110'

  initialize: ->
    @set 'reviews', Math.round(Math.random() * 100)
    console.log('hi there')
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
    @headers =
      ['name','department', 'professor', 'section', 'user', 'reviews']
  # sort_by_type

  search_by_type: (search_term='', search_type='name') ->
    return (@filter (course) =>
      course.matches_at(search_term, search_type) != -1)

    # x = _(_.difference (@filter (course) =>
    #   course.matches_at(search_term) != -1), data)
    # console.log @filter (course) =>
    #   course.matches_at(search_term) != -1

    # window.newww = @filter (course) =>
    #   course.matches_at(search_term) != -1

    # console.log 'hi'
    # console.log data
    # window.olddd = data
    # return x


