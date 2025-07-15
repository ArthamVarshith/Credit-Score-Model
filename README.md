# Credit Scoring Model for Aave V2 Wallets

## Overview

This project aims to develop a robust machine learning-inspired scoring mechanism to assess the creditworthiness of wallets interacting with the Aave V2 DeFi protocol. It uses only historical on-chain transaction behavior to assign a credit score between **0 and 1000**, where higher scores indicate responsible usage and lower scores may suggest exploitative or bot-like activity.



## Project Structure

```
credit-score-model/
├── user-wallet-transactions.json   # Input dataset
├── wallet_scores.csv               # Output scores
├── score_distribution.png          # Score distribution graph
├── credit_score.py                 # Main script
├── README.md                       # This file
└── analysis.md                     # Score distribution insights
```



## Methodology

### Step 1: Data Ingestion

* Load and parse the `user-wallet-transactions.json` file.
* Each transaction record includes:

  * `userWallet`: wallet address
  * `action`: type of DeFi action (deposit, borrow, repay, etc.)
  * `amount`, `assetSymbol`, `assetPriceUSD`
  * `timestamp`

### Step 2: Feature Engineering

For each wallet, we compute:

* `total_deposit_usd`
* `total_borrow_usd`
* `total_repay_usd`
* `liquidation_count`
* `wallet_age_days`
* `repay_ratio` (repay/borrow)
* `asset_diversity` (unique assets used)
* `daily_tx_rate` (transactions per day)

### Step 3: Scoring Logic

A custom scoring algorithm is applied (0–1000 range):

* +200 max: High repay/borrow ratio
* −50 per liquidation
* +100 for normal tx rate (0.1 to 5/day)
* −100 for bot-like activity (>5/day)
* +100 for using many asset types
* +150 max for deposits > \$10,000
* +100 max for wallets older than 1 year

### Step 4: Export & Visualization

* Scores are saved to `wallet_scores.csv`
* Score distribution is plotted in `score_distribution.png`
