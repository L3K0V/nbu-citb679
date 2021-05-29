import pandas as pd
import inquirer as inq
import pprint as pp

from rdflib import Graph, Literal, Namespace, RDF, BNode
from rdflib.namespace import FOAF, RDFS, SDO

OER = Namespace("http://oerschema.org/")


class KnowledgeLibrary:
    def __init__(self):
        self.graph = Graph()
        self.graph.bind("foaf", FOAF)
        self.graph.bind("oer", OER)
        self.graph.bind('sdo', SDO)

    def load(self, filename=None):
        if (not filename):
            return

        df = pd.read_excel(filename, index_col=0)
        df = df.dropna(how='all')

        for row in df.itertuples():
            course = BNode(row.Index.strip().split('.')[0])
            self.graph.add((course, RDF.type, OER.Course))

            material = BNode(row.Index)
            self.graph.add((material, RDF.type, OER.LearningComponent))
            self.graph.add((material, OER.forCourse, course))
            self.graph.add((material, RDFS.label, Literal(row._1)))

            self.__populateCourseDependencies(material, row)
            self.__populateCourseAgeRanges(material, row)
            self.__populateCourseTopics(material, row)
            self.__populateCourseLanguages(material, row)
            self.__populateCourseEduLevels(material, row)
            self.__populateCourseConcepts(material, row)
            self.__populateCourseTags(material, row)

    def __populateUnique(self, df, column):
        unique = df[column].unique()

        for item in unique:

            if type(item) is not str:
                continue

            node = BNode(item.strip())

            self.graph.add((node, RDF.type, SDO.DefinedTerm))
            self.graph.add((node, SDO.name, Literal(item.strip())))
            self.graph.add((node, SDO.description, Literal(column)))

    def __populateCourseDependencies(self, material, df):
        # Set material pre-requisites (T1.2,T1.3,T7.1-T7.15)
        # TODO: Ranges currently does not handle between values, just the first and the last
        # TODO: Spread T1 range to T1.1,T1.2,T1.3
        dependsOn = str(df._2).split(',')

        for dep in dependsOn:
            if dep.find('-') != -1:
                ranges = dep.split('-')
                for range in ranges:
                    self.graph.add(
                        (material, OER.coursePrerequisites, BNode(range.strip())))
            else:
                self.graph.add(
                    (material, OER.coursePrerequisites, BNode(dep.strip())))

    # Set age ranges for the learning material
    def __populateCourseAgeRanges(self, material, df):

        if type(df[3]) is not str:
            return

        ageRanges = str(df[3]).split(',')

        for range in ageRanges:
            self.graph.add(
                (material, SDO.typicalAgeRange, Literal(range.strip())))

    # Set learning material topics (Programming, Python, etc...)
    def __populateCourseTopics(self, material, df):

        if type(df[4]) is not str:
            return

        topics = str(df[4]).split(',')

        for topic in topics:
            self.graph.add(
                (material, OER.forTopic, Literal(topic.strip())))

    def __populateCourseLanguages(self, material, df):

        if type(df[5]) is not str:
            return

        items = str(df[5]).split(',')

        for item in items:
            self.graph.add(
                (material, SDO.inLanguage, Literal(item.strip())))

    # Set educational level (всички, математици, etc...)
    def __populateCourseEduLevels(self, material, df):

        if type(df[3]) is not str:
            return

        scopes = str(df[3]).split(',')

        for scope in scopes:
            self.graph.add(
                (material, SDO.educationalLevel, Literal(scope.strip())))

     # Set educational level (всички, математици, etc...)

    def __populateCourseConcepts(self, material, df):

        if type(df[6]) is not str:
            return

        items = str(df[6]).split(',')

        for item in items:
            self.graph.add(
                (material, SDO.teaches, Literal(item.strip())))

    def __populateCourseTags(self, material, df):

        if type(df[7]) is not str:
            return

        items = str(df[7]).split(',')

        for item in items:
            self.graph.add(
                (material, SDO.keywords, Literal(item.strip())))


library = KnowledgeLibrary()
library.load('data/1619073985303267.ods')

qres = library.graph.query(
    """
    SELECT DISTINCT ?age 
    WHERE {
        ?m SDO:typicalAgeRange ?age
    }
    ORDER BY ?age
    """, initNs={'SDO': SDO}
)

ages = []

for row in qres:
    ages.append(row[0])

questions = [
    inq.List('age',
        message = 'How old are you?',
        choices = ages
    )
]

answer = inq.prompt(questions)
age = answer['age']

qres = library.graph.query(
    """
    SELECT DISTINCT ?m
    WHERE {
        ?m SDO:typicalAgeRange '""" + age + """'
    }
    ORDER BY ?m
    """, initNs={'SDO': SDO, 'RDFS': RDFS}
)

# this should work, but title is not recognized as property for some reason
# qres = library.graph.query(
#     """
#     SELECT DISTINCT ?m
#     WHERE {
#         ?m SDO:typicalAgeRange '""" + age + """'
#         ?m RDFS:label ?title
#     }
#     ORDER BY ?title
#     """, initNs={'SDO': SDO, 'RDFS': RDFS}
# )

for row in qres:
    pp.pprint(row)


exit()

extraWhere = '?material oer:forTopic ?topic'

qres = library.graph.query(
    """
    SELECT DISTINCT ?topic 
    WHERE {
        ?m oer:coursePrerequisites* ?material .
        ?material rdfs:label ?title .
        """ + extraWhere + """
    }
    ORDER BY DESC(?topic)
    """, 
    initBindings={'m': BNode("T6.12")}
)

for row in qres:
    print("%s" % row[0])

    

# for row in qres:
#     print("(%s) %s" % (row[0], row[1]))

# for stmt in sorted(library.graph):
#     pprint.pprint(stmt)

# for i in g.transitive_objects(BNode("T6.1"), OER.coursePrerequisites):
#     for n in g.transitive_objects(i, OER.coursePrerequisites):
#         print(n)

# file = open("output/rdf.json", mode="w")
# file.write(library.graph.serialize(format='json-ld').decode('utf-8'))

# file = open("output/rdf.n3", mode="w")
# file.write(library.graph.serialize(format='n3').decode('utf-8'))

# file = open("output/rdf.turtle", mode="w")
# file.write(library.graph.serialize(format='turtle').decode('utf-8'))
