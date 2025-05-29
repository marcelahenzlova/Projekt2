import mysql.connector
from mysql.connector import Error


def pripojeni_db(test_mode=False):
    databaze = "task_manager_test" if test_mode else "task_manager"
    try:
        spojeni = mysql.connector.connect(
            host="localhost",
            user="root",
            password="1111",  
            database=databaze
        )
        if spojeni.is_connected():
            return spojeni
        
    except Error as e:
        print(f"Chyba při připojení k databázi: {e}")
        return None



def vytvoreni_tabulky(test_mode=False):
    conn = pripojeni_db(test_mode=test_mode)
    if conn is None:
        return

    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Ukoly (
            ID INT PRIMARY KEY AUTO_INCREMENT,
            Nazev VARCHAR(255) NOT NULL UNIQUE,
            Popis VARCHAR(255) NOT NULL,
            Stav ENUM('Nezahájeno', 'Probíhá', 'Hotovo') DEFAULT 'Nezahájeno',
            DatumVytvoreni TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    cursor.close()
    conn.close()
    print("Tabulka 'ukoly' byla v databazi 'task_manager' úspěšně vytvořena (nebo již existuje).")


def pridat_ukol(test_mode=False):
    while True:
        nazev = input("\nZadej název úkolu: ")
        popis = input("Zadej popis úkolu: ")

        try:
            if not nazev or not popis:
                raise ValueError("❌ Název i popis musí být vyplněny. Zkuste to znovu.")

            try:
                conn = pripojeni_db(test_mode=test_mode)
                if conn is None:
                    print("❌ Nepodařilo se připojit k databázi.")
                    return
                
                cursor = conn.cursor()
                cursor.execute("SELECT Nazev FROM ukoly WHERE Nazev = %s", (nazev,))
                existuje = cursor.fetchone()

                if existuje:
                    raise ValueError(f"❌ Úkol s názvem '{nazev}' už existuje. Zkuste jiný název.")

                cursor.execute("INSERT INTO ukoly (Nazev, Popis) VALUES (%s, %s)", (nazev, popis))
                id = cursor.lastrowid
                conn.commit()
                print(f"✅ Úkol '{id}. {nazev}' byl přidán.")

                cursor.close()
                conn.close()
                break

            except ValueError as e:
                print(f"Chyba: {e}")
                if test_mode:
                    break

            except Exception as e:
                print(f"❌ Neočekávaná chyba: {e}")
                break 

        except ValueError as e:
            print(f"Chyba: {e}")
            if test_mode:
                break

def zobrazit_ukoly(test_mode=False):
    try:
        conn = pripojeni_db(test_mode=test_mode)
        if conn is None:
            print("❌ Nepodařilo se připojit k databázi.")
            return

        cursor = conn.cursor()
        cursor.execute("SELECT ID, Nazev, Popis, Stav FROM Ukoly")
        rows = cursor.fetchall()
        cursor.execute("SELECT ID, Nazev, Popis, Stav FROM Ukoly WHERE Stav IN ('Nezahájeno', 'Probíhá')")
        filtr = cursor.fetchall()

        if not rows:
            print("\nSeznam úkolů je prázdný.")
        elif rows and not filtr:
            print("\nVšechny úkoly jsou již hotové.")
        else:
            print("\nSeznam nehotových úkolů:")
            for row in filtr:
                print(f"{row[0]}. {row[1]} – {row[2]} ({row[3]})")

        cursor.close()
        conn.close()
    
    except Exception as e:
        print(f"❌ Neočekávaná chyba: {e}")


def seznam_ukolu(test_mode=False):
    try:
        conn = pripojeni_db(test_mode=test_mode)
        if conn is None:
            print("❌ Nepodařilo se připojit k databázi.")
            return

        cursor = conn.cursor()
        cursor.execute("SELECT ID, Nazev, Popis, Stav FROM Ukoly")
        rows = cursor.fetchall()

        if not rows:
            print("\nSeznam úkolů je prázdný.")
        else:
            print("\nSeznam úkolů:")
            for row in rows:
                print(f"{row[0]}. {row[1]} – {row[2]} ({row[3]})")

        cursor.close()
        conn.close()
    
    except Exception as e:
        print(f"❌ Neočekávaná chyba: {e}")



def aktualizovat_ukol(test_mode=False):
    while True:
        try:
            stav = input("\nZadejte nový stav ('P' = Probíhá, 'H' = Hotovo): ").strip().upper()
            novy_stav = "Probíhá" if stav == "P" else "Hotovo" if stav == "H" else None
            if not novy_stav:
                raise ValueError("❌ Neplatná volba stavu, zkuste znovu.") 
            
            ukol_id = input("\nZadejte ID úkolu k aktualizaci: ")
            if not ukol_id.isdigit():
                raise ValueError("❌ ID musí být číslo ze zobrazeného seznamu úkolů, zkuste znovu.")
            ukol_id = int(ukol_id) 
                    
            try:
                conn = pripojeni_db(test_mode=test_mode)
                if conn is None:
                    print("❌ Nepodařilo se připojit k databázi.")
                    return
            
                cursor = conn.cursor()
                cursor.execute("SELECT Nazev FROM Ukoly WHERE ID = %s", (ukol_id,))
                nazev = cursor.fetchone()

                if not nazev:
                    raise ValueError(f"Číslo úkolu '{ukol_id}' nebylo nalezeno v seznamu úkolů, zkuste znovu.")
            
                cursor.execute("UPDATE Ukoly SET Stav = %s WHERE ID = %s", (novy_stav, ukol_id))
                conn.commit()
                print(f"Stav úkolu '{ukol_id}. {nazev[0]}' byl změněn na '{novy_stav}'.")

                cursor.close()
                conn.close()
                break

            except ValueError as e:
                print(f"Chyba: {e}")
                if test_mode:
                    break

            except Exception as e:
                print(f"❌ Neočekávaná chyba: {e}")
                break
        
        except ValueError as e:
            print(f"Chyba: {e}")
            if test_mode:
                break


def odstranit_ukol(test_mode=False):
    while True:
        try:
            ukol_id = input("\nZadejte ID úkolu k odstranění: ")
            if not ukol_id.isdigit():
                raise ValueError("❌ ID musí být číslo ze zobrazeného seznamu úkolů, zkuste znovu.")

            ukol_id = int(ukol_id)

            try:
                conn = pripojeni_db(test_mode=test_mode)
                if conn is None:
                    print("❌ Nepodařilo se připojit k databázi.")
                    return
                    
                cursor = conn.cursor()
                cursor.execute("SELECT Nazev FROM Ukoly WHERE ID = %s", (ukol_id,))
                nazev = cursor.fetchone()

                if not nazev:
                    raise ValueError(f"Číslo úkolu '{ukol_id}' nebylo nalezeno v seznamu úkolů, zkuste znovu.")
                        
                cursor.execute("DELETE FROM Ukoly WHERE ID = %s", (ukol_id,))
                conn.commit()
                print(f"Úkol '{ukol_id}. {nazev[0]}' byl odstraněn.")

                cursor.close()
                conn.close()
                break
                
            except ValueError as e:
                print(f"Chyba: {e}")
                if test_mode:
                    break

            except Exception as e:
                print(f"❌ Neočekávaná chyba: {e}")
                break
        
        except ValueError as e:
            print(f"Chyba: {e}")
            if test_mode:
                break


def hlavni_menu():
    while True:
        print("\nSprávce úkolu - Hlavní menu")
        print("1. Přidat úkol")
        print("2. Zobrazit úkoly")
        print("3. Aktualizovat úkol")
        print("4. Odstranit úkol")
        print("5. Ukončit program")
        volba = input("Vyberte možnost (0-5): ")

        if volba == "1":
            pridat_ukol()
            
        elif volba == "2":
            zobrazit_ukoly()

        elif volba == "3":
            seznam_ukolu()
            aktualizovat_ukol() 

        elif volba == "4":
            seznam_ukolu()
            odstranit_ukol()

        elif volba == "5":
            print("\nKonec programu.")
            break

        else:
            print("\nNeplatná volba, vyberte číslo 1–5.")


if __name__ == "__main__":
    vytvoreni_tabulky()
    hlavni_menu()