from core.logic.strategy import HybridStrategy
import time

def get_ai_prediction():
    print("🧠 Waking up AI Agent...")
    strategy = HybridStrategy("SOLUSDT")
    
    # Check if model loaded
    if not strategy.model:
        print("⚠️ AI Model not found. Training required.")
        return

    print("🤖 Analyzing Market State (DQN Inference)...")
    # Fetch real data for inference
    result = strategy.get_signals(news_headlines=None)
    
    if "error" in result:
        print(f"❌ AI Prediction Failed: {result['error']}")
        return

    ai_verdict = result.get('ai_opinion', 'UNKNOWN')
    rsi = result['indicators']['rsi']
    price = result['price']
    
    print("-" * 50)
    print(f"🔮 AI ORACLE PREDICTION: {ai_verdict}")
    print("-" * 50)
    
    if ai_verdict == "SELL":
        print(f"🚨 AI sees DANGER! (RSI: {rsi:.2f})")
        print("   -> Probability of Crash: HIGH")
        print("   -> Recommendation: EXIT NOW.")
        
    elif ai_verdict == "BUY":
        print(f"🚀 AI sees OPPORTUNITY! (Price: {price})")
        print("   -> Probability of Pump: HIGH")
        print("   -> Recommendation: ENTER / ADD POSITION.")
        
    else: # HOLD
        print(f"🛡️ AI says: HOLD THE LINE.")
        print("   -> Market is indecisive or trending safely.")
        print(f"   -> Current RSI: {rsi:.2f} (Neutral/High)")
        print("   -> Recommendation: Keep SL tight, let profit run.")

if __name__ == "__main__":
    import urllib3
    urllib3.disable_warnings()
    get_ai_prediction()
