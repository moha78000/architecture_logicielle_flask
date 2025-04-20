from flask import Blueprint , jsonify , Response
from flask_httpauth import HTTPTokenAuth
from spectree import SpecTree , SecurityScheme , BaseFile
from pydantic import BaseModel, Field
import archilog.models as models
from typing import Optional
from archilog.services import export_to_csv , import_from_csv
from uuid import UUID
import io





api = Blueprint("api", __name__, url_prefix="/api")
auth = HTTPTokenAuth(scheme='Bearer')
spec = SpecTree(
"flask",
security_schemes=[
    SecurityScheme(
        name="bearer_token",
        data={"type": "http", "scheme": "bearer"}
    )   
],
security=[{"bearer_token": []}]
)


tokens = {
"admin-token": {"username" : "admin" , "role": "admin"},
"user-token": {"username" : "user" , "role": "user"}
}


@auth.verify_token
def verify_token(token):
    if token in tokens:
        return tokens[token]
    return None


@auth.get_user_roles
def get_user_roles(user):
    return user.get("role", []) 

class CreateEntry(BaseModel):
    name: str = Field(min_length=2, max_length=100, description="Le nom de l'entrée")
    amount: float = Field(gt=0, description="Le montant de l'entrée")
    category: Optional[str] = Field(default=None, min_length=2, max_length=50, description="La catégorie de l'entrée (optionnelle)")



@api.route("/user", methods=["POST"])
@auth.login_required(role="admin")
@spec.validate(tags=["user"])   
def create_user(json: CreateEntry):
    models.create_entry(json.name, json.amount, json.category)
    # Ici, json contient un objet de type CreateEntry
    return jsonify({"message": f"User {json.name} created with amount {json.amount}"}), 201


class UpdateEntry(BaseModel):
    name: str = Field(min_length=2, max_length=100, description="Nouveau nom de l'entrée")  
    amount: float = Field(gt=0, description="Nouveau montant de l'entrée")
    category: Optional[str] = Field(default=None, min_length=2, max_length=50, description="Nouvelle catégorie de l'entrée (optionnelle)")


@api.route("/user/<id>", methods=["PUT"])
@auth.login_required(role="admin")
@spec.validate(tags=["user"])
def update_user(id: UUID, json: UpdateEntry):
    models.update_entry(UUID(id), json.name, json.amount, json.category)
    # Ici, json contient un objet de type UpdateEntry
    return jsonify({"message": f"User {id} updated"}), 200



class DeleteEntry(BaseModel):
    id: UUID = Field(description="ID de l'entrée à supprimer")

@api.route("/user/<id>", methods=["DELETE"])
@auth.login_required(role="admin")
@spec.validate(tags=["user"])
def delete_user(id: UUID):
    models.delete_entry(UUID(id))
    # Ici, json contient l'ID de l'utilisateur à supprimer
    return jsonify({"message": f"User {id} deleted"}), 204    



@api.route("/user", methods=["GET"])
@auth.login_required
@spec.validate(tags=["user"])
def get_entries():
    # Récupérer toutes les entrées depuis la base de données
    entries = models.get_all_entries()
    
    # Convertir les résultats en un format JSON pour la réponse
    entries_data = [{
        "id": entry.id,
        "name": entry.name,
        "amount": entry.amount,
        "category": entry.category
    } for entry in entries]
    
    # Retourner les entrées en format JSON
    return jsonify(entries_data), 200

@api.route("/user/<id>", methods=["GET"])
@auth.login_required
@spec.validate(tags=["user"])
def get_entry(id: UUID):
    entry = models.get_entry(UUID(id))

    if not entry:
        return jsonify({"error": "Entrée non trouvée"}), 404

    entry_data = {
            "id": str(entry["id"]),
            "name": entry["name"],
            "amount": entry["amount"],
            "category": entry["category"]
        }


    return jsonify(entry_data), 200

@api.route("/export/entries", methods=["GET"])
@spec.validate(tags=["import-export"])
@auth.login_required
def export_csv_api():
    csv_data = export_to_csv()
    return Response(csv_data.getvalue(), content_type="text/csv")

class File(BaseModel):
    file : BaseFile

@api.route("/import/entries", methods=["POST"])
@spec.validate(tags=["import-export"])
@auth.login_required(role="admin")
def import_csv(form : File): 
    filestream = io.StringIO(form.file.stream.read().decode("utf-8"))
    import_from_csv(filestream)
    return jsonify({"message": "CSV imported successfully"}), 201



@api.route('/')
@auth.login_required
def index():
    return "Hello, {}!".format(auth.current_user())


