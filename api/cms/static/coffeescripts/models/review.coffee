class app.models.Review extends Backbone.Model
  defaults:
    course: 'default_course_id',
    review: 'this is the default review text'

  initialize: ->
    _.map @defaults, (val, key) =>
      @set key, @defaults.key if not @get key

  clear: ->
    @destroy()
    @view.remove()

class app.collections.Reviews extends Backbone.Collection
  model: app.models.Review




