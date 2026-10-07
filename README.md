# 🛡️ UPI Shield — Intelligent Fraud Mitigation Gateway

An inline, real-time fraud mitigation switch for UPI payment processing. Operating as a pre-debit firewall, **UPI Shield** inspects transaction telemetry, hardware tokens, and kinematic behavioral metrics before funds leave the remitter's account.

---

## ⚡ Key Highlights

- **Inline Pre-Debit Interception:** Operates with sub-20ms switch latency, well within NPCI's 3,000ms timeout boundary.
- **Explainable Multi-Layer Engine:** Combines a deterministic rule-based firewall (balance sanity, scam VPA heuristics, velocity bounds) with an ensemble machine learning classifier.
- **3-Tier Adaptive Mitigation Policy:**
  - `Tier 1 (Pass)`: Frictionless clearance (ISO 20022 Code `00`).
  - `Tier 2 (Challenge)`: Pre-debit hold with step-up SMS OTP authentication (ISO Code `U16`).
  - `Tier 3 (Cooling / Terminated)`: Instant switch-level blocking to prevent account drain (ISO Code `U28`).
- **RBI Zero-Liability Compliance:** Immediate regulatory complaint dossier generation, cyber helpline escalation (1930), and inter-bank beneficiary lien triggers.
- **Zero Heavy Graph Dependencies:** Custom lightweight SVG vector gauges ensure instantaneous page loads without chart rendering deadlocks.

---

## 📊 Dataset & Model Architecture

- **Training Records:** 127,252 total transactions (173 fraud cases, 127,079 legitimate transfers).
- **Fraud Rate:** 0.14% baseline class imbalance handled via weighted loss penalization.
- **Transaction Types:** `N_P2P`, `N_RETAIL`, `N_FESTIVAL`, `N_BUSINESS`, and `N_FRAUD`.
- **Telemetry Feature Inputs (8 Vectors):**
  1. `amount`: Transaction value in INR
  2. `amount_to_avg`: Surge ratio against normal daily spending baseline
  3. `drain_ratio`: Account liquidity depletion proportion
  4. `hour_24`: Transaction hour of the day (0–23)
  5. `tx_count`: Rapid attempt frequency within a 10-minute window
  6. `is_new_device`: Hardware fingerprint / carrier subnet match
  7. `speed_kmh`: Physical transit speed between consecutive transaction coordinates
  8. `gap_sec`: Elapsed seconds since previous activity

---

## 📁 Repository Structure

```text
.
├── app.py                  # Main Streamlit web application
├── requirements.txt        # Python dependency manifest
├── scaler.pkl              # StandardScaler transformation pipeline
├── upi_fraud_model.pkl     # Trained fraud classification model
└── README.md               # Project documentation
