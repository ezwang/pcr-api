root = exports ? @

class app.views.SearchView extends Backbone.View
  # used to do keypress search
  template: app.templates.search_form
  tagName: 'div'
  className:'course-search'

  events:
    "keyup #search": "search_by_name"

  render: ->
    @$el.html _.template @template
    return @

  initialize: ->

  search_by_name: (e) ->
    root.search_vent.trigger('search:by_name')
