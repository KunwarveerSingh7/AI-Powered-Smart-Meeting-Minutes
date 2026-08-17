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

    if (Array.isArray(data.detail)) {

        employeeMessage.textContent =
            data.detail
                .map(function (error) {
                    return (
                        error.loc.join(" → ") +
                        ": " +
                        error.msg
                    );
                })
                .join(" | ");

    } else {

        employeeMessage.textContent =
            data.detail ||
            "Could not create employee.";
    }

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
const refreshMeetings =
    document.getElementById("refreshMeetings");

const meetingHistory =
    document.getElementById("meetingHistory");

    const showTeamAnalytics =
    document.getElementById("showTeamAnalytics");

const teamAnalyticsContainer =
    document.getElementById(
        "teamAnalyticsContainer"
    );


// This button just shows the employee creation form.
// this form would be hidden. only shown once clicked. to keep manager dashboard cleaner
showEmployeeForm.addEventListener("click", function () {

    if (employeeFormContainer.style.display === "none") {

        employeeFormContainer.style.display = "block";

        showEmployeeForm.textContent =
            "Hide Add Employee";

    } else {

        employeeFormContainer.style.display = "none";

        showEmployeeForm.textContent =
            "Add New Employee";
    }
});


// create a new employee account with this
employeeForm.addEventListener("submit", async function (event) {
    event.preventDefault();

    // Clear any old message before trying again.
    employeeMessage.textContent = "";

    // Get the values entered by the manager.
   const name =
    document.getElementById("employeeName").value;

const email =
    document.getElementById("employeeEmail").value;

const password =
    document.getElementById("employeePassword").value;

const position =
    document.getElementById("employeePosition").value;

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
            name: name,
            email: email,
            password: password,
            position: position
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

    const item =
        document.createElement("p");

    item.textContent =
        (employee.name || "No name") +
        " — " +
        (employee.position || "No position") +
        " — " +
        employee.email;

    employeeList.appendChild(item);
});

    } catch (error) {
        console.error("Employee list error:", error);

        employeeList.textContent =
            "Unable to load employees.";
    }
}

async function loadManagerAnalytics() {
    try {
        const response = await fetch(
            "/manager/analytics",
            {
                headers: {
                    "Authorization": "Bearer " + token
                }
            }
        );

        if (!response.ok) {
            console.error("Could not load analytics.");
            return;
        }

        const data = await response.json();

        document.getElementById("totalMeetings").textContent =
            data.meetings.total;

        document.getElementById("draftMeetings").textContent =
            data.meetings.draft;

        document.getElementById("publishedMeetings").textContent =
            data.meetings.published;

        document.getElementById("totalTasks").textContent =
            data.tasks.total;

        document.getElementById("pendingTasks").textContent =
            data.tasks.pending;

        document.getElementById("inProgressTasks").textContent =
            data.tasks.in_progress;

        document.getElementById("completedTasks").textContent =
            data.tasks.completed;

        document.getElementById("overdueTasks").textContent =
            data.tasks.overdue;

        document.getElementById("completionPercentage").textContent =
            data.completion_percentage + "%";

    } catch (error) {
        console.error("Analytics loading error:", error);
    }
}


async function loadTeamAnalytics() {

    try {

        const response = await fetch(
            "/manager/analytics/team",
            {
                headers: {
                    "Authorization":
                        "Bearer " + token
                }
            }
        );

        if (!response.ok) {
            console.error(
                "Could not load team analytics."
            );
            return;
        }

        const data =
            await response.json();

        const teamAnalytics =
            document.getElementById(
                "teamAnalytics"
            );

        const priorityBreakdown =
            document.getElementById(
                "priorityBreakdown"
            );

        const topEmployee =
            document.getElementById(
                "topEmployee"
            );


        teamAnalytics.innerHTML = "";

        data.employees.forEach(
            function (employee) {

                const employeeBox =
                    document.createElement("div");

                employeeBox.innerHTML =
                    "<h3>" +
                    employee.email +
                    "</h3>" +

                    "<p>Total Tasks: " +
                    employee.total_tasks +
                    "</p>" +

                    "<p>Pending: " +
                    employee.pending_tasks +
                    "</p>" +

                    "<p>In Progress: " +
                    employee.in_progress_tasks +
                    "</p>" +

                    "<p>Completed: " +
                    employee.completed_tasks +
                    "</p>" +

                    "<p>Overdue: " +
                    employee.overdue_tasks +
                    "</p>" +

                    "<p>Completion: " +
                    employee.completion_percentage +
                    "%</p><hr>";

                teamAnalytics.appendChild(
                    employeeBox
                );
            }
        );


        priorityBreakdown.innerHTML =
            "<p>High: " +
            data.priority_breakdown.high +
            "</p>" +

            "<p>Medium: " +
            data.priority_breakdown.medium +
            "</p>" +

            "<p>Low: " +
            data.priority_breakdown.low +
            "</p>";


        if (data.top_employee) {

            topEmployee.innerHTML =
                "<p>" +
                data.top_employee.email +
                "</p>" +

                "<p>Completed Tasks: " +
                data.top_employee.completed_tasks +
                "</p>";

        } else {

            topEmployee.textContent =
                "No employee data available.";
        }

    } catch (error) {

        console.error(
            "Team analytics error:",
            error
        );
    }
}


async function loadManagerMeetings() {

    try {
        const response = await fetch(
            "/manager/meetings",
            {
                headers: {
                    "Authorization":
                        "Bearer " + token
                }
            }
        );

        if (!response.ok) {
            meetingHistory.textContent =
                "Could not load meetings.";
            return;
        }

        const meetings =
            await response.json();

        meetingHistory.innerHTML = "";

        if (meetings.length === 0) {
            meetingHistory.textContent =
                "No meetings available.";
            return;
        }

        meetings.forEach(function (meeting) {

            const meetingBox =
                document.createElement("div");

            const title =
                document.createElement("h3");

            title.textContent =
                meeting.title +
                " (Meeting ID: " +
                meeting.id +
                ")";

            const status =
                document.createElement("p");

            status.textContent =
                "Status: " +
                meeting.status;

            const file =
                document.createElement("p");

            file.textContent =
                "File: " +
                meeting.original_filename;

            const published =
                document.createElement("p");

            published.textContent =
                "Published: " +
                (
                    meeting.published_at
                        ? new Date(
                            meeting.published_at
                        ).toLocaleString()
                        : "Not published"
                );

            const detailsButton =
                document.createElement("button");

            detailsButton.textContent =
                "View Details";

            const reviewButton =
                document.createElement("button");

            reviewButton.textContent =
                "Open Review";

            const detailsBox =
                document.createElement("div");

            detailsBox.style.display =
                "none";

            detailsButton.onclick =
                function () {

                    if (
                        detailsBox.style.display ===
                        "none"
                    ) {
                        detailsBox.style.display =
                            "block";

                        detailsButton.textContent =
                            "Hide Details";

                    } else {
                        detailsBox.style.display =
                            "none";

                        detailsButton.textContent =
                            "View Details";
                    }
                };

            reviewButton.onclick =
                function () {

                    window.location.href =
                        "/meeting-review/" +
                        meeting.id;
                };


            // Extracted meeting text
            const extractedTitle =
                document.createElement("h4");

            extractedTitle.textContent =
                "Extracted Meeting Text";

            const extractedText =
                document.createElement("pre");

            extractedText.textContent =
                meeting.raw_text ||
                "No extracted text available.";


            // AI summary
            const summaryTitle =
                document.createElement("h4");

            summaryTitle.textContent =
                "Meeting Summary";

            const summaryText =
                document.createElement("p");

            summaryText.textContent =
                meeting.ai_summary ||
                "No summary available.";


            // Decisions
            const decisionsTitle =
                document.createElement("h4");

            decisionsTitle.textContent =
                "Decisions";

            const decisionsContainer =
                document.createElement("div");

            if (
                meeting.decisions &&
                meeting.decisions.length > 0
            ) {
                meeting.decisions.forEach(
                    function (decision) {

                        const decisionItem =
                            document.createElement("p");

                        decisionItem.textContent =
                            "• " +
                            decision.decision_text;

                        decisionsContainer.appendChild(
                            decisionItem
                        );
                    }
                );

            } else {
                decisionsContainer.textContent =
                    "No decisions available.";
            }


            detailsBox.appendChild(
                extractedTitle
            );

            detailsBox.appendChild(
                extractedText
            );

            detailsBox.appendChild(
                summaryTitle
            );

            detailsBox.appendChild(
                summaryText
            );

            detailsBox.appendChild(
                decisionsTitle
            );

            detailsBox.appendChild(
                decisionsContainer
            );


            meetingBox.appendChild(title);
            meetingBox.appendChild(status);
            meetingBox.appendChild(file);
            meetingBox.appendChild(published);

            meetingBox.appendChild(
                detailsButton
            );

            meetingBox.appendChild(
                reviewButton
            );

            meetingBox.appendChild(
                detailsBox
            );

            meetingBox.appendChild(
                document.createElement("hr")
            );

            meetingHistory.appendChild(
                meetingBox
            );
        });

    } catch (error) {

        console.error(
            "Meeting history error:",
            error
        );

        meetingHistory.textContent =
            "Unable to load meetings.";
    }
}


// Lets the manager manually refresh the employee list.
refreshEmployees.addEventListener("click", function () {

    const employeeListContainer =
        document.getElementById(
            "employeeListContainer"
        );

    if (
        employeeListContainer.style.display ===
        "none"
    ) {

        employeeListContainer.style.display =
            "block";

        refreshEmployees.textContent =
            "Hide Employee List";

        loadEmployees();

    } else {

        employeeListContainer.style.display =
            "none";

        refreshEmployees.textContent =
            "Employee List";
    }
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
showMeetingForm.addEventListener(
    "click",
    function () {

        if (
            meetingFormContainer.style.display ===
            "none"
        ) {

            meetingFormContainer.style.display =
                "block";

            showMeetingForm.textContent =
                "Hide Upload Form";

        } else {

            meetingFormContainer.style.display =
                "none";

            showMeetingForm.textContent =
                "Upload Meeting Minutes";
        }
    }
);

refreshMeetings.addEventListener(
    "click",
    loadManagerMeetings
);

showTeamAnalytics.addEventListener(
    "click",
    function () {

        if (
            teamAnalyticsContainer.style.display ===
            "none"
        ) {

            teamAnalyticsContainer.style.display =
                "block";

            showTeamAnalytics.textContent =
                "Hide Team Analytics";

            loadTeamAnalytics();

        } else {

            teamAnalyticsContainer.style.display =
                "none";

            showTeamAnalytics.textContent =
                "Show Team Analytics";
        }
    }
);

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


        // Meeting upload worked.
// Tell the manager that AI analysis is now starting.
meetingUploadMessage.textContent =
    "Meeting uploaded. AI analysis is running...";


// Automatically analyse the newly uploaded meeting.
const analyseResponse = await fetch(
    "/meetings/" +
    data.meeting_id +
    "/analyse",
    {
        method: "POST",

        headers: {
            "Authorization":
                "Bearer " + token
        }
    }
);


// Read the AI analysis response.
const analyseData =
    await analyseResponse.json();


// The file was uploaded successfully,
// but something went wrong during AI analysis.
if (!analyseResponse.ok) {

    meetingUploadMessage.textContent =
        analyseData.detail ||
        "Meeting uploaded, but AI analysis failed.";

    return;
}


// Upload, text extraction and AI analysis
// have all completed successfully.
meetingUploadMessage.textContent =
    "Meeting analysed successfully. Opening review...";


// Clear the upload form.
meetingUploadForm.reset();


// Open the meeting review page.
// The AI summary, decisions and generated tasks
// should already be available there.
window.location.href =
    "/meeting-review/" +
    data.meeting_id;


} catch (error) {

    console.error(
        "Meeting upload/analysis error:",
        error
    );

    meetingUploadMessage.textContent =
        "Unable to upload or analyse meeting.";
}

});


// Automatically load manager meeting history
// when the manager dashboard opens.
loadManagerMeetings();
loadManagerAnalytics();
loadTeamAnalytics();