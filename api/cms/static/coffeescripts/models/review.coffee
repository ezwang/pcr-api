class app.models.Review extends Backbone.Model
  defaults:
    # name: 'Default Name',
    # permission: '0',
    # email: 'default@default.com',
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
  # comparator: (model) ->
  #   model.get @by
  # initialize: ->
  #   @by = "name"
  #   @headers =
  #     ['name','email']





