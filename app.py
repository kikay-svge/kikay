import os
import io
import csv
from flask import Flask, request, render_template_string, redirect, url_for, Response
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# --- Database Configuration ---
# Ensure these environment variables are set in your terminal/environment before running
app.config['SQLALCHEMY_DATABASE_URI'] = (
    f"postgresql://{os.environ.get('DB_USER')}:{os.environ.get('DB_PASSWORD')}"
    f"@{os.environ.get('DB_HOST')}:{os.environ.get('DB_PORT')}/{os.environ.get('DB_NAME')}"
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- Database Model ---
class Student(db.Model):
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    grade = db.Column(db.Integer, nullable=False)
    section = db.Column(db.String(100), nullable=False)

# Create the tables in the database if they don't exist yet
with app.app_context():
    db.create_all()

# --- Helper Logic ---
PASSING_GRADE = 75

def get_letter_grade(grade):
    if grade >= 90: return "A"
    elif grade >= 80: return "B"
    elif grade >= 75: return "C"
    else: return "F"

# --- Routes ---

@app.route('/')
def home():
    return redirect(url_for('list_students'))

@app.route('/students')
def list_students():
    # Query all students from the database
    students = Student.query.all()
    total_students = len(students)
    
    # Basic Analytics (Updated to use object attributes: s.grade instead of s["grade"])
    total_passed = sum(1 for s in students if s.grade >= PASSING_GRADE)
    total_failed = total_students - total_passed
    percent_passed = (total_passed / total_students * 100) if total_students else 0
    
    # Advanced Analytics
    avg_grade = sum(s.grade for s in students) / total_students if total_students else 0
    highest_grade = max((s.grade for s in students), default=0)
    lowest_grade = min((s.grade for s in students), default=0)
    
    # Grade Distribution for Chart
    grade_dist = {"A": 0, "B": 0, "C": 0, "F": 0}
    for s in students:
        grade_dist[get_letter_grade(s.grade)] += 1
    
    # Section Analytics
    section_grades = {}
    for s in students:
        section_grades.setdefault(s.section, []).append(s.grade)
    
    section_stats = []
    best_section = "N/A"
    if section_grades:
        for sec, grades in section_grades.items():
            section_stats.append({
                "name": sec,
                "avg": sum(grades) / len(grades),
                "highest": max(grades),
                "lowest": min(grades),
                "count": len(grades)
            })
        section_stats.sort(key=lambda x: x["avg"], reverse=True)
        best_section = section_stats[0]["name"]

    # HTML Template (Unchanged)
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Student Dashboard Pro</title>
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
            th.sortable:hover { cursor: pointer; background-color: #f8f9fa; }
        </style>
    </head>
    <body class="container mt-4 bg-light">
        <div class="d-flex justify-content-between align-items-center mb-4">
            <h2>📚 Student Dashboard Pro</h2>
            <div>
                <a href="/export_csv" class="btn btn-outline-secondary shadow-sm me-2">📥 Export CSV</a>
                <a href="/add_student_form" class="btn btn-success shadow-sm">➕ Add New Student</a>
            </div>
        </div>

        <div class="row mb-4">
            <div class="col-md-3">
                <div class="card text-bg-primary shadow-sm h-100 text-center">
                    <div class="card-body d-flex flex-column justify-content-center">
                        <h6 class="card-title text-uppercase opacity-75">Total Students</h6>
                        <h2 class="display-6 mb-0">{{total_students}}</h2>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card text-bg-info text-white shadow-sm h-100 text-center">
                    <div class="card-body d-flex flex-column justify-content-center">
                        <h6 class="card-title text-uppercase opacity-75">Class Average</h6>
                        <h2 class="display-6 mb-0">{{avg_grade|round(1)}}</h2>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card text-bg-warning text-white shadow-sm h-100 text-center">
                    <div class="card-body d-flex flex-column justify-content-center">
                        <h6 class="card-title text-uppercase opacity-75">Highest & Lowest</h6>
                        <h3 class="mb-0">▲ {{highest_grade}} | ▼ {{lowest_grade}}</h3>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card text-bg-dark shadow-sm h-100 text-center">
                    <div class="card-body d-flex flex-column justify-content-center">
                        <h6 class="card-title text-uppercase opacity-75">Top Section</h6>
                        <h3 class="mb-0 text-truncate" title="{{best_section}}">🏆 {{best_section}}</h3>
                    </div>
                </div>
            </div>
        </div>

        <div class="row mb-4">
            <div class="col-md-4">
                <div class="card shadow-sm h-100">
                    <div class="card-body">
                        <h6 class="text-muted mb-3 text-center">Grade Distribution</h6>
                        <canvas id="gradeChart"></canvas>
                    </div>
                </div>
            </div>

            <div class="col-md-8">
                <div class="card shadow-sm h-100">
                    <div class="card-body">
                        <h6 class="text-muted mb-3">Section Performance Breakdown</h6>
                        <div class="table-responsive">
                            <table class="table table-sm table-bordered text-center align-middle">
                                <thead class="table-light">
                                    <tr>
                                        <th>Section</th>
                                        <th>Students</th>
                                        <th>Average</th>
                                        <th>Highest</th>
                                        <th>Lowest</th>
                                    </tr>
                                </thead>
                                <tbody>
                                {% for stat in section_stats %}
                                    <tr>
                                        <td class="fw-bold">{{stat.name}}</td>
                                        <td>{{stat.count}}</td>
                                        <td class="{{ 'text-success fw-bold' if loop.first else '' }}">{{stat.avg|round(1)}}</td>
                                        <td>{{stat.highest}}</td>
                                        <td>{{stat.lowest}}</td>
                                    </tr>
                                {% else %}
                                    <tr><td colspan="5" class="text-muted">No data available</td></tr>
                                {% endfor %}
                                </tbody>
                            </table>
                        </div>
                        
                        <h6 class="text-muted mt-4 mb-2">Class Pass Rate Overview</h6>
                        <div class="progress" style="height: 25px;">
                            <div class="progress-bar bg-success" style="width: {{percent_passed}}%">
                                {{percent_passed|round(1)}}% Passed
                            </div>
                            <div class="progress-bar bg-danger" style="width: {{100 - percent_passed}}%">
                                {{(100 - percent_passed)|round(1)}}% Failed
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div class="card shadow-sm mb-5">
            <div class="card-header bg-white d-flex justify-content-between align-items-center py-3">
                <h5 class="mb-0">Student Roster</h5>
                <input type="text" id="searchInput" class="form-control w-25" placeholder="🔍 Search...">
            </div>
            <div class="table-responsive">
                <table class="table table-hover mb-0 align-middle" id="rosterTable">
                    <thead class="table-light">
                        <tr>
                            <th>ID</th>
                            <th class="sortable" onclick="sortTable(1)">Name ↕️</th>
                            <th class="sortable" onclick="sortTable(2)">Grade ↕️</th>
                            <th>Letter</th>
                            <th class="sortable" onclick="sortTable(4)">Section ↕️</th>
                            <th class="text-end pe-4">Actions</th>
                        </tr>
                    </thead>
                    <tbody id="studentTable">
                    {% for s in students %}
                        <tr>
                            <td class="text-muted fw-bold">#{{s.id}}</td>
                            <td class="fw-semibold">{{s.name}}</td>
                            <td>
                                <span class="badge rounded-pill {{ 'bg-success' if s.grade >= PASSING_GRADE else 'bg-danger' }} px-3 py-2">
                                    {{s.grade}}
                                </span>
                            </td>
                            <td><span class="badge bg-secondary">{{ get_letter_grade(s.grade) }}</span></td>
                            <td><span class="badge border border-info text-info bg-light">{{s.section}}</span></td>
                            <td class="text-end pe-3">
                                <a href="/edit_student/{{s.id}}" class="btn btn-sm btn-outline-primary">Edit</a>
                                <form action="/delete_student/{{s.id}}" method="POST" class="d-inline" onsubmit="return confirm('Delete {{s.name}}?')">
                                    <button type="submit" class="btn btn-sm btn-outline-danger">Delete</button>
                                </form>
                            </td>
                        </tr>
                    {% else %}
                        <tr>
                            <td colspan="6" class="text-center py-4 text-muted">No students found. Add one above!</td>
                        </tr>
                    {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>

        <script>
            document.getElementById('searchInput').addEventListener('keyup', function() {
                let filter = this.value.toLowerCase();
                let rows = document.querySelectorAll('#studentTable tr');
                rows.forEach(row => {
                    let text = row.innerText.toLowerCase();
                    row.style.display = text.includes(filter) ? '' : 'none';
                });
            });

            function sortTable(n) {
                var table, rows, switching, i, x, y, shouldSwitch, dir, switchcount = 0;
                table = document.getElementById("rosterTable");
                switching = true;
                dir = "asc"; 
                while (switching) {
                    switching = false;
                    rows = table.rows;
                    for (i = 1; i < (rows.length - 1); i++) {
                        shouldSwitch = false;
                        x = rows[i].getElementsByTagName("TD")[n];
                        y = rows[i + 1].getElementsByTagName("TD")[n];
                        
                        let valX = n === 2 ? parseInt(x.innerText) : x.innerHTML.toLowerCase();
                        let valY = n === 2 ? parseInt(y.innerText) : y.innerHTML.toLowerCase();

                        if (dir == "asc") {
                            if (valX > valY) { shouldSwitch = true; break; }
                        } else if (dir == "desc") {
                            if (valX < valY) { shouldSwitch = true; break; }
                        }
                    }
                    if (shouldSwitch) {
                        rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
                        switching = true;
                        switchcount ++;
                    } else {
                        if (switchcount == 0 && dir == "asc") {
                            dir = "desc";
                            switching = true;
                        }
                    }
                }
            }

            const ctx = document.getElementById('gradeChart').getContext('2d');
            new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: ['A (90-100)', 'B (80-89)', 'C (75-79)', 'F (<75)'],
                    datasets: [{
                        data: [{{grade_dist['A']}}, {{grade_dist['B']}}, {{grade_dist['C']}}, {{grade_dist['F']}}],
                        backgroundColor: ['#198754', '#0dcaf0', '#ffc107', '#dc3545'],
                        borderWidth: 0
                    }]
                },
                options: {
                    responsive: true,
                    plugins: { legend: { position: 'bottom' } }
                }
            });
        </script>
    </body>
    </html>
    """
    return render_template_string(html, students=students, total_students=total_students, 
                                 percent_passed=percent_passed, avg_grade=avg_grade,
                                 highest_grade=highest_grade, lowest_grade=lowest_grade,
                                 best_section=best_section, PASSING_GRADE=PASSING_GRADE,
                                 get_letter_grade=get_letter_grade, grade_dist=grade_dist,
                                 section_stats=section_stats)

@app.route('/export_csv')
def export_csv():
    students = Student.query.all()
    si = io.StringIO()
    cw = csv.writer(si)
    cw.writerow(['ID', 'Name', 'Grade', 'Letter Grade', 'Section'])
    
    # Updated to object attribute access
    for s in students:
        cw.writerow([s.id, s.name, s.grade, get_letter_grade(s.grade), s.section])
    
    output = si.getvalue()
    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-disposition": "attachment; filename=student_roster.csv"}
    )

@app.route('/add_student_form')
def add_student_form():
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Add Student - Dashboard Pro</title>
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
    </head>
    <body class="container mt-5 bg-light">
        <div class="row justify-content-center">
            <div class="col-md-6">
                <div class="card shadow-sm">
                    <div class="card-header bg-white py-3">
                        <h5 class="mb-0">➕ Add New Student</h5>
                    </div>
                    <div class="card-body">
                        <form action="/add_student" method="POST">
                            <div class="mb-3">
                                <label class="form-label fw-bold">Name</label>
                                <input type="text" name="name" class="form-control" required>
                            </div>
                            <div class="mb-3">
                                <label class="form-label fw-bold">Grade (0-100)</label>
                                <input type="number" name="grade" class="form-control" min="0" max="100" required>
                            </div>
                            <div class="mb-4">
                                <label class="form-label fw-bold">Section</label>
                                <input type="text" name="section" class="form-control" required>
                            </div>
                            <div class="d-flex justify-content-between">
                                <a href="/students" class="btn btn-outline-secondary">Cancel</a>
                                <button type="submit" class="btn btn-success px-4">Add Student</button>
                            </div>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    return render_template_string(html)

@app.route('/add_student', methods=['POST'])
def add_student():
    # Capture form data
    name = request.form.get('name')
    grade = int(request.form.get('grade', 0))
    section = request.form.get('section')
    
    # Create new database record
    new_student = Student(name=name, grade=grade, section=section)
    db.session.add(new_student)
    db.session.commit()
    
    return redirect(url_for('list_students'))

@app.route('/edit_student/<int:id>', methods=['GET', 'POST'])
def edit_student(id):
    # Fetch student or throw 404 if not found
    student = Student.query.get_or_404(id)

    if request.method == 'POST':
        # Update record in database
        student.name = request.form.get('name')
        student.grade = int(request.form.get('grade', 0))
        student.section = request.form.get('section')
        db.session.commit()
        
        return redirect(url_for('list_students'))

    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Edit Student - Dashboard Pro</title>
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
    </head>
    <body class="container mt-5 bg-light">
        <div class="row justify-content-center">
            <div class="col-md-6">
                <div class="card shadow-sm">
                    <div class="card-header bg-white py-3">
                        <h5 class="mb-0">✏️ Edit Student: {{ student.name }}</h5>
                    </div>
                    <div class="card-body">
                        <form method="POST">
                            <div class="mb-3">
                                <label class="form-label fw-bold">Name</label>
                                <input type="text" name="name" class="form-control" value="{{ student.name }}" required>
                            </div>
                            <div class="mb-3">
                                <label class="form-label fw-bold">Grade (0-100)</label>
                                <input type="number" name="grade" class="form-control" value="{{ student.grade }}" min="0" max="100" required>
                            </div>
                            <div class="mb-4">
                                <label class="form-label fw-bold">Section</label>
                                <input type="text" name="section" class="form-control" value="{{ student.section }}" required>
                            </div>
                            <div class="d-flex justify-content-between">
                                <a href="/students" class="btn btn-outline-secondary">Cancel</a>
                                <button type="submit" class="btn btn-primary px-4">Save Changes</button>
                            </div>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    return render_template_string(html, student=student)

@app.route('/delete_student/<int:id>', methods=['POST'])
def delete_student(id):
    student = Student.query.get_or_404(id)
    db.session.delete(student)
    db.session.commit()
    
    return redirect(url_for('list_students'))

if __name__ == '__main__':
    app.run(debug=True)
