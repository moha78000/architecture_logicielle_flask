import uuid
from flask import Blueprint, render_template, request, redirect, url_for, flash, Response  , abort
import archilog.models as models
import archilog.services as services
from flask_wtf import FlaskForm 
from wtforms import StringField, DecimalField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange, Optional
import logging


from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash , check_password_hash





web_ui = Blueprint("web_ui", __name__, url_prefix="/")

auth = HTTPBasicAuth()


# Configuration de l'authentification de base
users = {
    "admin": {
        "password": generate_password_hash("admin"),
        "role": "admin"
    },
    "user": {
        "password": generate_password_hash("user"),
        "role": "user"
    }
}



@auth.verify_password
def verify_password(username, password):
    """ Vérifie les identifiants de l'utilisateur """
    if username in users and check_password_hash(users[username]["password"], password):
        return username  # Retourne l'utilisateur connecté
    



@auth.get_user_roles
def get_user_roles(username):
    if username in users:
        return users[username]["role"]
    return [] # Aucun rôle si l'utilisateur n'existe pas
    



@web_ui.route("/")
@auth.login_required
def home():
    logging.info("Accès à la page d'accueil.")
    return render_template("home.html")

@web_ui.route("/entries")
@auth.login_required
def list_entries():
    logging.info(f"Consultation des entrées par {auth.current_user()}")
    entries = models.get_all_entries()
    logging.info(f"{len(entries)} entrées récupérées.")
    return render_template("entries.html", entries=entries)


@web_ui.route("/entry", methods=["GET"])
@auth.login_required
def get_entry():
    # Récupérer l'ID de la requête (depuis le formulaire)   
    entry_id = request.args.get("id")
    logging.info(f"Demande de récupération de l'entrée avec ID: {entry_id}")

    if entry_id:
        try:
            # Convertir l'ID en UUID
            entry_uuid = uuid.UUID(entry_id)
            entry = models.get_entry(entry_uuid)  # Récupérer l'entrée dans la base de données
            
            if entry:
                logging.info(f"Entrée trouvée: {entry}")
                return render_template("entry.html", entry=entry)  # Afficher l'entrée trouvée
            else:
                flash("Entrée non trouvée.", "error")  # Si l'entrée n'est pas trouvée
                logging.warning(f"Entrée non trouvée pour ID: {entry_id}")
        except ValueError:
            flash("ID invalide. Veuillez entrer un UUID valide.", "error")  # ID invalide
            logging.error(f"ID invalide reçu : {entry_id}")
    else:
        flash("Veuillez entrer un ID.", "error")
        logging.warning("Aucun ID fourni.")

    return redirect(url_for("web_ui.home"))  # Redirection vers la page d'accueil

class CreateForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(min=2, max=100)])
    amount = DecimalField("Amount", validators=[DataRequired(), NumberRange(min=0)])
    category = StringField("Category", validators=[Optional(), Length(min=2, max=50)])
    submit = SubmitField("Valider") 

@web_ui.route("/create", methods=["GET", "POST"])
@auth.login_required(role="admin")
def create_entry_form():
    logging.info(f"Accès au formulaire de création d'entrée. {auth.current_user()}")
    form = CreateForm()

    if form.validate_on_submit():  # Vérifier si le formulaire a été soumis avec des données valides
        name = form.name.data
        amount = form.amount.data
        category = form.category.data
        logging.info(f"Création d'une nouvelle entrée: {name}, {amount}, {category}")
        models.create_entry(name, amount, category)
        # Message de succès
        flash(f"Entrée créée: {name} ({amount}€) dans {category}", "success")

        
        logging.info(f"Entrée créée avec succès: {name}")
        # Rediriger vers la page d'accueil ou une autre page
        return redirect(url_for("web_ui.home"))

    return render_template("create.html", form=form)



class DeleteForm(FlaskForm):
    user_id = StringField("ID de l'entrée à supprimer", validators=[DataRequired()])
    submit = SubmitField("Supprimer")

@web_ui.route("/delete", methods=["GET", "POST"])
@auth.login_required(role="admin")
def delete_entry_form():
    logging.info(f"Accès au formulaire de suppression d'entrée. {auth.current_user()} ")
    form = DeleteForm()  # WTForms
    

    if form.validate_on_submit():
        user_id = form.user_id.data
        logging.info(f"Suppression de l'entrée avec ID: {user_id}")
        user_id = uuid.UUID(user_id)
        models.delete_entry(user_id)
        flash("Entrée supprimée avec succès.", "success")
        logging.info(f"Entrée avec ID {user_id} supprimée.")
        return redirect(url_for("web_ui.home"))

    return render_template("delete.html", form=form, entries= models.get_all_entries())



class UpdateForm(FlaskForm):
    id = StringField("ID", validators=[DataRequired()])
    name = StringField("Nom", validators=[DataRequired(), Length(min=2, max=100)])
    amount = DecimalField("Montant", validators=[
        DataRequired(),
        NumberRange(min=0, message="Le montant doit être positif")
    ])
    category = StringField("Catégorie", validators=[Optional(), Length(max=50)])
    submit = SubmitField("Mettre à jour")    

@web_ui.route("/update" , methods=["POST" , "GET"])
@auth.login_required(role="admin")
def update_entry_form():
    

    form = UpdateForm()

    if form.validate_on_submit():
        
        try:
            entry_id = uuid.UUID(form.id.data)
            name = form.name.data
            amount = form.amount.data
            category = form.category.data
            logging.info(f"Mise à jour de l'entrée: ID={entry_id}, Nom={name}, Montant={amount}, Catégorie={category}")
            models.update_entry(entry_id, name, amount, category)
            flash("Entrée mise à jour avec succès!", "success")
            logging.info(f"Entrée mise à jour avec succès: {entry_id}")
            return redirect(url_for('web_ui.home'))
        except Exception as e:
            flash(f"Erreur lors de la mise à jour : {str(e)}", "error")
            logging.error(f"Erreur lors de la mise à jour de l'entrée: {e}")

    return render_template("update.html", form=form, entries = models.get_all_entries())


@web_ui.route("/export_csv")
@auth.login_required(role=["admin", "user"])
def export_csv():
    logging.info("Exportation des données en CSV.")
    csv_file = services.export_to_csv()
    return Response(
        csv_file.getvalue(), 
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=export.csv"}
    )




@web_ui.route("/import_csv", methods=["GET", "POST"])
@auth.login_required(role="admin")
def import_csv():
    logging.info("Accès au formulaire d'importation CSV.")
    if request.method == "GET":
        return render_template("import_csv.html")  # Affiche le formulaire d'import

    file = request.files.get("csv_file")
    
    if file and file.filename.endswith(".csv"):
        logging.info(f"Importation du fichier CSV: {file.filename}")
        services.import_from_csv(file)
        flash("Fichier CSV importé avec succès!")
        logging.info("Fichier CSV importé avec succès.")
        return redirect(url_for("web_ui.home"))  # Redirige après succès

    flash("Le fichier doit être au format CSV.")
    logging.warning("Le fichier téléchargé n'est pas au format CSV.")
    return render_template("import_csv.html")  # Reste sur la page en cas d'erreur



@web_ui.errorhandler(500)
def handle_internal_error(error):
    flash("Erreur interne du serveur", "error")
    logging.exception(error)
    return redirect(url_for("web_ui.home"))


# Gestionnaire d'erreurs 404 (page introuvable)
def register_error_handlers(app):
    @app.errorhandler(404)
    def page_not_found(error):
        flash("Page non trouvée", "error")
        logging.error(f"Erreur 404: {error} - Page introuvable.")  # Logue l'erreur 404
        return render_template('404.html'), 404

# Route de test pour simuler une erreur 500
@web_ui.get("/users/create")
def users_create_form():
    abort(500)  # Force une erreur 500 pour tester le gestionnaire
    return render_template("users_create_form.html")