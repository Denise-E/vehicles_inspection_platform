from flask import Blueprint

inspections = Blueprint('inspections', __name__)

# Inspections routes TODO: Define inspection model
@inspections.route("/register", methods=['POST'])
# Register a new inspection
def register_inspection():
    return {"msg": 'Inspection registered!'}, 200
    
@inspections.route("/profile/<int:inspection_id>", methods=['GET'])
# Get inspection details by id
def inspection_details(inspection_id):
    return {"msg": 'Inspection profile!'}, 200
    
