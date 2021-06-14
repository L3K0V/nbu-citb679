import pprint as pp

import edu_graph


def test():
    library = edu_graph.KnowledgeLibrary()

    library.load("data/rdf.json", "json-ld")
    # library.generate('data/1619073985303267.ods')

    api = edu_graph.KnowledgeApi(library)
    api.prompt_for_user_profile()
    pp.pprint(api.user_data)

    # library.export("rdf.json", "json-ld")
    exit()


def main():
    edu_graph.edu_graph(prog_name='edu_graph')


if __name__ == "__main__":
    test()
