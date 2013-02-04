# Coffeescript yay!
root = exports ? this
root.app =
  models: {}
  collections: {}
  views: {}
  templates: {}

console.log 'hi'

$ ->
  window.Right = new app.views.RightView()

