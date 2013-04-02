root = exports ? @
class app.views.UserView extends Backbone.View
  template: app.templates.user

  tagName: 'tr'

  render: () ->
    @$el.html _.template @template, @model.toJSON()
    @$el.css 'color', @model.get 'color'
    return @

  events:
    "click" : "select_user"

  select: ->
    @$el.addClass 'selected'


  select_user: (e) ->
    console.log('here')
    e.preventDefault()
    $("tr").removeClass 'selected'
    # $(e.target).parent("tr").addClass 'selected'
    @$el.addClass 'selected'
    user_id = @model.id
    console.log 'triggering select_user'
    console.log(user_id)
    root.match_vent.trigger "select_user", name:user_id



