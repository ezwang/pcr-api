class indow.User extends Backbone.Model

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

class Users extends Backbone.Collection
  model: User






