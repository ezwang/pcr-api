class app.views.CourseView extends Backbone.View
  selected: false
  template: app.templates.course
  tagName: 'tr'
  events: ""
  render: () ->
    @$el.html _.template @template,
      {headers: @model.collection.headers, attributes: @model.attributes}
    if @selected
      @$el.addClass('selected')
      @$el.find('input[type=checkbox]').prop('checked', true)
    return @

  initialize: (options) ->
    @selected = options.is_selected
      # check it

    @render




