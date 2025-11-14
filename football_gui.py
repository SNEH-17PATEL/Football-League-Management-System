import os
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import simpledialog
import mysql.connector
import re

# ---------------- DATABASE CONNECTION ----------------
def connect_db():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", "Snehpatel04%"),
        database=os.getenv("DB_NAME", "FootballLeagueDB")
    )

# ---------------- Globals / mappings ----------------
match_label_to_id = {}
team_name_to_id = {}

# ---------------- Helpers to load DB data ----------------
def load_team_options():
    """Populate team_name_to_id and update comboboxes for creating matches."""
    global team_name_to_id
    team_name_to_id = {}
    db = None
    cursor = None
    try:
        db = connect_db()
        cursor = db.cursor()
        cursor.execute("SELECT team_id, team_name FROM Team ORDER BY team_name;")
        rows = cursor.fetchall()
    except mysql.connector.Error as e:
        messagebox.showerror("Database Error", f"Failed to load teams:\n{e}")
        rows = []
    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()

    names = []
    for team_id, team_name in rows:
        team_name_to_id[team_name] = team_id
        names.append(team_name)

    # update the create-match comboboxes
    team1_combobox['values'] = names
    team2_combobox['values'] = names

    # if teams exist, select first option by default
    if names:
        team1_combobox.current(0)
        if len(names) > 1:
            team2_combobox.current(1)
        else:
            team2_combobox.current(0)
    else:
        team1_combobox.set('')
        team2_combobox.set('')

def load_match_list():
    """Fetch matches and populate match_combobox with readable labels."""
    global match_label_to_id
    match_label_to_id = {}

    db = None
    cursor = None
    try:
        db = connect_db()
        cursor = db.cursor()
        cursor.execute("""
            SELECT m.match_id,
                   CONCAT(m.match_id, ': ',
                          COALESCE(t1.team_name, CONCAT('Team#', m.team1_id)),
                          ' vs ',
                          COALESCE(t2.team_name, CONCAT('Team#', m.team2_id)),
                          ' (', DATE_FORMAT(m.match_date, '%Y-%m-%d'), ')') AS label
            FROM Matches m
            LEFT JOIN Team t1 ON m.team1_id = t1.team_id
            LEFT JOIN Team t2 ON m.team2_id = t2.team_id
            ORDER BY m.match_date, m.match_id;
        """)
        rows = cursor.fetchall()
    except mysql.connector.Error as e:
        messagebox.showerror("Database Error", f"Failed to load matches:\n{e}")
        rows = []
    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()

    labels = []
    for match_id, label in rows:
        match_label_to_id[label] = match_id
        labels.append(label)

    match_combobox['values'] = labels
    if labels:
        match_combobox.current(0)
    else:
        match_combobox.set('')

# ---------------- CRUD / Actions ----------------
def fetch_teams():
    db = None
    cursor = None
    try:
        db = connect_db()
        cursor = db.cursor()
        cursor.execute("SELECT team_id, team_name, coach_name, foundation_year, tournament_id FROM Team")
        rows = cursor.fetchall()
    except mysql.connector.Error as e:
        messagebox.showerror("Database Error", str(e))
        rows = []
    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()

    for i in team_table.get_children():
        team_table.delete(i)
    for row in rows:
        team_table.insert("", tk.END, values=row)

    # Also refresh team dropdown options (so create-match comboboxes show latest)
    load_team_options()

def add_team():
    name = team_name_entry.get().strip()
    coach = team_coach_entry.get().strip()
    year_text = team_year_entry.get().strip()

    if not name or not coach:
        messagebox.showerror("Error", "Team Name and Coach Name are required!")
        return

    foundation_year = None
    if year_text:
        try:
            foundation_year = int(year_text)
        except ValueError:
            messagebox.showwarning("Input Error", "Foundation Year must be a number.")
            return

    db = None
    cursor = None
    try:
        db = connect_db()
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO Team (team_name, coach_name, foundation_year, tournament_id) VALUES (%s, %s, %s, %s)",
            (name, coach, foundation_year, 1)
        )
        db.commit()
        messagebox.showinfo("Success", f"Team '{name}' added successfully!")
        fetch_teams()
        load_match_list()
    except mysql.connector.Error as e:
        messagebox.showerror("Database Error", str(e))
    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()

def delete_team():
    selected = team_table.focus()
    if not selected:
        messagebox.showwarning("Selection Error", "Select a team to delete.")
        return
    values = team_table.item(selected, "values")
    team_id = values[0]

    db = None
    cursor = None
    try:
        db = connect_db()
        cursor = db.cursor()
        cursor.execute("DELETE FROM Team WHERE team_id = %s", (team_id,))
        db.commit()
        messagebox.showinfo("Deleted", "Team deleted successfully!")
        fetch_teams()
        load_match_list()
    except mysql.connector.Error as e:
        messagebox.showerror("Database Error", str(e))
    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()

def update_player_weight():
    player_name = update_name_entry.get().strip()
    new_weight = update_weight_entry.get().strip()

    if not player_name or not new_weight:
        messagebox.showwarning("Input Error", "Both fields are required!")
        return

    try:
        weight_val = float(new_weight)
    except ValueError:
        messagebox.showwarning("Input Error", "Weight must be a number (kg).")
        return

    db = None
    cursor = None
    try:
        db = connect_db()
        cursor = db.cursor()
        cursor.execute("SET SQL_SAFE_UPDATES = 0;")
        cursor.execute("UPDATE Player SET weight_kg = %s WHERE name = %s", (weight_val, player_name))
        cursor.execute("SET SQL_SAFE_UPDATES = 1;")
        db.commit()
        messagebox.showinfo("Success", f"Weight updated for {player_name}.")
    except mysql.connector.Error as e:
        messagebox.showerror("Database Error", str(e))
    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()

def show_leaderboard():
    db = None
    cursor = None
    try:
        db = connect_db()
        cursor = db.cursor()
        cursor.execute("SELECT team_id, team_name, matches_played, wins, draws, losses, goals_for, total_points FROM Leaderboard")
        rows = cursor.fetchall()
    except mysql.connector.Error as e:
        messagebox.showerror("Database Error", str(e))
        rows = []
    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()

    for i in leaderboard_table.get_children():
        leaderboard_table.delete(i)
    for row in rows:
        leaderboard_table.insert("", tk.END, values=row)

def add_match_result():
    sel = match_combobox.get().strip()
    if not sel:
        messagebox.showwarning("Input Error", "Select a match first.")
        return

    try:
        match_id = match_label_to_id[sel]
    except KeyError:
        messagebox.showerror("Input Error", "Selected match not recognized. Try reloading match list.")
        load_match_list()
        return

    try:
        goals1 = int(goals1_entry.get().strip())
        goals2 = int(goals2_entry.get().strip())
    except ValueError:
        messagebox.showwarning("Input Error", "Goals must be integers.")
        return

    db = None
    cursor = None
    try:
        db = connect_db()
        cursor = db.cursor()
        cursor.execute("SELECT team1_id, team2_id FROM Matches WHERE match_id = %s", (match_id,))
        row = cursor.fetchone()
        if not row:
            messagebox.showerror("Input Error", f"Match ID {match_id} does not exist (it may have been deleted).")
            load_match_list()
            return
        team1_id, team2_id = row

        cursor.callproc('AddMatchResult', (int(match_id), int(team1_id), int(goals1), int(team2_id), int(goals2)))
        db.commit()
        messagebox.showinfo("Success", "Match result added successfully!")
        show_leaderboard()
        load_match_list()
    except mysql.connector.Error as e:
        messagebox.showerror("Database Error", str(e))
    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()

def calculate_win_percentage():
    team_id_text = win_team_entry.get().strip()
    if not team_id_text:
        messagebox.showwarning("Input Error", "Enter team ID!")
        return
    try:
        team_id = int(team_id_text)
    except ValueError:
        messagebox.showwarning("Input Error", "Team ID must be an integer.")
        return

    db = None
    cursor = None
    try:
        db = connect_db()
        cursor = db.cursor()
        cursor.execute("SELECT GetWinPercentage(%s)", (team_id,))
        result = cursor.fetchone()
        win_pct = result[0] if result else 0
        messagebox.showinfo("Win Percentage", f"Team {team_id} Win % = {win_pct}")
    except mysql.connector.Error as e:
        messagebox.showerror("Database Error", str(e))
    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()

# ---------------- Create Match (GUI) ----------------
def create_match_from_gui():
    # read inputs from create-match widgets
    t1_name = team1_combobox.get().strip()
    t2_name = team2_combobox.get().strip()
    mdate = match_date_entry.get().strip()
    venue = match_venue_entry.get().strip()

    if not (t1_name and t2_name and mdate and venue):
        messagebox.showwarning("Input Error", "All create-match fields are required.")
        return

    if t1_name == t2_name:
        messagebox.showwarning("Input Error", "Team1 and Team2 must be different.")
        return

    # lightweight date validation (YYYY-MM-DD)
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", mdate):
        messagebox.showwarning("Input Error", "Match Date must be in YYYY-MM-DD format.")
        return

    # map names to IDs
    if t1_name not in team_name_to_id or t2_name not in team_name_to_id:
        messagebox.showerror("Input Error", "Selected team(s) not found. Try reloading teams.")
        return

    t1 = team_name_to_id[t1_name]
    t2 = team_name_to_id[t2_name]

    db = None
    cursor = None
    try:
        db = connect_db()
        cursor = db.cursor()

        # double-check both teams exist (safer)
        cursor.execute("SELECT COUNT(*) FROM Team WHERE team_id IN (%s, %s)", (t1, t2))
        cnt = cursor.fetchone()[0]
        if cnt < 2:
            messagebox.showerror("Input Error", "One or both selected teams do not exist.")
            return

        cursor.execute(
            "INSERT INTO Matches (tournament_id, team1_id, team2_id, match_date, venue, status) VALUES (%s,%s,%s,%s,%s,%s)",
            (1, t1, t2, mdate, venue, 'Scheduled')
        )
        db.commit()
        messagebox.showinfo("Created", "Match created successfully.")
        # refresh UI lists
        load_match_list()
    except mysql.connector.Error as e:
        messagebox.showerror("Database Error", str(e))
    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()

# ---------------- MAIN WINDOW ----------------
root = tk.Tk()
root.title("⚽ Football League Management System")
root.geometry("1100x740")
root.configure(bg="#f2f2f2")

title = tk.Label(root, text="Football League Management System", font=("Arial", 20, "bold"), bg="#0066cc", fg="white")
title.pack(fill=tk.X)

tabs = ttk.Notebook(root)
tabs.pack(fill=tk.BOTH, expand=True, pady=10, padx=10)

# ---------------- TAB 1: TEAM MANAGEMENT ----------------
team_tab = ttk.Frame(tabs)
tabs.add(team_tab, text="Manage Teams")

tk.Label(team_tab, text="Team Name:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
team_name_entry = tk.Entry(team_tab)
team_name_entry.grid(row=0, column=1, padx=5, pady=5)

tk.Label(team_tab, text="Coach Name:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
team_coach_entry = tk.Entry(team_tab)
team_coach_entry.grid(row=1, column=1, padx=5, pady=5)

tk.Label(team_tab, text="Foundation Year:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
team_year_entry = tk.Entry(team_tab)
team_year_entry.grid(row=2, column=1, padx=5, pady=5)

add_team_button = tk.Button(team_tab, text="Add Team", command=add_team, bg="green", fg="white")
add_team_button.grid(row=3, column=1, pady=10, sticky="ew")
tk.Button(team_tab, text="Delete Team", command=delete_team, bg="red", fg="white").grid(row=3, column=0, pady=10, sticky="ew")

team_table = ttk.Treeview(team_tab, columns=("ID", "Name", "Coach", "Year", "Tournament"), show="headings")
team_table.heading("ID", text="Team ID")
team_table.heading("Name", text="Team Name")
team_table.heading("Coach", text="Coach")
team_table.heading("Year", text="Year")
team_table.heading("Tournament", text="Tournament ID")
team_table.grid(row=4, column=0, columnspan=3, pady=10, sticky="nsew")
team_tab.grid_rowconfigure(4, weight=1)
team_tab.grid_columnconfigure(2, weight=1)

# ---------------- TAB 2: MATCH RESULTS + CREATE MATCH ----------------
match_tab = ttk.Frame(tabs)
tabs.add(match_tab, text="Add Match Results")

# --- Add Match Result section ---
tk.Label(match_tab, text="Match:").grid(row=0, column=0, padx=5, pady=3, sticky="e")
match_combobox = ttk.Combobox(match_tab, state="readonly", width=60)
match_combobox.grid(row=0, column=1, padx=5, pady=3, sticky="w")

tk.Label(match_tab, text="Team1 Goals:").grid(row=1, column=0, padx=5, pady=3, sticky="e")
goals1_entry = tk.Entry(match_tab)
goals1_entry.grid(row=1, column=1, padx=5, pady=3, sticky="w")

tk.Label(match_tab, text="Team2 Goals:").grid(row=2, column=0, padx=5, pady=3, sticky="e")
goals2_entry = tk.Entry(match_tab)
goals2_entry.grid(row=2, column=1, padx=5, pady=3, sticky="w")

tk.Button(match_tab, text="Add Match Result", command=add_match_result, bg="#0066cc", fg="white").grid(row=3, column=0, columnspan=2, pady=10)

# --- Reload & Create buttons ---
tk.Button(match_tab, text="Reload Matches", command=load_match_list, bg="#009933", fg="white").grid(row=4, column=0, pady=6, sticky="ew")
tk.Button(match_tab, text="Reload Teams", command=load_team_options, bg="#007acc", fg="white").grid(row=4, column=1, pady=6, sticky="ew")

# --- Separator label for clarity ---
sep = ttk.Separator(match_tab, orient='horizontal')
sep.grid(row=5, column=0, columnspan=2, sticky='ew', pady=8)

# --- Create Match section (in same tab) ---
tk.Label(match_tab, text="Create New Match", font=("Arial", 10, "bold")).grid(row=6, column=0, columnspan=2, pady=(0,6))

tk.Label(match_tab, text="Team 1:").grid(row=7, column=0, padx=5, pady=3, sticky="e")
team1_combobox = ttk.Combobox(match_tab, state="readonly", width=40)
team1_combobox.grid(row=7, column=1, padx=5, pady=3, sticky="w")

tk.Label(match_tab, text="Team 2:").grid(row=8, column=0, padx=5, pady=3, sticky="e")
team2_combobox = ttk.Combobox(match_tab, state="readonly", width=40)
team2_combobox.grid(row=8, column=1, padx=5, pady=3, sticky="w")

tk.Label(match_tab, text="Match Date (YYYY-MM-DD):").grid(row=9, column=0, padx=5, pady=3, sticky="e")
match_date_entry = tk.Entry(match_tab)
match_date_entry.grid(row=9, column=1, padx=5, pady=3, sticky="w")

tk.Label(match_tab, text="Venue:").grid(row=10, column=0, padx=5, pady=3, sticky="e")
match_venue_entry = tk.Entry(match_tab)
match_venue_entry.grid(row=10, column=1, padx=5, pady=3, sticky="w")

tk.Button(match_tab, text="Create Match", command=create_match_from_gui, bg="#0066cc", fg="white").grid(row=11, column=0, columnspan=2, pady=10)

# ---------------- TAB 3: LEADERBOARD ----------------
leaderboard_tab = ttk.Frame(tabs)
tabs.add(leaderboard_tab, text="Leaderboard")

leaderboard_table = ttk.Treeview(
    leaderboard_tab,
    columns=("Team ID", "Team Name", "Matches", "Wins", "Draws", "Losses", "Goals", "Points"),
    show="headings"
)
for col in ("Team ID", "Team Name", "Matches", "Wins", "Draws", "Losses", "Goals", "Points"):
    leaderboard_table.heading(col, text=col)
leaderboard_table.pack(fill=tk.BOTH, expand=True, pady=10)
tk.Button(leaderboard_tab, text="Show Leaderboard", command=show_leaderboard, bg="#0066cc", fg="white").pack(pady=6)

# ---------------- TAB 4: PLAYER UPDATE ----------------
update_tab = ttk.Frame(tabs)
tabs.add(update_tab, text="Update Player Weight")

tk.Label(update_tab, text="Player Name:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
update_name_entry = tk.Entry(update_tab)
update_name_entry.grid(row=0, column=1, padx=5, pady=5)

tk.Label(update_tab, text="New Weight (kg):").grid(row=1, column=0, padx=5, pady=5, sticky="e")
update_weight_entry = tk.Entry(update_tab)
update_weight_entry.grid(row=1, column=1, padx=5, pady=5)

tk.Button(update_tab, text="Update Weight", command=update_player_weight, bg="#0066cc", fg="white").grid(row=2, column=0, columnspan=2, pady=10)

# ---------------- TAB 5: TEAM STATS FUNCTION ----------------
stats_tab = ttk.Frame(tabs)
tabs.add(stats_tab, text="Team Stats")

tk.Label(stats_tab, text="Team ID:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
win_team_entry = tk.Entry(stats_tab)
win_team_entry.grid(row=0, column=1, padx=5, pady=5)

tk.Button(stats_tab, text="Get Win Percentage", command=calculate_win_percentage, bg="#0066cc", fg="white").grid(row=1, column=0, columnspan=2, pady=10)

# ---------------- initial data load ----------------
fetch_teams()
load_match_list()
show_leaderboard()

root.mainloop()
