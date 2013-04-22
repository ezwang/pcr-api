root = exports ? @

class app.views.ReviewFilterView extends Backbone.View
  template: app.templates.review_filter
  tagName: 'div'
  className:'review-summary'

  events:
    'change #review_filter' : 'course_filter'

  course_filter: ->
    course = $('#review_filter option:selected').data('id')
    root.review_filter_vent.trigger 'change_course', course_id: course

  render: ->
    @$el.html _.template @template, collection: @collection
    return @

  initialize: ->

