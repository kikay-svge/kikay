@app.route('/students')
def list_students():
    passed = [s for s in students if s["grade"] >= PASSING_GRADE]
    failed = [s for s in students if s["grade"] < PASSING_GRADE]

    total_students = len(students)
    total_passed = len(passed)
    total_failed = len(failed)

    # Avoid division by zero
    percent_passed = (total_passed / total_students * 100) if total_students else 0
    percent_failed = (total_failed / total_students * 100) if total_students else 0

    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Student List</title>
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

        <h3 class="text-success">✅ Passed Students</h3>
        <table class="table table-striped table-hover">
            <thead class="table-success">
                <tr>
                    <th>ID</th><th>Name</th><th>Grade</th><th>Section</th><th>Actions</th>
                </tr>
            </thead>
            <tbody>
            {% for s in passed %}
                <tr>
                    <td>{{s.id}}</td>
                    <td>{{s.name}}</td>
                    <td><span class="badge bg-success">{{s.grade}}</span></td>
                    <td><span class="badge bg-info">{{s.section}}</span></td>
                    <td><a href="/edit_student/{{s.id}}" class="btn btn-sm btn-primary">✏️ Edit</a></td>
                </tr>
            {% endfor %}
            </tbody>
        </table>

        <h3 class="text-danger mt-5">❌ Failed Students</h3>
        <table class="table table-striped table-hover">
            <thead class="table-danger">
                <tr>
                    <th>ID</th><th>Name</th><th>Grade</th><th>Section</th><th>Actions</th>
                </tr>
            </thead>
            <tbody>
            {% for s in failed %}
                <tr>
                    <td>{{s.id}}</td>
                    <td>{{s.name}}</td>
                    <td><span class="badge bg-danger">{{s.grade}}</span></td>
                    <td><span class="badge bg-info">{{s.section}}</span></td>
                    <td><a href="/edit_student/{{s.id}}" class="btn btn-sm btn-primary">✏️ Edit</a></td>
                </tr>
            {% endfor %}
            </tbody>
        </table>

        <a href="/add_student_form" class="btn btn-success mt-3">➕ Add New Student</a>
    </body>
    </html>
    """
    return render_template_string(
        html,
        passed=passed,
        failed=failed,
        total_students=total_students,
        total_passed=total_passed,
        total_failed=total_failed,
        percent_passed=percent_passed,
        percent_failed=percent_failed
    )
