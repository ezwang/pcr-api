app.templates.user_table = """
          <table class="table table-striped" id="user-table">
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
    <td> <%= name %> </td>
    <td> <%= email %> </td>
  """

app.templates.user_new = """
      <input class="input-small" type="text" id="add-name"/>
      <input class="input-medium" type="email" id="add-email"/>
      <input type="submit" id="add-user" />
    """

app.templates.search_form = """

      <form class="form-inline">
        <select id="course-search-by">
          <% _.each(options, function(option) { console.log(options)%>
            <option><% option.capitalize() %></option>
          <% }) %>
        </select>

        <input id="course-search" type="text" class="input-medium" placeholder="Search Courses">
        <label class="checkbox">
          <input type="checkbox"> Show Assigned
        </label>

      </form>

"""

app.templates.course_table = """
  <table class="table table-striped" id="course-table">
    <thead>
      <tr>
        <th>?</th>
        <% _.each(headers, function(header) { %>
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
  <td><%= attributes[key] %></td>
  <% }) %>
  """

