import mysql.connector
from werkzeug.security import generate_password_hash

DB_HOST = "localhost"
DB_USER = "root"
DB_PASS = ""
DB_NAME = "gestiune_it"

def reset_admin_password():
    try:
        db = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASS,
            database=DB_NAME
        )
        cursor = db.cursor()

        parola_noua = "admin"
        hash_nou = generate_password_hash(parola_noua)
        
        print(f"Hash generat: {hash_nou}")

        cursor.execute("DELETE FROM Utilizatori WHERE username = 'admin'")
        
        sql = """
            INSERT INTO Utilizatori (nume, username, password_hash, role) 
            VALUES (%s, %s, %s, 'admin')
        """
        valori = ('Administrator Sistem', 'admin', hash_nou)
        
        cursor.execute(sql, valori)
        db.commit()
        
        print("\nSUCCESS! ✅")
        print("Contul 'admin' a fost recreat cu succes.")
        print("Acum te poți loga cu user: admin / parola: admin")

    except mysql.connector.Error as err:
        print(f"Eroare SQL: {err}")
    except Exception as e:
        print(f"Eroare Generală: {e}")
    finally:
        if 'db' in locals() and db.is_connected():
            cursor.close()
            db.close()

if __name__ == "__main__":
    reset_admin_password()