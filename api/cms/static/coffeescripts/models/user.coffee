root = exports ? this
random_color = ->
  return '#' + (0x1000000 + (Math.random()) * 0xffffff).toString(16).substr(1, 6)
random_id = ->
  return Math.ceil(Math.random() * 10000)

class app.models.User extends Backbone.RelationalModel

  relations: [{
    type: Backbone.HasMany
    key: 'courses'
    relatedModel: 'app.models.Course'
    includeInJSON: ['color', '_id']
    collectionType: 'app.collections.Courses'
    # collectionKey: 'root.courses'
    reverseRelation: {
      key: 'user'
      type: Backbone.HasOne
      includeInJson: false
      # collectionKey: 'app.models.User'
    }
  }]

  defaults:
    id: random_id() # temporarily, from the python models
    name: 'Default Name',
    permission: '0',
    email: 'default@default.com',
    color: '#000000'

  initialize: ->
    @.set 'color', random_color()
    @.set 'id', random_id()
    _.map @defaults, (val, key) =>
      @set key, @defaults.key if not @get key

  activate: ->

  clear: ->
    @destroy()
    @view.remove()

app.models.User.setup() # required for coffeescript

class app.collections.Users extends Backbone.Collection
  model: app.models.User
  comparator: (model) ->
    model.get @by
  initialize: ->
    @by = "name"
    @headers =
      ['name','email']


