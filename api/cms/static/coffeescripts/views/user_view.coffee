class app.views.UserView extends Backbone.View
  template: app.templates.user
  events: ""
  render: () ->
    @$el.html _.template @template  @model.toJSON()


