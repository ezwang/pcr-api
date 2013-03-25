root = exports ? @

class app.views.ReviewTableView extends Backbone.View
  template: app.templates.review_table
  tagName: 'table'
  className:'review-table'

  render: (course_id) ->
    @$el.html _.template @template

    review_list = []
    @collection.filter_by_course(course_id).each (data, i) ->
      review_list.push new app.views.ReviewView(model: data).render()

    @$el.find('tbody').html _.pluck review_list, 'el'
    @

  initialize: ->
    @listenTo root.review_filter_vent, 'change_course', @filter_reviews

  filter_reviews: (data) ->
    console.log(data)
    @render(data.course_id)

