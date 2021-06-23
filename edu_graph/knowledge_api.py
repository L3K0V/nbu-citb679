import inquirer as inq
from rdflib.term import BNode
import pprint as pp


class KnowledgeApi:
    def __init__(self, library):
        self.library = library
        self.user_data = {}

    def __language_where_clause(self):
        if (not self.user_data['language'] or self.user_data['language'] == 'Non-specific'):
            return 'FILTER NOT EXISTS {?m sdo:inLanguage ?language}'
        else:
            return '?m sdo:inLanguage "' + self.user_data['language'] + '"'

    def __concept_where_clause(self):
        if (not self.user_data['concept'] or self.user_data['concept'] == 'Non-specific'):
            return 'FILTER NOT EXISTS {?m sdo:teaches ?concept}'
        else:
            return '?m sdo:teaches "' + self.user_data['concept'] + '"'

    def __edu_level_where_clause(self):
        if (not self.user_data['edu_level'] or self.user_data['edu_level'] == 'Non-specific'):
            return 'FILTER NOT EXISTS {?m sdo:educationalLevel ?edu_level}'
        else:
            return '?m sdo:educationalLevel "' + self.user_data['edu_level'] + '"'


    def __ask_for_age(self):
        ages = self.list_ages()

        questions = [
            inq.List('age',
                     message='How old are you?',
                     choices=ages
                     )
        ]

        self.user_data.update(inq.prompt(questions))

    def __ask_for_topic(self):
        topics = self.list_topics()

        questions = [
            inq.List('topic',
                     message='Which topic would you like to study?',
                     choices=topics
                     )
        ]

        self.user_data.update(inq.prompt(questions))

    def __ask_for_lang(self):
        languages = self.list_languages()

        questions = [
            inq.List('language',
                     message='Which language do you want to study about?',
                     choices=languages
                     )
        ]

        self.user_data.update(inq.prompt(questions))

    def __ask_for_concept(self):

        concepts = self.list_concepts()

        questions = [
            inq.List('concept',
                     message='Which concept would you like to learn?',
                     choices=concepts
                     )
        ]

        self.user_data.update(inq.prompt(questions))

    def __ask_for_level(self):

        edu_levels = self.list_educations()

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
                """ + self.__concept_where_clause() + """ .
                """ + self.__edu_level_where_clause() + """ .
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
            if node in row[0]:
                continue
            course_deps.append((str(row[1]), row[0]))

        questions = [
            inq.Checkbox('already_known',
                         message="What do you know already?",
                         choices=course_deps,
                         ),
        ]

        self.user_data.update(inq.prompt(questions))

    def __build_query(self):
        query = []

        if (self.user_data.get('age')):
            query.append("""?m sdo:typicalAgeRange '""" +
                         self.user_data['age'] + """' .""")
        if (self.user_data.get('topic')):
            query.append("""?m oer:forTopic '""" +
                         self.user_data['topic'] + """' .""")
        if (self.user_data.get('language')):
            query.append("""""" + self.__language_where_clause() + """ .""")
        if (self.user_data.get('concept')):
            query.append("""""" + self.__concept_where_clause() + """ .""")
        if (self.user_data.get('edu_level')):
            query.append("""""" + self.__edu_level_where_clause() + """ .""")

        return query

    def prompt_for_user_profile(self):
        self.user_data = {}
        self.__ask_for_age()
        self.__ask_for_topic()
        self.__ask_for_lang()
        self.__ask_for_concept()
        self.__ask_for_level()
        self.__ask_for_material()
        self.__ask_for_already_known()

    def get_learning_path_by_criteria(self):
        node, course, title = self.user_data['edu_material']
        
        qRes = self.library.graph.query(
            """
            SELECT DISTINCT ?material ?title
            WHERE {
                ?m oer:coursePrerequisites* ?material .
                ?material rdfs:label ?title .
            }
            ORDER BY ?material
            """, initBindings={'m': node}
        )

        course_materials_to_learn = []
        for row in qRes:
            if row[0] in self.user_data['already_known']:
                continue
            course_materials_to_learn.append(row[0] + " " + row[1])
            
        print("Learning path is as follows:")
        for material in course_materials_to_learn:
            print("vvv")
            print(material)

    def set_age(self, age):
        self.user_data['age'] = age

    def set_topic(self, topic):
        self.user_data['topic'] = topic

    def set_lang(self, lang):
        self.user_data['language'] = lang

    def set_concept(self, concept):
        self.user_data['concept'] = concept

    def set_education(self, education):
        self.user_data['edu_level'] = education

    def search(self):
        """Search for learning materials based on the user data. Edit user data in order to search no precise."""

        query = self.__build_query()

        result_set = self.library.graph.query(
            """
            SELECT DISTINCT ?m ?course ?title
            WHERE {
                """ + ''.join(query) + """
                ?m rdfs:label ?title .
                ?m oer:forCourse ?course .
            }
            ORDER BY ?m
            """
        )

        return result_set

    def search_deps(self, node: str = None):

        if not node:
            return []

        result_set = self.library.graph.query(
            """
            SELECT DISTINCT ?material ?course ?title
            WHERE {
                ?m oer:coursePrerequisites* ?material .
                ?material rdfs:label ?title .
                ?material oer:forCourse ?course .
            }
            ORDER BY ?material
            """, initBindings={'m': BNode(node.strip())}
        )

        return result_set

    def list_ages(self):
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

        return ages

    def list_topics(self, filter: bool = True):

        if filter:
            query = self.__build_query()
        else:
            query = []

        available_topics = self.library.graph.query(
            """
            SELECT DISTINCT ?topic
            WHERE {
                """ + ''.join(query) + """
                ?m oer:forTopic ?topic
            }
            ORDER BY ?topic
            """
        )

        topics = []

        for row in available_topics:
            topics.append(row[0])

        return topics

    def list_languages(self, filter: bool = True):

        if filter:
            query = self.__build_query()
        else:
            query = []

        available_languages = self.library.graph.query(
            """
            SELECT DISTINCT ?language
            WHERE {
                """ + ''.join(query) + """
                ?m sdo:inLanguage ?language .
            }
            ORDER BY ?language
            """
        )

        languages = []

        entries_without_language = self.library.graph.query(
            """
            SELECT DISTINCT ?language
            WHERE {
                """ + ''.join(query) + """
                FILTER NOT EXISTS {?m sdo:inLanguage ?language} .
            }
            ORDER BY ?language
            """
        )

        if len(entries_without_language) > 0:
            languages = ['Non-specific']

        for row in available_languages:
            languages.append(row[0])

        return languages

    def list_concepts(self, filter: bool = True):

        if filter:
            query = self.__build_query()
        else:
            query = []

        available_concepts = self.library.graph.query(
            """
            SELECT DISTINCT ?concept
            WHERE {
                """ + ''.join(query) + """
                ?m sdo:teaches ?concept .
            }
            ORDER BY ?concept
            """
        )

        concepts = []

        entries_without_concepts = self.library.graph.query(
            """
            SELECT DISTINCT ?concept
            WHERE {
                """ + ''.join(query) + """
                FILTER NOT EXISTS {?m sdo:teaches ?concept} .
            }
            ORDER BY ?concept
            """
        )

        if len(entries_without_concepts) > 0:
            concepts = ['Non-specific']

        for row in available_concepts:
            concepts.append(row[0])

        return concepts

    def list_educations(self, filter: bool = True):

        if filter:
            query = self.__build_query()
        else:
            query = []

        available_levels = self.library.graph.query(
            """
            SELECT DISTINCT ?edu_level
            WHERE {
                """ + ''.join(query) + """
                ?m sdo:educationalLevel ?edu_level .
            }
            ORDER BY ?edu_level
            """
        )

        edu_levels = []

        entries_without_edu_levels = self.library.graph.query(
            """
            SELECT DISTINCT ?edu_level
            WHERE {
                """ + ''.join(query) + """
                FILTER NOT EXISTS {?m sdo:educationalLevel ?edu_level} .
            }
            ORDER BY ?edu_level
            """
        )

        if len(entries_without_edu_levels) > 0:
            edu_levels = ['Non-specific']

        for row in available_levels:
            edu_levels.append(row[0])

        return edu_levels
