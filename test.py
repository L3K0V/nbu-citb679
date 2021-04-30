from rdflib import Graph, Literal, RDF, URIRef, FOAF
# rdflib knows about some namespaces, like FOAF
from rdflib.namespace import FOAF , XSD

# create a Graph
g = Graph()

# Create an RDF URI node to use as the subject for multiple triples
t1_1 = URIRef("http://example.org/t1_1")

# Add triples using store's add() method.
g.add((t1_1, RDF.type, FOAF.Document))
g.add((t1_1, FOAF.topic, Literal("Какво е език за програмиране?")))
g.add((t1_1, FOAF.primaryTopic, Literal("Programming")))
g.add((t1_1, FOAF.interest, Literal("tag1")))

t1_2 = URIRef("http://example.org/t1_2")

# Add triples using store's add() method.
g.add((t1_2, RDF.type, FOAF.Document))
g.add((t1_2, FOAF.topic, Literal("Компилатори и интерпретатори")))
g.add((t1_2, FOAF.primaryTopic, Literal("Programming")))
g.add((t1_2, FOAF.interest, Literal("tag2")))

t1_3 = URIRef("http://example.org/t1_3")

# Add triples using store's add() method.
g.add((t1_3, RDF.type, FOAF.Document))
g.add((t1_3, FOAF.topic, Literal("Разширения на езика")))
g.add((t1_3, FOAF.primaryTopic, Literal("Programming")))
g.add((t1_3, FOAF.interest, Literal("tag1")))

t1_4 = URIRef("http://example.org/t1_4")

# Add triples using store's add() method.
g.add((t1_4, RDF.type, FOAF.Document))
g.add((t1_4, FOAF.topic, Literal("Етапи на създаване на програма")))
g.add((t1_4, FOAF.primaryTopic, Literal("Programming")))
g.add((t1_4, FOAF.interest, Literal("tag4")))

qres = g.query(
    """
       SELECT ?b
       WHERE {
          ?b foaf:interest 'tag1' .
       }""")

print(qres)