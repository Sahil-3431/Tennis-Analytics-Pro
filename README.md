# 🎾 Tennis Analytics Pro
### Tennis Data Analytics & Insights Platform

**Tennis Analytics Pro** is an interactive data analytics platform built using Python and Streamlit. It transforms tennis ranking data into meaningful insights through interactive dashboards, player comparisons, country-level analysis, performance evaluation, and SQL-based analytics.

The platform provides an organized way to explore tennis ranking information, understand player performance, and analyze ranking trends through data visualization.

---

## 🚀 Key Features

### 📊 1. Executive Dashboard
- Overall tennis ranking overview.
- Key performance indicators (KPIs).
- Interactive charts and visualizations.
- Global ranking insights.

### 🏆 2. Player Rankings
- Explore player ranking information.
- Analyze ranking positions and points.
- Compare player ranking performance.
- Interactive ranking data tables.

### 🔍 3. Competitor Explorer
- Search and explore competitors.
- Analyze individual competitor information.
- Compare competitor performance.

### 🌍 4. Country Analytics
- Country-wise ranking analysis.
- Explore competitor distribution by country.
- Analyze country-level tennis performance.

### 📈 5. Performance Analysis
- Analyze player ranking performance.
- Explore ranking patterns and movements.
- Interactive performance visualizations.

### 🛡️ 6. Data Quality
- Explore data quality information.
- Identify potential data inconsistencies.
- Review dataset completeness and reliability.

### 💡 7. Insights & Recommendations
- Discover meaningful insights from tennis data.
- Explore analytical findings.
- Understand ranking patterns and trends.

### 🗄️ 8. SQL Analytics
- Perform database-driven analysis.
- Explore available database tables.
- Execute analytical SQL queries.
- Access advanced built-in analytical queries.

---

## 🛠️ Technology Stack

| Technology | Purpose |
|---|---|
| Python | Core programming language |
| Streamlit | Interactive web application |
| Pandas | Data manipulation and analysis |
| Plotly | Interactive visualizations |
| SQLite | Database management |
| SQL | Database querying and analytics |
| Requests | API communication |
| Python-dotenv | Environment variable management |

---

## 📁 Project Structure

```text
Tennis_Game_Analytics/
│
├── app.py
├── README.md
├── requirements.txt
├── .env
├── .gitignore
│
├── dashboard/
│   ├── overview.py
│   ├── rankings.py
│   ├── competitor.py
│   ├── country.py
│   ├── performance_analysis.py
│   ├── data_quality.py
│   ├── insights.py
│   └── sql_analytics.py
│
├── database/
│   ├── connection.py
│   └── queries.py
│
├── data/
│   ├── competitors.csv
│   ├── doubles_rankings.csv
│   ├── doubles_rankings_raw.json
│   ├── ranking_analysis_summary.csv
│   ├── ranking_snapshots.csv
│   ├── tennis_rankings.db
│   └── top_10_doubles_rankings.csv
│
└── utils/
    ├── charts.py
    ├── data_loader.py
    ├── global_filters.py
    ├── sidebar.py
    └── styling.py
```

---

## ⚙️ Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/Sahil-3431/Tennis-Analytics-Pro.git
```

### 2. Navigate to the Project Directory

```bash
cd Tennis-Analytics-Pro
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root if your application requires API credentials.

Add the environment variable names expected by your application and configure your own API credentials.

**Important:** Never upload your `.env` file or API keys to GitHub.

### 5. Run the Application

```bash
streamlit run app.py
```

The application will open in your browser at:

```text
http://localhost:8501
```

---

## 🗄️ Database Information

The project uses an SQLite database:

`data/tennis_rankings.db`

The database includes the following tables:

- `Competitors`
- `DoublesRankings`
- `RankingSnapshots`

The database is used for structured data storage and SQL-based analysis.

---

## ☁️ Deployment

The application can be deployed using **Streamlit Community Cloud**.

1. Push the project to a GitHub repository.
2. Visit https://share.streamlit.io/
3. Sign in using your GitHub account.
4. Select the Tennis Analytics Pro repository.
5. Set the main file path to `app.py`.
6. Configure any required API credentials in the Streamlit Cloud app's Secrets settings, using the variable names expected by the application.
7. Deploy the application.

---

## 🎨 User Interface

The platform includes:
- Interactive sidebar navigation.
- Dark and Light themes.
- Dynamic KPI cards.
- Interactive Plotly charts.
- Styled analytical data tables.
- Global filters across supported dashboard pages.

---

## 🎯 Project Objectives

- Make tennis ranking data easier to explore and understand.
- Convert raw data into meaningful analytical insights.
- Build interactive data visualization dashboards.
- Apply SQL for structured database analysis.
- Demonstrate practical Python and data analytics skills.

---

## 👨‍💻 Author

**Sahil Khan**

Data Analyst 

**Project:** Tennis Analytics Pro

---

## ⭐ Support

If you find this project interesting, consider giving the repository a ⭐ on GitHub.

**Tennis Analytics Pro — Unlocking Tennis Data with SportRadar API.**
