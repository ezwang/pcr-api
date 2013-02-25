class app.views.UserView extends Backbone.View
  template: app.templates.user

  tagName: 'tr'

  render: () ->
    @$el.html _.template @template, @model.toJSON()
    return @

#  events: 'click' : 'select'

  select: ->
    @$el.addClass 'selected'



