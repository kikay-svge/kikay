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
    total_students = len(students)
    if total_students == 0:
        return "No students found. <a href='/add_student_form'>Add one</a>"

    # Basic Counts
    passed_list = [s for s in students if s["grade"] >= PASSING_GRADE]
    total_passed = len(passed_list)
    total_failed = total_students - total_passed
    
    # Percentages and Averages
    percent_passed = (total_passed / total_students * 100)
    avg_grade = sum(s["grade"] for s in students) / total_students

    # Performance Tiers
    top_performers = sum(1 for s in students if s["grade"] >= 90)
    needs_help = total_failed

    # Section-based Analytics
    sections = {}
    for s in students:
        sec = s["section"]
        if sec not in sections:
            sections[sec] = {"count": 0, "total_grade": 0}
        sections[sec]["count"] += 1
        sections[sec]["total_grade"] += s["grade"]
    
    for sec in sections:
        sections[sec]["avg"] = sections[sec]["total_grade"] / sections[sec]["count"]

    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Student Dashboard Pro</title>
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
    </head>
    <body class="container mt-4">
        <div class="d-flex justify-content-between align-items-center mb-4">
            <h2>📊 Student Analytics Dashboard</h2>
            <a href="/add_student_form" class="btn btn-success">➕ Add New Student</a>
        </div>

        <div class="row mb-4">
            <div class="col-md-3">
                <div class="card text-white bg-primary h-100">
                    <div class="card-body text-center">
                        <h6>Total Students</h6>
                        <h2 class="display-6">{{total_students}}</h2>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card text-white bg-info h-100">
                    <div class="card-body text-center">
                        <h6>Class Average</h6>
                        <h2 class="display-6">{{avg_grade|round(1)}}</h2>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card text-white bg-success h-100">
                    <div class="card-body text-center">
                        <h6>Passing Rate</h6>
                        <h2 class="display-6">{{percent_passed|round(1)}}%</h2>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card text-white bg-warning h-100">
                    <div class="card-body text-center">
                        <h6>Top Performers (90+)</h6>
                        <h2 class="display-6">{{top_performers}}</h2>
                    </div>
                </div>
            </div>
        </div>

        <div class="row">
            <div class="col-md-5">
                <h4>Section Performance</h4>
                <table class="table table-bordered table-sm mt-3">
                    <thead class="table-light">
                        <tr>
                            <th>Section</th>
                            <th>Students</th>
                            <th>Avg Grade</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for sec_name, data in sections.items() %}
                        <tr>
                            <td>{{sec_name}}</td>
                            <td>{{data.count}}</td>
                            <td><strong>{{data.avg|round(1)}}</strong></td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>

            <div class="col-md-7">
                <h4>Student List</h4>
                <table class="table table-hover mt-3">
                    <thead class="table-dark">
                        <tr>
                            <th>Name</th><th>Grade</th><th>Section</th><th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                    {% for s in students %}
                        <tr class="{{ 'table-success' if s.grade >= PASSING_GRADE else 'table-danger' }}">
                            <td>{{s.name}}</td>
                            <td>{{s.grade}}</td>
                            <td>{{s.section}}</td>
                            <td>
                                <a href="/edit_student/{{s.id}}" class="btn btn-sm btn-outline-dark">✏️</a>
                                <form action="/delete_student/{{s.id}}" method="POST" style="display:inline;">
                                    <button type="submit" class="btn btn-sm btn-outline-danger">🗑️</button>
                                </form>
                            </td>
                        </tr>
                    {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
    </body>
    </html>
    """
    return render_template_string(
        html, 
        students=students, 
        total_students=total_students,
        total_passed=total_passed,
        percent_passed=percent_passed,
        avg_grade=avg_grade,
        top_performers=top_performers,
        sections=sections,
        PASSING_GRADE=PASSING_GRADE
    )
