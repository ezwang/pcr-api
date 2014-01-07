class app.views.CourseView extends Backbone.View
  template: app.templates.course
  tagName: 'tr'

  selected: false
  selected_user: null
  events:
    "click": "assign_course"

  render: ->
    @$el.html _.template @template,
      {headers: @model.collection.headers, attributes: @model.attributes}

    if @model.get('user') == @selected_user?.id
      @$el.addClass('selected')
    else
      @$el.removeClass('selected')

    if @model.get('user')
      color = users.get(@model.get('user')).get('color')
      @$el.css('color', color)

    return @

  initialize: (options) ->
    # if there's a selection, set selected equal to true
    @selected_user = options.selected_user
    if options.selected_user
      @selected = @selected_user.id == @model.get("user")

  assign_course: (e) ->
    if @selected_user
      @selected = not @selected
      @select_course()
      @render()

  select_course: ->
    if not @selected
      # if current user and search user is the same, set the model attribute to undefined (unassign this guy)
      @model.save(user: null)
      @$el.css('color', 'black')

      @$el.removeClass('selected')
    else
      @model.save(user: @selected_user.id)
      @$el.addClass('selected')
      @$el.find('input[type=checkbox]').prop('checked', true)
