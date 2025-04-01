from flask import request, redirect, render_template, flash, current_app as app
from .models import *

from .forms import TwoSearchForm, ThreeSearchForm, CypherSearchForm

# views.py
# contains all the @app.route s

# default page, search using a two node relationship
@app.route('/', methods=['GET', 'POST'])
def index():
    search = TwoSearchForm(request.form)

    results = []
    if request.method == 'POST':
        # get data from the webform
        search_string_n1 = search.data['search_1']
        search_string_n2 = search.data['search_2']
        search_type_r1 = search.data['relationship_type_1']
        search_n1_type = search.data['node_1_type']
        search_n2_type = search.data['node_2_type']
        search_n1_exact = search.data['search_1_exact']
        search_n2_exact = search.data['search_2_exact']

        # search the database
        results = search_two(a_term = search_string_n1.lower(),
                               a_type = search_n1_type,
                               b_term = search_string_n2.lower(),
                               b_type = search_n2_type,
                               r1_type = search_type_r1,
                               a_exact = search_n1_exact,
                               b_exact = search_n2_exact)

        if len(results) < 1:
            flash('No results found!')
            return redirect('/')
        else:
            groups = results.groupby(['a.type','b.type']).size().reset_index()
            results_by_group = list()

            for row_index in range(groups.shape[0]):
                row_results = results.loc[(results['a.type']==groups['a.type'][row_index]) & (results['b.type']==groups['b.type'][row_index])]
                results_by_group.append(row_results)
            results = results_by_group

    return render_template('index_search2.html', form=search, results=results)

# search using a three node relationship
@app.route('/search', methods=['GET', 'POST'])
def search():
    search = ThreeSearchForm(request.form)
    #search_list = TagSearchForms(request.form)

    results = []
    if request.method == 'POST':
        search_string_n1 = search.data['search_1']
        search_string_n2 = search.data['search_2']
        search_string_n3 = search.data['search_3']
        search_type_r1 = search.data['relationship_type_1']
        search_type_r2 = search.data['relationship_type_2']
        search_n1_type = search.data['node_1_type']
        search_n2_type = search.data['node_2_type']
        search_n3_type = search.data['node_3_type']
        search_n1_exact = search.data['search_1_exact']
        search_n2_exact = search.data['search_2_exact']
        search_n3_exact = search.data['search_3_exact']

        results = search_three(a_term = search_string_n1.lower(),
                               a_type = search_n1_type,
                               b_term = search_string_n2.lower(),
                               b_type = search_n2_type,
                               c_term = search_string_n3.lower(),
                               c_type = search_n3_type,
                               r1_type = search_type_r1,
                               r2_type = search_type_r2,
                               a_exact = search_n1_exact,
                               b_exact = search_n2_exact,
                               c_exact = search_n3_exact)

        if len(results) < 1:
            flash('No results found!')
            return redirect('/search')
        else:
            groups = results.groupby(['a.type','b.type','c.type']).size().reset_index()
            results_by_group = list()

            for row_index in range(groups.shape[0]):
                row_results = results.loc[(results['a.type']==groups['a.type'][row_index]) & (results['b.type']==groups['b.type'][row_index]) & (results['c.type']==groups['c.type'][row_index])]
                results_by_group.append(row_results)
            results = results_by_group

    return render_template('index_search3.html', form=search, results=results)

# search using a Cypher Query
@app.route('/CYPHER', methods=['GET', 'POST'])
def CYPHER():
    search = CypherSearchForm(request.form)
    #search_list = TagSearchForms(request.form)
    results = []
    if request.method == 'POST':
        search_cypher_string = search.data['search']
        results = search_cypher(search_cypher_string).to_html()
        if len(results) < 1:
            flash('No results found!')
            return redirect('/')

    return render_template('cypher_search.html', form=search, results=results)

# old page... displays all relationships to an entity
# needs to have a link into it somewhere
# used to have hyperlinks from the search results
@app.route('/chems/<chem_id>')
def chems(chem_id):

    results_from = []
    results_from = search_relationships_from(chem_id, search_type="ALL")

    results_to = []
    results_to = search_relationships_to(chem_id)
    results_to = results_to.loc[results_to['type(r)'] != "is associated with"]
    results_to = results_to.loc[results_to['type(r)'] != "binds with"]


    return render_template(
        'chem_profile.html',
        results_from=results_from,
        results_to=results_to,
        chem = chem_id
    )
