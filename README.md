# 🤖 Autonomous Quantitative Trading Agent (Python/PyTorch)

**Live Market Deployment: New York Session 2025**

This repository contains the full source code and high-frequency trading logs for an Autonomous AI Agent designed to trade Crypto (SOL) and Commodities (Gold) using Deep Reinforcement Learning.

## 📂 Portfolio Case Study
For a detailed technical breakdown, architecture diagrams, and performance analysis, please read the Case Study:
👉 **[PORTFOLIO_CASE_STUDY.md](PORTFOLIO_CASE_STUDY.md)**

## 🛠️ Technology Stack
*   **Core:** Python 3.10, AsyncIO
*   **AI/ML:** PyTorch (DQN), Scikit-learn
*   **Data:** Pandas, NumPy, TA-Lib
*   **Connectivity:** CCXT (Simulated), Websockets

## 🚀 Key Features
*   **ROUND-ROBIN FAILOVER:** Robust API handling for unstable exchange feeds.
*   **SENTIMENT DIVERGENCE:** Logic to detect price/news outliers (e.g., Bullish reaction to Bearish Data).
*   **SESSION EXECUTORS:** Dedicated logic for London vs. New York volatility profiles.

---
*Engineering Project by [Raden Muhammad Yudie Sanjaya](https://github.com/dioerden)*
