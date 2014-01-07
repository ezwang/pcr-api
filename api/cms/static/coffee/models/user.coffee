root = exports ? this
random_color = ->
  return '#' + (0x1000000 + (Math.random()) * 0xffffff).toString(16).substr(1, 6)

class app.models.User extends Backbone.Model
  urlRoot: '/cms/users/'
  defaults:
    id: _.uniqueId()
    name: 'Default Name',
    permission: '0',
    email: 'default@default.com',
    color: '#000000',
    reviews: '0',
    profile: '/user/<%= id %>',
    user_type: 'WR',
    specialty: 'Wharton'

  initialize: ->
    @set 'color', random_color()
    _.map @defaults, (val, key) =>
      @set key, @defaults.key if not @get key
  clear: ->
    @destroy()
    @view.remove()

# app.models.User.setup() # required for coffeescript

class app.collections.Users extends Backbone.Collection
  model: app.models.User
  comparator: (model) ->
    model.get @by
  initialize: ->
    @by = "name"
    a = new @model

    @headers =
      _.filter(_.keys(a.attributes), (item)->
        item != 'id' and item != 'color' and item != 'permission' and item != 'courses'
      )
      # ['name','email', 'reviews', 'profile', 'specialty']
