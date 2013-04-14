root = exports ? @

class app.views.UserNewView extends Backbone.View
  # used to do keypress search
  template: app.templates.user_new
  tagName: 'form'
  className: 'form-inline'
  id: 'user-new'

  events:
    "submit" : "add_one"

  render: ->
    @$el.html _.template @template
    return @

  initialize: ->

  add_one: (e) ->
    e.preventDefault()
    root.create_vent.trigger('user:create', {name: @$el.find('#add-name').val(), email: @$el.find('#add-email').val()})

