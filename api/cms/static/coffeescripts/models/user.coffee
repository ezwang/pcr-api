class app.models.User extends Backbone.Model
  defaults:
    name: 'Default Name',
    permission: '0',
    email: 'default@default.com',

  initialize: ->
    _.map @defaults, (val, key) =>
      @set key, @defaults.key if not @get key

  activate: ->

  clear: ->
    @destroy()
    @view.remove()

class app.collections.Users extends Backbone.Collection
  model: app.models.User






