import os

from flask import Flask, request
from flask import render_template

from ..edu_graph import KnowledgeLibrary
from ..edu_graph import KnowledgeApi

app = Flask(__name__)


dirname = os.path.dirname(__file__)
filename = os.path.join(dirname, 'static/rdf.json')

library = KnowledgeLibrary()
library.load(filename, "json-ld")
api = KnowledgeApi(library)


@app.route('/', methods=['GET', 'POST'])
def index():

    api.set_age(request.args.get('age', None))
    api.set_topic(request.args.get('topic', None))
    api.set_lang(request.args.get('language', None))
    api.set_education(request.args.get('edu_level', None))
    api.set_concept(request.args.get('concept', None))
    material = request.args.get('material', None)

    return render_template(
        'index.html',
        user=api.user_data,
        formdata={
            "ages": api.list_ages(),
            "topics": api.list_topics(),
            "concepts": api.list_concepts(),
            "languages": api.list_languages(),
            "educations": api.list_educations(),
        },
        material=material,
        results=api.search(),
        deps=api.search_deps(material)
    )
