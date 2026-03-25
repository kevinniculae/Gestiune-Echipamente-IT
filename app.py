from flask import Flask, render_template, jsonify, request, session, redirect, url_for, flash
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

app = Flask(__name__)
app.secret_key = 'cheie_secreta_proiect_it'

def get_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="gestiune_it"
    )


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('role') != 'admin':
            flash("Acces interzis! Doar administratorul are acces aici.", "danger")
            return redirect(url_for('profil_meu'))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Utilizatori WHERE username = %s", (username,))
        user = cursor.fetchone()
        cursor.close()
        db.close()

        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id_utilizator']
            session['username'] = user['username']
            session['nume'] = user['nume']
            session['role'] = user['role']
            
            if user['role'] == 'admin':
                return redirect(url_for('dashboard'))
            else:
                return redirect(url_for('profil_meu'))
        else:
            flash('Date incorecte!', 'danger')
            
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        nume_real = request.form['nume']
        username = request.form['username']
        password = request.form['password']
        email = request.form.get('email')

        hashed_password = generate_password_hash(password)

        db = get_db()
        cursor = db.cursor()
        try:
            cursor.execute("INSERT INTO Utilizatori (nume, username, password_hash, email, role) VALUES (%s, %s, %s, %s, 'user')", 
                           (nume_real, username, hashed_password, email))
            db.commit()
            flash('Cont creat! Te poți loga.', 'success')
            return redirect(url_for('login'))
        except mysql.connector.Error:
            flash('Username-ul există deja.', 'danger')
        finally:
            cursor.close()
            db.close()

    return render_template('signup.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/profil')
@login_required
def profil_meu():
    user_id = session['user_id']
    db = get_db()
    cursor = db.cursor(dictionary=True)
    
    query = """
        SELECT e.*, l.denumire as locatie_nume 
        FROM Echipamente e
        LEFT JOIN Locatii l ON e.locatie_id = l.id_locatie
        WHERE e.utilizator_id = %s
    """
    cursor.execute(query, (user_id,))
    echipamente = cursor.fetchall()
    
    cursor.close()
    db.close()
    return render_template('profil_meu.html', echipamente=echipamente)



@app.route('/')
def index():
    if 'user_id' in session:
        if session.get('role') == 'admin':
            return redirect(url_for('dashboard'))
        return redirect(url_for('profil_meu'))
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
@admin_required
def dashboard():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    
    cursor.execute("SELECT COUNT(*) as total FROM Echipamente")
    total = cursor.fetchone()['total']
    
    cursor.execute("SELECT COUNT(*) as active FROM Echipamente WHERE activ=1")
    active = cursor.fetchone()['active']
    
    defecte = total - active

    cursor.execute("""
        SELECT COUNT(*) as interventii_luna 
        FROM Interventii 
        WHERE MONTH(data_interventie) = MONTH(CURRENT_DATE()) 
        AND YEAR(data_interventie) = YEAR(CURRENT_DATE())
    """)
    interventii_luna = cursor.fetchone()['interventii_luna']
    
    cursor.close()
    db.close()
    
    return render_template('dashboard.html', total=total, active=active, defecte=defecte, interventii_luna=interventii_luna)

@app.route('/echipamente')
@login_required
@admin_required
def echipamente():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Locatii")
    locatii = cursor.fetchall()
    cursor.execute("SELECT * FROM Utilizatori WHERE role != 'admin' OR role IS NULL") 
    utilizatori = cursor.fetchall()
    cursor.close()
    db.close()
    return render_template('echipamente.html', locatii=locatii, utilizatori=utilizatori)


@app.route('/api/echipamente/adauga', methods=['POST'])
@login_required
@admin_required
def adauga_echipament():
    data = request.json
    db = get_db()
    cursor = db.cursor()
    query = """INSERT INTO Echipamente (denumire, nr_inventar, tip, modalitate_dobandire, specificatii, software, locatie_id, utilizator_id, data_primire, activ)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 1)"""
    values = (
        data.get('denumire'), data.get('nr_inventar'), data.get('tip'), 
        data.get('modalitate_dobandire'), data.get('specificatii'), 
        data.get('software'), data.get('locatie_id'), data.get('utilizator_id'),
        data.get('data_primire')
    )
    try:
        cursor.execute(query, values)
        db.commit()
        return jsonify({"message": "Succes"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        db.close()


@app.route('/api/echipamente', methods=['GET'])
@login_required
def api_echipamente():
    if session.get('role') != 'admin':
        return jsonify({"error": "Unauthorized"}), 403
        
    db = get_db()
    cursor = db.cursor(dictionary=True)
    query = """
        SELECT e.id_echipament AS id, e.nr_inventar, e.denumire, e.tip,
        CONCAT(l.denumire, ', ', l.camera) AS locatie, u.nume AS utilizator, e.activ
        FROM Echipamente e
        LEFT JOIN Locatii l ON e.locatie_id = l.id_locatie
        LEFT JOIN Utilizatori u ON e.utilizator_id = u.id_utilizator
    """
    cursor.execute(query)
    rows = cursor.fetchall()
    db.close()
    return jsonify(rows)

@app.route('/api/echipamente/filtre', methods=['GET'])
@login_required
def api_filtre():
    tip = request.args.get('tip')
    locatie_id = request.args.get('locatie')
    status = request.args.get('status')

    db = get_db()
    cursor = db.cursor(dictionary=True)

    query = """
        SELECT 
            e.id_echipament AS id, e.nr_inventar, e.denumire, e.tip,
            CONCAT(l.denumire, ', ', l.camera) AS locatie,
            u.nume AS utilizator, e.activ
        FROM Echipamente e
        LEFT JOIN Locatii l ON e.locatie_id = l.id_locatie
        LEFT JOIN Utilizatori u ON e.utilizator_id = u.id_utilizator
        WHERE 1=1
    """
    params = []

    if tip:
        query += " AND e.tip = %s"
        params.append(tip)
    
    if locatie_id and locatie_id != "":
        query += " AND e.locatie_id = %s"
        params.append(int(locatie_id))

    if status and status != "":
        query += " AND e.activ = %s"
        params.append(int(status))

    try:
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return jsonify(rows)
    except Exception as e:
        print(f"Eroare SQL Filtrare: {e}")
        return jsonify({"error": "Eroare la filtrare"}), 500
    finally:
        cursor.close()
        db.close()

@app.route('/api/echipament/info/<int:id>', methods=['GET'])
@login_required
def get_info(id):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Echipamente WHERE id_echipament=%s", (id,))
    data = cursor.fetchone()
    db.close()
    
    if data and data.get('data_primire'):
        data['data_primire'] = str(data['data_primire'])

    return jsonify(data)

@app.route('/api/echipamente/modifica/<int:id>', methods=['POST'])
@login_required
@admin_required
def modifica_echipament(id):
    data = request.json
    db = get_db()
    cursor = db.cursor()

    query = """
        UPDATE Echipamente 
        SET denumire=%s, nr_inventar=%s, tip=%s, modalitate_dobandire=%s, 
            specificatii=%s, software=%s, locatie_id=%s, utilizator_id=%s, 
            data_primire=%s, activ=%s
        WHERE id_echipament=%s
    """
    values = (
        data.get('denumire'), data.get('nr_inventar'), data.get('tip'),
        data.get('modalitate_dobandire'), data.get('specificatii'),
        data.get('software'), data.get('locatie_id'), data.get('utilizator_id'),
        data.get('data_primire'),
        data.get('activ'), 
        id
    )

    try:
        cursor.execute(query, values)
        db.commit()
        return jsonify({"message": "Actualizat cu succes"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        db.close()

@app.route('/echipament/<int:id_echipament>')
@login_required
def fisa_echipament(id_echipament):

    db = get_db()
    cursor = db.cursor(dictionary=True)
    query = """SELECT e.*, l.denumire as locatie, u.nume as utilizator FROM Echipamente e
               LEFT JOIN Locatii l ON e.locatie_id = l.id_locatie
               LEFT JOIN Utilizatori u ON e.utilizator_id = u.id_utilizator WHERE id_echipament=%s"""
    cursor.execute(query, (id_echipament,))
    echip = cursor.fetchone()
    
    cursor.execute("SELECT * FROM Interventii WHERE id_echipament=%s", (id_echipament,))
    interventii = cursor.fetchall()
    db.close()
    return render_template('fisa_echipament.html', echipament=echip, interventii=interventii)

@app.route('/api/interventii/adauga', methods=['POST'])
@login_required
@admin_required
def adauga_int():
    data = request.json
    db = get_db()
    cursor = db.cursor()
    cursor.execute("INSERT INTO Interventii (id_echipament, tip_interventie, descriere, tehnician, data_interventie) VALUES (%s,%s,%s,%s,NOW())",
                   (data.get('id_echipament'), data.get('tip_interventie'), data.get('descriere'), data.get('tehnician')))
    db.commit()
    db.close()
    return jsonify({"ok": True})

@app.route('/locatii')
@login_required
def locatii():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Locatii")
    rows = cursor.fetchall()
    db.close()
    return render_template('locatii.html', locatii=rows)

@app.route('/utilizatori')
@login_required
@admin_required
def users():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("""SELECT u.*, COUNT(e.id_echipament) as nr_echipamente 
                      FROM Utilizatori u 
                      LEFT JOIN Echipamente e ON u.id_utilizator = e.utilizator_id 
                      WHERE u.role != 'admin' 
                      GROUP BY u.id_utilizator""")
    rows = cursor.fetchall()
    db.close()
    return render_template('utilizatori.html', utilizatori=rows)

@app.route('/interventii')
@login_required
@admin_required
def all_interventii():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT i.*, e.denumire, e.nr_inventar FROM Interventii i JOIN Echipamente e ON i.id_echipament=e.id_echipament ORDER BY data_interventie DESC")
    rows = cursor.fetchall()
    db.close()
    return render_template('interventii.html', interventii=rows)

@app.route('/software')
@login_required
def soft():
    return render_template('software.html', programe=[])

@app.route('/api/utilizator/<int:id>/echipamente', methods=['GET'])
@login_required
def get_echipamente_user(id):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    
    query = """
        SELECT denumire, nr_inventar, tip
        FROM Echipamente 
        WHERE utilizator_id = %s
    """
    cursor.execute(query, (id,))
    items = cursor.fetchall()
    
    cursor.close()
    db.close()
    return jsonify(items)

if __name__ == '__main__':
    app.run(debug=True)