root = exports ? @
class app.views.UserView extends Backbone.View
  template: app.templates.user

  tagName: 'tr'

  render: () ->
    console.log @model.toJSON()
    @$el.html _.template @template,
      {headers: @model.collection.headers, attributes: @model.attributes}
    @$el.css 'color', @model.get 'color'
    return @

  events:
    "click" : "select_user"

  select: ->
    @$el.addClass 'selected'


  select_user: (e) ->
    e.preventDefault()
    $("tr").removeClass 'selected'
    # $(e.target).parent("tr").addClass 'selected'
    @$el.addClass 'selected'
    user_model = @model
    root.match_vent.trigger "select_user", user:user_model



