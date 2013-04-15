root = exports ? this
root.app = if root.app then root.app else
  models: {}
  collections: {}
  views: {}
  templates: {}


app.templates.user_table = """
          <table class="table" id="user-table">
            <thead>
              <tr>
                <% _.each(headers, function(header) { %>
                <th <% if (selected === header) { %>class='selected'<% } %> data-by='<%= header %>'><%= header.capitalize() %></th>
                <% }) %>
              </tr>
            </thead>
            <tbody id="editor-table">
            </tbody>
          </table>
  """

app.templates.user = """

    <% _.each(headers, function(key) { %>

    <td data-category='<%= key %>'>
      <% // if equal to user, read it from the model %>
      <% if (key === 'profile' && attributes[key] !== undefined) { %>

        <button onclick="window.location = '<%= attributes[key] %>'"> <i class="icon-share-alt"></i> </button>
      <% } else %>
      <%= attributes[key] %>
    </td>
    <% }) %>

  """

app.templates.user_new = """
      <input class="input-small" type="text" id="add-name"/>
      <input class="input-medium" type="email" id="add-email"/>
      <input type="submit" id="add-user" />
    """

app.templates.search_form = """

      <form class="form-inline">
        <select id="course-search-by">
          <% _.each(options, function(option) { %>
            <option><%= option %></option>
          <% }) %>
        </select>

        <input id="course-search" type="text" class="input-medium" placeholder="Search Courses">
        <label class="checkbox">
          <input type="checkbox"> Show Assigned
        </label>

      </form>

"""

app.templates.course_table = """
  <table class="table " id="course-table">
    <thead>
      <tr>
        <th>?</th>
        <% _.each(headers, function(header) {  %>
        <th <% if (selected === header) { %>class='selected'<% } %> data-by='<%= header %>'><%= header.capitalize() %></th>
        <% }) %>
      </tr>
    </thead>
    <tbody>
    </tbody>
  </table>
  """
app.templates.course = """
  <td><input type='checkbox'></td>
  <% _.each(headers, function(key) { %>

  <td data-category='<%= key %>'>
    <% // if equal to user, read it from the model %>
    <% if (key === 'user' && attributes[key] !== undefined) { %>
    <%= attributes[key].get('name') %>
    <% } else %>
    <%= attributes[key] %>
  </td>
  <% }) %>
  """



##########################################
# Edit View
##########################################

app.templates.review = """
  <p><%= review_text %> </p>
  """


app.templates.review_table = """
  <table class="table" id="review-table">
    <tbody>
    </tbody>
  </table>
  """

app.templates.review_summary = """
  <textarea id="review-summary-text"></textarea>
  <button class="btn" type="button">Submit</button>
  <button class="btn" type="button">Save</button>
  <button class="btn" type="button">Approve</button>
  """

app.templates.review_filter = """
  <select id="review_filter">
    <option data-id="">
      All Reviews
    </option>
    <% collection.each(function(model) { %>
      <option data-id="<%= model.attributes.course_id %>">
        <%= model.attributes.department + ' ' + model.attributes.section + ' ' + model.attributes.name %>
      </option>
    <% }) %>
  </select>
  """
