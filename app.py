from flask import Flask, request, render_template_string, redirect, url_for

app = Flask(__name__)

# Sample in-memory data
students = [
    {"id": 1, "name": "Juan", "grade": 85, "section": "Stallman"},
    {"id": 2, "name": "Maria", "grade": 90, "section": "Stallman"},
    {"id": 3, "name": "Pedro", "grade": 70, "section": "Zion"},
    {"id": 4, "name": "Elena", "grade": 95, "section": "Zion"}
]

PASSING_GRADE = 75  

@app.route('/')
def home():
    return redirect(url_for('list_students'))

@app.route('/students')
def list_students():
    # --- Data Calculations ---
    total_students = len(students)
    if total_students == 0:
        return "No students found. <a href='/add_student_form'>Add one</a>"

    passed_list = [s for s in students if s["grade"] >= PASSING_GRADE]
    total_passed = len(passed_list)
    avg_grade = sum(s["grade"] for s in students) / total_students
    top_scorer = max(students, key=lambda x: x['grade'])

    # --- Section Analytics (Interesting Feature 1) ---
    sections = {}
    for s in students:
        sec = s["section"]
        if sec not in sections:
            sections[sec] = {"count": 0, "total": 0}
        sections[sec]["count"] += 1
        sections[sec]["total"] += s["grade"]
    
    for sec in sections:
        sections[sec]["avg"] = sections[sec]["total"] / sections[sec]["count"]

    # --- Data for JavaScript Chart (Interesting Feature 2) ---
    chart_labels = [s["name"] for s in students]
    chart_values = [s["grade"] for s in students]

    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Student Insights Pro</title>
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
            .card { border: none; border-radius: 12px; transition: transform 0.2s; }
            .card:hover { transform: translateY(-5px); }
            .metric-val { font-weight: bold; font-size: 1.8rem; }
        </style>
    </head>
    <body class="bg-light">
        <div class="container py-4">
            <div class="d-flex justify-content-between align-items-center mb-4">
                <h2>🎓 Academic Dashboard</h2>
                <a href="/add_student_form" class="btn btn-primary shadow-sm">+ New Student</a>
            </div>

            <div class="row g-3 mb-4">
                <div class="col-md-3">
                    <div class="card shadow-sm text-center p-3">
                        <small class="text-muted">Class Average</small>
                        <div class="metric-val text-primary">{{avg_grade|round(1)}}</div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card shadow-sm text-center p-3">
                        <small class="text-muted">Pass Rate</small>
                        <div class="metric-val text-success">{{((total_passed/total_students)*100)|round(0)}}%</div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card shadow-sm text-center p-3">
                        <small class="text-muted">Top Performer</small>
                        <div class="metric-val text-info" style="font-size: 1.2rem; padding-top: 10px;">{{top_scorer.name}}</div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card shadow-sm text-center p-3 text-white bg-dark">
                        <small class="text-light opacity-75">Enrollment</small>
                        <div class="metric-val">{{total_students}}</div>
                    </div>
                </div>
            </div>

            <div class="row">
                <div class="col-lg-6 mb-4">
                    <div class="card shadow-sm p-4">
                        <h5 class="mb-3">Grade Distribution</h5>
                        <canvas id="gradeChart" height="200"></canvas>
                    </div>
                    
                    <div class="card shadow-sm mt-4 p-4">
                        <h5 class="mb-3">Section Averages</h5>
                        <table class="table table-sm mb-0">
                            <thead><tr><th>Section</th><th>Students</th><th>Avg Grade</th></tr></thead>
                            <tbody>
                                {% for sec, data in sections.items() %}
                                <tr>
                                    <td>{{sec}}</td>
                                    <td>{{data.count}}</td>
                                    <td><span class="badge bg-secondary">{{data.avg|round(1)}}</span></td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                </div>

                <div class="col-lg-6">
                    <div class="card shadow-sm p-4">
                        <h5 class="mb-3">Student Roster</h5>
                        <div class="table-responsive">
                            <table class="table align-middle">
                                <thead class="table-light">
                                    <tr><th>Name</th><th>Grade Progress</th><th class="text-end">Actions</th></tr>
                                </thead>
                                <tbody>
                                {% for s in students %}
                                    <tr>
                                        <td><strong>{{s.name}}</strong><br><small class="text-muted">{{s.section}}</small></td>
                                        <td style="min-width: 150px;">
                                            <div class="progress" style="height: 10px;">
                                                <div class="progress-bar {{ 'bg-success' if s.grade >= PASSING_GRADE else 'bg-danger' }}" 
                                                     style="width: {{s.grade}}%"></div>
                                            </div>
                                            <small>{{s.grade}}%</small>
                                        </td>
                                        <td class="text-end">
                                            <a href="/edit_student/{{s.id}}" class="btn btn-sm btn-outline-secondary border-0">✏️</a>
                                            <form action="/delete_student/{{s.id}}" method="POST" style="display:inline;">
                                                <button class="btn btn-sm btn-outline-danger border-0">🗑️</button>
                                            </form>
                                        </td>
                                    </tr>
                                {% endfor %}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <script>
            new Chart(document.getElementById('gradeChart'), {
                type: 'bar',
                data: {
                    labels: {{ chart_labels|safe }},
                    datasets: [{
                        label: 'Grade',
                        data: {{ chart_values|safe }},
                        backgroundColor: '#0d6efd88',
                        borderColor: '#0d6efd',
                        borderWidth: 1,
                        borderRadius: 5
                    }]
                },
                options: { scales: { y: { beginAtZero: true, max: 100 } } }
            });
        </script>
    </body>
    </html>
    """
    return render_template_string(
        html, students=students, total_students=total_students,
        total_passed=total_passed, avg_grade=avg_grade, 
        top_scorer=top_scorer, sections=sections,
        chart_labels=chart_labels, chart_values=chart_values,
        PASSING_GRADE=PASSING_GRADE
    )

# --- Standard Form Routes (Keeping your original logic) ---

@app.route('/add_student_form')
def add_student_form():
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Add Student</title>
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
    </head>
    <body class="container mt-5">
        <div class="col-md-6 offset-md-3">
            <div class="card shadow p-4">
                <h2>Add New Student</h2>
                <form action="/add_student" method="POST" class="mt-3">
                    <div class="mb-3"><label class="form-label">Name</label><input type="text" name="name" class="form-control" required></div>
                    <div class="mb-3"><label class="form-label">Grade</label><input type="number" name="grade" class="form-control" required></div>
                    <div class="mb-3"><label class="form-label">Section</label><input type="text" name="section" class="form-control" required></div>
                    <button type="submit" class="btn btn-success w-100">Add Student</button>
                    <a href="/students" class="btn btn-link w-100 mt-2">Cancel</a>
                </form>
            </div>
        </div>
    </body>
    </html>
    """
    return render_template_string(html)

@app.route('/add_student', methods=['POST'])
def add_student():
    name = request.form.get("name")
    grade = int(request.form.get("grade"))
    section = request.form.get("section")
    new_id = max([s["id"] for s in students], default=0) + 1
    students.append({"id": new_id, "name": name, "grade": grade, "section": section})
    return redirect(url_for('list_students'))

@app.route('/edit_student/<int:id>', methods=['GET', 'POST'])
def edit_student(id):
    student = next((s for s in students if s["id"] == id), None)
    if not student: return "Not found", 404
    if request.method == 'POST':
        student.update({"name": request.form["name"], "grade": int(request.form["grade"]), "section": request.form["section"]})
        return redirect(url_for('list_students'))
    
    html = """
    <body class="container mt-5">
        <form method="POST" class="card p-4 col-md-6 offset-md-3 shadow">
            <h2>Edit Student</h2>
            <input type="text" name="name" value="{{student.name}}" class="form-control mb-2">
            <input type="number" name="grade" value="{{student.grade}}" class="form-control mb-2">
            <input type="text" name="section" value="{{student.section}}" class="form-control mb-2">
            <button type="submit" class="btn btn-primary">Update</button>
        </form>
    </body>
    """
    return render_template_string(html, student=student)

@app.route('/delete_student/<int:id>', methods=['POST'])
def delete_student(id):
    global students
    students = [s for s in students if s["id"] != id]
    return redirect(url_for('list_students'))

if __name__ == '__main__':
    app.run(debug=True)
