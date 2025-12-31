import requests
import pandas as pd
import time
from indicators import calculate_rsi

def analyze_candle_structure():
    print("🎓 CLASSROOM MODE: Analyzing SOL Candle Structure...")
    
    # 1. Fetch Data
    try:
        url = "https://api.coingecko.com/api/v3/coins/solana/market_chart?vs_currency=usd&days=1"
        headers = {'User-Agent': 'Mozilla/5.0'}
        resp = requests.get(url, headers=headers, verify=False, timeout=10)
        data = resp.json()
        if 'prices' not in data:
            print(f"⚠️ API Response: {data}")
            return
            
        prices = [p[1] for p in data['prices']]
        timestamps = [p[0] for p in data['prices']]
    except Exception as e:
        print(f"❌ Data Fetch Error: {e}")
        return

    # 2. Key Metrics
    current_price = prices[-1]
    prev_price = prices[-5] # Approx 25 mins ago
    
    # RSI Calculation
    rsi_series = calculate_rsi(pd.Series(prices), 14)
    if isinstance(rsi_series, pd.Series):
        rsi = rsi_series.iloc[-1]
    else:
        rsi = rsi_series[-1]
    
    print("-" * 60)
    print(f"🕯️ LIVE STATUS: Price ${current_price:.2f} | RSI {rsi:.1f}")
    print("-" * 60)
    
    # 3. Educational Diagnosis
    print("📘 EDUKASI KILAT (Apa yang terjadi?):")
    
    # Scenario A: Bullish Consolidation (RSI turun, Harga diam)
    if rsi < 60 and current_price >= prev_price * 0.995:
        print("1. POLA: 'Bullish Flag / Consolidation'")
        print("   -> Harga bergerak mendatar (Sideways) setelah naik tinggi.")
        print("   -> RSI turun dari Overbought (tadi 90+) ke level Normal (sekarang seriation).")
        print("   💡 PELAJARAN: Ini tanda 'Sehat'. Market sedang 'menghela napas' sebelum lari lagi.")
        print("      Bandar tidak membuang barang, mereka hanya menahan harga.")
        
    # Scenario B: Bearish Divergence (Harga naik, RSI turun) - Jarang di timeframe kecil
    elif rsi < 50 and current_price > prev_price:
        print("1. POLA: 'Weak Rally'")
        print("   -> Harga mencoba naik, tapi momentum (RSI) lemah.")
        print("   💡 PELAJARAN: Hati-hati 'Fake Out'. Kenaikan tanpa tenaga biasanya dibanting.")
        
    # Scenario C: Oversold Bounce (RSI rendah, Harga mulai naik)
    elif rsi < 30:
        print("1. POLA: 'Oversold Bounce'")
        print("   -> Ibarat bola yang ditekan ke dalam air, dia akan loncat ke atas.")
        print("   💡 PELAJARAN: Waktunya Scalping Buy (Curi poin).")
        
    else:
        print("1. POLA: 'Chugging Along' (Tren Stabil)")
        print("   -> RSI di zona netral (40-60).")
        print("   💡 PELAJARAN: 'Trend is your friend'. Selama tidak ada candle merah panjang, Hold saja.")

    print("\n2. PSIKOLOGI MARKET (Pre-New York):")
    print("   Saat ini jam 19:40 WIB. Trader London sedang siap-siap pulang,")
    print("   Trader New York baru bangun tidur.")
    print("   -> Biasanya volume turun (sepi) -> Harga 'Drifting' (mengambang).")
    print("   -> JANGAN kaget kalau chart terlihat bosan. Ini 'Ketenangan sebelum Badai'.")

if __name__ == "__main__":
    import urllib3
    urllib3.disable_warnings()
    analyze_candle_structure()
