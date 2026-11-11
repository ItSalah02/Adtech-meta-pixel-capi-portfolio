# 📊 AdTech Data Pipeline & Business Intelligence Portfolio

This repository contains an end-to-end project covering web infrastructure, data engineering, and business intelligence for advanced ad campaign measurement. The main goal is to demonstrate the technical implementation and the business analysis of **event deduplication** between the **Meta Pixel (browser)** and the **Conversions API (server)**.

> ⚠️ **Note:** all campaign data in this project is synthetically generated. The conclusions below illustrate the analytical method, not real market behaviour.

## 🧰 Technology Stack & Reproducibility

*   **Frontend:** HTML5, CSS3, JavaScript (Meta Pixel).
*   **Backend / API testing:** Postman, Meta Conversions API.
*   **Data engineering:** Python 3, Pandas, SQLite3.
*   **Business intelligence:** Google Sheets, Looker Studio.

**How to reproduce the data pipeline:**

```bash
# 1. Generate the simulated raw data (Pixel and CAPI tables)
python simulador.py

# 2. Run the SQL deduplication and generate the final clean dataset
python deduplicacion.py
```

## 🚀 Project Architecture

The data flow follows this lifecycle:

1.  **Web capture:** a simulated e-commerce site (`index.html` / `product.html`) equipped with the Meta Pixel.
2.  **Server ingest:** simulated server-side event delivery through the Conversions API using **Postman**.
3.  **Data simulation:** a Python script generates 30 days of historical data and deliberately injects statistical noise: ad-blocker loss (15%) and missing match parameters on the server side (10% of emails, 5% of phones).
4.  **Data engineering:** deduplication in **SQL (SQLite)** plus a custom *Match Score* calculation.
5.  **Visualization:** interactive dashboard in **Looker Studio**, connected to Google Sheets.

---

## 🛠️ Phase 1: Meta Pixel & Conversions API

A Meta Pixel was configured and injected into the website code. The "Buy" button triggers a `Purchase` event with a fixed `event_id` (`ORDER_DEMO_001`). The same event was then replicated through Postman using the Conversions API with the identical `event_id`, which Meta deduplicated automatically.

*   **Deduplication test:** Events Manager confirmed that Meta receives both events (browser and server) but counts a single conversion. Meta deduplicates only when both the event name **and** the `event_id` match, within its attribution window.

---

## 🐍 Phase 2: Data Engineering (Python & SQL)

Because real browsers lose events to ad blockers and server-side payloads sometimes arrive without match parameters, the simulator recreates both failure modes:

*   **Ground truth:** 4,500 simulated purchases.
*   **Received (Pixel):** 3,836 events — a 14.8% loss attributed to ad blockers.
*   **Received (CAPI):** 4,500 events — 100% server delivery, but with **~10% null emails and ~5% null phones**.
*   **SQL deduplication:** a `LEFT JOIN` from the CAPI table to the Pixel table keeps the **entire universe of 4,500 purchases** (recovering the 664 events the browser never sent) and enriches each row with browser data when available.
*   **Match Score (custom, 0–1):** per deduplicated event, 1.0 if the CAPI email matches the Pixel email, 0.5 if only the phone matches, and 0 otherwise (including the 655 events with no browser counterpart) → **0.81**.

---

## 📈 Phase 3: Business Intelligence (Looker Studio)

The deduplicated dataset (4,500 unique conversions) was exported to Google Sheets and connected to **Looker Studio**.

### 🔗 [View the interactive dashboard](https://datastudio.google.com/reporting/24c72b3e-624c-4274-8d8a-7fcf78b659f9)
<details>
  <summary>📊 <b>Click to preview the dashboard screenshot</b></summary>
  <br>
  <img src="Dashboard.pn" alt="Dashboard Preview" width="100%">
</details>

**Main dashboard KPIs (30-day simulation):**

| Metric | Value |
|---|---|
| Total spend | €76.710,92 |
| Total revenue | €383,193.61 |
| Blended ROAS | 5.00× |
| Average CPA (4,500 deduplicated conversions) | €17,05 |
| Custom Match Score | 0.81 / 1.00 |

---

## 🧠 Business Analysis & Strategic Recommendations

*(Technical report)*

1.  **The risk of skipping deduplication.** Without the CAPI and the `event_id` strategy, the reported ROAS would have been artificially inflated by double-counting browser and server conversions. Cross-channel integration is what prevents attribution blindness and recovers the ~15% of events lost to ad blockers.
2.  **Blended ROAS vs. campaign breakdown.** The 5.00× blended ROAS is driven by budget weight, not by average efficiency. Cold Traffic absorbs €57.9k of the €76.7k total (75.5%) at a 3.35× ROAS, while Retargeting returns 10.06× on just €18.8k and generates almost the same revenue (€189.3k vs €193.9k).
    *   **Recommendation:** keep funding Cold Traffic for volume, but scale Retargeting until audience saturation, as it delivers the highest return.
3.  **Match Score quality (0.81).** The Match Score is capped by the 14.8% of events with no browser counterpart; among events that do have one, the remaining gap comes from missing server-side identifiers (~10% email, ~5% phone), which points to stricter checkout validation.

---

## ⚠️ Limitations

*   The `LEFT JOIN` assumes `event_id` is unique and reliable across both sources; a duplicated or reused `event_id` would silently collapse two purchases into one.
*   Ad-blocker loss is modelled as a flat 15%; real loss varies by audience, device and browser.
*   No attribution windows or view-through modelling: every conversion is credited to a single campaign.
*   Average order value is held constant by the simulator, so ROAS differences come from conversion volume and spend, not from basket mix.

---

## 📂 Repository Structure

*   `/assets`: CSS, Pixel JavaScript and supporting images.
*   `index.html` & `product.html`: simulated e-commerce interface.
*   `simulador.py`: data generation script with statistical noise.
*   `deduplicacion.py`: SQLite script using `LEFT JOIN` to cross-reference sources and compute the Match Score.
*   `postman_payload.json`: exact payload sent to the Conversions API.

---
*Project developed as a technical demonstration of AdTech, data engineering and BI.*
