// hhttps://github.com/fastapi/full-stack-fastapi-template
// source for the idea of this code


const token = localStorage.getItem("access_token");

async function checkManager() {
    if (!token) {
        window.location.href = "/login-page";
        return;
    }

    try {
        const response = await fetch("/me", {
            headers: {
                "Authorization": "Bearer " + token
            }
        });

        if (!response.ok) {
            localStorage.removeItem("access_token");
            window.location.href = "/login-page";
            return;
        }

        const user = await response.json();

        if (user.role !== "manager") {
            window.location.href = "/employee-dashboard";
            return;
        }

        document.getElementById("welcome_message").textContent =
            "Logged in as: " + user.email;

    } catch (error) {
        localStorage.removeItem("access_token");
        window.location.href = "/login-page";
    }
}

function logout() {
    localStorage.removeItem("access_token");
    window.location.href = "/login-page";
}

checkManager();

// this would grab all the lements needed from the manager dahboard
// ids have been matched with manager_dashboard.html
const showEmployeeForm = document.getElementById("showEmployeeForm");
const employeeFormContainer = document.getElementById("employeeFormContainer");
const employeeForm = document.getElementById("employeeForm");
const employeeMessage = document.getElementById("employeeMessage");
const employeeList = document.getElementById("employeeList");
const refreshEmployees = document.getElementById("refreshEmployees");


// This button just shows the employee creation form.
// this form would be hidden. only shown once clicked. to keep manager dashboard cleaner
showEmployeeForm.addEventListener("click", function () {
    employeeFormContainer.style.display = "block";
});


// create a new employee account with this
employeeForm.addEventListener("submit", async function (event) {
    event.preventDefault();

    // Clear any old message before trying again.
    employeeMessage.textContent = "";

    // Get the values entered by the manager.
    const email = document.getElementById("employeeEmail").value;
    const password = document.getElementById("employeePassword").value;

    try {
        // new employee details sent to backend
        // The manager's token is included so the backend can confirm
        // that this request came only from the manager
        const response = await fetch("/employees", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": "Bearer " + token
            },
            body: JSON.stringify({
                email: email,
                password: password
            })
        });

        const data = await response.json();

        // If something went wrong, like an existing email
        // display the backend error message
        if (!response.ok) {
            employeeMessage.textContent =
                data.detail || "Could not create employee.";
            return;
        }

        // Iwhen employee created manager informed with this message
        employeeMessage.textContent =
            "Employee account created successfully.";

        // reset so that manager is able to add another person to the employee list
        employeeForm.reset();

        // reload so new employee account pops up after adding.
        loadEmployees();

    } catch (error) {
        console.error("Employee creation error:", error);

        employeeMessage.textContent =
            "Unable to connect to the server.";
    }
});


// used to load all employee accounts from the backend
// they will be displayed on manager dashboard
async function loadEmployees() {
    try {
        const response = await fetch("/employees", {
            headers: {
                "Authorization": "Bearer " + token
            }
        });

        // message for if the request is failed
        if (!response.ok) {
            employeeList.textContent =
                "Could not load employees.";
            return;
        }

        const employees = await response.json();

        // Iwhen employee accounts are nil
        // show message instead of leaving blank
        if (employees.length === 0) {
            employeeList.textContent =
                "No employee accounts created yet.";
            return;
        }

        // old list removed before updates
        employeeList.innerHTML = "";

        // Create one paragraph for each employee.
        // This is simple for now and can be replaced by a proper table later.
        employees.forEach(function (employee) {
            const item = document.createElement("p");

            item.textContent =
                employee.email + " - " + employee.role;

            employeeList.appendChild(item);
        });

    } catch (error) {
        console.error("Employee list error:", error);

        employeeList.textContent =
            "Unable to load employees.";
    }
}


// Lets the manager manually refresh the employee list.
refreshEmployees.addEventListener("click", function () {
    loadEmployees();
});


// Load employees automatically when the dashboard opens.
loadEmployees();

// meeting upload section
// this section is for the manager to upload meeting minutes
// the uploaded meeting minutes will be stored in the backend
// elements taken from manager_dashboard.html to be used in this section
// check ids match with manager_dashboard.html
const showMeetingForm = document.getElementById("showMeetingForm");
const meetingFormContainer = document.getElementById("meetingFormContainer");
const meetingUploadForm = document.getElementById("meetingUploadForm");
const meetingUploadMessage = document.getElementById("meetingUploadMessage");


// upload form is hidden. only shown on click of upload button.
// When manager clicks the upload button, the form becomes visible.
showMeetingForm.addEventListener("click", function () {
    meetingFormContainer.style.display = "block";
});


// Runs when manager submits the meeting minutes form
meetingUploadForm.addEventListener("submit", async function (event) {

    // Stops the browser from refreshing the whole page after submitting
    event.preventDefault();

    // Clear any message from the previous upload attempt
    meetingUploadMessage.textContent = "";

    // Get meeting information entered by manager
    const title =
        document.getElementById("meetingTitle").value;

    const meetingDate =
        document.getElementById("meetingDate").value;

    // Get the uploaded meeting minutes file
    const fileInput =
        document.getElementById("meetingFile");

    const file = fileInput.files[0];


    // Do not continue if manager hasn't selected a file
    if (!file) {
        meetingUploadMessage.textContent =
            "Please select a meeting file.";
        return;
    }


    // FormData is used because we are sending both
    // normal meeting information and an actual file to the backend
    const formData = new FormData();

    formData.append("title", title);
    formData.append("meeting_date", meetingDate);
    formData.append("file", file);


    try {

        // Send the meeting minutes to the backend upload route
        const response = await fetch("/meetings/upload", {
            method: "POST",

            headers: {
                // Manager token is sent so backend can check
                // that the person uploading is actually a manager
                "Authorization": "Bearer " + token
            },

            body: formData
        });


        // Read whatever response comes back from FastAPI
        const data = await response.json();


        // Show backend error if upload was rejected
        if (!response.ok) {
            meetingUploadMessage.textContent =
                data.detail || "Meeting upload failed.";
            return;
        }


        // Let manager know that upload worked
        meetingUploadMessage.textContent =
            "Meeting uploaded successfully.";

        // Clear the form after successful upload
        meetingUploadForm.reset();


        // Backend gives us the ID of the new meeting.
        // Use it to open the review page for that specific meeting.
        window.location.href =
            "/meeting-review/" + data.meeting_id;


    } catch (error) {

        // This normally happens if frontend cannot reach the backend
        // or another unexpected connection problem happens.
        console.error("Meeting upload error:", error);

        meetingUploadMessage.textContent =
            "Unable to upload meeting.";
    }

});
