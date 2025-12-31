import time
import datetime
import requests
import sys

def wait_and_signal():
    # Target: 20:05 WIB = 13:05 UTC
    target_hour = 13
    target_minute = 5
    
    print(f"⏳ COUNTDOWN TO MARKET ENTRY (20:05 WIB)...")
    print("   Strategy: Let the NY Open volatility settle (5 mins).")
    print("   Goal: Enter on 'Confirmation' not 'Chaos'.")
    print("-" * 50)
    
    while True:
        now = datetime.datetime.now(datetime.timezone.utc)
        
        # Check if time passed
        if now.hour > target_hour or (now.hour == target_hour and now.minute >= target_minute):
            print("\n🚨 TIME'S UP! (20:05 WIB REACHED) 🚨")
            print("-" * 50)
            break
            
        # Countdown
        wait_seconds = ((target_hour - now.hour) * 3600) + ((target_minute - now.minute) * 60) - now.second
        mins, secs = divmod(wait_seconds, 60)
        print(f"⏱️ Waiting... {int(mins)}m {int(secs)}s remaining", end="\r")
        time.sleep(1)

    # Execution Signal
    print("🔍 CHECKING FINAL PRICE CONDITION (SOLUSDT)...")
    
    # Simple Manual Check Prompt (Reliable)
    print("\n👉 BUKA MEXC SEKARANG.")
    print("1. Cek Harga SOLUSDT.")
    print("2. ATURAN MAIN:")
    print("   - [HIJAU] Jika Harga > $126.00: GAS BUY (Market).")
    print("     -> Artinya support kuat, buyer New York masuk.")
    print("   - [MERAH] Jika Harga < $125.50: WAIT (Jangan paksa).")
    print("     -> Artinya market dumping, tunggu di $124.")
    print("-" * 50)
    print("🚀 REKOMENDASI: TEKAN 'OPEN LONG' SEKARANG (Jika > $126)")
    print("-" * 50)

if __name__ == "__main__":
    wait_and_signal()
