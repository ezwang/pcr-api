class app.views.RightView extends Backbone.View
  #  template: app.templates.right
  # el: $('#editor-table')
  template: app.templates.user_table
  tagName: 'table'
  className: 'table table-striped'
  id: 'user-table'

  render: ->
    @$el.html _.template @template
    user_views = []
    @collection.each (user) ->
      user_view = new app.views.UserView(model: user)
      user_views.push user_view.render()
    user_view_els = _.pluck user_views, 'el'
    @$el.find('tbody').html user_view_els
    return @

  events:
    "click" : "addOne"

  initialize: ->
    @listenTo @collection, 'add', @render

  addOne: (user) ->
    view = new app.views.UserView({model: user})
    @$el.html(view.render().el)
    return @

