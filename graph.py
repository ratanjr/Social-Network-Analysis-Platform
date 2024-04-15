from flask import Flask, render_template, jsonify, request
from neo4j import GraphDatabase
import pandas as pd
from pyvis.network import Network
import pyvis
pyvis.__version__


# app = Flask(__name__)
app = Flask(__name__, template_folder='templates')
app.secret_key = 'super secret key'

# Neo4j connection
driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "password")) 

@app.route('/')
def index():
    return render_template('main.html')

@app.route('/index')
def home():
    return render_template('index2.html')

@app.route('/influential-users')
def influential_users():
    influential_users = find_influential_users()
    return jsonify(influential_users)


@app.route('/query1')
def query1():
    with driver.session() as session:
        # Execute Neo4j query
        result = session.run("MATCH (n) RETURN n.id LIMIT 100")
        # Extract nodes from query result
        nodes = [record['n.id'] for record in result]
        # Render HTML template with query results
        return render_template('query1.html', nodes=nodes)
    
@app.route('/query2')
def query2():
    with driver.session() as session:
        # Execute Neo4j query to get nodes with relationships
        result = session.run("""
            MATCH (n:Node)-[r:CONNECTED_TO]->(m:Node)
            RETURN n.id, r, m.id
            LIMIT 100
        """)
        # Extract nodes and relationships from query result
        data = [(record['n.id'], record['r'].type, record['m.id']) for record in result]
        # Render HTML template with query results
        return render_template('query2.html', data=data)
    
@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        # Get user input from form submission
        search_term = request.form['node_id']
        # convert search term to integer
        search_term = int(search_term)
        with driver.session() as session:
            # Execute Neo4j query to search for nodes
            result = session.run("""
                MATCH (n:Node {id: $search_term})-[r:CONNECTED_TO]->(m:Node)
                RETURN n.id,r,m.id
            """, search_term=search_term)
            result2=session.run("""
                MATCH (n:Node {id: $search_term})-[r:CONNECTED_TO]->(m:Node)
                RETURN count(m)
            """, search_term=search_term)
            # Extract nodes from query result
            nodes = [(record['n.id'],record['r'].type,record['m.id']) for record in result]
            count = [record['count(m)'] for record in result2]
            # Render HTML template with search results
            return render_template('search_result.html', nodes=nodes,count=count)
    else:
        # Render HTML template with search form
        return render_template('search_form.html')
    
@app.route('/query3', methods=['GET', 'POST'])
def query3():
    if request.method == 'POST':
        # Get user input from form submission
        id1 = request.form['node_id1']
        id2 = request.form['node_id2']
        # convert search term to integer
        id1 = int(id1)
        id2 = int(id2)
        with driver.session() as session:
            # Execute Neo4j query to search for nodes
            result = session.run("""
                MATCH (u1:Node {id: $id1})-[:CONNECTED_TO]->(friend:Node)-[:CONNECTED_TO]->(u2:Node {id: $id2})
                RETURN friend.id

            """, id1=id1,id2=id2)
            result2 = session.run("""
                MATCH (u1:Node {id: $id1})-[:CONNECTED_TO]->(friend:Node)-[:CONNECTED_TO]->(u2:Node {id: $id2})
                RETURN count(friend)

            """, id1=id1,id2=id2)
            # Extract nodes from query result
            nodes = [(record['friend.id']) for record in result]
            count = [record['count(friend)'] for record in result2]
            # Render HTML template with search results
            return render_template('common_result.html', nodes=nodes,count=count)
    else:
        # Render HTML template with search form
        return render_template('common_form.html')
    
@app.route('/get_network_data')
def get_network_data():
    #Loading the data
    data = pd.read_csv("datasets/facebook_combined.txt", sep=" ", header=None)
    data.columns = ["person1", "person2"]
    sample = data.sample(5000, random_state = 1)
    sample.head(10)
    net = Network(notebook = True, cdn_resources = "remote",
                bgcolor = "#222222",
                font_color = "white",
                height = "750px",
                width = "100%",
    )
    # store the value in nodes and edges
    nodes = list(set([*sample.person1,*sample.person2]))
    edges = sample.values.tolist()
    net.add_nodes(nodes)
    net.add_edges(edges)
    net.show("templates/graph.html")
    return render_template('graph.html')

@app.route('/filter_graph')
def filter_graph():
    data = pd.read_csv("datasets/facebook_combined.txt", sep=" ", header=None)
    data.columns = ["person1", "person2"]
    sample = data.sample(5000, random_state = 1)
    sample.head(10)
    net = Network(notebook = True, cdn_resources = "remote",
                bgcolor = "#222222",
                font_color = "white",
                height = "750px",
                width = "100%",
                select_menu = True,
                filter_menu = True,
    )
    nodes = list(set([*sample.person1,*sample.person2]))
    edges = sample.values.tolist()
    net.add_nodes(nodes)
    net.add_edges(edges)
    net.show("templates/graph_with_menu.html")
    return render_template('graph_with_menu.html')


def find_influential_users():
    with driver.session() as session:
        result = session.run("""
            MATCH (u:Node)-[r:CONNECTED_TO]->(v:Node)
            RETURN u.id, COUNT(r) AS degree
            ORDER BY degree DESC
            LIMIT 10 ;
        """)

        influential_users = [record['u.id'] for record in result]
        return influential_users
    




if __name__ == '__main__':
    app.run(debug=True)



