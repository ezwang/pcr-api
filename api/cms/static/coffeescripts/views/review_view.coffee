root = exports ? @

class app.views.ReviewView extends Backbone.View
  template: app.templates.review
  tagName: 'tr'
  className:'review'

  render: ->
    @$el.html _.template @template
    return @

  initialize: ->

