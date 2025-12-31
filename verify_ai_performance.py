import torch
import torch.nn as nn
import os
import pandas as pd
from mexc_client import MEXCClient
from strategy import DQN

def verify_ai(symbol="SOLUSDT"):
    print(f"🔬 Auditing AI Performance for {symbol}...")
    
    # 1. Load Model
    if not os.path.exists("trading_agent.pth"):
        print("❌ Error: No AI model (trading_agent.pth) found.")
        return

    try:
        state_dim = torch.load("trading_agent_metadata.pth")
        model = DQN(state_dim, 3)
        model.load_state_dict(torch.load("trading_agent.pth"))
        model.eval()
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        return

    # 2. Fetch Recent Data
    client = MEXCClient()
    klines = client.get_klines(symbol, "15m", limit=300) # Recent 300 candles
    if not klines:
        print("❌ Error: Could not fetch klines.")
        return

    closes = [float(k[4]) for k in klines]
    
    # 3. Test Predictions
    correct_direc = 0
    total_eval = 0
    predictions = []
    
    # Convert to DataFrame for easier calculation
    data = pd.DataFrame(closes, columns=['close'])
    
    # Calculate locally for audit
    data['ema9'] = data['close'].ewm(span=9, adjust=False).mean()
    data['ema21'] = data['close'].ewm(span=21, adjust=False).mean()
    
    delta = data['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    data['rsi'] = 100 - (100 / (1 + rs))
    data.ffill(inplace=True)
    data.bfill(inplace=True)

    sample_size = 100
    start_index = max(21, len(data) - sample_size - 1)
    
    for i in range(start_index, len(data) - 1):
        row = data.iloc[i]
        price = row['close']
        next_price = data.iloc[i + 1]['close']
        
        # State: [price, ema9, ema21, rsi, 100, 0, progress]
        state = torch.FloatTensor([
            row['close'], 
            row['ema9'], 
            row['ema21'], 
            row['rsi'], 
            100.0, 
            0.0, 
            (i + 1) / len(data)
        ]).unsqueeze(0)
        
        with torch.no_grad():
            q_values = model(state)
            action = torch.argmax(q_values).item()
            opinion = ["HOLD", "BUY", "SELL"][action]

        is_correct = False
        if opinion == "BUY" and next_price > price: is_correct = True
        elif opinion == "SELL" and next_price < price: is_correct = True
        elif opinion == "HOLD": is_correct = "N/A" # Neutral

        if is_correct != "N/A":
            total_eval += 1
            if is_correct: correct_direc += 1
        
        predictions.append(opinion)

    accuracy = (correct_direc / total_eval * 100) if total_eval > 0 else 0
    
    print("\n--- AI Audit Summary ---")
    print(f"Accuracy (Direct Move): {accuracy:.2f}%")
    print(f"Sample Size: {total_eval} Significant Opinions")
    
    counts = pd.Series(predictions).value_counts()
    print("\nOpinion Distribution:")
    print(counts)

    if accuracy < 55:
        print("\n⚠️ WARNING: AI accuracy is currently low. Recommend relying more on Technical Indicators for London Open.")
    else:
        print("\n✅ AI is showing decent alignment with recent price action.")

if __name__ == "__main__":
    verify_ai("SOLUSDT")
    print("-" * 30)
    verify_ai("BTCUSDT")
