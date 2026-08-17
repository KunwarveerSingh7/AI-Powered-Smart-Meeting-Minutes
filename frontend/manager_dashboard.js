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

            renderManagerCharts(data);

    } catch (error) {
        console.error("Analytics loading error:", error);
    }
}


function renderManagerCharts(data) {

    const chartArea =
        document.getElementById(
            "managerChartArea"
        );

    chartArea.innerHTML = "";


    // -----------------------------------------
    // TASK STATUS DONUT
    // -----------------------------------------

    const taskChartCard =
        document.createElement("div");

    taskChartCard.className =
        "chart-card";


    const taskChartTitle =
        document.createElement("h3");

    taskChartTitle.textContent =
        "Task Status Overview";


    const totalTasks =
        data.tasks.total || 0;

    const pending =
        data.tasks.pending || 0;

    const inProgress =
        data.tasks.in_progress || 0;

    const completed =
        data.tasks.completed || 0;

    const cancelled =
        data.tasks.cancelled || 0;


    const donut =
        document.createElement("div");

    donut.className =
        "task-donut";


    if (totalTasks > 0) {

        const pendingPercent =
            (
                pending /
                totalTasks
            ) * 100;

        const progressPercent =
            (
                inProgress /
                totalTasks
            ) * 100;

        const completedPercent =
            (
                completed /
                totalTasks
            ) * 100;


        const pendingEnd =
            pendingPercent;

        const progressEnd =
            pendingEnd +
            progressPercent;

        const completedEnd =
            progressEnd +
            completedPercent;


        donut.style.background =
            `conic-gradient(
                #f59e0b 0% ${pendingEnd}%,
                #3b82f6 ${pendingEnd}% ${progressEnd}%,
                #10b981 ${progressEnd}% ${completedEnd}%,
                #94a3b8 ${completedEnd}% 100%
            )`;

    } else {

        donut.style.background =
            "#e2e8f0";
    }


    const donutCentre =
        document.createElement("div");

    donutCentre.className =
        "donut-centre";


    const totalNumber =
        document.createElement("strong");

    totalNumber.textContent =
        totalTasks;


    const totalLabel =
        document.createElement("span");

    totalLabel.textContent =
        "Tasks";


    donutCentre.appendChild(
        totalNumber
    );

    donutCentre.appendChild(
        totalLabel
    );

    donut.appendChild(
        donutCentre
    );


    // Legend

    const legend =
        document.createElement("div");

    legend.className =
        "chart-legend";


    legend.innerHTML = `
        <div>
            <span class="legend-dot pending-dot"></span>
            Pending: ${pending}
        </div>

        <div>
            <span class="legend-dot progress-dot"></span>
            In Progress: ${inProgress}
        </div>

        <div>
            <span class="legend-dot completed-dot"></span>
            Completed: ${completed}
        </div>

        <div>
            <span class="legend-dot cancelled-dot"></span>
            Cancelled: ${cancelled}
        </div>
    `;


    taskChartCard.appendChild(
        taskChartTitle
    );

    taskChartCard.appendChild(
        donut
    );

    taskChartCard.appendChild(
        legend
    );



    // -----------------------------------------
    // MEETING STATUS CHART
    // -----------------------------------------

    const meetingChartCard =
        document.createElement("div");

    meetingChartCard.className =
        "chart-card";


    const meetingTitle =
        document.createElement("h3");

    meetingTitle.textContent =
        "Meeting Status";


    const totalMeetings =
        data.meetings.total || 0;

    const published =
        data.meetings.published || 0;

    const draft =
        data.meetings.draft || 0;


    let publishedPercent = 0;
    let draftPercent = 0;


    if (totalMeetings > 0) {

        publishedPercent =
            (
                published /
                totalMeetings
            ) * 100;

        draftPercent =
            (
                draft /
                totalMeetings
            ) * 100;
    }


    const meetingBars =
        document.createElement("div");

    meetingBars.className =
        "meeting-bars";


    meetingBars.innerHTML = `

        <div class="bar-item">

            <div class="bar-heading">

                <span>Published</span>

                <strong>
                    ${published}
                </strong>

            </div>

            <div class="bar-background">

                <div
                    class="bar-fill published-bar"
                    style="width: ${publishedPercent}%"
                ></div>

            </div>

        </div>


        <div class="bar-item">

            <div class="bar-heading">

                <span>Draft</span>

                <strong>
                    ${draft}
                </strong>

            </div>

            <div class="bar-background">

                <div
                    class="bar-fill draft-bar"
                    style="width: ${draftPercent}%"
                ></div>

            </div>

        </div>
    `;


    meetingChartCard.appendChild(
        meetingTitle
    );

    meetingChartCard.appendChild(
        meetingBars
    );


    chartArea.appendChild(
        taskChartCard
    );

    chartArea.appendChild(
        meetingChartCard
    );
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

        data.employees.forEach(function (employee) {

        const card =
        document.createElement("div");

        card.className =
        "employee-flip-card";


        const inner =
        document.createElement("div");

        inner.className =
        "employee-flip-inner";


        const front =
        document.createElement("div");

        front.className =
        "employee-card-face employee-card-front";


        const back =
        document.createElement("div");

        back.className =
        "employee-card-face employee-card-back";


        // FRONT SIDE
        front.innerHTML = `
        <h3>
            ${employee.name || "Employee"}
        </h3>

        <p>
            <strong>Position:</strong>
            ${employee.position || "Not specified"}
        </p>

        <p>
            <strong>Email:</strong>
            ${employee.email}
        </p>

        <p class="flip-hint">
            Click to view analytics
        </p>
        `;


        // BACK SIDE
        back.innerHTML = `
        <h3>
            Employee Analytics
        </h3>

        <p>
            Total Tasks:
            <strong>${employee.total_tasks}</strong>
        </p>

        <p>
            Pending:
            <strong>${employee.pending_tasks}</strong>
        </p>

        <p>
            In Progress:
            <strong>${employee.in_progress_tasks}</strong>
        </p>

        <p>
            Completed:
            <strong>${employee.completed_tasks}</strong>
        </p>

        <p>
            Overdue:
            <strong>${employee.overdue_tasks}</strong>
        </p>

        <p>
            Completion:
            <strong>
                ${employee.completion_percentage}%
            </strong>
        </p>

        <p class="flip-hint">
            Click to go back
        </p>
        `;


        inner.appendChild(front);
        inner.appendChild(back);

        card.appendChild(inner);


        card.addEventListener(
        "click",
        function () {

            card.classList.toggle(
                "flipped"
            );
        }
        );


        teamAnalytics.appendChild(card);
        });

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

            renderPriorityChart(
            data.priority_breakdown
            );


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

function renderPriorityChart(priorityData) {

    const chart =
        document.getElementById(
            "priorityChart"
        );

    const high =
        priorityData.high || 0;

    const medium =
        priorityData.medium || 0;

    const low =
        priorityData.low || 0;

    const total =
        high + medium + low;


    chart.innerHTML = "";


    if (total === 0) {

        chart.textContent =
            "No priority data available.";

        return;
    }


    const highPercent =
        (high / total) * 100;

    const mediumPercent =
        (medium / total) * 100;

    const lowPercent =
        (low / total) * 100;


    const highEnd =
        highPercent;

    const mediumEnd =
        highEnd +
        mediumPercent;


    const donut =
        document.createElement("div");

    donut.className =
        "priority-donut";


    donut.style.background =
        `conic-gradient(
            #ef4444 0% ${highEnd}%,
            #f59e0b ${highEnd}% ${mediumEnd}%,
            #10b981 ${mediumEnd}% 100%
        )`;


    const centre =
        document.createElement("div");

    centre.className =
        "priority-donut-centre";

    centre.innerHTML = `
        <strong>${total}</strong>
        <span>Tasks</span>
    `;


    donut.appendChild(
        centre
    );


    chart.appendChild(
        donut
    );
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

    const meetingCard =
        document.createElement("div");

    meetingCard.className =
        "meeting-card";


    const title =
        document.createElement("h3");

    title.textContent =
        meeting.title;


    const meetingId =
        document.createElement("p");

    meetingId.className =
        "meeting-id";

    meetingId.textContent =
        "Meeting ID: " + meeting.id;


    const buttonRow =
        document.createElement("div");

    buttonRow.className =
        "meeting-card-actions";


    // INFO BUTTON
    const infoButton =
        document.createElement("button");

    infoButton.textContent =
        "Info";

    infoButton.className =
        "secondary-action";


    // VIEW DETAILS BUTTON
    const detailsButton =
        document.createElement("button");

    detailsButton.textContent =
        "View Details";

    detailsButton.className =
        "secondary-action";


    // OPEN REVIEW BUTTON
    const reviewButton =
        document.createElement("button");

    reviewButton.textContent =
        "Open Review";

    reviewButton.className =
        "primary-action";


    // -------------------------------------------------
    // INFO MODAL
    // -------------------------------------------------

    infoButton.onclick = function () {

        openMeetingModal(
            "Meeting Information",
            `
                <p><strong>Title:</strong> ${meeting.title}</p>

                <p>
                    <strong>Meeting ID:</strong>
                    ${meeting.id}
                </p>

                <p>
                    <strong>Date:</strong>
                    ${
                        meeting.meeting_date
                            ? new Date(
                                meeting.meeting_date
                            ).toLocaleDateString()
                            : "Not provided"
                    }
                </p>

                <p>
                    <strong>Status:</strong>
                    ${meeting.status}
                </p>

                <p>
                    <strong>Published:</strong>
                    ${
                        meeting.published_at
                            ? new Date(
                                meeting.published_at
                            ).toLocaleString()
                            : "Not published"
                    }
                </p>

                <p>
                    <strong>File:</strong>
                    ${meeting.original_filename}
                </p>
            `
        );
    };


    // -------------------------------------------------
    // DETAILS MODAL
    // -------------------------------------------------

    detailsButton.onclick = function () {

        let decisionsHtml =
            "<p>No decisions available.</p>";

        if (
            meeting.decisions &&
            meeting.decisions.length > 0
        ) {

            decisionsHtml =
                meeting.decisions
                    .map(function (decision) {
                        return (
                            "<p>• " +
                            decision.decision_text +
                            "</p>"
                        );
                    })
                    .join("");
        }


        openMeetingModal(
            "Meeting Details",
            `
                <h4>Extracted Meeting Text</h4>

                <pre class="modal-notes">
${meeting.raw_text || "No extracted text available."}
                </pre>


                <h4>AI Summary</h4>

                <p>
                    ${
                        meeting.ai_summary ||
                        "No summary available."
                    }
                </p>


                <h4>Decisions</h4>

                ${decisionsHtml}
            `
        );
    };


    // -------------------------------------------------
    // OPEN REVIEW
    // -------------------------------------------------

    reviewButton.onclick = function () {

        window.location.href =
            "/meeting-review/" +
            meeting.id;
    };


    buttonRow.appendChild(
        infoButton
    );

    buttonRow.appendChild(
        detailsButton
    );

    buttonRow.appendChild(
        reviewButton
    );


    meetingCard.appendChild(
        title
    );

    meetingCard.appendChild(
        meetingId
    );

    meetingCard.appendChild(
        buttonRow
    );


    meetingHistory.appendChild(
        meetingCard
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

function openMeetingModal(
    title,
    content
) {

    const overlay =
        document.createElement("div");

    overlay.className =
        "meeting-modal-overlay";


    const modal =
        document.createElement("div");

    modal.className =
        "meeting-modal";


    const heading =
        document.createElement("h2");

    heading.textContent =
        title;


    const contentBox =
        document.createElement("div");

    contentBox.className =
        "meeting-modal-content";

    contentBox.innerHTML =
        content;


    const closeButton =
        document.createElement("button");

    closeButton.textContent =
        "Close";

    closeButton.className =
        "primary-action";


    closeButton.onclick =
        function () {

            document.body.removeChild(
                overlay
            );
        };


    overlay.onclick =
        function (event) {

            if (event.target === overlay) {

                document.body.removeChild(
                    overlay
                );
            }
        };


    modal.appendChild(
        heading
    );

    modal.appendChild(
        contentBox
    );

    modal.appendChild(
        closeButton
    );


    overlay.appendChild(
        modal
    );


    document.body.appendChild(
        overlay
    );
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