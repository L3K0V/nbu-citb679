# nbu-citb679

## Getting started

Create virtual environment via:

```shell
$ python3 -m venv env
```

activate it

```shell
$ source env/bin/activate
```

and install all requirements

```shell

$ pip install -r requirements.txt
```

### Search for materials

```
py edu_graph.py search --help
Usage: edu_graph search [OPTIONS] FILENAME

  Search within the graph for a materials based on a set of criterias

Options:
  -c, --concept TEXT        The concept to learn
  -e, --education TEXT      The education frield the material are focused for.
                            (eg. mathematicians, musicians, all)
  -l, --lang TEXT           The programming language which materials are for
  -t, --topic TEXT          The topic to search materials for
  -a, --age TEXT            Age range for the search (eg. 8-10)
  -p, --print [plain|JSON]  Print format  [required]
  --format TEXT             Format of the specified file  [required]
  --help                    Show this message and exit.
```

**NOTE:** If you are not sure what available age, topic, concepts etc the graph contains use the other commands to list them.

Example usage:

```
py edu_graph.py search data/rdf.json --format json-ld --age 8-10 --topic Програмиране --lang Python --concept кортежи --education всички
```

### List some stuff

Executing

```
py edu_graph.py
Usage: edu_graph [OPTIONS] COMMAND [ARGS]...

  A CLI for querying learning materials from a RDF based educational graph

Options:
  --help  Show this message and exit.

Commands:
  ages        List all available ages within all the matarials
  concepts    List all available concepts within all the matarials
  educations  List all available education fields within all the matarials
  languages   List all available languages within all the matarials
  search      Search within the graph for a materials based on a set of...
  topics      List all available topics within all the matarials
```

Example usage:

```
py edu_graph.py concepts data/rdf.json --format json-ld
```
