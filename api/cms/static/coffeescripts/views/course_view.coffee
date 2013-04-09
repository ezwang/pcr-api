class app.views.CourseView extends Backbone.View
  template: app.templates.course
  tagName: 'tr'
  selected: false
  selected_user: undefined
  current_user: undefined
  events:
    "click": "assign_course"
  render: () ->
    @$el.html _.template @template,
      {headers: @model.collection.headers, attributes: @model.attributes}
    @$el.css('color', @model.get('user').get('color'))
    @select_course()
    return @

  initialize: (options) ->
    # if there's a selection, set selected equal to true
    # console.log 'hi'
    # console.log @model.get('user')
    @current_user = @model.get('user')
    @selected_user = options.selected_user
    if options.selected_user
      @selected = @selected_user == @model.attributes.user
    # check it

    @render()

  assign_course: (e) ->
    if @selected_user
      @selected = not @selected
    @select_course()
    @render()

  select_course: ->
    if not @selected
      # if current user and search user is the same, set the model attribute to undefined (unassign this guy)
      if @current_user.id == @selected_user
        @model.attributes.user = undefined
      else
        @model.attributes.user = @current_user
      @$el.removeClass('selected')
      return
    @model.attributes.user = @selected_user
    @$el.addClass('selected')
    @$el.find('input[type=checkbox]').prop('checked', true)
    @model.attributes.user = if @selected_user then @selected_user else @$el.find('td[data-category="user"]').html()

