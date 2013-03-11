class app.models.Course extends Backbone.Model

  defaults: ->
    user: 11235424  # id
    name: 'Default Course Name'
    department: 'default department'
    professor: 'professory dude'
    section: 's139'

  initialize: ->
    @set 'reviews', Math.random() * 100

  activate: ->

  clear: ->
    @destroy()
    @view.remove()

  matches_at: (search_query, search_type) ->
    console.log search_type
    @get(search_type).indexOf search_query

class app.collections.Courses extends Backbone.Collection
  model: app.models.Course
  comparator: (model) ->
    model.get @by
  initialize: ->
    @by = "name"
    @headers =
      ['name','department', 'professor', 'section', 'user', 'reviews']

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


