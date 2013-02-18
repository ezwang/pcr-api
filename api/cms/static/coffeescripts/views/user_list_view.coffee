class app.views.UserListView extends Backbone.View
  #  template: app.templates.right
  # el: $('#editor-table')
  template: app.templates.user_table
  tagName: 'div'
  className: 'user-list'

  render: ->
    @$el.html _.template @template
    user_views = []
    @collection.each (user) ->
      user_view = new app.views.UserView(model: user)
      user_views.push user_view.render()
    user_view_els = _.pluck user_views, 'el'
    @$el.find('tbody').html user_view_els
    @$el.prepend app.templates.user_new
    return @

  events:
    "submit form" : "addOne"
    "click th": "sort_reviews"

  initialize: ->
    @listenTo @collection, 'add', @render
    @listenTo @collection, 'sort', @render

  addOne: (e) ->
    e.preventDefault()
    user = new app.models.User
      name: @$el.find('#add-name').val()
      email: @$el.find('#add-email').val()
    # user.save()
    @collection.add user
    return @

  sort_reviews: (e) ->
    e.preventDefault()
    @collection.by = $(e.target).attr 'data-by'
    console.log(@collection.by)
    @collection.sort()

