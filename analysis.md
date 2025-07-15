Wallet Score Analysis

This document analyzes the output scores assigned to Aave V2 user wallets by the credit scoring script.

Score Distribution

The score ranges from 0 to 1000. Below is the distribution of scores in bins of 100:

Score Range

Number of Wallets

0–100

0

100–200

0

200–300

1

300–400

1

400–500

186

500–600

258

600–700

387

700–800

1864

800–900

407

900–1000

391

Score distribution graph:



Behavior Patterns

🔴 Low Score Wallets (0–300)

Often had frequent liquidations

Many lacked repayment after borrowing

Very high transaction rate (possible bots)

Low deposit activity and short lifespan

🟡 Mid-Score Wallets (400–700)

Moderate deposit and borrow behavior

Occasional repayment and some asset diversity

Mixed levels of wallet age and activity

🟢 High Score Wallets (800–1000)

Long-standing wallets (active for >6 months)

Consistent deposits and full loan repayments

Minimal or zero liquidations

Good asset diversification and organic tx activity

Conclusion

This scoring model helps differentiate reliable DeFi users from risky or automated behavior. It could support DeFi risk engines, lending rules, or even insurance premiums.

