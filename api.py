import os
from flask import Flask, request
from flask_restplus import Resource, Api, fields
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

app = Flask(__name__)
api = Api(app, title="My API")
CORS(app)
db = SQLAlchemy(app)
db.init_app(app)
db.create_all()

nsp = api.namespace('Projects', description='Manage projects')
nst = api.namespace('Teammates', description='Manage teammates')

#DB MODELS >>>
class Teammate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=False)
    function = db.Column(db.String(64), index=True, unique=True)

    def serialize(self):
        return "'id': '{}', 'name':'{}', 'function':'{}'".format(self.id, self.name, self.function)

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64), index=True, unique=True)
    description = db.Column(db.String(64), index=True, unique=True)

    def serialize(self):
        return "'id': '{}', 'title':'{}', 'description':'{}'".format(self.id, self.title, self.description)

#CONFIG >>>
basedir = os.path.abspath(os.path.dirname(__file__))
app.config.update(
    TESTING=True,
    SECRET_KEY='mySecretKey',
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
)

#MODELS >>>
project = api.model('Project', {
    'title' : fields.String(required=True, description='the project title'),
    'description' : fields.String(required=True, description='the project description')
})

teammate = api.model('Teammate', {
    'name' : fields.String(required=True, description='the teammate name'),
    'function' : fields.String(required=True, description='the teammate function')
})

#REQUEST PARSER >>>
""" project_parser = api.parser()
project_parser.add_argument('id', type=int, help='The id')
project_parser.add_argument('title', type=str, help='The project title')
project_parser.add_argument('description', type=str, help='The project description')

teammate_parser = api.parser()
teammate_parser.add_argument('id', type=int, help='The id')
teammate_parser.add_argument('name', type=str, help='The teammate name')
teammate_parser.add_argument('function', type=str, help='The teammate function') """

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'teammate': Teammate, 'project': Project}

#PROJECT >>>
@nsp.route('/')
class ProjectList(Resource):
    def get(self):
        '''List projects'''
        data = Project.query.all()
        res = [d.serialize() for d in data]
        return res

    @nsp.marshal_with(project)
    @nsp.expect(project)
    def post(self):
        '''Add a new project'''
        data = request.get_json()
        title = data['title']
        description = data['description']
        new_project = Project(title=title, description=description)
        db.session.add(new_project)
        db.session.commit()
        return new_project, 200

@nsp.route('/<int:id>')
class SingleProject(Resource):
    def get(self, id):
        '''Display a single project'''
        project = Project.query.filter_by(id=id).first()
        res = project.serialize()
        return res, 200
    
    @nsp.marshal_with(project)
    @nsp.expect(project)
    def put(self, id):
        '''Update a project'''
        data = request.get_json()
        title = data['title']
        description = data['description']
        p = Project.query.filter_by(id=id).first()
        p.title = title
        p.description = description
        db.session.commit()
        return 'Project updated', 200

    def delete(self, id):
        '''Delete a project'''
        p = Project.query.filter_by(id=id).first()
        db.session.delete(p)
        db.session.commit()
        return 'Project deleted', 200

#TEAMMATES >>>
@nst.route('/')
class TeammateList(Resource):
    def get(self):
        '''List teammates'''
        data = Teammate.query.all()
        res = [d.serialize() for d in data]
        return res, 200

    @nst.marshal_with(teammate)
    @nst.expect(teammate)
    def post(self):
        '''Add a new teammate'''
        data = request.get_json()
        name = data['name']
        function = data['function']
        new_teammate = Teammate(name=name, function=function)
        db.session.add(new_teammate)
        db.session.commit()
        return 'Teammate added', 200

@nst.route('/<int:id>')
class ShowTeammate(Resource):
    def get(self, id):
        '''Display a single teammate'''
        teammate = Teammate.query.filter_by(id=id).first()
        res = teammate.serialize()
        return res, 200

    def delete(self, id):
        '''Delete a teammate'''
        t = Teammate.query.filter_by(id=id).first()
        db.session.delete(t)
        db.session.commit()
        return 'Teammate deleted', 200

if __name__ == '__main__':
    app.run(debug=True, port='8000')