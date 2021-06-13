import click
import json

from .knowledge_api import KnoledgeApi
from .knowledge_library import KnowledgeLibrary


def __list(filename, format, field, print):
    library = KnowledgeLibrary()
    library.load(filename, format)
    api = KnoledgeApi(library)

    method = f'list_{field}'

    result = getattr(api, method)()

    if (print == "JSON"):
        click.echo(json.dumps({"{field}": result}))
    else:
        click.echo(list(map(lambda item: str(item), result)))


@click.group()
def edu_graph():
    """A CLI for querying learning materials from a RDF based educational graph"""


@click.argument('filename')
@click.option('--format', help="Format of the specified file", required=True, type=str)
@click.option('-p', '--print', help="Print format", required=True, default="plain", type=click.Choice(['plain', 'JSON']))
@click.option('-a', '--age', help="Age range for the search (eg. 8-10)", required=False, type=str)
@click.option('-t', '--topic', help="The topic to search materials for", required=False, type=str)
@click.option('-l', '--lang', help="The programming language which materials are for", required=False, type=str)
@click.option('-e', '--education', help="The education frield the material are focused for. (eg. mathematicians, musicians, all)", required=False, type=str, default="всички")
@click.option('-c', '--concept', help="The concept to learn", required=False, type=str)
@edu_graph.command(help="Search within the graph for a materials based on a set of criterias")
def search(filename, format, print, age, topic, lang, education, concept):
    library = KnowledgeLibrary()
    library.load(filename, format)
    api = KnoledgeApi(library)

    if age:
        api.set_age(age)
    if topic:
        api.set_topic(topic)
    if lang:
        api.set_lang(lang)
    if education:
        api.set_education(education)
    if concept:
        api.set_concept(concept)

    result = api.search()

    if (print == "JSON"):
        click.echo(json.dumps(
            list(map(lambda item: {"id": item[0], "title": item[2], "course": item[1]}, result)), ensure_ascii=False).encode('utf8').decode())
    else:
        click.echo(
            list(map(lambda item: "{} - {} ({})".format(item[0], item[2], item[1]), result)))


@ click.argument('filename')
@ click.option('--format', help="Format of the specified file", required=True, type=str)
@ edu_graph.command(help="List all available ages within all the matarials")
def ages(filename, format):
    __list(filename, format, "ages", print)


@ click.argument('filename')
@ click.option('--format', help="Format of the specified file", required=True, type=str)
@ click.option('-p', '--print', help="Print format", required=True, default="plain", type=click.Choice(['plain', 'JSON']))
@ edu_graph.command(help="List all available topics within all the matarials")
def topics(filename, format, print):
    __list(filename, format, "topics", print)


@ click.argument('filename')
@ click.option('--format', help="Format of the specified file", required=True, type=str)
@ click.option('-p', '--print', help="Print format", required=True, default="plain", type=click.Choice(['plain', 'JSON']))
@ edu_graph.command(help="List all available languages within all the matarials")
def languages(filename, format, print):
    __list(filename, format, "languages", print)


@ click.argument('filename')
@ click.option('--format', help="Format of the specified file", required=True, type=str)
@ click.option('-p', '--print', help="Print format", required=True, default="plain", type=click.Choice(['plain', 'JSON']))
@ edu_graph.command(help="List all available concepts within all the matarials")
def concepts(filename, format, print):
    __list(filename, format, "concepts", print)


@ click.argument('filename')
@ click.option('--format', help="Format of the specified file", required=True, type=str)
@ click.option('-p', '--print', help="Print format", required=True, default="plain", type=click.Choice(['plain', 'JSON']))
@ edu_graph.command(help="List all available education fields within all the matarials")
def educations(filename, format, print):
    __list(filename, format, "educations", print)
