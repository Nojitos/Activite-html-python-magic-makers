from flask import Flask, render_template, session, request, url_for, redirect
import os, bcrypt

#base de données
import pymongo

# création de l'app 
app = Flask(__name__)

#on crée une clef de chiffrement -> obligatoire pour utiliser session
#on crée une valeur au hasard de 24 bits
app.secret_key = os.urandom(24)

#connection db
mongo = pymongo.MongoClient('mongodb+srv://notix:test@cluster0.e7xl79u.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')

@app.route('/')
def index():
    db_annonce = mongo.annonce.annonce
    annonce = db_annonce.find({})
    if 'utilisateur' in session:
        return render_template('index.html', annonce=annonce, utilisateur=session['utilisateur'])
    else:
        return render_template('index.html', annonce=annonce)

@app.route('/register', methods=["GET", 'POST'])
def register():
    #On vérifie si la méthode est POST pour traiter le formulaire reçu
    if request.method == 'POST':
        #On récupère la table "users" de notre bdd
        db_users = mongo.db.Users
        #On vérifie que le nom d'utilisateur n'existe pas déjà
        if db_users.find_one({"nom":request.form['utilisateur']}):
            return render_template("register.html", erreur = "Veuillez sélectionner un nom inexistant.")
        else:
            #On ajoute l'utilisateur à bdd après avoir chiffré son mdp, si les mdp fournis sont égaux
            if request.form['mdp'] == request.form['verif_mdp']:
                #On chiffre le mdp
                #gensalt pour hash le mdp
                mdp_chiffre = bcrypt.hashpw(
                    request.form['mdp'].encode('utf-8'),
                    bcrypt.gensalt()
                )
                db_users.insert_one({"nom":request.form['utilisateur'],
                                     'mdp':mdp_chiffre})
                #On ajoute le cookie utilisateur de connexion
                session["utilisateur"] = request.form['utilisateur']
                return redirect(url_for('index'))
            
            else:
                #On affiche l'erreur : les mdp sont différents
                return render_template("register.html", erreur = 'Les mots de passe sont différents.')


    #Autrement si c'est GET on affiche la page
    else:
        return render_template('register.html')

@app.route('/login', methods=["GET", 'POST'])
def login():
    #On vérifie si la méthode est POST pour traiter le formulaire reçu
    if request.method == 'POST':
        #On récupère la table "users" de notre bdd
        db_users = mongo.db.Users
        user=db_users.find_one({"nom":request.form['utilisateur']})
        if user :
            if bcrypt.checkpw(request.form['mdp'].encode('utf-8'), user['mdp']):
                session['utilisateur'] = request.form['utilisateur']
                return redirect(url_for('index'))
        return render_template('login.html', erreur = 'Les identifiants ne sont pas reconnus.')
            
    else :
        return render_template('login.html')
    

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


@app.route('/publier_annonce', methods=['GET', 'POST'])
def publier_annonce():
    if 'utilisateur' in session:
        if request.method == 'POST':
            db_annonce = mongo.annonce.annonce
            titre = request.form['titre']
            description = request.form['description']

            if (titre and description):
                db_annonce.insert_one({
                    'titre' : titre,
                    'description' : description,
                    'auteur' : session['utilisateur']
                })
                return render_template('publier_annonce.html', succes="Annonce publiée avec succès.")

            else:
                return render_template('publier_annonce.html', erreur="Veuillez remplir tous les champs.")    
            
        else:
            return render_template('publier_annonce.html')

    else:     
        return redirect(url_for('login'))

#test de notre db
@app.route('/test')
def test():
    db_test = mongo.db.test
    test = db_test.find({})
    return render_template("test.html", test=test)

#éxecution de l'app
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=4200)
