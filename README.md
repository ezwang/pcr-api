## The API consists of three parts:

- api, a django app that responds to the queries
- scripts, a collection of import scripts that imports the PCR data from the old PCR site (and soon, ISC)
- wrappers, a set of of language wrappers for the API.  Currently, this means only an old PHP one.

# For deploying
- Make sure to alias the `STATIC_DIR` folder to `STATIC_ROOT` in your Apache config.
