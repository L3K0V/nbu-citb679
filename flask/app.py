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

    if request.method == 'POST':
        age = request.form.get('age')
        topic = request.form.get('topic')
        lang = request.form.get('lang')

    return render_template(
        'index.html',
        user=api.user_data,
        ages=api.list_ages(),
        topics=api.list_topics(),
        concepts=api.list_concepts(),
        languages=api.list_languages(),
        educations=api.list_educations())


@app.route('/list/')
@app.route('/list/<type>')
def hello(type=None):

    results = []

    if type:
        method = f'list_{type}'
        results = getattr(api, method)()

    return render_template('list.html', results=results)
