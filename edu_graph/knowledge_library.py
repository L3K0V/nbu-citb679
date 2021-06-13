import pandas as pd

from rdflib import Graph, Literal, Namespace, RDF, BNode
from rdflib.namespace import FOAF, RDFS, SDO

OER = Namespace("http://oerschema.org/")


class KnowledgeLibrary:
    def __init__(self):
        self.graph = Graph()
        self.graph.bind("foaf", FOAF)
        self.graph.bind("oer", OER)
        self.graph.bind('sdo', SDO)

    def generate(self, filename=None):
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
        """Populate all course dependencies or prerequisites
        """
        dependsOn = str(df._2).split(',')

        for dep in dependsOn:
            if dep.find('-') != -1:

                base, ranges = self.__spreadRanges(dep)

                for r in ranges:
                    self.graph.add(
                        (material, OER.coursePrerequisites, BNode(f'{base.strip()}.{r}')))
            else:
                self.graph.add(
                    (material, OER.coursePrerequisites, BNode(dep.strip())))

    def __spreadRanges(self, data):
        """Spread ranges like T1.1-T1.8 to
        T1.1, T1.2, T1.3 .... T.1.8
        """
        ranges = data.split('-')

        if len(ranges) != 2:
            return

        fromParts = ranges[0].split('.')
        toParts = ranges[1].split('.')
        base = fromParts[0]
        fromDep = int(fromParts[1][0:])
        toDep = int(toParts[1])

        ranges = range(fromDep, toDep + 1)

        return (base, ranges)

    def __populateCourseAgeRanges(self, material, df):
        """Populate all age ranges for the learning material in a
        format of a tuples 8-10, 10-20 etc.
        """

        if type(df[3]) is not str:
            return

        ageRanges = str(df[3]).split(',')

        for range in ageRanges:
            self.graph.add(
                (material, SDO.typicalAgeRange, Literal(range.strip())))

    def __populateCourseTopics(self, material, df):
        """Populate all course learning material topics (Programming, Python, etc...)
        """

        if type(df[4]) is not str:
            return

        topics = str(df[4]).split(',')

        for topic in topics:
            self.graph.add(
                (material, OER.forTopic, Literal(topic.strip())))

    def __populateCourseLanguages(self, material, df):
        """Populate all course programming languages
        """

        if type(df[5]) is not str:
            return

        items = str(df[5]).split(',')

        for item in items:
            self.graph.add(
                (material, SDO.inLanguage, Literal(item.strip())))

    def __populateCourseEduLevels(self, material, df):
        """Set educational level (всички, математици, etc...)
        """

        if type(df[8]) is not str:
            return

        scopes = str(df[8]).split(',')

        for scope in scopes:
            self.graph.add(
                (material, SDO.educationalLevel, Literal(scope.strip())))

    def __populateCourseConcepts(self, material, df):
        """Populate all course concetps
        """

        if type(df[6]) is not str:
            return

        items = str(df[6]).split(',')

        for item in items:
            self.graph.add(
                (material, SDO.teaches, Literal(item.strip())))

    def __populateCourseTags(self, material, df):
        """Populate all course tags
        """

        if type(df[7]) is not str:
            return

        items = str(df[7]).split(',')

        for item in items:
            self.graph.add(
                (material, SDO.keywords, Literal(item.strip())))

    def export(self, relative_path, format):
        """Exports the graph into a one of the supported
        formats and given filename.

        Supported formats:
        - n3
        - nquads
        - nt
        - pretty-xml
        - trig
        - trig
        - turtle
        - xml
        - json-ld
        """
        import os
        import sys

        dirname = os.path.dirname(sys.modules['__main__'].__file__)
        filename = os.path.join(dirname, relative_path)
        file = open(filename, mode="w+")
        file.write(self.graph.serialize(format=format).decode('utf-8'))
        file.close()

    def load(self, filename=None, format=None):
        """Imports a graph from a file with selected format

        Supported formats:
        - n3
        - nquads
        - nt
        - pretty-xml
        - trig
        - trig
        - turtle
        - xml
        - json-ld
        """
        if (not filename or not format):
            return

        self.graph.parse(filename, format=format)
