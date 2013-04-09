root = exports ? @

class app.views.ReviewView extends Backbone.View
  template: app.templates.review
  tagName: 'tr'
  className:'review'

  render: ->
    # @model
    @$el.html _.template(@template,
      { course: @model.attributes.course
      review_text: @model.attributes.review } )
    return @

  initialize: ->

