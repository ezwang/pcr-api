app.templates.user_table = """
            <thead>
              <tr>
                <th>Name</th>
                <th>Email</th>
              </tr>
            </thead>
            <tbody id="editor-table">
            </tbody>

  """

app.templates.user = """
    <td> <%= name %> </td>
    <td> <%= email %> </td>
  """

app.templates.course_table = """
  <thead>
    <tr>
      <th>?</th>
      <th>Course</th>
      <th>Section</th>
      <th>Text</th>
      <th>Editor</th>
      <th>Status</th>
    </tr>
  </thead>
  <tbody>
  </tbody>
  """
app.templates.course = """
  <td><input type='checkbox'></td>
  <td><%= name %></td>
  <td><%= department %></td>
  <td><%= professor %></td>
  <td><%= section %></td>
  <td><%= user %></td>
  """

