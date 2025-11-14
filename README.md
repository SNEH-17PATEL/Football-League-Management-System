# ⚽ Football League Management System

A complete Database Management System (DBMS) mini-project built using **MySQL** and **Python Tkinter GUI**.  
This system manages football tournaments, teams, players, match scheduling, match results, scores, and leaderboards with full CRUD operations, triggers, stored procedures, and functions.

---

## 📌 Features

### 🏆 Tournament & Team Management
- Add, view, and delete teams
- Store coach details and foundation year
- Auto-refresh team list and comboboxes
- Manage tournament details

### 👥 Player Management
- Maintain player information: age, position, height, weight, jersey number
- Update player weight through GUI
- Built-in validation to avoid incorrect entry

### ⚽ Match Scheduling & Results
- Schedule matches with teams, date, and venue
- Enter match results (goals)
- Stored procedure auto-calculates:
  - Win / Loss / Draw
  - Points
  - Score entries
  - Match status update
- Auto-updated match list

### 📊 Leaderboard & Team Analytics
- Live leaderboard using SQL VIEW
- Shows matches played, wins, draws, losses, goals, and points
- Win Percentage calculated using SQL FUNCTION

### 🛡️ Database Automation
- **Triggers** for:
  - Auto-increase match count
  - Prevent negative goal/point entries
- **Stored Procedures** for:
  - Inserting match results
  - Team performance summary
- **Functions** for:
  - Win percentage calculation
- **Joins, Nested Queries, Aggregate Queries** used across project

---

## 🧰 Technologies Used

### Backend:
- **MySQL**
- SQL (DDL, DML, Views, Joins, Triggers, Functions, Procedures)

### Frontend:
- **Python**
- **Tkinter GUI**
- `mysql.connector` for database connectivity

### Tools:
- MySQL Workbench
- VS Code / PyCharm / IDLE

---

## 📂 Project Structure

```
Football-League-Management-System/
│
├── football_gui.py         
├── database.sql            
├── README.md              
├── screenshots/           
└── ER_Diagram.png         
```

---

## 🚀 Setup Instructions

### 1️⃣ Install Dependencies
```
pip install mysql-connector-python
```

### 2️⃣ Import Database
Run `database.sql` in MySQL Workbench.

### 3️⃣ Configure DB Credentials
Inside `football_gui.py` update:
```
host="localhost"
user="root"
password="your_password"
database="FootballLeagueDB"
```

### 4️⃣ Run the Application
```
python football_gui.py
```

---

## 📝 Key DBMS Concepts Implemented

| Concept | Status |
|--------|--------|
| DDL Commands | ✔ |
| DML CRUD Operations | ✔ |
| Join Queries | ✔ |
| Nested Queries | ✔ |
| Aggregate Queries | ✔ |
| Views | ✔ |
| Stored Procedures | ✔ (2) |
| Functions | ✔ (1) |
| Triggers | ✔ (2) |
| GUI Integration | ✔ |

---

## 📄 License
For educational and academic use.
