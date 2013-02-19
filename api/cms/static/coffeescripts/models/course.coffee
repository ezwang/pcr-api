class app.models.Course extends Backbone.Model
  defaults:
    user: 11235424,  # id
    name: 'Default Course Name'
    department: 'default department',
    professor: 'professory dude',
    section: 's139',

  initialize: ->
    @set 'reviews', Math.random() * 100

  activate: ->

  clear: ->
    @destroy()
    @view.remove()

  matches: (search_query) ->
    @get('name').indexOf(search_query) != -1

class app.collections.Courses extends Backbone.Collection
  model: app.models.Course
  comparator: (model) ->
    model.get @by
  initialize: ->
    @by = "name"
  search_by_name: (search_term='') ->
    return _(@filter (course) =>
      course.matches search_term)


