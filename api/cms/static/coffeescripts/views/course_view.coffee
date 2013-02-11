class app.views.CourseView extends Backbone.View
  template: app.templates.course
  tagName: 'tr'
  events: ""
  render: () ->
    @$el.html _.template @template, @model.toJSON()
    return @


