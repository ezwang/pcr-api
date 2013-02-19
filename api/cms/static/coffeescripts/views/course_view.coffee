class app.views.CourseView extends Backbone.View
  template: app.templates.course
  tagName: 'tr'
  events: ""
  render: () ->
    @$el.html _.template @template,
      {headers: @model.collection.headers, attributes: @model.attributes}
    return @


