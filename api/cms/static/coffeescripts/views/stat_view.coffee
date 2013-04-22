root = exports ? @

class app.views.StatUserView extends Backbone.View

class app.views.StatCourseView extends Backbone.View

class app.views.StatSummaryView extends Backbone.View

class app.views.StatView extends Backbone.View
  # used to do keypress search
  template: app.templates.stat_view
  tagName: 'div'
  id: 'stats'
  options: ['name', 'department', 'professor', 'section', 'user']
  expanded: false
  auto_height: '0px'
  contract_height: '20px'
  events:
    "keyup #course-search": "search"
    "click" : "toggle"

  render: ->

    course_categories = _.unique(root.courses.pluck('category'))
    course_statuses = _.unique(root.courses.pluck('status'))
    user_specialties = _.unique(root.users.pluck('specialty'))
    @course_stats = {
      statuses: {}
      categories: {}
    }
    @user_stats = {}
    _.each course_categories, (item) =>
      @course_stats.categories[item] = root.courses.where({category: item}).length
    _.each course_statuses, (item) =>
      @course_stats.statuses[item] = root.courses.where({status: item}).length
    _.each user_specialties, (item) =>
      @user_stats[item] = root.users.where({specialty: item}).length
    @user_stats['Total'] = root.users.length
    console.log('here')
    # console.log(@course_stats)

    @statistics = {

    }

    @$el.html _.template @template,
      course_stats: @course_stats
      user_stats: @user_stats

    return @

  initialize: ->
    @$el.height(@contract_height)

  search: (e) ->
    root.search_vent.trigger 'course:search_by', search_type: $('select option:selected').html()

  toggle: ->
    if parseInt(@auto_height) == 0
      @$el.height('auto')
      @auto_height = @$el.height()
      @$el.height(@contract_height)
    if not @expanded
      @$el.find('i').removeClass('icon-chevron-down').addClass('icon-chevron-up')
      @$el.stop().animate height: @auto_height, 200, ->
    else
      @$el.find('i').removeClass('icon-chevron-up').addClass('icon-chevron-down')
      @$el.stop().animate height: @contract_height, 200, ->
    @expanded = not @expanded
