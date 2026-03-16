from flask import Flask, request, render_template_string, redirect, url_for

app = Flask(__name__)

# Sample in-memory data
students = [
    {"id": 1, "name": "Juan", "grade": 85, "section": "Stallman"},
    {"id": 2, "name": "Maria", "grade": 90, "section": "Stallman"},
    {"id": 3, "name": "Pedro", "grade": 70, "section": "Zion"}
]

PASSING_GRADE = 75  # threshold for pass/fail

@app.route('/')
def home():
    return redirect(url_for('list_students'))

# Show all students with analytics and unified table
@app.route('/students')
def list_students():
    total_students = len(students)
    total_passed = sum(1 for s in students if s["grade"] >= PASSING_GRADE)
    total_failed = total_students - total_passed

    percent_passed = (total_passed / total_students * 100) if total_students else 0
    percent_failed = (total_failed / total_students * 100) if total_students else 0

    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Student Dashboard</title>
        <link rel="stylesheet"
              href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
    </head>
    <body class="container mt-4">
        <h2 class="mb-4">📚 Student Dashboard</h2>

        <!-- Analytics Summary -->
        <div class="row mb-4">
            <div class="col-md-4">
                <div class="card text-bg-primary mb-3">
                    <div class="card-body text-center">
                        <h5 class="card-title">Total Students</h5>
                        <p class="display-6">{{total_students}}</p>
                    </div>
                </div>
            </div>
            <div class="col-md-4">
                <div class="card text-bg-success mb-3">
                    <div class="card-body text-center">
                        <h5 class="card-title">Passed</h5>
                        <p class="display-6">{{total_passed}}</p>
                        <small>{{percent_passed|round(1)}}%</small>
                    </div>
                </div>
            </div>
            <div class="col-md-4">
                <div class="card text-bg-danger mb-3">
                    <div class="card-body text-center">
                        <h5 class="card-title">Failed</h5>
                        <p class="display-6">{{total_failed}}</p>
                        <small>{{percent_failed|round(1)}}%</small>
                    </div>
                </div>
            </div>
        </div>

        <!-- Unified Student Table -->
        <table class="table table-striped table-hover">
            <thead class="table-dark">
                <tr>
                    <th>ID</th><th>Name</th><th>Grade & Remark</th><th>Section</th><th>Actions</th>
                </tr>
            </thead>
            <tbody>
            {% for s in students %}
                {% if s.grade >= PASSING_GRADE %}
                    <tr class="table-success">
                        <td>{{s.id}}</td>
                        <td>{{s.name}}</td>
                        <td><span class="badge bg-success">{{s.grade}} (Passed)</span></td>
                        <td><span class="badge bg-info">{{s.section}}</span></td>
                        <td>
                            <a href="/edit_student/{{s.id}}" class="btn btn-sm btn-primary">✏️ Edit</a>
                            <form action="/delete_student/{{s.id}}" method="POST" style="display:inline;">
                                <button type="submit" class="btn btn-sm btn-danger">🗑️ Delete</button>
                            </form>
                        </td>
                    </tr>
                {% else %}
                    <tr class="table-danger">
                        <td>{{s.id}}</td>
                        <td>{{s.name}}</td>
                        <td><span class="badge bg-danger">{{s.grade}} (Failed)</span></td>
                        <td><span class="badge bg-info">{{s.section}}</span></td>
                        <td>
                            <a href="/edit_student/{{s.id}}" class="btn btn-sm btn-primary">✏️ Edit</a>
                            <form action="/delete_student/{{s.id}}" method="POST" style="display:inline;">
                                <button type="submit" class="btn btn-sm btn-danger">🗑️ Delete</button>
                            </form>
                        </td>
                    </tr>
                {% endif %}
            {% endfor %}
            </tbody>
        </table>

        <a href="/add_student_form" class="btn btn-success mt-3">➕ Add New Student</a>
    </body>
    </html>
    """
    return render_template_string(
        html,
        students=students,
        total_students=total_students,
        total_passed=total_passed,
        total_failed=total_failed,
        percent_passed=percent_passed,
        percent_failed=percent_failed,
        PASSING_GRADE=PASSING_GRADE
    )

# Add student form
@app.route('/add_student_form')
def add_student_form():
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Add Student</title>
        <link rel="stylesheet"
              href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
    </head>
    <body class="container mt-4">
        <h2>Add New Student</h2>
        <form action="/add_student" method="POST" class="mt-3">
            <div class="mb-3">
                <label class="form-label">Name</label>
                <input type="text" name="name" class="form-control" autofocus>
            </div>
            <div class="mb-3">
                <label class="form-label">Grade</label>
                <input type="number" name="grade" class="form-control">
            </div>
            <div class="mb-3">
                <label class="form-label">Section</label>
                <input type="text" name="section" class="form-control">
            </div>
            <button type="submit" class="btn btn-success">Add Student</button>
            <a href="/students" class="btn btn-secondary">Back</a>
        </form>
    </body>
    </html>
    """
    return render_template_string(html)

# Add student (POST)
@app.route('/add_student', methods=['POST'])
def add_student():
    name = request.form.get("name")
    grade = int(request.form.get("grade"))
    section = request.form.get("section")
    new_id = max([s["id"] for s in students], default=0) + 1
    new_student = {"id": new_id, "name": name, "grade": grade, "section": section}
    students.append(new_student)
    return redirect(url_for('list_students'))

# Edit student
@app.route('/edit_student/<int:id>', methods=['GET', 'POST'])
def edit_student(id):
    student = next((s for s in students if s["id"] == id), None)
    if not student:
        return "Student not found", 404
    if request.method == 'POST':
        student["name"] = request.form["name"]
        student["grade"] = int(request.form["grade"])
        student["section"] = request.form["section"]
        return redirect(url_for('list_students'))
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Edit Student</title>
        <link rel="stylesheet"
              href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
    </head>
    <body class="container mt-4">
        <h2>Edit Student</h2>
        <form method="POST" class="mt-3">
            <div class="mb-3">
                <label class="form-label">Name</label>
                <input type="text" name="name" value="{{student.name}}" class="form-control">
            </div>
            <div class="mb-3">
                <label class="form-label">Grade</label>
                <input type="number" name="grade" value="{{student.grade}}" class="form-control">
            </div>
            <div class="mb-3">
                <label class="form-label">Section</label>
                <input type="text" name="section" value="{{student.section}}" class="form-control">
            </div>
            <button type="submit" class="btn btn-primary">Update</button>
            <a href="/students" class="btn btn-secondary">Back</a>
        </form>
    </body>
    </html>
    """
    return render_template_string(html, student=student)

# Delete student
@app.route('/delete_student/<int:id>', methods=['POST'])
def delete_student(id):
    global students
    students = [s for s in students if s["id"] != id]
    return redirect(url_for('list_students'))

if __name__ == '__main__':
    app.run(debug=True)

