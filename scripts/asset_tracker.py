from mexc_client import MEXCClient

def track_assets():
    client = MEXCClient()
    account_info = client.get_account_info()
    
    if 'balances' in account_info:
        print(f"{'Asset':<10} | {'Free':<15} | {'Locked':<15}")
        print("-" * 45)
        for balance in account_info['balances']:
            free = float(balance['free'])
            locked = float(balance['locked'])
            if free > 0 or locked > 0:
                print(f"{balance['asset']:<10} | {free:<15.8f} | {locked:<15.8f}")
    else:
        print("Could not fetch account info. Check your API keys.")
        print("Response:", account_info)

if __name__ == "__main__":
    track_assets()
