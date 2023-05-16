import pickle

from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

projects = []
# print(type(projects))

with open('./projects.pickle', 'rb') as handle:
  my_data = pickle.load(handle)
  # when I load this pickle file, it is a dictionary not a list:
  # print(type(my_data))
  # print(my_data)
  # so I neet to put it's content to a list:
  projects = my_data['projects']

# print(type(projects))
# print(projects)


# ez egy endpoint, ha a böngészőben a főoldalt ("/") jeleníti meg. Ez egy HTTP REQUEST GET METHOD:
@app.route("/")
def home():
  return render_template("index.html.j2", name="István")


# ez az endpoint már nem a főoldalt, hanem ha az urlbe azt írom, hogy "/projects" akkor az alábbi return-t jeleníti meg:
@app.route("/projects")
def get_projects():
  # return jsonify({'projects': projects})
  # ha azt akarom, hogy ezt elérje másik domain-ről egy web alkalmazás, akkor így kell megírni (konkrét elérési út helyett a * bárkit enged hozzáférni):
  return jsonify({'projects': projects}), 200, {
      'Access-Control-Allow-Origin': 'http://127.0.0.1:5500'
  }


# projekt hozzáadása POST methoddal:
@app.route("/project", methods=['POST'])
def create_project():
  request_data = request.get_json()
  new_project = {'name': request_data['name'], 'tasks': request_data['tasks']}
  projects.append(new_project)
  return jsonify(new_project), 201


# ez pedig már egy változó beírását is lehetővé teszi az url-be, és annak megfelelő a response:
@app.route("/project/<string:proj_id>")
def get_project(proj_id):
  for project in projects:
    if project['project_id'] == proj_id:
      return jsonify(project)
  return jsonify({'message': 'project not found'}), 404


@app.route("/project/<string:name>/tasks")
def get_project_tasks(name):
  for project in projects:
    if project['name'] == name:
      return jsonify({'tasks': project['tasks']})
  return jsonify({'message': 'project not found'}), 404


# task hozzáadása endpoint (POST METHOD):
@app.route("/project/<string:name>/task", methods=['POST'])
def add_task_to_project(name):
  request_data = request.get_json()
  for project in projects:
    if 'name' in project and project['name'] == name:
      if 'completed' not in request_data or type(
          request_data['completed']) is not bool:
        return jsonify({'message': 'completed must be a boolean'}), 400
      new_task = {
          'name': request_data['name'],
          'completed': request_data['completed']
      }
      project['tasks'].append(new_task)
      return jsonify(new_task), 201
  return jsonify({'message': 'project not found'}), 404
