# forms.py

from wtforms import Form, StringField, SelectField, FieldList, FormField, BooleanField

class TagSearchForm(Form):
    search = StringField('')
    choices = [('ALL', 'All types'),
                ('ASSOCIATED_WITH','Associated with'),
                ('BINDS_WITH','Binds with'),
                ('ISOLATED_FROM','Isolated from'),
                ('METABOLITE_OF', 'Metabolite of')]
    relationship_type = SelectField("Relationship type", choices=choices)
    entity_type = SelectField("Enitity type", choices=[("ALL", "All types"),
    ("BIOLOGICAL_ACTIVITY", "Biological activity"),
    ("CHEMICAL", "Chemical"),
    ("METABOLITE", "Metabolite"),
    ("PROTEIN", "Protein"),
    ("SPECIES", 'Species'),
    ("SPECTRAL_DATA", "Spectral data")])

class CypherSearchForm(Form):
    search = StringField(default='MATCH (n)-[r]-(m) WHERE n.ID contains "rat" AND m.ID contains "one" Return n.ID, n.type,type(r),r.Pubmed,m.ID,m.type',
    render_kw={'class':'wide_input'})

class TwoSearchForm(Form):
    search_1 = StringField('')
    search_2 = StringField('')

    type_choices = [("ALL", "All types"),
                    ("Bbiological_activity", "Biological activity"),
                    ("Chemical", "Chemical"),
                    ("Metabolite", "Metabolite"),
                    ("Protein", "Protein"),
                    ("Species", 'Species'),
                    ("Spectral_data", "Spectral data")]

    relationship_choices = [('ALL', 'All types'),
                ('ASSOCIATED_WITH','Associated with'),
                ('BINDS_WITH','Binds with'),
                ('ISOLATED_FROM','Isolated from'),
                ('PRODUCES','Produces'),
                ('METABOLITE_OF', 'Metabolite of'),
                ('METABOLISES_TO', 'Metabolises to')]
    relationship_type_1 = SelectField("Relationship type", choices=relationship_choices)
    node_1_type = SelectField("Node 1 type", choices=type_choices)
    node_2_type = SelectField("Node 2 type", choices=type_choices)

    search_1_exact = BooleanField("Node 1 exact match:")
    search_2_exact = BooleanField("Node 2 exact match:")

class ThreeSearchForm(Form):
    search_1 = StringField('')
    search_2 = StringField('')
    search_3 = StringField('')

    type_choices = [("ALL", "All types"),
                    ("Bbiological_activity", "Biological activity"),
                    ("Chemical", "Chemical"),
                    ("Metabolite", "Metabolite"),
                    ("Protein", "Protein"),
                    ("Species", 'Species'),
                    ("Spectral_data", "Spectral data")]

    relationship_choices = [('ALL', 'All types'),
                ('ASSOCIATED_WITH','Associated with'),
                ('BINDS_WITH','Binds with'),
                ('ISOLATED_FROM','Isolated from'),
                ('PRODUCES','Produces'),
                ('METABOLITE_OF', 'Metabolite of'),
                ('METABOLISES_TO', 'Metabolises to')]
    relationship_type_1 = SelectField("Relationship 1 type", choices=relationship_choices)
    relationship_type_2 = SelectField("Relationship 2 type", choices=relationship_choices)

    node_1_type = SelectField("Node 1 type", choices=type_choices)
    node_2_type = SelectField("Node 2 type", choices=type_choices)
    node_3_type = SelectField("Node 3 type", choices=type_choices)

    search_1_exact = BooleanField("Node 1 exact match:")
    search_2_exact = BooleanField("Node 2 exact match:")
    search_3_exact = BooleanField("Node 3 exact match:")

class TagSearchForms(Form):
    searchList = FieldList(FormField(TagSearchForm), min_entries=1)
