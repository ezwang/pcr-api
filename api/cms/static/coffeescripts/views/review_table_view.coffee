root = exports ? @

class app.views.ReviewTableView extends Backbone.View
  template: app.templates.review_table
  tagName: 'table'
  className:'review-table'

  render: ->
    @$el.html _.template @template

    review_list = []
    @collection.each (data, i) ->
      review_list.push new app.views.ReviewView(model: data).render()

    @$el.find('tbody').html _.pluck review_list, 'el'
    @

  initialize: ->

