
# FUZZY LOGIC ENGINE - Perhitungan Manual
import numpy as np

class FuzzyMobil:
    def __init__(self):
        # --- Definisi Variabel & Himpunan Fuzzy ---
        self.variables = {
            "harga": {
                "name": "Harga Jual",
                "range": [0, 40],
                "sets": {
                    "murah":   [0, 0, 12, 20],
                    "sedang":  [8, 18, 28],
                    "mahal":   [18, 30, 40, 40],
                }
            },
            "umur": {
                "name": "Umur Mobil",
                "range": [0, 25],
                "sets": {
                    "baru":     [0, 0, 5, 10],
                    "menengah": [4, 10, 16],
                    "tua":      [10, 18, 25, 25],
                }
            },
            "km": {
                "name": "Jarak Tempuh",
                "range": [0, 250000],
                "sets": {
                    "rendah":  [0, 0, 50000, 100000],
                    "sedang":  [40000, 100000, 160000],
                    "tinggi":  [100000, 180000, 250000, 250000],
                }
            },
            "rasio_harga": {
                "name": "Rasio Harga",
                "range": [0, 1.2],
                "sets": {
                    "bagus":  [0, 0, 0.4, 0.6],
                    "cukup":  [0.3, 0.55, 0.8],
                    "buruk":  [0.5, 0.9, 1.2, 1.2],
                }
            },
            "pemilik": {
                "name": "Riwayat Pemilik",
                "range": [0, 5],
                "sets": {
                    "sedikit":  [0, 0, 1, 3],
                    "menengah": [1, 2.5, 4],
                    "banyak":   [2, 4, 5, 5],
                }
            }
        }
        
        # --- Rule Base ---
        self.rules = {}
        
        # DIREKOMENDASIKAN (2)
        direkomendasikan = [
            (0,0,0,0,0),
            (0,0,0,0,1), (0,0,0,1,0), (0,0,1,0,0), (0,1,0,0,0), (1,0,0,0,0),
            (0,0,0,1,1), (0,0,1,0,1), (0,0,1,1,0), (0,1,0,0,1), (0,1,0,1,0),
            (0,1,1,0,0), (1,0,0,0,1), (1,0,0,1,0), (1,0,1,0,0), (1,1,0,0,0),
            (0,0,1,1,1), (0,0,2,0,0), (0,0,2,0,1), (0,0,2,1,0), (0,0,2,1,1),
            (0,0,1,2,0), (0,0,1,2,1),
        ]
        
        # CUKUP (1)
        cukup = [
            (0,0,1,1,2), (0,0,1,2,1), (0,0,2,1,0), (0,1,0,1,2),
            (0,1,1,0,2), (0,1,1,1,1), (0,1,1,1,2),
            (0,1,1,2,1), (0,1,1,2,0), (0,1,0,2,1), (1,0,1,1,1),
            (0,1,1,1,0), (0,1,1,0,1), (0,1,0,1,1), (0,0,1,1,1),
            (1,0,1,1,0), (1,0,1,0,1), (1,0,0,1,1), (1,1,0,1,0),
            (1,1,0,0,1), (1,0,0,1,0),
            (1,1,1,1,0), (1,1,1,0,1), (1,1,0,1,1), (1,0,1,1,1), (0,1,1,1,1),
            (1,1,1,1,1),
            (1,0,0,0,2), (1,0,0,2,0), (1,0,2,0,0), (1,1,0,0,2),
            (0,2,0,0,1), (2,0,0,0,1),
        ]
        
        for a in range(3):
            for b in range(3):
                for c in range(3):
                    for d in range(3):
                        for e in range(3):
                            rule_key = (a, b, c, d, e)
                            if rule_key in direkomendasikan:
                                self.rules[rule_key] = 2
                            elif rule_key in cukup:
                                self.rules[rule_key] = 1
                            else:
                                self.rules[rule_key] = 0
    
    def _fuzzifikasi_segitiga(self, x, params):
        a, b, c = params
        if x <= a or x >= c:
            return 0
        elif a < x <= b:
            return (x - a) / (b - a)
        elif b < x < c:
            return (c - x) / (c - b)
        return 0
    
    def _fuzzifikasi_trapesium(self, x, params):
        a, b, c, d = params
        if x <= a or x >= d:
            return 0
        elif b <= x <= c:
            return 1
        elif a < x < b:
            return (x - a) / (b - a)
        elif c < x < d:
            return (d - x) / (d - c)
        return 0
    
    def _fuzzify(self, x, params):
        if len(params) == 3:
            return self._fuzzifikasi_segitiga(x, params)
        else:
            return self._fuzzifikasi_trapesium(x, params)
    
    def _get_derajat(self, var_name, value):
        result = {}
        for set_name, params in self.variables[var_name]["sets"].items():
            result[set_name] = self._fuzzify(value, params)
        return result
    
    def _inferensi(self, derajat_input):
        output_aggregate = {
            "tidak_direkomendasikan": 0,
            "cukup": 0,
            "direkomendasikan": 0,
        }
        
        output_map = {
            0: "tidak_direkomendasikan",
            1: "cukup",
            2: "direkomendasikan",
        }
        
        any_fired = False
        
        for rule_key, output_idx in self.rules.items():
            firing = 1.0
            var_names = ["harga", "umur", "km", "rasio_harga", "pemilik"]
            set_names = [
                list(derajat_input[v].keys())[rule_key[i]]
                for i, v in enumerate(var_names)
            ]
            
            for i, var_name in enumerate(var_names):
                set_name = set_names[i]
                mu = derajat_input[var_name][set_name]
                firing = min(firing, mu)
                if firing == 0:
                    break
            
            if firing > 0:
                output_name = output_map[output_idx]
                output_aggregate[output_name] = max(output_aggregate[output_name], firing)
                any_fired = True
        
        return output_aggregate, any_fired
    
    def _hitung_skor_mentah(self, harga, umur, km, rasio_harga, pemilik):
        """
        Kalau gak ada rule yang fired, hitung skor langsung dari nilai.
        Range 0-1, makin kecil nilai = makin bagus.
        """
        # Normalisasi tiap kriteria ke 0-1 (0 = terbaik, 1 = terburuk)
        skor_harga = min(harga / 35, 1.0)
        skor_umur = min(umur / 20, 1.0)
        skor_km = min(km / 200000, 1.0)
        skor_rasio = min(rasio_harga / 1.1, 1.0)
        skor_pemilik = min(pemilik / 4, 1.0)
        
        # Rata-rata (makin kecil makin baik)
        rata_buruk = (skor_harga + skor_umur + skor_km + skor_rasio + skor_pemilik) / 5
        
        # Balik: 0 = buruk, 1 = bagus
        skor = 1.0 - rata_buruk
        
        return skor
    
    def _defuzzifikasi(self, aggregated, any_fired, harga, umur, km, rasio_harga, pemilik):
        if any_fired:
            # Pakai centroid kalau ada rule yang fired
            centroids = {
                "tidak_direkomendasikan": 0.20,
                "cukup": 0.50,
                "direkomendasikan": 0.80,
            }
            
            numerator = 0
            denominator = 0
            
            for name, mu in aggregated.items():
                if mu > 0:
                    numerator += mu * centroids[name]
                    denominator += mu
            
            if denominator > 0:
                return numerator / denominator
        
        # Kalau gak ada rule fired, hitung dari data mentah
        return self._hitung_skor_mentah(harga, umur, km, rasio_harga, pemilik)
    
    def hitung(self, harga, umur, km, rasio_harga, pemilik):
        # Fuzzifikasi
        derajat = {
            "harga": self._get_derajat("harga", harga),
            "umur": self._get_derajat("umur", umur),
            "km": self._get_derajat("km", km),
            "rasio_harga": self._get_derajat("rasio_harga", rasio_harga),
            "pemilik": self._get_derajat("pemilik", pemilik),
        }
        
        # Inferensi
        aggregated, any_fired = self._inferensi(derajat)
        
        # Defuzzifikasi
        skor = self._defuzzifikasi(aggregated, any_fired, harga, umur, km, rasio_harga, pemilik)
        
        # Threshold
        if skor >= 0.55:
            status = "Direkomendasikan"
        elif skor >= 0.30:
            status = "Cukup"
        else:
            status = "Tidak Direkomendasikan"
        
        return round(skor, 3), status
    
    def get_derajat_keanggotaan(self, harga, umur, km, rasio_harga, pemilik):
        return {
            "harga": self._get_derajat("harga", harga),
            "umur": self._get_derajat("umur", umur),
            "km": self._get_derajat("km", km),
            "rasio_harga": self._get_derajat("rasio_harga", rasio_harga),
            "pemilik": self._get_derajat("pemilik", pemilik),
        }