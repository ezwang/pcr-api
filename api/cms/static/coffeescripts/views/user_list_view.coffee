root = exports ? this

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

  initialize: ->
    @listenTo @collection, 'add', @render
    @listenTo @collection, 'sort', @render
    @listenTo root.search_vent, 'user:add', @add_one

  add_one: () ->
    new_name = $('#add-name').val()
    new_email = $('#add-email').val()
    if not (new_name and new_email) then return
    user = new app.models.User
      name: new_name
      email: new_email
    @collection.add user
    return @

  sort_reviews: (e) ->
    e.preventDefault()
    @collection.by = $(e.target).attr 'data-by'
    console.log(@collection.by)
    @collection.sort()

