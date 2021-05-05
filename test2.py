import pprint
import pandas as pd

from rdflib import Graph, Literal, Namespace, RDF, BNode
from rdflib.namespace import FOAF, XSD, RDFS, SDO

OER = Namespace("http://oerschema.org/")

df = pd.read_excel('data/1619073985303267.ods', index_col=0)
df = df.dropna()

# create a Graph
g = Graph()
g.bind("foaf", FOAF)
g.bind("oer", OER)

for row in df.itertuples():
    course = BNode(row.Index.strip().split('.')[0])
    g.add((course, RDF.type, OER.Course))

    item = BNode(row.Index)
    g.add((item, RDF.type, OER.LearningComponent))
    g.add((item, OER.forCourse, course))
    g.add((item, RDFS.label, Literal(row._1)))

    # Set educational level (всички, математици, etc...)
    scopes = row[5].split(',')

    for scope in scopes:
        g.add((item, SDO.educationalLevel, Literal(scope.strip())))

    # Set learning material topics (Programming, Python, etc...)
    topics = row[4].split(',')

    for topic in topics:
        g.add((item, OER.forTopic, Literal(topic.strip())))

    # Set age ranges for the learning material
    ageRanges = row[3].split(',')

    for range in ageRanges:
        g.add((item, SDO.typicalAgeRange, Literal(range.strip())))

    # Set material pre-requisites (T1.2,T1.3,T7.1-T7.15)
    # TODO: Ranges currently does not handle between values, just the first and the last
    # TODO: Spread T1 range to T1.1,T1.2,T1.3
    dependsOn = str(row._2).split(',')

    for dep in dependsOn:
        if dep.find('-') != -1:
            ranges = dep.split('-')
            for range in ranges:
                g.add((item, OER.coursePrerequisites, BNode(range.strip())))
        else:
            g.add((item, OER.coursePrerequisites, BNode(dep.strip())))

qres = g.query(
    """
    SELECT DISTINCT ?material
    WHERE {
        ?m oer:coursePrerequisites* ?material .
    }
    """, initBindings={'m': BNode("T6.12")})

for row in qres:
    print("%s" % row)

# for stmt in sorted(g):
#     pprint.pprint(stmt)

# for i in g.transitive_objects(BNode("T6.1"), OER.coursePrerequisites):
#     for n in g.transitive_objects(i, OER.coursePrerequisites):
#         print(n)

# file = open("output/rdf.json", mode="w")
# file.write(g.serialize(format='json-ld').decode('utf-8'))

# file = open("output/rdf.n3", mode="w")
# file.write(g.serialize(format='n3').decode('utf-8'))

# file = open("output/rdf.turtle", mode="w")
# file.write(g.serialize(format='turtle').decode('utf-8'))
