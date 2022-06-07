## Using [Pipenv][]:

1. Set `GITUB_TOKEN` environment variable. The easiest way to do this is to create a file `.env` and in it put:

      ```
      GITHUB_TOKEN=...
      ```
      
2. Run the code using `pipenv`:

      ```
      pipenv run python ops-issues.py 'Sprint week 21 and 22 2022' -o issues.csv
      ```

[pipenv]: https://pipenv.pypa.io/en/latest/
