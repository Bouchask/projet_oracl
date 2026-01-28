from flask import Flask, render_template, redirect, url_for

# On spécifie les dossiers templates et static explicitement
app = Flask(__name__, template_folder='templates', static_folder='static')

# 1. Route racine -> Redirige vers Login
@app.route('/')
def index():
    return redirect(url_for('login_page'))

# 2. Page de Login
@app.route('/login')
def login_page():
    return render_template('login.html')

# 3. Dashboard Admin
@app.route('/admin')
def admin_dashboard():
    # Ici, on pourrait ajouter une vérification de session côté serveur
    # Mais pour l'instant, on laisse le JS gérer la sécurité basique
    return render_template('dashboard_admin.html')

# 4. Placeholders pour Teacher et Student (Pour éviter erreur 404 si on redirige)
@app.route('/teacher')
def teacher_dashboard():
    return "<h1>Bienvenue Professeur (Page en construction)</h1>"

@app.route('/student')
def student_dashboard():
    return "<h1>Bienvenue Étudiant (Page en construction)</h1>"

if __name__ == '__main__':
    # IMPORTANT: On lance sur le port 5001 pour ne pas bloquer le Backend (5000)
    print("Frontend running on http://localhost:5001")
    app.run(debug=True, port=5001)