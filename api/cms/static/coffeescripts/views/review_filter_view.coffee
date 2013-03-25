root = exports ? @

class app.views.ReviewFilterView extends Backbone.View
  template: app.templates.review_filter
  tagName: 'div'
  className:'review-summary'
  render: ->
    @$el.html _.template @template
    return @

  initialize: ->

