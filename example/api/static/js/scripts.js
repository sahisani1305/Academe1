document.addEventListener('DOMContentLoaded', function() {
    const teacherIdInput = document.querySelector('input[name="teacher_id"]');
    
    if (teacherIdInput) {
        teacherIdInput.addEventListener('focus', function() {
            alert("Your request for teacher ID will be sent to admin for approval.");
        });
    }
});

function resetForm() {
    document.getElementById('signup-form').reset();
}

function showSection(section) {
    var sections = ['upload-section', 'notes-section', 'lectures-section', 'assignments-section', 'requests-section', 'activity-section', 'deleted-section', 'teachers-section', 'students-section', 'filter_students-section', 'student-assignments-section'];

    sections.forEach(function(id) {
        var element = document.getElementById(id);
        if (element) {
            element.style.display = 'none';
        }
    });

    var selectedSection = document.getElementById(section + '-section');
    if (!selectedSection && section === 'student_assignments') {
        selectedSection = document.getElementById('student-assignments-section');
    }

    if (selectedSection) {
        selectedSection.style.display = 'block';
    }
}

function updateSemesters(section) {
    const year = document.getElementById(section + '-year').value; // Get the year from the correct section
    const semesterSelect = document.getElementById(section + '-semester'); // Get the semester select for the correct section
    semesterSelect.innerHTML = '<option value="">Select Semester</option>'; // Clear previous options

    if (year === '1') {
        semesterSelect.innerHTML += '<option value="1">Semester 1</option>';
        semesterSelect.innerHTML += '<option value="2">Semester 2</option>';
    } else if (year === '2') {
        semesterSelect.innerHTML += '<option value="3">Semester 3</option>';
        semesterSelect.innerHTML += '<option value="4">Semester 4</option>';
    } else if (year === '3') {
        semesterSelect.innerHTML += '<option value="5">Semester 5</option>';
        semesterSelect.innerHTML += '<option value="6">Semester 6</option>';
    } else if (year === '4') {
        semesterSelect.innerHTML += '<option value="7">Semester 7</option>';
        semesterSelect.innerHTML += '<option value="8">Semester 8</option>';
    }
}

function toggleStudentFields() {
    var isTeacherChecked = document.getElementById('is_teacher').checked;
    var isStudentChecked = document.getElementById('is_student').checked;
    var studentFields = document.getElementById('student-fields');
    
    if (isStudentChecked) {
        studentFields.style.display = 'block';
        document.querySelectorAll('#student-fields input, #student-fields select').forEach(function(input) {
            input.required = true;
        });
        document.getElementById('is_teacher').checked = false;
    } else {
        studentFields.style.display = 'none';
        document.querySelectorAll('#student-fields input, #student-fields select').forEach(function(input) {
            input.required = false;
        });
    }

    if (isTeacherChecked) {
        document.getElementById('is_student').checked = false;
    }
}
