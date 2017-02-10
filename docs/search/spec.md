
# PennCourseReview Search Endpoint

Author: @Ceasar

# Introduction

The PennCourseReview search endpoint is a service that enable API developers to search for courses, instructors, and departments.

## Scenarios

In designing products, it helps to imagine a few real life stories of how actual (stereotypical) people would use them. We'll look at two scenarios.

### Scenario 1

Consider that we (Labs) make use of search for the autocomplete feature on PennCourseReview.

When a user types in the search box on the PennCourseReview front-end, the server sends a request to `/autocomplete_data.json/(.*)` with the user's query. That route then hits our API and returns a JSON document representing courses, instructors, and departments relevant to the query.

Moving the dataset endpoint to the server has the immediate advantage of reducing the number of requests our server makes and achieves better separation of concerns.

### Scenario 2

Consider a developer who wants to plot course review data for each department on separate graphs, like [CourseGrapher][4].

On such a site it may be desirable to, in addition to enable users to locate a specific course on a graph, enable users to search directly for a course of interest.

## Non-Goals

This version will neither commit to nor describe any relevance metrics for responses. The ordering of results is subject to change at will.

# Overview

Returns a mixed collection of relevant resources (courses, instructors, departments) matching a specified query.

## Resource Information

<table>
    <tbody>
        <tr>
            <td>URL</td>
            <td><code>http://api.penncoursereview.com/1.1/search</code></td>
        </tr>
        <tr>
            <td>HTTP Methods</td>
            <td>GET</td>
        </tr>
        <tr>
            <td>Response Formats</td>
            <td>json</td>
        </tr>
        <tr>
            <td>Rate Limited?</td>
            <td></td>
        </tr>
        <tr>
            <td>Request per rate limit window</td>
            <td></td>
        </tr>
        <tr>
            <td>Authentication</td>
            <td></td>
        </tr>
        <tr>
            <td>API Version</td>
            <td>v1.1</td>
        </tr>
    </tbody>
</table>

<strong>Open Issue:</strong> Need to decide if the endpoint will be rate-limited.

<strong>Open Issue:</strong> Need to decide if the endpoint requires authentication.

## Request Information

### Parameters

<table>
    <thead>
        <tr>
            <th>Name</th>
            <th>Default</th>
            <th>Description</th>
            <th>Example Values</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>q</td>
            <td><tt>Required</tt></td>
            <td>A search query.</td>
            <td><tt>econ</tt>, <tt>spiegel</tt></td>
        </tr>
        <tr>
            <td>result_type</td>
            <td>mixed</td>
            <td>
                <p>The type of results to fetch. Valid values include:</p>
                <br>
                <tt>mixed</tt>: Include courses, instructors, and departments.
                <br>
                <tt>courses</tt>: Include courses.
                <br>
                <tt>instructors</tt>: Include instructors.
                <br>
                <tt>departments</tt>: Include departments.
            </td>
            <td><tt>departments</tt>, <tt>mixed</tt></td>
        </tr>
        <tr>
            <td>count</td>
            <td>15</td>
            <td>The number of results to return per page.</td>
            <td><tt>11</tt>, <tt>7</tt></td>
        </tr>
        <tr>
            <td>page</td>
            <td>0</td>
            <td>The page to fetch results.</td>
            <td><tt>2</tt>, <tt>5</tt></td>
        </tr>
    </tbody>
</table>

### Example

GET: `http://api.penncoursereview.com/1.1/search?q=econ&result_type=mixed&count=3`

## Response Information

A response returns multiple datasets.

Responses are compatible with [typeahead.js][1].

### Example

<pre>
{
    "courses": [
        {
            "value": "ECON 001",
            "tokens": [
              "econ001",
              "econ-001",
              "econ",
              "001",
              "intro",
              "to",
              "micro"
            ],
            "path": "/courses/ECON-001",
            "name": "INTRO TO MICRO",
            "description": "Discussion of special research topics"
        }, {
            "value": "CIS 120",
            "tokens": [
              "cis120",
              "cis-120",
              "cis",
              "120",
              "prog",
              "lang",
              "&",
              "tech",
              "i"
            ],
            "path": "/courses/CIS-120",
            "name": "PROG LANG & TECH I",
            "description": "Introduction to the fundamental concepts of programming."
        }
    ],
    "instructors": [
        {
            "value": "Uriel Spiegel",
            "tokens": [
                "uriel",
                "spiegel",
                "econ"
            ],
            "path": "/instructors/1360-URIEL-SPIEGEL",
            "departments": ["ECON"]
        }, {
            "value": "Carita C. Huang",
            "tokens": [
                "carita",
                "c.",
                "huang",
                "hssc",
                "hsoc"
            ],
            "path": "/instructors/2182-CARITA-C--HUANG",
            "departments": ["HSSC", "HSOC"]
        }
    ],
    "departments": [
        {
            "value": "Economics",
            "tokens": [
                "econ",
                "economics"
            ],
            "path": "/depts/ECON",
            "id": "ECON"
        }, {
            "value": "Computer and Information Science",
            "tokens": [
                "cis",
                "computer",
                "and",
                "information",
                "science"
            ],
            "path": "/depts/CIS",
            "id": "CIS"
        }
    ]
}
</pre>

### Datum

A datum is an individual unit of a dataset.

The canonical form of a datum is an object with a `value` property, `tokens` property, and `path` property.

- `value` is a string that represents the underlying value of the datum.
- `token` is an array of single-word strings that aids in matching a datum with a given query.
- `path` is a string that represents the path to the full object.

<table>
    <thead>
        <tr>
            <td>Type</td>
            <td>Example</td>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>Course</td>
            <td>
<pre>
{
    "value": "ECON 001",
    "tokens": [
      "econ001",
      "econ-001",
      "econ",
      "001",
      "intro",
      "to",
      "micro"
    ],
    "path": "/courses/ECON-001",
    "name": "INTRO TO MICRO",
    "description": "Discussion of special research topics"
}
</pre>
            </td>
        </tr>
        <tr>
            <td>Instructor</td>
            <td>
<pre>
{
    "value": "Uriel Spiegel",
    "tokens": [
        "uriel",
        "spiegel"
    ],
    "path": "/instructors/1360-URIEL-SPIEGEL",
    "departments": [
        "ECON"
    ]
}
</pre>
            </td>
        </tr>
        <tr>
            <td>Department</td>
            <td>
<pre>
{
    "value": "Economics",
    "tokens": [
        "economics"
    ],
    "path": "/depts/ECON",
    "id": "ECON"
}
</pre>
            </td>
        </tr>
    </tbody>
</table>

[1]: http://twitter.github.io/typeahead.js/ "typeahead.js"
[2]: https://github.com/pennappslabs/pcr/blob/master/apps/searchbar/views.py
[3]: https://github.com/pennappslabs/pcr/blob/master/media/front-end/coffee/searchbox.coffee
[4]: http://coursegrapher.appspot.com/
