root = exports ? @
class app.views.UserListView extends Backbone.View
  #  template: app.templates.right
  # el: $('#editor-table')
  template: app.templates.user_table
  tagName: 'div'
  className: 'user-list'

  render: ->
    @$el.html _.template @template,
      {headers: @collection.headers, selected: @collection.by}
    user_views = []
    @collection.each (user) ->
      user_view = new app.views.UserView(model: user)
      user_views.push user_view.render()
    user_view_els = _.pluck user_views, 'el'
    @$el.find('tbody').html user_view_els
    return @

  events:
    "click th": "sort_reviews"
    "click tr" : "select_user"

  initialize: ->
    @listenTo @collection, 'add', @render
    @listenTo @collection, 'sort', @render
    @listenTo root.create_vent, 'user:create', @addOne

  # event given by user_new_view
  addOne: (data) ->
    user = new app.models.User
      name: data.name
      email: data.email
    @collection.add user
    return @

  sort_reviews: (e) ->
    e.preventDefault()
    @collection.by = $(e.target).attr 'data-by'
    @collection.sort()

  select_user: (e) ->
    e.preventDefault()
    $("tr").removeClass 'selected'
    $(e.target).parent("tr").addClass 'selected'
    user_name = $("tr.selected td:first").text().trim()
    root.match_vent.trigger "select_user", name:user_name


