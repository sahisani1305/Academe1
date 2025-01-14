// scripts.js
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
    document.getElementById('notes-section').style.display = 'none';
    document.getElementById('lectures-section').style.display = 'none';
    document.getElementById('assignments-section').style.display = 'none';

    document.getElementById(section + '-section').style.display = 'block';
}
function showSection(section) {
    document.getElementById('requests-section').style.display = 'none';
    document.getElementById('activity-section').style.display = 'none';
    document.getElementById('deleted-section').style.display = 'none';
    document.getElementById('teachers-section').style.display = 'none';
    document.getElementById('students-section').style.display = 'none';

    document.getElementById(section + '-section').style.display = 'block';
}
function updateSemesters() {
    const year = document.getElementById('year').value;
    const semesterSelect = document.getElementById('semester');
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