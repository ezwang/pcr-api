root = exports ? @

class app.views.SearchView extends Backbone.View
  # used to do keypress search
  template: app.templates.search_form
  tagName: 'div'
  id:'course-stats'
  options: ['name', 'department', 'professor', 'section', 'user']
  # events:

  render: ->
    @$el.html _.template @template,
        options: @options
    return @

  initialize: ->

