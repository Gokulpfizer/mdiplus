from flask import Flask
import json
from bson.json_util import dumps
from flask_restful import Resource, Api
from flask_pymongo import PyMongo
from app.views import mdi_plus_users,mdi_plus_projects,mdi_plus_attributes,mdi_plus_app_json,mdi_plus_meta_data,\
mdi_plus_measures,mdi_plus_atrribute_cells,mdi_plus_header_cells,mdi_plus_preferences,mdi_plus_data_grid
from app import app


#app = Flask(__name__)


api = Api(app)


api.add_resource(mdi_plus_users.Login, '/login')
api.add_resource(mdi_plus_users.Users, '/users')
api.add_resource(mdi_plus_projects.Projects, '/projects')
api.add_resource(mdi_plus_attributes.Comporators, '/comporators')

#DataGridComporators
api.add_resource(mdi_plus_attributes.DataGridComporators, '/dataGridComporators')

#DataGridAttributes
api.add_resource(mdi_plus_attributes.DataGridAttributes, '/dataGridAttributes')



#dataGridPreferences


api.add_resource(mdi_plus_attributes.DataGridPreferences, '/dataGridPreferences')


api.add_resource(mdi_plus_attributes.Preferences, '/preferences')
api.add_resource(mdi_plus_attributes.Attributes, '/attributes')
api.add_resource(mdi_plus_attributes.AttributeType, '/attribute_type')
api.add_resource(mdi_plus_projects.ProjectAccess, '/project_access')
api.add_resource(mdi_plus_app_json.MdiPlusAppJson, '/mdi_plus_app_json')
api.add_resource(mdi_plus_meta_data.MetaData, '/metadata')
api.add_resource(mdi_plus_measures.Measures, '/measures')
api.add_resource(mdi_plus_measures.SourceDocuments, '/source_documents')
api.add_resource(mdi_plus_projects.ProjectsList, '/projects_list')

api.add_resource(mdi_plus_measures.ReadMeasures, '/read_measures')
api.add_resource(mdi_plus_measures.ReadNotes, '/read_notes')
api.add_resource(mdi_plus_measures.Analysis, '/analysis')
api.add_resource(mdi_plus_users.AppointmentController, '/render_temp')
api.add_resource(mdi_plus_atrribute_cells.Attributecells, '/attribute_cells')
api.add_resource(mdi_plus_header_cells.Headercells, '/header_cells')
api.add_resource(mdi_plus_preferences.PreferenceCells, '/preference_cells')
#api.add_resource(Users, '/users')

# api.add_resource(mdi_plus_atrribute_cells.mdi_plus_cell_entry, '/v1/mdi_plus_cell')

api.add_resource(mdi_plus_atrribute_cells.ReadProjectCells, '/v1/read/projectcells')

api.add_resource(mdi_plus_atrribute_cells.MultiAttributeCells, '/v1/mdi_plus_cellmulti')

api.add_resource(mdi_plus_data_grid.DataGrid, '/v1/read/data_grid')

api.add_resource(mdi_plus_data_grid.DataGridUpdate, '/v1/update/data_grid')


if __name__ == '__main__':
    app.run(host="162.48.180.89", port=5000, debug=True)
