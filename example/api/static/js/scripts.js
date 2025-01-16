document.addEventListener('DOMContentLoaded', function() {
    const teacherIdInput = document.querySelector('input[name="teacher_id"]');
    
    if (teacherIdInput) {
        teacherIdInput.addEventListener('focus', function() {
            alert("Your request for teacher ID will be sent to admin for approval.");
        });
    }

    loadCurrentSection();
});

function resetForm() {
    document.getElementById('signup-form').reset();
}

function showSection(sectionId) {
    const sections = document.querySelectorAll('.section, .section-content');
    sections.forEach(section => {
        section.style.display = 'none';
    });
    document.getElementById(`${sectionId}-section`).style.display = 'block';
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

function toggleFollowUpForm(postId) {
    const followUpSection = document.getElementById(`followup-section-${postId}`);
    if (followUpSection.style.display === "none") {
        followUpSection.style.display = "block";
    } else {
        followUpSection.style.display = "none";
    }
}

function saveCurrentSection(sectionId) {
    localStorage.setItem('currentSection', sectionId);
}

function loadCurrentSection() {
    const currentSection = localStorage.getItem('currentSection');
    if (currentSection) {
        showSection(currentSection);
    } else {
        showSection('notes'); // Default section
    }
}
