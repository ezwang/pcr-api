root = exports ? @

class app.views.SearchView extends Backbone.View
  # used to do keypress search
  template: app.templates.search_form
  tagName: 'div'
  className:'course-search-form'
  options: ['name', 'department', 'professor', 'section', 'user']
  events:
    "keyup #course-search": "search"

  render: ->
    @$el.html _.template @template,
      {
        options: @options
      }
    return @

  initialize: ->

  search: (e) ->
    root.search_vent.trigger('course:search_by_name')
