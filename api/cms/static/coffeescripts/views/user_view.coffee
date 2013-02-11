class app.views.UserView extends Backbone.View
  template: app.templates.user
  tagName: 'tr'
  events: ""
  render: () ->
    @$el.html _.template @template, @model.toJSON()
    return @


