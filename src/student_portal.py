"""
Student Portal - Attendance & Result Management System  (Python + Tkinter)

Python port of the HTML/CSS/JS project (main.html, admin.html, teacher.html,
student.html + storage.js, auth.js, admin.js, teacher.js, student.js).

 * localStorage  ->  portal_data.json (saved next to this file)
 * 3 roles       ->  admin / teacher / student  (default password: 123)
 * Look          ->  teal "Student Management System" style

Run:  python student_portal.py
Needs only the Python standard library (tkinter).
"""

import json
import os
import random
import tkinter as tk
from datetime import date, datetime, timedelta
from tkinter import filedialog, messagebox, simpledialog, ttk

# ----------------------------------------------------------------------------
# Look & feel
# ----------------------------------------------------------------------------
FONT = "Arial"
TEAL = "#0f8f8b"
TEAL_DARK = "#0a6f6c"
TEAL_ROW = "#12a9a4"
BG = "#d9d9d9"
GREEN, BLUE, ORANGE, RED = "#16a34a", "#2563eb", "#ea580c", "#dc2626"

DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "portal_data.json")
DATA_VERSION = "2.0"


# ----------------------------------------------------------------------------
# storage.js  ->  Storage
# ----------------------------------------------------------------------------
class Storage:
    def __init__(self):
        self.data = {}
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                self.data = json.load(f)
        except (OSError, ValueError):
            self.data = {}
        self.initialize_all_data()

    def save(self):
        try:
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2)
        except OSError as e:
            print("Could not save data:", e)

    def get(self, key):
        return self.data.setdefault(key, [])

    def set(self, key, value):
        self.data[key] = value
        self.save()

    @staticmethod
    def now_text(delta_hours=0):
        return (datetime.now() - timedelta(hours=delta_hours)).strftime("%Y-%m-%d %H:%M:%S")

    def initialize_all_data(self):
        d = self.data
        if d.get("dataVersion") != DATA_VERSION:
            d.clear()
            d["dataVersion"] = DATA_VERSION

        if "systemUsers" not in d:
            d["systemUsers"] = [
                {"id": 1, "name": "Ali Ahmed", "username": "admin", "role": "admin", "status": "active"},
                {"id": 2, "name": "Fatima Khan", "username": "teacher", "role": "teacher", "status": "active"},
                {"id": 3, "name": "Sara Malik", "username": "student", "role": "student", "status": "active"},
                {"id": 4, "name": "Ahmed Hassan", "username": "ahmed", "role": "teacher", "status": "active"},
                {"id": 5, "name": "Zainab Ali", "username": "zainab", "role": "student", "status": "active"},
                {"id": 6, "name": "Omar Farooq", "username": "omar", "role": "student", "status": "active"},
            ]

        if "courses" not in d:
            d["courses"] = [
                {"code": "CS101", "name": "Introduction to Programming", "teacher": "Fatima Khan", "students": 15},
                {"code": "CS202", "name": "Data Structures", "teacher": "Ahmed Hassan", "students": 12},
                {"code": "CS303", "name": "Web Development", "teacher": "Fatima Khan", "students": 10},
            ]

        if "students" not in d:
            d["students"] = [
                {"rollNo": "2024-001", "name": "Sara Malik", "course": "CS101", "email": "sara@student.pk"},
                {"rollNo": "2024-002", "name": "Zainab Ali", "course": "CS101", "email": "zainab@student.pk"},
                {"rollNo": "2024-003", "name": "Omar Farooq", "course": "CS202", "email": "omar@student.pk"},
            ]

        if "attendanceRecords" not in d:
            records = []
            today = datetime.now()
            for i in range(5):
                day = today - timedelta(days=i)
                ds = day.date().isoformat()
                records.append({
                    "courseCode": "CS101", "date": ds, "markedBy": "Fatima Khan",
                    "timestamp": day.isoformat(),
                    "students": [
                        {"rollNo": "2024-001", "status": "present" if random.random() > 0.2 else "absent"},
                        {"rollNo": "2024-002", "status": "present" if random.random() > 0.15 else "late"},
                    ],
                })
                records.append({
                    "courseCode": "CS202", "date": ds, "markedBy": "Ahmed Hassan",
                    "timestamp": day.isoformat(),
                    "students": [
                        {"rollNo": "2024-003", "status": "present" if random.random() > 0.15 else "absent"},
                    ],
                })
            d["attendanceRecords"] = records

        if "resultsRecords" not in d:
            ts = datetime.now().isoformat()

            def rec(code, typ, total, by, studs):
                return {"courseCode": code, "assessmentType": typ, "totalMarks": total,
                        "uploadedBy": by, "timestamp": ts, "approved": True, "students": studs}

            d["resultsRecords"] = [
                rec("CS101", "midterm", 100, "Fatima Khan", [
                    {"rollNo": "2024-001", "marks": 85, "grade": "A", "percentage": "85.00"},
                    {"rollNo": "2024-002", "marks": 92, "grade": "A+", "percentage": "92.00"}]),
                rec("CS101", "quiz", 20, "Fatima Khan", [
                    {"rollNo": "2024-001", "marks": 18, "grade": "A", "percentage": "90.00"},
                    {"rollNo": "2024-002", "marks": 20, "grade": "A+", "percentage": "100.00"}]),
                rec("CS202", "midterm", 100, "Ahmed Hassan", [
                    {"rollNo": "2024-003", "marks": 82, "grade": "A-", "percentage": "82.00"}]),
                rec("CS202", "assignment", 50, "Ahmed Hassan", [
                    {"rollNo": "2024-003", "marks": 44, "grade": "A", "percentage": "88.00"}]),
            ]

        if "systemActivity" not in d:
            items = [("User Login", "Ali Ahmed"), ("Attendance Marked", "Fatima Khan"),
                     ("Results Updated", "Ahmed Hassan"), ("Course Added", "Ali Ahmed"),
                     ("Student Enrolled", "Ali Ahmed"), ("User Login", "Fatima Khan"),
                     ("Attendance Marked", "Ahmed Hassan"), ("Results Updated", "Fatima Khan")]
            d["systemActivity"] = [
                {"action": a, "user": u, "time": self.now_text(i + 1)} for i, (a, u) in enumerate(items)]
        self.save()

    def log_activity(self, action, user):
        self.get("systemActivity").append({"action": action, "user": user, "time": self.now_text()})
        self.save()


# ----------------------------------------------------------------------------
# auth.js  ->  fixed demo users
# ----------------------------------------------------------------------------
USERS = {
    "admin": {"username": "admin", "password": "123", "role": "admin", "fullName": "Ali Ahmed"},
    "teacher": {"username": "teacher", "password": "123", "role": "teacher", "fullName": "Fatima Khan"},
    "student": {"username": "student", "password": "123", "role": "student", "fullName": "Sara Malik"},
}


def grade_from_percentage(p):
    if p >= 90: return "A+"
    if p >= 85: return "A"
    if p >= 80: return "A-"
    if p >= 75: return "B+"
    if p >= 70: return "B"
    if p >= 65: return "B-"
    if p >= 60: return "C+"
    if p >= 55: return "C"
    if p >= 50: return "C-"
    return "F"


def grade_color(grade):
    if grade.startswith("A"): return GREEN
    if grade.startswith("B"): return BLUE
    if grade.startswith("C"): return ORANGE
    return RED


# ----------------------------------------------------------------------------
# Small reusable widgets
# ----------------------------------------------------------------------------
def make_button(parent, text, command, width=14, danger=False):
    bg = RED if danger else TEAL
    return tk.Button(parent, text=text, command=command, width=width, bg=bg, fg="white",
                     activebackground=TEAL_DARK if not danger else "#a31515",
                     activeforeground="white", relief="raised", bd=2, cursor="hand2",
                     font=(FONT, 10))


def make_table(parent, columns, widths, height=8):
    """Treeview styled like the screenshot (teal / white striped rows)."""
    frame = tk.Frame(parent, bg=BG)
    ids = ["c%d" % i for i in range(len(columns))]
    tree = ttk.Treeview(frame, columns=ids, show="headings", height=height)
    for cid, text, w in zip(ids, columns, widths):
        tree.heading(cid, text=text)
        tree.column(cid, width=w, anchor="center", stretch=True)
    vsb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=vsb.set)
    tree.pack(side="left", fill="both", expand=True)
    vsb.pack(side="right", fill="y")
    tree.tag_configure("alt", background=TEAL_ROW)
    tree.tag_configure("plain", background="white")
    for name, col in (("gA", GREEN), ("gB", BLUE), ("gC", ORANGE), ("gF", RED)):
        tree.tag_configure(name, foreground=col)
    return frame, tree


def fill_table(tree, rows, empty_msg, extra_tags=None):
    tree.delete(*tree.get_children())
    n = len(tree["columns"])
    if not rows:
        tree.insert("", "end", values=(empty_msg,) + ("",) * (n - 1), tags=("plain",))
        return
    for i, row in enumerate(rows):
        tags = ["alt" if i % 2 == 0 else "plain"]
        if extra_tags:
            t = extra_tags(row)
            if t:
                tags.append(t)
        tree.insert("", "end", values=row, tags=tuple(tags))


def selected_values(tree):
    sel = tree.selection()
    if not sel:
        messagebox.showinfo("Select a row", "Please select a row from the table first.")
        return None
    return tree.item(sel[0], "values")


def stat_cards(parent, items):
    row = tk.Frame(parent, bg=BG)
    row.pack(fill="x", pady=6)
    labels = {}
    for i, (key, title, init) in enumerate(items):
        row.columnconfigure(i, weight=1, uniform="cards")
        lf = tk.LabelFrame(row, text=title, bg=BG, font=(FONT, 10))
        lf.grid(row=0, column=i, sticky="nsew", padx=5)
        lbl = tk.Label(lf, text=init, font=(FONT, 26, "bold"), fg=TEAL_DARK, bg=BG)
        lbl.pack(pady=10)
        labels[key] = lbl
    return labels


def page_header(parent, title, subtitle=None, btn_text=None, btn_cmd=None):
    f = tk.Frame(parent, bg=BG)
    f.pack(fill="x", pady=(4, 8))
    left = tk.Frame(f, bg=BG)
    left.pack(side="left")
    tk.Label(left, text=title, font=(FONT, 18, "bold"), fg=TEAL_DARK, bg=BG).pack(anchor="w")
    if subtitle:
        tk.Label(left, text=subtitle, font=(FONT, 10), fg="#444", bg=BG).pack(anchor="w")
    if btn_text:
        make_button(f, btn_text, btn_cmd, width=18).pack(side="right")
    return f


def card(parent, text=""):
    lf = tk.LabelFrame(parent, text=text, bg=BG, font=(FONT, 11), padx=10, pady=8)
    lf.pack(fill="x", pady=6)
    return lf


class ScrollFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=BG)
        self.canvas = tk.Canvas(self, bg=BG, highlightthickness=0)
        vsb = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.inner = tk.Frame(self.canvas, bg=BG)
        self.win = self.canvas.create_window((0, 0), window=self.inner, anchor="nw")
        self.inner.bind("<Configure>",
                        lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfigure(self.win, width=e.width))


def form_dialog(root, title, fields, submit_text, on_submit):
    """fields: list of (label, key, kind, options)   kind: entry | password | combo"""
    win = tk.Toplevel(root)
    win.title(title)
    win.configure(bg=BG)
    win.transient(root)
    win.resizable(False, False)
    tk.Label(win, text=title, bg=TEAL, fg="white", font=(FONT, 14, "bold"), pady=10).pack(fill="x")
    box = tk.LabelFrame(win, text="Details", bg=BG, font=(FONT, 10), padx=14, pady=10)
    box.pack(fill="both", padx=16, pady=12)
    variables, first = {}, None
    for r, (label, key, kind, opts) in enumerate(fields):
        tk.Label(box, text=label, bg=BG, font=(FONT, 10)).grid(row=r, column=0, sticky="w", pady=6, padx=(0, 10))
        var = tk.StringVar()
        variables[key] = var
        if kind == "combo":
            w = ttk.Combobox(box, textvariable=var, values=opts, state="readonly", width=32)
        else:
            w = tk.Entry(box, textvariable=var, width=34, show="*" if kind == "password" else "")
        w.grid(row=r, column=1, pady=6)
        first = first or w

    def submit(_e=None):
        if on_submit({k: v.get() for k, v in variables.items()}):
            win.destroy()

    bar = tk.Frame(win, bg=BG)
    bar.pack(pady=(0, 14))
    make_button(bar, "Cancel", win.destroy, width=12).pack(side="left", padx=6)
    make_button(bar, submit_text, submit, width=14).pack(side="left", padx=6)
    win.bind("<Return>", submit)
    win.bind("<Escape>", lambda e: win.destroy())
    win.update_idletasks()
    x = root.winfo_rootx() + (root.winfo_width() - win.winfo_width()) // 2
    y = root.winfo_rooty() + (root.winfo_height() - win.winfo_height()) // 3
    win.geometry("+%d+%d" % (max(x, 0), max(y, 0)))
    try:
        win.grab_set()
    except tk.TclError:
        pass
    if first:
        first.focus_set()


def write_pdf(path, lines):
    """Tiny dependency-free PDF writer. lines = [(text, font_size, indent)]"""
    pages, y = [[]], 800
    for text, size, indent in lines:
        lead = size + 6
        if y - lead < 50:
            pages.append([])
            y = 800
        y -= lead
        pages[-1].append((text, size, indent, y))

    def esc(s):
        return s.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")

    n = len(pages)
    kids = " ".join("%d 0 R" % (5 + 2 * i) for i in range(n))
    objs = [b"<< /Type /Catalog /Pages 2 0 R >>",
            ("<< /Type /Pages /Kids [%s] /Count %d >>" % (kids, n)).encode(),
            b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>"]
    for i, items in enumerate(pages):
        stream = "\n".join("BT /F1 %d Tf %d %d Td (%s) Tj ET" % (s, 50 + ind, yy, esc(t))
                           for t, s, ind, yy in items).encode("cp1252", "replace")
        objs.append(b"<< /Length %d >>\nstream\n" % len(stream) + stream + b"\nendstream")
        objs.append(("<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] "
                     "/Resources << /Font << /F1 3 0 R >> >> /Contents %d 0 R >>" % (4 + 2 * i)).encode())
    out, offsets = bytearray(b"%PDF-1.4\n"), []
    for i, o in enumerate(objs, 1):
        offsets.append(len(out))
        out += b"%d 0 obj\n" % i + o + b"\nendobj\n"
    xref = len(out)
    out += b"xref\n0 %d\n0000000000 65535 f \n" % (len(objs) + 1)
    for off in offsets:
        out += b"%010d 00000 n \n" % off
    out += b"trailer\n<< /Size %d /Root 1 0 R >>\nstartxref\n%d\n%%%%EOF" % (len(objs) + 1, xref)
    with open(path, "wb") as f:
        f.write(out)


# ----------------------------------------------------------------------------
# Dashboard base (navbar + sidebar + switchable sections)
# ----------------------------------------------------------------------------
class Dashboard:
    NAV_TITLE = "Student Management System"
    PANEL = ""
    MENU = []  # (section_key, label)

    def __init__(self, app):
        self.app, self.root, self.store, self.user = app, app.root, app.store, app.user
        self.frame = tk.Frame(self.root, bg=BG)
        self.frame.pack(fill="both", expand=True)

        nav = tk.Frame(self.frame, bg=TEAL, height=64)
        nav.pack(fill="x")
        nav.pack_propagate(False)
        tk.Label(nav, text=self.NAV_TITLE, bg=TEAL, fg="white", font=(FONT, 20, "bold")).pack(side="left", padx=20)
        tk.Button(nav, text="Logout", command=app.logout, bg="white", fg=TEAL_DARK, relief="flat",
                  font=(FONT, 10, "bold"), cursor="hand2", width=9).pack(side="right", padx=16)
        tk.Label(nav, text=self.user["fullName"], bg=TEAL, fg="white", font=(FONT, 11)).pack(side="right", padx=8)

        body = tk.Frame(self.frame, bg=BG)
        body.pack(fill="both", expand=True, padx=12, pady=12)
        side = tk.LabelFrame(body, text=self.PANEL, bg=BG, font=(FONT, 11), padx=8, pady=8)
        side.pack(side="left", fill="y")
        self.main = tk.Frame(body, bg=BG)
        self.main.pack(side="right", fill="both", expand=True, padx=(12, 0))

        self.sections, self.buttons, self.current = {}, {}, None
        for key, label in self.MENU:
            b = tk.Button(side, text=label, anchor="w", width=22, relief="flat", bg="#c4c4c4",
                          font=(FONT, 10), cursor="hand2", padx=10, pady=6,
                          command=lambda k=key: self.show_section(k))
            b.pack(fill="x", pady=3)
            self.buttons[key] = b
            sf = ScrollFrame(self.main)
            self.sections[key] = sf
            getattr(self, "build_" + key)(sf.inner)

        self.root.bind_all("<MouseWheel>", self._wheel)
        self.root.bind_all("<Button-4>", self._wheel)
        self.root.bind_all("<Button-5>", self._wheel)
        self.refresh()
        self.show_section(self.MENU[0][0])

    def _wheel(self, e):
        if self.current is None or isinstance(e.widget, ttk.Treeview):
            return
        try:
            step = -1 if (e.num == 4 or getattr(e, "delta", 0) > 0) else 1
            self.sections[self.current].canvas.yview_scroll(step, "units")
        except tk.TclError:
            pass

    def show_section(self, key):
        for k, sf in self.sections.items():
            sf.pack_forget()
            self.buttons[k].configure(bg="#c4c4c4", fg="black")
        self.sections[key].pack(fill="both", expand=True)
        self.buttons[key].configure(bg=TEAL, fg="white")
        self.current = key
        self.refresh()

    def destroy(self):
        for ev in ("<MouseWheel>", "<Button-4>", "<Button-5>"):
            self.root.unbind_all(ev)
        self.frame.destroy()

    def refresh(self):
        pass


# ----------------------------------------------------------------------------
# admin.html + admin.js
# ----------------------------------------------------------------------------
class AdminDashboard(Dashboard):
    PANEL = "Admin Panel"
    MENU = [("overview", "Overview"), ("users", "User Management"), ("courses", "Course Management"),
            ("students", "Student Enrollment"), ("reports", "Reports & Analytics")]

    # ---- build ----
    def build_overview(self, p):
        page_header(p, "Dashboard Overview", "Welcome back, Administrator")
        self.stats = stat_cards(p, [("users", "Total Users", "0"), ("teachers", "Teachers", "0"),
                                    ("students", "Students", "0"), ("courses", "Active Courses", "0")])
        self.activity_box = card(p, "Recent System Activity")

    def build_users(self, p):
        page_header(p, "User Management", btn_text="Add New User", btn_cmd=self.open_add_user)
        frame, self.users_tree = make_table(p, ["ID", "Name", "Username", "Role", "Status"],
                                            [60, 200, 150, 110, 110], 10)
        frame.pack(fill="x", pady=4)
        bar = tk.Frame(p, bg=BG)
        bar.pack(fill="x", pady=6)
        make_button(bar, "Edit", self.edit_user).pack(side="left", padx=4)
        make_button(bar, "Delete", self.delete_user, danger=True).pack(side="left", padx=4)

    def build_courses(self, p):
        page_header(p, "Course Management", btn_text="Add New Course", btn_cmd=self.open_add_course)
        frame, self.courses_tree = make_table(p, ["Course Code", "Course Name", "Teacher", "Students"],
                                              [110, 260, 160, 90], 10)
        frame.pack(fill="x", pady=4)
        bar = tk.Frame(p, bg=BG)
        bar.pack(fill="x", pady=6)
        make_button(bar, "Edit", self.edit_course).pack(side="left", padx=4)
        make_button(bar, "Delete", self.delete_course, danger=True).pack(side="left", padx=4)

    def build_students(self, p):
        page_header(p, "Student Enrollment", btn_text="Enroll Student", btn_cmd=self.open_enroll)
        frame, self.students_tree = make_table(p, ["Roll No", "Name", "Email", "Enrolled Course"],
                                               [100, 170, 200, 220], 10)
        frame.pack(fill="x", pady=4)
        bar = tk.Frame(p, bg=BG)
        bar.pack(fill="x", pady=6)
        make_button(bar, "Edit", self.edit_student).pack(side="left", padx=4)
        make_button(bar, "Delete", self.delete_student, danger=True).pack(side="left", padx=4)

    def build_reports(self, p):
        page_header(p, "Reports & Analytics")
        row = tk.Frame(p, bg=BG)
        row.pack(fill="x")
        items = [("Attendance Reports", "Generate attendance reports by class, course, or date range.",
                  "Generate Report", self.attendance_report),
                 ("Performance Analytics", "View student performance trends and statistics.",
                  "View Analytics", self.view_analytics),
                 ("Result Summary", "Download complete result sheets and grade reports.",
                  "Download PDF", self.download_report)]
        for i, (t, d, b, cmd) in enumerate(items):
            row.columnconfigure(i, weight=1, uniform="rep")
            lf = tk.LabelFrame(row, text=t, bg=BG, font=(FONT, 11), padx=10, pady=10)
            lf.grid(row=0, column=i, sticky="nsew", padx=5)
            tk.Label(lf, text=d, bg=BG, wraplength=200, justify="left", font=(FONT, 10)).pack(pady=(0, 10))
            make_button(lf, b, cmd, width=16).pack()
        self.analytics_box = tk.LabelFrame(p, text="Performance Analytics", bg=BG, font=(FONT, 11), padx=10, pady=8)

    # ---- refresh ----
    def refresh(self):
        users, courses = self.store.get("systemUsers"), self.store.get("courses")
        self.stats["users"].config(text=len(users))
        self.stats["teachers"].config(text=len([u for u in users if u["role"] == "teacher"]))
        self.stats["students"].config(text=len([u for u in users if u["role"] == "student"]))
        self.stats["courses"].config(text=len(courses))

        for w in self.activity_box.winfo_children():
            w.destroy()
        activity = self.store.get("systemActivity")
        if not activity:
            tk.Label(self.activity_box, text="No recent activity", bg=BG, fg="#666").pack(anchor="w")
        for act in list(reversed(activity[-5:])):
            f = tk.Frame(self.activity_box, bg="white", padx=8, pady=4)
            f.pack(fill="x", pady=2)
            tk.Label(f, text="%s by %s" % (act["action"], act["user"]), bg="white",
                     font=(FONT, 10, "bold")).pack(anchor="w")
            tk.Label(f, text=act["time"], bg="white", fg="#777", font=(FONT, 9)).pack(anchor="w")

        fill_table(self.users_tree, [(u["id"], u["name"], u["username"], u["role"], u["status"]) for u in users],
                   "No users found")
        fill_table(self.courses_tree, [(c["code"], c["name"], c["teacher"], c["students"]) for c in courses],
                   "No courses found")
        rows = []
        for s in self.store.get("students"):
            c = next((c for c in courses if c["code"] == s["course"]), None)
            rows.append((s["rollNo"], s["name"], s["email"], c["name"] if c else "Not Enrolled"))
        fill_table(self.students_tree, rows, "No students found")

    # ---- users ----
    def open_add_user(self):
        fields = [("Full Name:", "name", "entry", None), ("Username:", "username", "entry", None),
                  ("Password:", "password", "password", None),
                  ("Role:", "role", "combo", ["admin", "teacher", "student"])]

        def submit(v):
            name, username, password, role = v["name"].strip(), v["username"].strip(), v["password"], v["role"]
            if not name or not username or not password or not role:
                messagebox.showwarning("Missing data", "Please fill all fields!")
                return False
            users = self.store.get("systemUsers")
            if any(u["username"] == username for u in users):
                messagebox.showwarning("Duplicate", "Username already exists!")
                return False
            users.append({"id": max([u["id"] for u in users] + [0]) + 1, "name": name, "username": username,
                          "password": password, "role": role, "status": "active"})
            self.store.set("systemUsers", users)
            if role == "student":
                students = self.store.get("students")
                n = len(students) + 1
                while any(s["rollNo"] == "2024-%03d" % n for s in students):
                    n += 1
                students.append({"rollNo": "2024-%03d" % n, "name": name, "course": "",
                                 "email": username + "@student.pk"})
                self.store.set("students", students)
            messagebox.showinfo("Success", "User added successfully!")
            self.refresh()
            return True

        form_dialog(self.root, "Add New User", fields, "Add User", submit)

    def edit_user(self):
        vals = selected_values(self.users_tree)
        if not vals or not str(vals[0]).isdigit():
            return
        users = self.store.get("systemUsers")
        user = next((u for u in users if u["id"] == int(vals[0])), None)
        if not user:
            return
        new = simpledialog.askstring("Edit User", "Edit name:", initialvalue=user["name"], parent=self.root)
        if new:
            user["name"] = new
            self.store.set("systemUsers", users)
            messagebox.showinfo("Success", "User updated successfully!")
            self.refresh()

    def delete_user(self):
        vals = selected_values(self.users_tree)
        if not vals or not str(vals[0]).isdigit():
            return
        if not messagebox.askyesno("Confirm", "Are you sure you want to delete this user?"):
            return
        users = self.store.get("systemUsers")
        user = next((u for u in users if u["id"] == int(vals[0])), None)
        if user and user["role"] == "student":
            self.store.set("students", [s for s in self.store.get("students") if s["name"] != user["name"]])
        self.store.set("systemUsers", [u for u in users if u["id"] != int(vals[0])])
        messagebox.showinfo("Success", "User deleted successfully!")
        self.refresh()

    # ---- courses ----
    def open_add_course(self):
        teachers = [u["name"] for u in self.store.get("systemUsers") if u["role"] == "teacher"]
        fields = [("Course Code:", "code", "entry", None), ("Course Name:", "name", "entry", None),
                  ("Assign Teacher:", "teacher", "combo", teachers)]

        def submit(v):
            code, name, teacher = v["code"].strip().upper(), v["name"].strip(), v["teacher"]
            if not code or not name or not teacher:
                messagebox.showwarning("Missing data", "Please fill all fields!")
                return False
            courses = self.store.get("courses")
            if any(c["code"] == code for c in courses):
                messagebox.showwarning("Duplicate", "Course code already exists!")
                return False
            courses.append({"code": code, "name": name, "teacher": teacher, "students": 0})
            self.store.set("courses", courses)
            messagebox.showinfo("Success", "Course added successfully!")
            self.refresh()
            return True

        form_dialog(self.root, "Add New Course", fields, "Add Course", submit)

    def edit_course(self):
        vals = selected_values(self.courses_tree)
        if not vals:
            return
        courses = self.store.get("courses")
        course = next((c for c in courses if c["code"] == vals[0]), None)
        if not course:
            return
        new = simpledialog.askstring("Edit Course", "Edit course name:", initialvalue=course["name"], parent=self.root)
        if new:
            course["name"] = new
            self.store.set("courses", courses)
            messagebox.showinfo("Success", "Course updated successfully!")
            self.refresh()

    def delete_course(self):
        vals = selected_values(self.courses_tree)
        if not vals:
            return
        if not messagebox.askyesno("Confirm", "Are you sure you want to delete this course?"):
            return
        self.store.set("courses", [c for c in self.store.get("courses") if c["code"] != vals[0]])
        messagebox.showinfo("Success", "Course deleted successfully!")
        self.refresh()

    # ---- students / enrollment ----
    def open_enroll(self):
        students = [u["name"] for u in self.store.get("systemUsers") if u["role"] == "student"]
        courses = ["%s - %s" % (c["code"], c["name"]) for c in self.store.get("courses")]
        fields = [("Select Student:", "student", "combo", students), ("Select Course:", "course", "combo", courses)]

        def submit(v):
            name, course_txt = v["student"], v["course"]
            if not name or not course_txt:
                messagebox.showwarning("Missing data", "Please select both student and course!")
                return False
            code = course_txt.split(" - ")[0]
            studs, courses_ = self.store.get("students"), self.store.get("courses")
            s = next((s for s in studs if s["name"] == name), None)
            if not s:
                messagebox.showerror("Error", "Student not found!")
                return False
            c = next((c for c in courses_ if c["code"] == code), None)
            if not c:
                messagebox.showerror("Error", "Course not found!")
                return False
            s["course"] = code
            c["students"] += 1
            self.store.set("students", studs)
            self.store.set("courses", courses_)
            messagebox.showinfo("Success", "Student enrolled successfully in " + code)
            self.refresh()
            return True

        form_dialog(self.root, "Enroll Student in Course", fields, "Enroll Student", submit)

    def edit_student(self):
        vals = selected_values(self.students_tree)
        if not vals:
            return
        studs = self.store.get("students")
        s = next((s for s in studs if s["rollNo"] == vals[0]), None)
        if not s:
            return
        new = simpledialog.askstring("Edit Student", "Edit email:", initialvalue=s["email"], parent=self.root)
        if new:
            s["email"] = new
            self.store.set("students", studs)
            self.refresh()

    def delete_student(self):
        vals = selected_values(self.students_tree)
        if not vals:
            return
        if not messagebox.askyesno("Confirm", "Are you sure you want to delete this student?"):
            return
        self.store.set("students", [s for s in self.store.get("students") if s["rollNo"] != vals[0]])
        self.refresh()

    # ---- reports ----
    def view_analytics(self):
        results, attendance = self.store.get("resultsRecords"), self.store.get("attendanceRecords")
        total_pct = count = 0
        for r in results:
            for s in r["students"]:
                total_pct += float(s["percentage"])
                count += 1
        avg_perf = "%.2f" % (total_pct / count) if count else "0"
        present = classes = 0
        for r in attendance:
            for s in r["students"]:
                classes += 1
                if s["status"] in ("present", "late"):
                    present += 1
        avg_att = round(present / classes * 100) if classes else 0

        for w in self.analytics_box.winfo_children():
            w.destroy()
        self.analytics_box.pack(fill="x", pady=10)
        row = tk.Frame(self.analytics_box, bg=BG)
        row.pack(fill="x")
        for i, (t, v) in enumerate([("Average Performance", "%s%%" % avg_perf),
                                    ("Average Attendance", "%s%%" % avg_att),
                                    ("Total Assessments", str(len(results)))]):
            row.columnconfigure(i, weight=1, uniform="an")
            lf = tk.LabelFrame(row, text=t, bg=BG, font=(FONT, 10))
            lf.grid(row=0, column=i, sticky="nsew", padx=5)
            tk.Label(lf, text=v, font=(FONT, 22, "bold"), fg=TEAL_DARK, bg=BG).pack(pady=10)

    def download_report(self):
        path = filedialog.asksaveasfilename(defaultextension=".pdf", initialfile="system-report.pdf",
                                            filetypes=[("PDF", "*.pdf")])
        if not path:
            return
        users = self.store.get("systemUsers")
        lines = [("Student Portal - System Report", 20, 0),
                 ("Generated on: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 12, 0),
                 ("", 12, 0), ("System Statistics:", 16, 0),
                 ("Total Users: %d" % len(users), 12, 0),
                 ("Total Teachers: %d" % len([u for u in users if u["role"] == "teacher"]), 12, 0),
                 ("Total Students: %d" % len([u for u in users if u["role"] == "student"]), 12, 0),
                 ("Total Courses: %d" % len(self.store.get("courses")), 12, 0),
                 ("Total Assessments: %d" % len(self.store.get("resultsRecords")), 12, 0),
                 ("Total Attendance Records: %d" % len(self.store.get("attendanceRecords")), 12, 0)]
        write_pdf(path, lines)
        messagebox.showinfo("Success", "Report downloaded successfully!")

    def attendance_report(self):
        path = filedialog.asksaveasfilename(defaultextension=".pdf", initialfile="attendance-report.pdf",
                                            filetypes=[("PDF", "*.pdf")])
        if not path:
            return
        lines = [("Attendance Report", 18, 0), ("", 10, 0)]
        for rec in self.store.get("attendanceRecords"):
            lines.append(("%s - %s" % (rec["courseCode"], rec["date"]), 14, 0))
            for s in rec["students"]:
                lines.append(("%s: %s" % (s["rollNo"], s["status"]), 10, 10))
            lines.append(("", 6, 0))
        write_pdf(path, lines)
        messagebox.showinfo("Success", "Attendance report downloaded!")


# ----------------------------------------------------------------------------
# teacher.html + teacher.js
# ----------------------------------------------------------------------------
class TeacherDashboard(Dashboard):
    NAV_TITLE = "Student Management System - Teacher"
    PANEL = "Teacher Panel"
    MENU = [("overview", "Dashboard"), ("attendance", "Mark Attendance"),
            ("results", "Upload Results"), ("mycourses", "My Courses")]

    def teacher_courses(self):
        return [c for c in self.store.get("courses") if c["teacher"] == self.user["fullName"]]

    def build_overview(self, p):
        page_header(p, "Teacher Dashboard", "Welcome back, " + self.user["fullName"])
        self.stats = stat_cards(p, [("courses", "My Courses", "0"), ("students", "Total Students", "0"),
                                    ("att", "Attendance Marked", "0"), ("res", "Results Uploaded", "0")])
        qa = card(p, "Quick Actions")
        row = tk.Frame(qa, bg=BG)
        row.pack(fill="x")
        for i, (t, d, b, key) in enumerate([
                ("Mark Attendance", "Quickly mark today's attendance for your classes.", "Go to Attendance", "attendance"),
                ("Upload Results", "Enter and upload student marks and grades.", "Upload Results", "results")]):
            row.columnconfigure(i, weight=1, uniform="qa")
            lf = tk.LabelFrame(row, text=t, bg=BG, font=(FONT, 11), padx=10, pady=10)
            lf.grid(row=0, column=i, sticky="nsew", padx=5)
            tk.Label(lf, text=d, bg=BG, font=(FONT, 10), wraplength=260, justify="left").pack(pady=(0, 10))
            make_button(lf, b, lambda k=key: self.show_section(k), width=18).pack()

    # ---- attendance ----
    def build_attendance(self, p):
        page_header(p, "Mark Attendance", "Select course and date to mark attendance")
        f = card(p)
        tk.Label(f, text="Select Course:", bg=BG).grid(row=0, column=0, sticky="w", padx=4)
        tk.Label(f, text="Date (YYYY-MM-DD):", bg=BG).grid(row=0, column=1, sticky="w", padx=4)
        self.att_course = tk.StringVar()
        self.att_date = tk.StringVar(value=date.today().isoformat())
        self.att_combo = ttk.Combobox(f, textvariable=self.att_course, state="readonly", width=34)
        self.att_combo.grid(row=1, column=0, padx=4, pady=4)
        tk.Entry(f, textvariable=self.att_date, width=20).grid(row=1, column=1, padx=4, pady=4)
        make_button(f, "Load Students", self.load_students_attendance).grid(row=1, column=2, padx=10)
        self.att_card = tk.LabelFrame(p, text="Student List - Mark Attendance", bg=BG, font=(FONT, 11),
                                      padx=10, pady=8)
        self.att_rows, self.att_vars = None, {}

    def load_students_attendance(self):
        code = self.att_course.get().split(" - ")[0]
        d = self.att_date.get().strip()
        try:
            datetime.strptime(d, "%Y-%m-%d")
        except ValueError:
            d = ""
        if not code or not d:
            messagebox.showwarning("Missing data", "Please select both course and a valid date (YYYY-MM-DD)!")
            return
        studs = [s for s in self.store.get("students") if s["course"] == code]
        if not studs:
            messagebox.showinfo("No students", "No students found for this course!")
            return
        for w in self.att_card.winfo_children():
            w.destroy()
        self.att_card.pack(fill="x", pady=6)
        self.att_vars = {}
        grid = tk.Frame(self.att_card, bg=BG)
        grid.pack(fill="x")
        for c, t in enumerate(("Roll No", "Student Name", "Status")):
            tk.Label(grid, text=t, bg="#f2f2f2", font=(FONT, 10, "bold"), width=22, relief="groove").grid(row=0, column=c, sticky="ew")
        for r, s in enumerate(studs, 1):
            bg = TEAL_ROW if r % 2 == 1 else "white"
            tk.Label(grid, text=s["rollNo"], bg=bg, width=22).grid(row=r, column=0, sticky="ew")
            tk.Label(grid, text=s["name"], bg=bg, width=22).grid(row=r, column=1, sticky="ew")
            var = tk.StringVar(value="Present")
            self.att_vars[s["rollNo"]] = var
            ttk.Combobox(grid, textvariable=var, values=["Present", "Absent", "Late"],
                         state="readonly", width=18).grid(row=r, column=2, padx=4, pady=1)
        make_button(self.att_card, "Save Attendance", self.save_attendance, width=18).pack(pady=(12, 2), anchor="w")

    def save_attendance(self):
        code, d = self.att_course.get().split(" - ")[0], self.att_date.get().strip()
        if not self.att_vars:
            messagebox.showwarning("No data", "No attendance data to save!")
            return
        try:
            records = self.store.get("attendanceRecords")
            record = {"courseCode": code, "date": d, "markedBy": self.user["fullName"],
                      "timestamp": datetime.now().isoformat(),
                      "students": [{"rollNo": r, "status": v.get().lower()} for r, v in self.att_vars.items()]}
            idx = next((i for i, r in enumerate(records) if r["courseCode"] == code and r["date"] == d), -1)
            if idx >= 0:
                records[idx] = record
                messagebox.showinfo("Success", "Attendance updated successfully!")
            else:
                records.append(record)
                messagebox.showinfo("Success", "Attendance saved successfully!")
            self.store.set("attendanceRecords", records)
            self.att_card.pack_forget()
            self.att_vars = {}
            self.att_course.set("")
            self.refresh()
        except Exception as e:  # noqa
            print("Error saving attendance:", e)
            messagebox.showerror("Error", "Failed to save attendance. Please try again.")

    # ---- results ----
    def build_results(self, p):
        page_header(p, "Upload Results", "Enter student marks and grades")
        f = card(p)
        self.res_course, self.res_type, self.res_total = tk.StringVar(), tk.StringVar(), tk.StringVar()
        tk.Label(f, text="Select Course:", bg=BG).grid(row=0, column=0, sticky="w", padx=4)
        tk.Label(f, text="Assessment Type:", bg=BG).grid(row=0, column=1, sticky="w", padx=4)
        tk.Label(f, text="Total Marks:", bg=BG).grid(row=0, column=2, sticky="w", padx=4)
        self.res_combo = ttk.Combobox(f, textvariable=self.res_course, state="readonly", width=34)
        self.res_combo.grid(row=1, column=0, padx=4, pady=4)
        ttk.Combobox(f, textvariable=self.res_type, state="readonly", width=16,
                     values=["Mid Term", "Final Exam", "Assignment", "Quiz"]).grid(row=1, column=1, padx=4)
        tk.Entry(f, textvariable=self.res_total, width=10).grid(row=1, column=2, padx=4)
        make_button(f, "Load Students", self.load_students_results).grid(row=1, column=3, padx=10)
        self.res_card = tk.LabelFrame(p, text="Enter Student Marks", bg=BG, font=(FONT, 11), padx=10, pady=8)
        self.mark_vars, self.grade_labels, self.res_total_value = {}, {}, 0

    TYPE_MAP = {"Mid Term": "midterm", "Final Exam": "final", "Assignment": "assignment", "Quiz": "quiz"}

    def load_students_results(self):
        code = self.res_course.get().split(" - ")[0]
        typ, total = self.res_type.get(), self.res_total.get().strip()
        if not code or not typ or not total:
            messagebox.showwarning("Missing data", "Please fill all fields!")
            return
        if not total.isdigit() or int(total) < 1:
            messagebox.showwarning("Invalid", "Total marks must be a positive number!")
            return
        studs = [s for s in self.store.get("students") if s["course"] == code]
        if not studs:
            messagebox.showinfo("No students", "No students found for this course!")
            return
        self.res_total_value = int(total)
        for w in self.res_card.winfo_children():
            w.destroy()
        self.res_card.pack(fill="x", pady=6)
        self.mark_vars, self.grade_labels = {}, {}
        grid = tk.Frame(self.res_card, bg=BG)
        grid.pack(fill="x")
        for c, t in enumerate(("Roll No", "Student Name", "Marks Obtained", "Grade")):
            tk.Label(grid, text=t, bg="#f2f2f2", font=(FONT, 10, "bold"), width=18, relief="groove").grid(row=0, column=c, sticky="ew")
        for r, s in enumerate(studs, 1):
            bg = TEAL_ROW if r % 2 == 1 else "white"
            tk.Label(grid, text=s["rollNo"], bg=bg, width=18).grid(row=r, column=0, sticky="ew")
            tk.Label(grid, text=s["name"], bg=bg, width=18).grid(row=r, column=1, sticky="ew")
            var = tk.StringVar()
            self.mark_vars[s["rollNo"]] = var
            tk.Entry(grid, textvariable=var, width=14, justify="center").grid(row=r, column=2, pady=2)
            gl = tk.Label(grid, text="-", bg=bg, width=18)
            gl.grid(row=r, column=3, sticky="ew")
            self.grade_labels[s["rollNo"]] = gl
            var.trace_add("write", lambda *_a, rn=s["rollNo"]: self.calculate_grade(rn))
        make_button(self.res_card, "Save Results", self.save_results, width=18).pack(pady=(12, 2), anchor="w")

    def calculate_grade(self, roll):
        var, label, total = self.mark_vars[roll], self.grade_labels[roll], self.res_total_value
        try:
            marks = float(var.get())
        except ValueError:
            label.config(text="-")
            return
        if marks < 0:
            label.config(text="-")
            return
        if marks > total:
            messagebox.showwarning("Invalid marks", "Marks cannot exceed %d" % total)
            var.set(str(total))
            return
        grade = grade_from_percentage(marks / total * 100)
        label.config(text=grade, font=(FONT, 10, "bold"), fg=grade_color(grade))

    def save_results(self):
        if not self.mark_vars:
            messagebox.showwarning("No data", "No results data to save!")
            return
        if not all(v.get().strip() for v in self.mark_vars.values()):
            if not messagebox.askyesno("Confirm", "Some marks are missing. Do you want to continue?"):
                return
        try:
            total = self.res_total_value
            records = self.store.get("resultsRecords")
            students = []
            for roll, var in self.mark_vars.items():
                try:
                    marks = float(var.get())
                except ValueError:
                    marks = 0
                marks = int(marks) if marks == int(marks) else marks
                students.append({"rollNo": roll, "marks": marks, "grade": self.grade_labels[roll].cget("text"),
                                 "percentage": "%.2f" % (marks / total * 100)})
            records.append({"courseCode": self.res_course.get().split(" - ")[0],
                            "assessmentType": self.TYPE_MAP.get(self.res_type.get(), self.res_type.get().lower()),
                            "totalMarks": total, "uploadedBy": self.user["fullName"],
                            "timestamp": datetime.now().isoformat(), "approved": True, "students": students})
            self.store.set("resultsRecords", records)
            messagebox.showinfo("Success", "Results saved successfully!")
            self.res_card.pack_forget()
            self.mark_vars = {}
            self.res_course.set("")
            self.res_type.set("")
            self.res_total.set("")
            self.refresh()
        except Exception as e:  # noqa
            print("Error saving results:", e)
            messagebox.showerror("Error", "Failed to save results. Please try again.")

    # ---- my courses ----
    def build_mycourses(self, p):
        page_header(p, "My Courses")
        frame, self.my_tree = make_table(p, ["Course Code", "Course Name", "Students Enrolled"], [120, 300, 150], 10)
        frame.pack(fill="x", pady=4)
        bar = tk.Frame(p, bg=BG)
        bar.pack(fill="x", pady=6)
        make_button(bar, "View Details", self.view_details).pack(side="left", padx=4)

    def view_details(self):
        vals = selected_values(self.my_tree)
        if vals:
            messagebox.showinfo("Course Details", "Course Details: " + vals[0])

    def refresh(self):
        mine = self.teacher_courses()
        codes = [c["code"] for c in mine]
        self.stats["courses"].config(text=len(mine))
        self.stats["students"].config(text=len([s for s in self.store.get("students") if s["course"] in codes]))
        self.stats["att"].config(text=len([r for r in self.store.get("attendanceRecords") if r["courseCode"] in codes]))
        self.stats["res"].config(text=len([r for r in self.store.get("resultsRecords") if r["courseCode"] in codes]))
        values = ["%s - %s" % (c["code"], c["name"]) for c in mine]
        self.att_combo.configure(values=values)
        self.res_combo.configure(values=values)
        fill_table(self.my_tree, [(c["code"], c["name"], c["students"]) for c in mine], "No courses assigned")


# ----------------------------------------------------------------------------
# student.html + student.js
# ----------------------------------------------------------------------------
class StudentDashboard(Dashboard):
    PANEL = "Student Panel"
    MENU = [("overview", "Dashboard"), ("attendance", "My Attendance"), ("results", "My Results"),
            ("courses", "My Courses"), ("profile", "My Profile")]

    def __init__(self, app):
        students = app.store.get("students")
        self.student = next((s for s in students if s["name"] == app.user["fullName"]),
                            students[0] if students else None)
        self.roll = self.student["rollNo"] if self.student else "2024-001"
        self.course = self.student["course"] if self.student else "CS101"
        super().__init__(app)

    # ---- calculations ----
    def overall_attendance(self, records):
        total = present = 0
        for r in records:
            s = next((s for s in r["students"] if s["rollNo"] == self.roll), None)
            if s:
                total += 1
                if s["status"] in ("present", "late"):
                    present += 1
        return total, present, round(present / total * 100) if total else 0

    def average_grade(self, records):
        total_pct = count = 0
        for r in records:
            s = next((s for s in r["students"] if s["rollNo"] == self.roll), None)
            if s and r["approved"]:
                total_pct += float(s["percentage"])
                count += 1
        grade = grade_from_percentage(total_pct / count) if count else "-"
        return grade, count, (total_pct / count) if count else 0

    # ---- build ----
    def build_overview(self, p):
        page_header(p, "Student Dashboard", "Welcome back, " + self.user["fullName"])
        self.ov = stat_cards(p, [("courses", "Enrolled Courses", "0"), ("att", "Overall Attendance", "0%"),
                                 ("grade", "Average Grade", "-"), ("assess", "Assessments", "0")])
        self.alert = tk.LabelFrame(p, text="Attendance Warning", bg="#f3d6d6", fg="#991b1b", font=(FONT, 11, "bold"),
                                   padx=10, pady=8)
        tk.Label(self.alert, bg="#f3d6d6", fg="#7f1d1d", font=(FONT, 10), justify="left", wraplength=700,
                 text="Your attendance is below 75%. Please attend classes regularly to meet the minimum requirement."
                 ).pack(anchor="w")
        qa = card(p, "Quick Overview")
        row = tk.Frame(qa, bg=BG)
        row.pack(fill="x")
        for i, (t, d, b, key) in enumerate([
                ("Attendance Status", "Check your attendance percentage for all courses.", "View Attendance", "attendance"),
                ("Academic Performance", "View your marks, grades, and performance reports.", "View Results", "results")]):
            row.columnconfigure(i, weight=1, uniform="qo")
            lf = tk.LabelFrame(row, text=t, bg=BG, font=(FONT, 11), padx=10, pady=10)
            lf.grid(row=0, column=i, sticky="nsew", padx=5)
            tk.Label(lf, text=d, bg=BG, font=(FONT, 10), wraplength=260, justify="left").pack(pady=(0, 10))
            make_button(lf, b, lambda k=key: self.show_section(k), width=18).pack()

    def build_attendance(self, p):
        page_header(p, "My Attendance", "View your attendance records for all courses")
        box = card(p, "Overall Attendance Summary")
        self.att_cards = stat_cards(box, [("total", "Total Classes", "0"), ("att", "Classes Attended", "0"),
                                          ("pct", "Attendance Percentage", "0%")])
        cw = card(p, "Course-wise Attendance")
        frame, self.cw_tree = make_table(cw, ["Course Code", "Course Name", "Total Classes", "Present", "Absent",
                                              "Percentage", "Status"], [90, 190, 90, 70, 70, 90, 70], 4)
        frame.pack(fill="x")
        lg = card(p, "Attendance Log")
        tk.Label(lg, text="Filter by Course:", bg=BG).pack(anchor="w")
        self.att_filter = tk.StringVar()
        self.att_filter_combo = ttk.Combobox(lg, textvariable=self.att_filter, state="readonly", width=40)
        self.att_filter_combo.pack(anchor="w", pady=4)
        self.att_filter_combo.bind("<<ComboboxSelected>>", lambda e: self.filter_attendance_log())
        frame, self.log_tree = make_table(lg, ["Date", "Course", "Status"], [120, 320, 120], 6)
        frame.pack(fill="x", pady=4)

    def build_results(self, p):
        page_header(p, "My Results", "View your academic performance and grades")
        box = card(p, "Performance Summary")
        self.res_cards = stat_cards(box, [("total", "Total Assessments", "0"), ("pct", "Average Percentage", "0%"),
                                          ("grade", "Average Grade", "-")])
        cr = card(p, "Course-wise Results")
        tk.Label(cr, text="Select Course:", bg=BG).pack(anchor="w")
        self.res_filter = tk.StringVar()
        self.res_filter_combo = ttk.Combobox(cr, textvariable=self.res_filter, state="readonly", width=40)
        self.res_filter_combo.pack(anchor="w", pady=4)
        self.res_filter_combo.bind("<<ComboboxSelected>>", lambda e: self.filter_course_results())
        frame, self.res_tree = make_table(cr, ["Assessment Type", "Total Marks", "Obtained Marks", "Percentage",
                                               "Grade", "Date"], [120, 90, 110, 90, 70, 100], 6)
        frame.pack(fill="x", pady=4)

    def build_courses(self, p):
        page_header(p, "My Courses")
        frame, self.mc_tree = make_table(p, ["Course Code", "Course Name", "Teacher", "Attendance"],
                                         [110, 260, 160, 100], 8)
        frame.pack(fill="x", pady=4)

    def build_profile(self, p):
        page_header(p, "My Profile")
        box = card(p, "Student Information")
        self.profile = {}
        for r, (key, label) in enumerate([("name", "Full Name:"), ("roll", "Roll Number:"),
                                          ("email", "Email:"), ("course", "Enrolled Course:")]):
            tk.Label(box, text=label, bg=BG, font=(FONT, 10, "bold"), width=18, anchor="w").grid(row=r, column=0, pady=6)
            lbl = tk.Label(box, text="-", bg=BG, font=(FONT, 10), anchor="w")
            lbl.grid(row=r, column=1, sticky="w")
            self.profile[key] = lbl

    # ---- refresh ----
    def refresh(self):
        courses = self.store.get("courses")
        att_records, res_records = self.store.get("attendanceRecords"), self.store.get("resultsRecords")

        mine = [c for c in courses if c["code"] == self.course]
        total, present, pct = self.overall_attendance(att_records)
        grade, count, avg_pct = self.average_grade(res_records)

        # overview
        self.ov["courses"].config(text=len(mine) or 1)
        self.ov["att"].config(text="%d%%" % pct)
        self.ov["grade"].config(text=grade)
        self.ov["assess"].config(text=count)
        if pct < 75:
            self.alert.pack(fill="x", pady=6, before=self.alert.master.winfo_children()[-1]) \
                if False else self.alert.pack(fill="x", pady=6)
        else:
            self.alert.pack_forget()

        # attendance summary
        self.att_cards["total"].config(text=total)
        self.att_cards["att"].config(text=present)
        self.att_cards["pct"].config(text="%d%%" % pct)
        self.load_course_wise_attendance(att_records, courses)
        values = [""] + ["%s - %s" % (c["code"], c["name"]) for c in courses]
        self.att_filter_combo.configure(values=["All Courses"] + values[1:])
        if not self.att_filter.get():
            self.att_filter.set("All Courses")
        self.filter_attendance_log()

        # results summary
        self.res_cards["total"].config(text=count)
        self.res_cards["pct"].config(text="%s%%" % ("%.2f" % avg_pct if count else 0))
        self.res_cards["grade"].config(text=grade)
        codes = []
        for r in res_records:
            if r["courseCode"] not in codes:
                codes.append(r["courseCode"])
        opts = ["%s - %s" % (c, next(x["name"] for x in courses if x["code"] == c))
                for c in codes if any(x["code"] == c for x in courses)]
        self.res_filter_combo.configure(values=opts)
        if not self.res_filter.get():
            fill_table(self.res_tree, [], "Please select a course")
        else:
            self.filter_course_results()

        self.load_my_courses(mine, att_records)

        # profile
        self.profile["name"].config(text=self.user["fullName"])
        self.profile["roll"].config(text=self.roll)
        self.profile["email"].config(text=self.student["email"] if self.student else "student@example.com")
        self.profile["course"].config(text=self.course)

    def load_course_wise_attendance(self, records, courses):
        agg = {}
        for r in records:
            s = next((s for s in r["students"] if s["rollNo"] == self.roll), None)
            if s:
                a = agg.setdefault(r["courseCode"], {"total": 0, "present": 0, "absent": 0})
                a["total"] += 1
                if s["status"] in ("present", "late"):
                    a["present"] += 1
                else:
                    a["absent"] += 1
        rows = []
        for code, a in agg.items():
            c = next((c for c in courses if c["code"] == code), None)
            pct = round(a["present"] / a["total"] * 100)
            rows.append((code, c["name"] if c else "Unknown", a["total"], a["present"], a["absent"],
                         "%d%%" % pct, "Good" if pct >= 75 else "Low"))
        fill_table(self.cw_tree, rows, "No attendance records found",
                   lambda row: "gA" if row[-1] == "Good" else "gF")

    def filter_attendance_log(self):
        sel = self.att_filter.get()
        code = "" if sel in ("", "All Courses") else sel.split(" - ")[0]
        records = self.store.get("attendanceRecords")
        courses = self.store.get("courses")
        rows = []
        for r in records:
            if code and r["courseCode"] != code:
                continue
            s = next((s for s in r["students"] if s["rollNo"] == self.roll), None)
            if s:
                c = next((c for c in courses if c["code"] == r["courseCode"]), None)
                rows.append((r["date"], "%s - %s" % (r["courseCode"], c["name"] if c else "Unknown"),
                             s["status"].capitalize()))
        rows.sort(key=lambda x: x[0], reverse=True)
        fill_table(self.log_tree, rows, "No records found")

    def filter_course_results(self):
        sel = self.res_filter.get()
        if not sel:
            fill_table(self.res_tree, [], "Please select a course")
            return
        code = sel.split(" - ")[0]
        rows = []
        for r in self.store.get("resultsRecords"):
            if r["courseCode"] != code or not r["approved"]:
                continue
            s = next((s for s in r["students"] if s["rollNo"] == self.roll), None)
            if s:
                rows.append((r["assessmentType"].capitalize(), r["totalMarks"], s["marks"],
                             "%s%%" % s["percentage"], s["grade"], r["timestamp"][:10]))
        fill_table(self.res_tree, rows, "No results found for this course",
                   lambda row: "g" + (row[4][0] if row[4][0] in "ABC" else "F"))

    def load_my_courses(self, mine, att_records):
        rows = []
        for c in mine:
            total = present = 0
            for r in att_records:
                if r["courseCode"] != c["code"]:
                    continue
                s = next((s for s in r["students"] if s["rollNo"] == self.roll), None)
                if s:
                    total += 1
                    if s["status"] in ("present", "late"):
                        present += 1
            rows.append((c["code"], c["name"], c["teacher"], "%d%%" % (round(present / total * 100) if total else 0)))
        fill_table(self.mc_tree, rows, "No courses enrolled")


# ----------------------------------------------------------------------------
# main.html + auth.js  ->  App (login screen + session handling)
# ----------------------------------------------------------------------------
class App:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Student Management System")
        self.root.geometry("1150x700")
        self.root.minsize(980, 620)
        self.root.configure(bg=BG)
        self.store = Storage()
        self.user = None
        self.view = None

        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("Treeview", rowheight=26, font=(FONT, 10), fieldbackground="white")
        style.configure("Treeview.Heading", font=(FONT, 10), background="#f2f2f2", relief="groove")
        style.map("Treeview", background=[("selected", TEAL_DARK)], foreground=[("selected", "white")])

        existing = self.store.data.get("currentUser")
        self.show_login()
        if existing and messagebox.askyesno(
                "Already logged in",
                "You are already logged in as %s. Go to dashboard?" % existing["fullName"]):
            self.user = existing
            self.open_dashboard()

    def clear_view(self):
        if self.view is not None:
            if isinstance(self.view, Dashboard):
                self.view.destroy()
            else:
                self.view.destroy()
            self.view = None

    # ---- login screen ----
    def show_login(self):
        self.clear_view()
        f = tk.Frame(self.root, bg=BG)
        f.pack(fill="both", expand=True)
        self.view = f

        head = tk.Frame(f, bg=TEAL, height=90)
        head.pack(fill="x")
        head.pack_propagate(False)
        tk.Label(head, text="Student Management System", bg=TEAL, fg="white",
                 font=(FONT, 26, "bold")).pack(expand=True)

        box = tk.LabelFrame(f, text="Student Portal Login", bg=BG, font=(FONT, 12), padx=40, pady=24)
        box.place(relx=0.5, rely=0.55, anchor="center")
        tk.Label(box, text="Attendance & Result Management System", bg=BG, fg="#444",
                 font=(FONT, 10)).grid(row=0, column=0, columnspan=2, pady=(0, 16))

        role, username, password = tk.StringVar(), tk.StringVar(), tk.StringVar()
        tk.Label(box, text="Select Role:", bg=BG, font=(FONT, 11)).grid(row=1, column=0, sticky="w", pady=8)
        ttk.Combobox(box, textvariable=role, values=["admin", "teacher", "student"], state="readonly",
                     width=28).grid(row=1, column=1, padx=10)
        tk.Label(box, text="Username:", bg=BG, font=(FONT, 11)).grid(row=2, column=0, sticky="w", pady=8)
        user_entry = tk.Entry(box, textvariable=username, width=31)
        user_entry.grid(row=2, column=1, padx=10)
        tk.Label(box, text="Password:", bg=BG, font=(FONT, 11)).grid(row=3, column=0, sticky="w", pady=8)
        tk.Entry(box, textvariable=password, show="*", width=31).grid(row=3, column=1, padx=10)

        def do_login(_e=None):
            self.login(role.get(), username.get().strip(), password.get(), password)

        make_button(box, "Login", do_login, width=20).grid(row=4, column=0, columnspan=2, pady=(18, 0))
        self.root.bind("<Return>", do_login)
        user_entry.focus_set()

    def login(self, role, username, password, password_var):
        if not role or not username or not password:
            messagebox.showwarning("Login", "Please fill in all fields!")
            return
        full_name = None
        u = USERS.get(role)
        if u and u["username"] == username and u["password"] == password:
            full_name = u["fullName"]
        else:  # users added by the admin (stored with their own password)
            for su in self.store.get("systemUsers"):
                if su.get("username") == username and su.get("password") == password and su["role"] == role:
                    full_name = su["name"]
        if not full_name:
            messagebox.showerror("Login", "Invalid credentials! Please check your username and password.")
            password_var.set("")
            return
        self.user = {"username": username, "role": role, "fullName": full_name,
                     "loginTime": datetime.now().isoformat()}
        self.store.set("currentUser", self.user)
        self.store.log_activity("User Login", full_name)
        self.open_dashboard()

    def open_dashboard(self):
        self.root.unbind("<Return>")
        self.clear_view()
        cls = {"admin": AdminDashboard, "teacher": TeacherDashboard, "student": StudentDashboard}[self.user["role"]]
        self.view = cls(self)

    def logout(self):
        if self.user:
            self.store.log_activity("User Logout", self.user["fullName"])
        self.store.data.pop("currentUser", None)
        self.store.save()
        self.user = None
        self.show_login()

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    App().run()