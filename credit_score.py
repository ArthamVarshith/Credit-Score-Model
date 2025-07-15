import json
from collections import defaultdict
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt


# Function to normalize token amount based on asset's decimal places
def normalize_amount(amount_str, asset_symbol):
    decimals = {
        'USDC': 6,
        'USDT': 6,
        'DAI': 18,
        'WETH': 18,
        'WBTC': 8,
        'WMATIC': 18,
        'WPOL': 18
    }.get(asset_symbol, 18)  # Default to 18 decimals if asset is unknown

    try:
        return int(amount_str) / (10 ** decimals)
    except:
        return 0

# Function to process all transactions and group them by wallet
def process_transactions(data):
    wallets = defaultdict(lambda: {
        'total_deposit_usd': 0,
        'total_borrow_usd': 0,
        'total_repay_usd': 0,
        'total_redeem_usd': 0,
        'liquidation_count': 0,
        'assets': set(),
        'timestamps': [],
        'actions': defaultdict(int)
    })

    for txn in data:
        try:
            wallet = txn.get("userWallet")
            if not wallet:
                continue

            action = txn.get("action")
            action_data = txn.get("actionData", {})

            asset_symbol = action_data.get("assetSymbol", "")
            amount_str = action_data.get("amount", "0")
            price_str = action_data.get("assetPriceUSD", "1.0")
            timestamp = txn.get("timestamp")

            # Convert and validate values
            try:
                amount = normalize_amount(amount_str, asset_symbol)
                price = float(price_str)
                usd_value = amount * price
                timestamp = int(timestamp)
            except (ValueError, TypeError):
                continue

            # Update wallet stats
            wallets[wallet]['timestamps'].append(timestamp)
            wallets[wallet]['assets'].add(asset_symbol)

            if action == "deposit":
                wallets[wallet]['total_deposit_usd'] += usd_value
            elif action == "borrow":
                wallets[wallet]['total_borrow_usd'] += usd_value
            elif action == "repay":
                wallets[wallet]['total_repay_usd'] += usd_value
            elif action == "redeemunderlying":
                wallets[wallet]['total_redeem_usd'] += usd_value
            elif action == "liquidationcall":
                wallets[wallet]['liquidation_count'] += 1

            wallets[wallet]['actions'][action] += 1

        except Exception as e:
            print(f"Error processing transaction: {e}")
            continue

    return wallets

# Function to calculate credit scores per wallet
def calculate_scores(wallets):
    records = []

    for wallet, data in wallets.items():
        if not data['timestamps']:
            continue

        # Time-based features
        min_ts = min(data['timestamps'])
        max_ts = max(data['timestamps'])
        wallet_age_days = (max_ts - min_ts) / (3600 * 24) if min_ts != max_ts else 0

        # Activity rate
        tx_count = sum(data['actions'].values())
        daily_tx_rate = tx_count / (wallet_age_days or 1)

        # Financial ratio
        total_borrow = data['total_borrow_usd']
        total_repay = data['total_repay_usd']
        repay_ratio = total_repay / total_borrow if total_borrow > 0 else 1.0

        # Asset usage
        asset_diversity = len(data['assets'])

        # Scoring Logic
        score = 500  # Base score

        # Reward high repay ratio (max 200)
        score += min(repay_ratio, 2.0) * 100

        # Penalize for each liquidation
        score -= data['liquidation_count'] * 50

        # Score based on activity level
        if 0.1 < daily_tx_rate < 5:
            score += 100  # Normal activity
        elif daily_tx_rate >= 5:
            score -= 100  # Possible bot

        # Score for using multiple assets
        score += min(asset_diversity * 20, 100)

        # Score for deposit behavior
        if data['total_deposit_usd'] > 1000:
            score += min(data['total_deposit_usd'] / 10000 * 150, 150)

        # Score based on wallet longevity
        score += min(wallet_age_days / 365 * 100, 100)

        # Clamp score to range 0-1000
        score = max(0, min(1000, int(score)))

        records.append({
            'wallet': wallet,
            'score': score,
            'total_deposit_usd': data['total_deposit_usd'],
            'total_borrow_usd': data['total_borrow_usd'],
            'total_repay_usd': data['total_repay_usd'],
            'liquidation_count': data['liquidation_count'],
            'wallet_age_days': round(wallet_age_days, 2),
            'repay_ratio': round(repay_ratio, 2),
            'asset_diversity': asset_diversity,
            'daily_tx_rate': round(daily_tx_rate, 2),
            'tx_count': tx_count
        })

    return records

# Main function to run all steps
def main():
    # Load transaction data from JSON
    with open('user-wallet-transactions.json', 'r') as f:
        data = json.load(f)

    # Step 1: Process raw transactions
    wallets = process_transactions(data)

    # Step 2: Score each wallet
    records = calculate_scores(wallets)

    # Step 3: Save to CSV
    df = pd.DataFrame(records)
    df.to_csv('wallet_scores.csv', index=False)

    # Step 4: Visualize score distribution
    plt.figure(figsize=(10, 6))
    plt.hist(df['score'], bins=20, edgecolor='black')
    plt.title('Wallet Credit Score Distribution')
    plt.xlabel('Credit Score')
    plt.ylabel('Number of Wallets')
    plt.grid(True)
    plt.savefig('score_distribution.png')
    plt.show()

    print(f"Processed {len(records)} wallets. \nScores saved to 'wallet_scores.csv'.")

    # Print wallet count in score bins
    bin_counts = pd.cut(df['score'], bins=[0,100,200,300,400,500,600,700,800,900,1000]).value_counts().sort_index()
    print("Score Range | Wallet Count")
    for interval, count in bin_counts.items():
        print(f"{interval} | {count}")


# Entry point
if __name__ == '__main__':
    main()
