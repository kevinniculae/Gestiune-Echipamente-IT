DROP DATABASE IF EXISTS gestiune_it;
CREATE DATABASE gestiune_it;
USE gestiune_it;

CREATE TABLE Locatii (
    id_locatie INT AUTO_INCREMENT PRIMARY KEY,
    denumire VARCHAR(100) NOT NULL,
    camera VARCHAR(20)
);

CREATE TABLE Utilizatori (
    id_utilizator INT AUTO_INCREMENT PRIMARY KEY,
    nume VARCHAR(100) NOT NULL
);

CREATE TABLE Echipamente (
    id_echipament INT AUTO_INCREMENT PRIMARY KEY,
    denumire VARCHAR(100) NOT NULL,
    nr_inventar VARCHAR(50) UNIQUE,
    tip VARCHAR(50),
    locatie_id INT,
    utilizator_id INT,
    activ BOOLEAN DEFAULT 1,
    data_achizitie DATE,
    FOREIGN KEY (locatie_id) REFERENCES Locatii(id_locatie),
    FOREIGN KEY (utilizator_id) REFERENCES Utilizatori(id_utilizator)
);

CREATE TABLE Interventii (
    id_interventie INT AUTO_INCREMENT PRIMARY KEY,
    id_echipament INT,
    data_interventie DATETIME DEFAULT CURRENT_TIMESTAMP,
    tip_interventie VARCHAR(50),
    descriere TEXT,
    tehnician VARCHAR(100),
    FOREIGN KEY (id_echipament) REFERENCES Echipamente(id_echipament)
);

INSERT INTO Locatii (denumire, camera) VALUES ('Sediu Central', '101');
INSERT INTO Utilizatori (nume) VALUES ('Popescu Ion');