class app.views.RightView extends Backbone.View
  #  template: app.templates.right
  el: $('#editor-table')

  render: () ->

  events:
    "click" : "addOne"

  initialize: () ->


  addOne: () ->
    view = new app.views.UserView({name: Math.random(200) + 'hi'})
    @el.append(view.render().el)




