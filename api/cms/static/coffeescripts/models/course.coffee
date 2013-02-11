class app.models.Course extends Backbone.Model
  defaults:
    user: 11235424,  # id
    name: 'Default Course Name'
    department: 'default department',
    professor: 'professory dude',
    section: 's139',

  initialize: ->
    _.map @defaults, (val, key) =>
      @set key, @defaults.key if not @get key

  activate: ->

  clear: ->
    @destroy()
    @view.remove()

class app.collections.Courses extends Backbone.Collection
  model: app.models.Course
