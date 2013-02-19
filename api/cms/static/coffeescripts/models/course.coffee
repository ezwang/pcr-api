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

  matches_at: (search_query) ->
    @get('name').indexOf search_query

class app.collections.Courses extends Backbone.Collection
  model: app.models.Course
  comparator: (model) ->
    model.get @by
  initialize: ->
    @by = "name"
    @headers =
      ['name','department', 'professor', 'section', 'user', 'reviews']
  search_by_name: (search_term='') ->
    return _(@filter (course) =>
      course.matches_at(search_term) != -1)


