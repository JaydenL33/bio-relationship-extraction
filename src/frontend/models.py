from .data.db_session import db_auth
import re

graph = db_auth()

def clean_relationship(results):
    if len(results) > 0:
        for cols in ['type(r)', 'type(r1)', 'type(r2)']:
            print(cols)
            if cols in results.columns:
                results[cols] = results[cols].str.lower().str.replace("_", " ")
                results[cols] = results[cols].str.replace("associated with", "is associated with")
                results[cols] = results[cols].str.replace("isolated from", "is isolated from")
                results[cols] = results[cols].str.replace("metabolite of", "is a metabolite of")
    return results

def search_three(a_term = '', a_type = 'ALL',
                    b_term = '', b_type = 'ALL',
                    c_term = '', c_type = 'ALL',
                    r1_type = 'ALL', r2_type = 'ALL',
                    a_exact = False, b_exact = False, c_exact = False):


    query = """
    MATCH p=(a)-[r1]->(b)-[r2]->(c)
    WHERE """

    first_filter = False
    if(a_term != ''):
        if a_exact:
            query += f"a.ID='{a_term}' "
        else:
            query += f"a.ID CONTAINS '{a_term}' "
        first_filter = True
    if(a_type != 'ALL'):
        if first_filter:
            query += "AND "
        query += f"a.type='{a_type}' "
        first_filter = True
    if(b_term != ''):
        if first_filter:
            query += "AND "
        if b_exact:
            query += f"b.ID='{b_term}' "
        else:
            query += f"b.ID CONTAINS '{b_term}' "
        first_filter = True
    if(b_type != 'ALL'):
        if first_filter:
            query += "AND "
        query += f"b.type='{b_type}' "
        first_filter = True
    if(c_term != ''):
        if first_filter:
            query += "AND "
        if c_exact:
            query += f"c.ID='{c_term}' "
        else:
            query += f"d.ID CONTAINS '{d_term}' "
        first_filter = True
    if(c_type != 'ALL'):
        if first_filter:
            query += "AND "
        query += f"c.type='{c_type}' "
        first_filter = True
    if(r1_type != 'ALL'):
        if first_filter:
            query += "AND "
        query += f"type(r1)='{r1_type}' "
        first_filter = True
    if(r2_type != 'ALL'):
        if first_filter:
            query += "AND "
        query += f"type(r2)='{r2_type}' "
        first_filter = True

    query+="""
    RETURN a.ID,a.type,type(r1),r1.Pubmed,r1.citation,b.ID,b.type,type(r2),r2.Pubmed,r2.citation,c.ID,c.type
    """
    print(query)

    results = graph.run(query).to_data_frame()
    if len(results) < 1:
        return results
    else:
        # drop any results where the 3rd and 1st node are the same
        results = results.drop(results[(results['a.ID']==results['c.ID'])].index)


        if (a_exact is False and a_term != ''):
            results['a.ID'] = results['a.ID'].str.replace(a_term, ("<b>"+a_term+"</b>"))
        if (b_exact is False and b_term != ''):
            results['b.ID'] = results['b.ID'].str.replace(b_term, ("<b>"+b_term+"</b>"))
        if (c_exact is False and c_term != ''):
            results['c.ID'] = results['c.ID'].str.replace(c_term, ("<b>"+c_term+"</b>"))

        results['a.type'] = results['a.type'].str.replace("_", " ")
        results['b.type'] = results['b.type'].str.replace("_", " ")
        results['c.type'] = results['c.type'].str.replace("_", " ")

        results['query'] = query
        return clean_relationship(results)

def search_two(a_term = '', a_type = 'ALL',
                    b_term = '', b_type = 'ALL',
                    r1_type = 'ALL',
                    a_exact = False, b_exact = False):


    query = """
    MATCH p=(a)-[r1]->(b)
    WHERE """

    first_filter = False
    if(a_term != ''):
        if a_exact:
            query += f"a.ID='{a_term}' "
        else:
            query += f"a.ID CONTAINS '{a_term}' "
        first_filter = True
    if(a_type != 'ALL'):
        if first_filter:
            query += "AND "
        query += f"a.type='{a_type}' "
        first_filter = True
    if(b_term != ''):
        if first_filter:
            query += "AND "
        if b_exact:
            query += f"b.ID='{b_term}' "
        else:
            query += f"b.ID CONTAINS '{b_term}' "
        first_filter = True
    if(b_type != 'ALL'):
        if first_filter:
            query += "AND "
        query += f"b.type='{b_type}' "
        first_filter = True
    if(r1_type != 'ALL'):
        if first_filter:
            query += "AND "
        query += f"type(r1)='{r1_type}' "
        first_filter = True

    query+="""
    RETURN a.ID,a.type,type(r1),r1.Pubmed,r1.citation,b.ID,b.type
    """
    print(query)
    results = graph.run(query).to_data_frame()

    # check if there are any results...
    if len(results) < 1:
        return results
    else:
        results['a.ID'] = results['a.ID'].str.capitalize()

        if (a_exact is False and a_term != ''):
            results['a.ID'] = results['a.ID'].map(lambda a: re.sub(r'('+a_term+')',r'<b>\1</b>' ,a))
            results['a.ID'] = results['a.ID'].map(lambda a: re.sub(r'('+a_term.capitalize()+')',r'<b>\1</b>' ,a))
            #results['a.ID'] = results['a.ID'].str.replace(a_term, ("<b>"+a_term+"</b>"))
            #results['a.ID'] = results['a.ID'].str.replace(a_term.capitalize(), ("<b>"+a_term.capitalize()+"</b>"))
        if (b_exact is False and b_term != ''):
            results['b.ID'] = results['b.ID'].str.replace(b_term, ("<b>"+b_term+"</b>"))

        results['a.type'] = results['a.type'].str.replace("_", " ")
        results['b.type'] = results['b.type'].str.replace("_", " ")

        results['query'] = query
        return clean_relationship(results)

def search_cypher(cypher_query = ''):
    print(cypher_query)
    results = graph.run(cypher_query).to_data_frame()
    #print(results)
    return results

def search_relationships_from(tag, search_type):
    tag = tag.lower()
    if search_type == "ALL":
        query = """
        MATCH p=(a1)-[r]->(a2)
        WHERE a1.ID=$tag
        RETURN a1.ID, type(r), r.Pubmed, a2.ID
        """
    else:
        query = """
        MATCH p=(a1)-[r]->(a2)
        WHERE a1.ID=$tag AND type(r)=$search_type
        RETURN a1.ID, type(r), r.Pubmed, a2.ID
        """
    results = graph.run(query, tag=tag, search_type=search_type).to_data_frame()
    return clean_relationship(results)

def search_relationships_to(tag):

    query = """
    MATCH p=(a1)-[r]->(a2)
    WHERE a2.ID=$tag
    RETURN a1.ID, type(r), r.Pubmed, a2.ID
    """

    results = graph.run(query, tag=tag).to_data_frame()
    return clean_relationship(results)
