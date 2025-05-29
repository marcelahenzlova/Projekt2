import mysql.connector
import pytest
from tests.test_init import vytvoreni_test_tabulky, vytvoreni_test_tabulky_app
from src.Vylepseny_task_manager import pripojeni_db, pridat_ukol, aktualizovat_ukol, odstranit_ukol

#vytvoreni tabulky pred testy
@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    vytvoreni_test_tabulky()

#oddelena databaze
@pytest.fixture(scope="module")
def db_connection():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="1111",
        database="task_manager_test"
    )
    yield conn
    conn.close()

#uklid testovaci databaze pred kazdym testem
@pytest.fixture(autouse=True)
def clean_ukoly_table(db_connection):
    cursor = db_connection.cursor()
    cursor.execute("DELETE FROM Ukoly")
    cursor.execute("ALTER TABLE Ukoly AUTO_INCREMENT = 1")
    db_connection.commit()
    cursor.close()



#testovani funkcnosti databaze funkce 'pridat_ukol' pro ruzne vstupy 'nazev' a 'popis'
@pytest.mark.pridat_ukol
@pytest.mark.parametrize("nazev, popis, validni", [
    ("Test_nazev", "Test_popis", True),
    ("Duplicitni_nazev", "Duplicitni_popis", False),
    ("BezPopisu", None, False),
    (None, "BezNazvu", False),
    (None, None, False)
])
def test_db_pridat_ukol(nazev, popis, validni, db_connection, monkeypatch):
    cursor = db_connection.cursor()
    result = cursor.execute("INSERT INTO ukoly (Nazev, Popis) VALUES ('Duplicitni_nazev', 'Duplicitni_popis')")
    print(result)
    db_connection.commit()

    cursor.execute("SELECT COUNT(*) FROM ukoly WHERE Nazev = %s", (nazev,))
    pocet_pred = cursor.fetchone()[0]

    vstupy = iter([
    "" if nazev is None else nazev,
    "" if popis is None else popis
    ])
    monkeypatch.setattr("builtins.input", lambda _: next(vstupy))

    pridat_ukol(test_mode=True)
    cursor.execute("SELECT COUNT(*) FROM ukoly WHERE Nazev = %s", (nazev,))
    pocet_po = cursor.fetchone()[0]

    if validni:
        assert pocet_po > pocet_pred
    else:
        assert pocet_po == pocet_pred

    cursor.close()



#testovani vystupnich hlasek funkce 'pridat_ukol' pro ruzne vstupy 'nazev' a 'popis'
@pytest.mark.pridat_ukol
@pytest.mark.parametrize("nazev, popis, ocekavany_vystup", [
    ("Test_nazev", "Test_popis", "byl přidán"),
    ("Duplicitni_nazev", "Duplicitni_popis", "už existuje"),
    ("BezPopisu", None, "musí být vyplněny"),
    (None, "BezNazvu", "musí být vyplněny"),
    (None, None, "musí být vyplněny")
])
def test_print_pridat_ukol(nazev, popis, ocekavany_vystup, db_connection, monkeypatch, capsys):
    cursor = db_connection.cursor()
    cursor.execute("INSERT INTO Ukoly (Nazev, Popis) VALUES ('Duplicitni_nazev', 'Duplicitni_popis')")
    db_connection.commit()
    
    vstupy = iter([
    "" if nazev is None else nazev,
    "" if popis is None else popis
    ])
    monkeypatch.setattr("builtins.input", lambda _: next(vstupy))

    pridat_ukol(test_mode=True)

    skutecny_vystup = capsys.readouterr().out
    assert ocekavany_vystup in skutecny_vystup



#testovani funkcnosti databaze funkce 'aktualizovat_ukol' pro ruzne vstupy 'id' a 'stav'
@pytest.mark.aktualizovat_ukol
@pytest.mark.parametrize("id, validni", [
    (1, True),
    (1000, False),
    ("Text", False),
    (None, False)
])
@pytest.mark.parametrize("pocatecni_stav, zvoleny_stav, ocekavany_stav", [
    ("Nezahájeno", "P", "Probíhá"),
    ("Nezahájeno", "H", "Hotovo"),
    ("Nezahájeno", "X", None) 
])
def test_db_aktualizovat_ukol(id, validni, pocatecni_stav, zvoleny_stav, ocekavany_stav, db_connection, monkeypatch, capsys):
    cursor = db_connection.cursor()
    cursor.execute("INSERT INTO Ukoly (Nazev, Popis, Stav) VALUES ('Nazev_k_aktualizaci', 'Popis_k_aktualizaci', %s)", (pocatecni_stav,))
    db_connection.commit()

    vstupID = str(id) if id is not None else ""
    vstupy = iter([zvoleny_stav, str(vstupID)])
    monkeypatch.setattr("builtins.input", lambda _: next(vstupy))

    aktualizovat_ukol(test_mode=True)

    cursor.execute("SELECT Stav FROM Ukoly")
    novy_stav = cursor.fetchone()[0]

    if validni and ocekavany_stav:
        assert novy_stav == ocekavany_stav
    else:
        assert novy_stav == pocatecni_stav

    cursor.close()



#testovani vystupnich hlasek funkce 'aktualizovat_ukol' pro ruzne vstupy 'id' a 'stav'
@pytest.mark.aktualizovat_ukol
@pytest.mark.parametrize("id, ocekavany_vystup", [
    (1, "byl změněn"),
    (1000, "nebylo nalezeno v seznamu úkolů"),
    ("Text", "musí být číslo ze zobrazeného seznamu úkolů"),
    (None, "musí být číslo ze zobrazeného seznamu úkolů")
])
@pytest.mark.parametrize("pocatecni_stav, zvoleny_stav, ocekavany_stav", [
    ("Nezahájeno", "P", "Probíhá"),
    ("Nezahájeno", "H", "Hotovo"),
    ("Nezahájeno", "X", None)
])
def test_print_aktualizovat_ukol(id, ocekavany_vystup, pocatecni_stav, zvoleny_stav, ocekavany_stav, db_connection, monkeypatch, capsys):
    cursor = db_connection.cursor()
    cursor.execute("INSERT INTO Ukoly (Nazev, Popis, Stav) VALUES ('Nazev_k_aktualizaci', 'Popis_k_aktualizaci', %s)", (pocatecni_stav,))
    db_connection.commit()

    vstupID = str(id) if id is not None else ""
    vstupy = iter([zvoleny_stav, str(vstupID)])
    monkeypatch.setattr("builtins.input", lambda _: next(vstupy))

    aktualizovat_ukol(test_mode=True)

    skutecny_vystup = capsys.readouterr().out

    if not ocekavany_stav:
        assert "Neplatná volba stavu, zkuste znovu." in skutecny_vystup  
    else:
        assert ocekavany_vystup in skutecny_vystup

    cursor.close()



#testovani funkcnosti databaze funkce 'odstranit_ukol' pro ruzne vstupy 'id'
@pytest.mark.odstranit_ukol
@pytest.mark.parametrize("id, validni", [
    (1, True),
    (1000, False),
    ("Text", False),
    (None, False)
])
def test_db_odstranit_ukol(id, validni, db_connection, monkeypatch):
    cursor = db_connection.cursor()
    cursor.execute("INSERT INTO Ukoly (Nazev, Popis) VALUES ('Nazev_k_smazani', 'Popis_k_smazani')")
    db_connection.commit()

    cursor.execute("SELECT COUNT(*) FROM Ukoly")
    pocet_pred = cursor.fetchone()[0]

    vstupID = str(id) if id is not None else ""
    vstupy = iter([vstupID])
    monkeypatch.setattr("builtins.input", lambda _: next(vstupy))

    odstranit_ukol(test_mode=True)

    cursor.execute("SELECT COUNT(*) FROM Ukoly")
    pocet_po = cursor.fetchone()[0]

    if validni:
        assert pocet_po < pocet_pred
    else:
        assert pocet_po == pocet_pred

    cursor.close()



#testovani vystupnich hlasek funkce 'odstranit_ukol' pro ruzne vstupy 'id'
@pytest.mark.odstranit_ukol
@pytest.mark.parametrize("id, ocekavany_vystup", [
    (1, "byl odstraněn"),
    (1000, "nebylo nalezeno v seznamu úkolů"),
    ("Text", "musí být číslo ze zobrazeného seznamu úkolů"),
    (None, "musí být číslo ze zobrazeného seznamu úkolů")
])
def test_print_odstranit_ukol(id, ocekavany_vystup, db_connection, monkeypatch, capsys):
    cursor = db_connection.cursor()
    cursor.execute("INSERT INTO Ukoly (Nazev, Popis) VALUES ('Nazev_k_smazani', 'Popis_k_smazani')")
    db_connection.commit()

    vstup = str(id) if id is not None else ""
    vstupy = iter([vstup])
    monkeypatch.setattr("builtins.input", lambda _: next(vstupy))

    odstranit_ukol(test_mode=True)

    skutecny_vystup = capsys.readouterr().out
    assert ocekavany_vystup in skutecny_vystup
