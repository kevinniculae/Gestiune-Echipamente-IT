=========================================================
PROIECT: Gestiune Echipamente IT - Parchet
=========================================================

DESCRIERE:
Aplicație web completă pentru evidența echipamentelor IT, managementul utilizatorilor 
și istoricul intervențiilor de service. Aplicația respectă cerințele clientului 
(Parchetul de pe lângă Tribunal) și include securitate pe bază de roluri.

TEHNOLOGII UTILIZATE:
- Backend: Python (Flask)
- Bază de date: MySQL
- Frontend: HTML5, CSS3, Bootstrap 5, JavaScript (jQuery + DataTables)

=========================================================
INSTRUCȚIUNI DE INSTALARE ȘI RULARE
=========================================================

PASUL 1: BAZA DE DATE
1. Deschideți phpMyAdmin (sau un alt client MySQL).
2. Creați o bază de date goală numită: gestiune_it
3. Importați fișierul 'gestiune_it.sql' (găsit în acest folder) în baza de date creată.
   *Notă: Aplicația este configurată pentru userul 'root' fără parolă (standard XAMPP).*

PASUL 2: DEPENDINȚE PYTHON
1. Deschideți terminalul (CMD/PowerShell) în folderul proiectului.
2. Instalați librăriile necesare rulând comanda:
   pip install flask mysql-connector-python werkzeug

PASUL 3: RULARE
1. În terminal, rulați comanda:
   python app.py
2. Deschideți browserul și accesați:
   http://127.0.0.1:5000

=========================================================
CONTURI DE ACCES (CREDENTIALE)
=========================================================

1. CONT ADMINISTRATOR (Acces Total):
   - Username: admin
   - Parola: admin
   *Poate gestiona tot inventarul, utilizatorii, locațiile și service-ul.*

2. CONT ANGAJAT (Acces Limitat):
   - Puteți crea un cont nou folosind butonul "Înregistrează-te" din pagina de Login.
   - Angajații văd doar pagina "Profilul Meu" cu echipamentele alocate lor.

=========================================================
FUNCȚIONALITĂȚI IMPLEMENTATE
=========================================================

1. Securitate & Roluri (RBAC):
   - Autentificare securizată (parole hash-uite).
   - Rute protejate (Admin vs Angajat).

2. Gestiune Echipamente:
   - CRUD complet (Adăugare, Modificare, Ștergere logică prin status).
   - Filtrare avansată (după Tip, Locație - dropdown, Status).
   - Statusuri: Activ vs Inactiv/Defect.

3. Service & Mentenanță:
   - Jurnal de intervenții per echipament.
   - Jurnal global de service (vizibil doar adminului).

4. Rapoarte & UI:
   - Dashboard cu statistici live (Total, Active, Defecte).
   - Generare Fișă Echipament (format optimizat pentru Print).
   - Sortare și Căutare rapidă în tabele.