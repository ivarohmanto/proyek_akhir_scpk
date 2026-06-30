
import mysql.connector
import pandas as pd
from config import DB_CONFIG

class Database:
    def __init__(self):
        self.conn = None
        self.cursor = None
        
    def connect(self):
        try:
            self.conn = mysql.connector.connect(**DB_CONFIG)
            self.cursor = self.conn.cursor()
            return True
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            return False
    
    def disconnect(self):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
    
    def create_tables(self):
        # Hanya tabel hasil_rekomendasi
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS hasil_rekomendasi (
                id INT AUTO_INCREMENT PRIMARY KEY,
                car_name VARCHAR(100),
                year INT,
                selling_price FLOAT,
                umur INT,
                kms_driven INT,
                rasio_harga FLOAT,
                owner INT,
                fuel_type VARCHAR(20),
                transmission VARCHAR(20),
                skor_fuzzy FLOAT,
                status_rekomendasi VARCHAR(30),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.conn.commit()
    
    def save_rekomendasi(self, car_name, year, selling_price, umur, kms_driven, 
                          rasio_harga, owner, fuel_type, transmission, skor_fuzzy, status):
        self.cursor.execute("""
            INSERT INTO hasil_rekomendasi (car_name, year, selling_price, umur, 
                kms_driven, rasio_harga, owner, fuel_type, transmission, skor_fuzzy, status_rekomendasi)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (car_name, year, selling_price, umur, kms_driven, rasio_harga, 
              owner, fuel_type, transmission, skor_fuzzy, status))
        self.conn.commit()
    
    def get_all_rekomendasi(self):
        self.cursor.execute("""
            SELECT * FROM hasil_rekomendasi ORDER BY skor_fuzzy DESC, created_at DESC
        """)
        columns = [desc[0] for desc in self.cursor.description]
        return pd.DataFrame(self.cursor.fetchall(), columns=columns)
    
    def delete_rekomendasi_by_id(self, id_rekom):
        self.cursor.execute("DELETE FROM hasil_rekomendasi WHERE id = %s", (id_rekom,))
        self.conn.commit()
    
    def clear_all_rekomendasi(self):
        self.cursor.execute("DELETE FROM hasil_rekomendasi")
        self.conn.commit()
    
    def count_rekomendasi(self):
        self.cursor.execute("SELECT COUNT(*) FROM hasil_rekomendasi")
        return self.cursor.fetchone()[0]