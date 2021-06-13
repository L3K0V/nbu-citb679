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
        dirname = os.path.dirname(__file__)
        filename = os.path.join(dirname, relative_path)
        file = open(filename, mode="w+")
        file.write(self.graph.serialize(format=format).decode('utf-8'))
        file.close()

    def import(self, filename=None, format=None):
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


class KnoledgeGenrator:
    def __init__(self, library):
        self.library = library
        self.user_data = {}

    def __language_where_clause(self):
        if (self.user_data['language'] == 'Non-specific'):
            return 'FILTER NOT EXISTS {?m sdo:inLanguage ?language}'
        else:
            return '?m sdo:inLanguage "' + self.user_data['language'] + '"'

    def __ask_for_age(self):
        available_ages = self.library.graph.query(
            """
            SELECT DISTINCT ?age
            WHERE {
                ?m sdo:typicalAgeRange ?age
            }
            ORDER BY ?age
            """
        )

        ages = []

        for row in available_ages:
            ages.append(row[0])

        questions = [
            inq.List('age',
                     message='How old are you?',
                     choices=ages
                     )
        ]

        self.user_data.update(inq.prompt(questions))

    def __ask_for_topic(self):
        available_topics = self.library.graph.query(
            """
            SELECT DISTINCT ?topic
            WHERE {
                ?m sdo:typicalAgeRange '""" + self.user_data['age'] + """' .
                ?m oer:forTopic ?topic
            }
            ORDER BY ?topic
            """
        )

        topics = []

        for row in available_topics:
            topics.append(row[0])

        questions = [
            inq.List('topic',
                     message='Which topic would you like to study?',
                     choices=topics
                     )
        ]

        self.user_data.update(inq.prompt(questions))

    def __ask_for_lang(self):
        available_languages = self.library.graph.query(
            """
            SELECT DISTINCT ?language
            WHERE {
                ?m sdo:typicalAgeRange '""" + self.user_data['age'] + """' .
                ?m oer:forTopic '""" + self.user_data['topic'] + """' .
                ?m sdo:inLanguage ?language .
            }
            ORDER BY ?language
            """
        )

        languages = ['Non-specific']

        for row in available_languages:
            languages.append(row[0])

        questions = [
            inq.List('language',
                     message='Which language do you want to study about?',
                     choices=languages
                     )
        ]

        self.user_data.update(inq.prompt(questions))

    def __ask_for_concept(self):

        available_concepts = self.library.graph.query(
            """
            SELECT DISTINCT ?concept
            WHERE {
                ?m sdo:typicalAgeRange '""" + self.user_data['age'] + """' .
                ?m oer:forTopic '""" + self.user_data['topic'] + """' .
                """ + self.__language_where_clause() + """ .
                ?m sdo:teaches ?concept .
            }
            ORDER BY ?concept
            """
        )

        concepts = []

        for row in available_concepts:
            concepts.append(row[0])

        questions = [
            inq.List('concept',
                     message='Which concept would you like to learn?',
                     choices=concepts
                     )
        ]

        self.user_data.update(inq.prompt(questions))

    def __ask_for_level(self):
        available_levels = self.library.graph.query(
            """
            SELECT DISTINCT ?eduLevel
            WHERE {
                ?m sdo:typicalAgeRange '""" + self.user_data['age'] + """' .
                ?m oer:forTopic '""" + self.user_data['topic'] + """' .
                """ + self.__language_where_clause() + """ .
                ?m sdo:teaches '""" + self.user_data['concept'] + """' .
                ?m sdo:educationalLevel ?eduLevel .
            }
            ORDER BY ?eduLevel
            """
        )

        edu_levels = []

        for row in available_levels:
            edu_levels.append(row[0])

        questions = [
            inq.List('edu_level',
                     message='What is you education level?',
                     choices=edu_levels
                     )
        ]

        self.user_data.update(inq.prompt(questions))

    def __ask_for_material(self):
        available_materials = self.library.graph.query(
            """
            SELECT DISTINCT ?m ?course ?title
            WHERE {
                ?m sdo:typicalAgeRange '""" + self.user_data['age'] + """' .
                ?m oer:forTopic '""" + self.user_data['topic'] + """' .
                """ + self.__language_where_clause() + """ .
                ?m sdo:teaches '""" + self.user_data['concept'] + """' .
                ?m sdo:educationalLevel '""" + self.user_data['edu_level'] + """' .
                ?m rdfs:label ?title .
                ?m oer:forCourse ?course .
            }
            ORDER BY ?course
            """
        )

        edu_materials = []

        for row in available_materials:
            edu_materials.append((row[1] + " " + row[2], row))

        questions = [
            inq.List('edu_material',
                     message='Which educational material would you like to use?',
                     choices=edu_materials
                     )
        ]

        self.user_data.update(inq.prompt(questions))

    def __ask_for_already_known(self):
        node, course, title = self.user_data['edu_material']

        course_deps_result_set = self.library.graph.query(
            """
            SELECT DISTINCT ?material ?title
            WHERE {
                ?m oer:coursePrerequisites* ?material .
                ?material rdfs:label ?title .
            }
            ORDER BY ?material
            """, initBindings={'m': node}
        )

        course_deps = []

        for row in course_deps_result_set:
            course_deps.append((str(row[1]), row[0]))

        questions = [
            inq.Checkbox('already_known',
                         message="What do you know already?",
                         choices=course_deps,
                         ),
        ]

        self.user_data.update(inq.prompt(questions))

    def prompt_for_user_profile(self):
        self.user_data = {}
        self.__ask_for_age()
        self.__ask_for_topic()
        self.__ask_for_lang()
        self.__ask_for_concept()
        self.__ask_for_level()
        self.__ask_for_material()
        self.__ask_for_already_known()


def main():
    library = KnowledgeLibrary()

    library.parse("rdf.json", "json-ld")
    # library.generate('data/1619073985303267.ods')

    generator = KnoledgeGenrator(library)
    generator.prompt_for_user_profile()
    pp.pprint(generator.user_data)

    library.export("rdf.json", "json-ld")
    exit()


if __name__ == "__main__":
    main()

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
