app.templates.user_table = """
          <table class="table table-striped" id="user-table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Email</th>
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
    <form class="form-inline">
      <input class="input-small" type="text" id="add-name"/>
      <input class="input-medium" type="email" id="add-email"/>
      <input type="submit" id="add-user" />
    </form>
    """

app.templates.course_sort_form = """

      <form class="form-inline">

        <label> Sort by: </label>
        <div class="btn-group">
          <button class="btn" id="sort-reviews">Review Count</button>
          <button class="btn">Middle</button>
          <button class="btn">Right</button>
        </div>

        <input type="text" class="input-medium" placeholder="Search Courses">
        <label class="checkbox">
          <input type="checkbox"> Show Assigned
        </label>

      </form>

"""

app.templates.course_table = """
  <table class="table table-striped" id="course-table">
    <thead>
      <tr>
        <th data-by='reviews' >?</th>
        <th data-by='name' >Course</th>
        <th data-by='department' >Section</th>
        <th data-by='professor' >Professor</th>
        <th data-by='section' >Section</th>
        <th data-by='user' >Editor</th>
        <th data-by='reviews' >Reviews</th>
      </tr>
    </thead>
    <tbody>
    </tbody>
  </table>
  """
app.templates.course = """
  <td><input type='checkbox'></td>
  <td><%= name %></td>
  <td><%= department %></td>
  <td><%= professor %></td>
  <td><%= section %></td>
  <td><%= user %></td>
  <td><%= reviews %></td>
  """

