import pprint
import pandas as pd

from rdflib import Graph, Literal, Namespace, RDF, BNode
from rdflib.namespace import FOAF, XSD, RDFS

OER = Namespace("http://oerschema.org/")

df = pd.read_excel('data/1619073985303267.ods', index_col=0)
df = df.dropna()

# create a Graph
g = Graph()
g.bind("foaf", FOAF)
g.bind("oer", OER)

# Fill topic courses T1, T2, T3...
for topic in df.index:
    topic_node = BNode(topic.strip().split('.')[0])
    g.add((topic_node, RDF.type, OER.Course))

# Fill material for courses T1.1, T1.2...
for row in df.itertuples():
    item = BNode(row.Index)
    g.add((item, RDF.type, OER.LearningComponent))
    g.add((item, OER.forCourse, BNode(row.Index.split('.')[0])))
    g.add((item, RDFS.label, Literal(row._1)))

    dependsOn = str(row._2).split(',')

    for dep in dependsOn:
        if dep.find('-') != -1:
            ranges = dep.split('-')
            for range in ranges:
                g.add((item, OER.coursePrerequisites, BNode(range.strip())))
        else:
            g.add((item, OER.coursePrerequisites, BNode(dep.strip())))

# for stmt in sorted(g):
#     pprint.pprint(stmt)

for i in g.transitive_objects(BNode("T6.1"), OER.coursePrerequisites):
    for n in g.transitive_objects(i, OER.coursePrerequisites):
        print(n)
