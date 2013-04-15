root = exports ? @

class app.views.StatView extends Backbone.View
  # used to do keypress search
  template: app.templates.stat_view
  tagName: 'div'
  className:'course-search-form'
  options: ['name', 'department', 'professor', 'section', 'user']
  events:
    "keyup #course-search": "search"

  render: ->
    @$el.html _.template @template
    return @

  initialize: ->

  search: (e) ->
    root.search_vent.trigger 'course:search_by', search_type: $('select option:selected').html()
