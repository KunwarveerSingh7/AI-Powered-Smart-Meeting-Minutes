const token = localStorage.getItem("access_token");



async function checkEmployee() {
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

        if (user.role !== "employee") {
            window.location.href = "/manager-dashboard";
            return;
        }

        // Employee profile details
        document.getElementById(
            "employeeProfileName"
        ).textContent =
        user.name || "Not specified";

        document.getElementById(
            "employeeProfilePosition"
        ).textContent =
        user.position || "Employee";

        document.getElementById(
            "employeeProfileEmail"
        ).textContent =
        user.email;


        // Keep this old element available
        // because some existing code may still use it.
        document.getElementById(
            "welcome_message"
        ).textContent =
        "Welcome " +
        (user.name || user.email);

    } catch (error) {
        localStorage.removeItem("access_token");
        window.location.href = "/login-page";
    }
}

function logout() {
    localStorage.removeItem("access_token");
    window.location.href = "/login-page";
}



const taskList =
    document.getElementById("taskList");

const refreshTasks =
    document.getElementById("refreshTasks");

const showTaskHistory =
    document.getElementById("showTaskHistory");

const taskHistoryList =
    document.getElementById("taskHistoryList");

    const showMeetingSummary =
    document.getElementById("showMeetingSummary");

const meetingSummaryBox =
    document.getElementById("meetingSummaryBox");

const showDecisions =
    document.getElementById("showDecisions");

const decisionsBox =
    document.getElementById("decisionsBox");
    
const showMeetingNotes =
    document.getElementById("showMeetingNotes");

const meetingNotesBox =
    document.getElementById("meetingNotesBox");

const employeeMeetingList = document.getElementById("employeeMeetingList");


async function loadTasks() {

    try {
        const response = await fetch(
            "/tasks",
            {
                headers: {
                    "Authorization":
                        "Bearer " + token
                }
            }
        );

        if (!response.ok) {
            taskList.textContent =
                "Could not load tasks.";
            return;
        }

        const tasks =
            await response.json();

        taskList.innerHTML = "";
        let currentColumn = null;

        if (tasks.length === 0) {
            taskList.textContent =
                "No tasks assigned to you.";
            return;
        }

        tasks.forEach(function (task) {

            const taskIndex =
            tasks.indexOf(task);

        if (taskIndex % 3 === 0) {

            currentColumn =
                document.createElement("div");

            currentColumn.className =
                "employee-task-column";

            taskList.appendChild(
                currentColumn
            );
        }

            const taskBox =
                document.createElement("div");

            taskBox.className =
                "employee-task";

            const title =
                document.createElement("h3");

            title.textContent =
                task.title;

            const description =
                document.createElement("p");

            description.textContent =
            "Description: " +
            (task.description || "No description");


            const meeting =
            document.createElement("p");

            meeting.textContent =
            "Meeting ID: " + task.meeting_id;


            const priority =
                document.createElement("p");

            priority.textContent =
                "Priority: " +
                task.priority;

            const status =
                document.createElement("p");

            status.textContent =
                "Status: " +
                task.status;

            const deadline =
                document.createElement("p");

            deadline.textContent =
                "Deadline: " +
                (
                    task.due_date
                        ? new Date(
                            task.due_date
                        ).toLocaleDateString()
                        : "No deadline"
                );


            // Employee task status control
const statusLabel =
    document.createElement("p");

statusLabel.textContent =
    "Update Status:";

const statusSelect =
    document.createElement("select");

[
    "pending",
    "in_progress",
    "completed"
].forEach(function (statusValue) {

    const option =
        document.createElement("option");

    option.value = statusValue;

    if (statusValue === "pending") {
        option.textContent = "Pending";
    }

    if (statusValue === "in_progress") {
        option.textContent = "In Progress";
    }

    if (statusValue === "completed") {
        option.textContent = "Completed";
    }

    if (task.status === statusValue) {
        option.selected = true;
    }

    statusSelect.appendChild(option);});
// Progress percentage
const progressLabel =
    document.createElement("p");

progressLabel.textContent =
    "Progress Percentage:";

const progressInput =
    document.createElement("input");

progressInput.type = "number";
progressInput.min = "0";
progressInput.max = "100";
progressInput.value = "0";


// Progress comment
const commentLabel =
    document.createElement("p");

commentLabel.textContent =
    "Progress Comment:";

const commentInput =
    document.createElement("textarea");

commentInput.rows = 3;
commentInput.placeholder =
    "Add a progress update...";


// Save progress button
const saveProgressButton =
    document.createElement("button");

saveProgressButton.textContent =
    "Save Progress";

const progressMessage =
    document.createElement("p");

    // Task history button
const historyButton =
    document.createElement("button");

historyButton.textContent =
    "View History";

const historyContainer =
    document.createElement("div");

historyButton.onclick =
    async function () {

        await loadTaskHistory(
            task.id,
            historyContainer
        );
    };

saveProgressButton.onclick =
    async function () {

        await updateTaskProgress(
            task.id,
            statusSelect.value,
            Number(progressInput.value),
            commentInput.value,
            progressMessage
        );
    };    

            taskBox.appendChild(title);
taskBox.appendChild(description);
taskBox.appendChild(meeting);
taskBox.appendChild(priority);
taskBox.appendChild(status);
taskBox.appendChild(deadline);

// Stage 5.4 controls
taskBox.appendChild(statusLabel);
taskBox.appendChild(statusSelect);

taskBox.appendChild(progressLabel);
taskBox.appendChild(progressInput);

taskBox.appendChild(commentLabel);
taskBox.appendChild(commentInput);

taskBox.appendChild(saveProgressButton);
taskBox.appendChild(progressMessage);

taskBox.appendChild(historyButton);
taskBox.appendChild(historyContainer);

currentColumn.appendChild(
    taskBox
);
        });

    } catch (error) {

        console.error(
            "Task loading error:",
            error
        );

        taskList.textContent =
            "Unable to load tasks.";
    }
}

async function getAccessibleMeetings() {

    const response = await fetch(
        "/employee/meetings",
        {
            headers: {
                "Authorization":
                    "Bearer " + token
            }
        }
    );

    if (!response.ok) {
        const errorData =
            await response.json();

        throw new Error(
            errorData.detail ||
            "Could not load meetings"
        );
    }

    return await response.json();
}

async function loadCompletedTasks() {

    try {
        const response = await fetch(
            "/tasks/history",
            {
                headers: {
                    "Authorization":
                        "Bearer " + token
                }
            }
        );

        if (!response.ok) {
            taskHistoryList.textContent =
                "Could not load task history.";
            return;
        }

        const tasks =
            await response.json();

        taskHistoryList.innerHTML = "";

        if (tasks.length === 0) {
            taskHistoryList.textContent =
                "No completed tasks yet.";
            return;
        }

        tasks.forEach(function (task) {

            const taskBox =
                document.createElement("div");

            taskBox.className = 
            "employee-history-card";    

            const title =
                document.createElement("h3");

            title.textContent =
                task.title;

            const meeting =
                document.createElement("p");

            meeting.textContent =
                "Meeting ID: " +
                task.meeting_id;

            const priority =
                document.createElement("p");

            priority.textContent =
                "Priority: " +
                task.priority;

            const status =
                document.createElement("p");

            status.textContent =
                "Status: " +
                task.status;

            const deadline =
                document.createElement("p");

            deadline.textContent =
                "Deadline: " +
                (
                    task.due_date
                        ? new Date(
                            task.due_date
                        ).toLocaleDateString()
                        : "No deadline"
                );

            taskBox.appendChild(title);
            taskBox.appendChild(meeting);
            taskBox.appendChild(priority);
            taskBox.appendChild(status);
            taskBox.appendChild(deadline);

            

            taskHistoryList.appendChild(
                taskBox
            );
        });

    } catch (error) {

        console.error(
            "Task history loading error:",
            error
        );

        taskHistoryList.textContent =
            "Unable to load task history.";
    }
}


async function updateTaskProgress(
    taskId,
    status,
    progressPercentage,
    comment,
    messageElement
) {

    try {

        const response = await fetch(
            "/tasks/" + taskId,
            {
                method: "PUT",

                headers: {
                    "Authorization":
                        "Bearer " + token,

                    "Content-Type":
                        "application/json"
                },

                body: JSON.stringify({
                    status: status,
                    progress_percentage:
                        progressPercentage,
                    comment: comment
                })
            }
        );

        const data =
            await response.json();

        if (!response.ok) {

            messageElement.textContent =
                data.detail ||
                "Could not update task progress.";

            return;
        }

        messageElement.textContent =
            "Progress updated successfully.";

    } catch (error) {

        console.error(
            "Task progress update error:",
            error
        );

        messageElement.textContent =
            "Unable to update task progress.";
    }
}

async function loadEmployeeAnalytics() {

    try {

        const response = await fetch(
            "/employee/analytics",
            {
                headers: {
                    "Authorization":
                        "Bearer " + token
                }
            }
        );

        if (!response.ok) {

            console.error(
                "Could not load employee analytics."
            );

            return;
        }

        const data =
            await response.json();


        document.getElementById(
            "employeeTotalTasks"
        ).textContent =
            data.total_tasks;


        document.getElementById(
            "employeePendingTasks"
        ).textContent =
            data.pending_tasks;


        document.getElementById(
            "employeeInProgressTasks"
        ).textContent =
            data.in_progress_tasks;


        document.getElementById(
            "employeeCompletedTasks"
        ).textContent =
            data.completed_tasks;


        document.getElementById(
            "employeeOverdueTasks"
        ).textContent =
            data.overdue_tasks;


        document.getElementById(
            "employeeCompletionPercentage"
        ).textContent =
            data.completion_percentage + "%";

        renderEmployeeAnalyticsChart(data);

    } catch (error) {

        console.error(
            "Employee analytics loading error:",
            error
        );
    }
}


function renderEmployeeAnalyticsChart(data) {

    const chartArea =
        document.getElementById(
            "employeeChartArea"
        );

    chartArea.innerHTML = "";


    const chartCard =
        document.createElement("div");

    chartCard.className =
        "chart-card employee-chart-card";


    const title =
        document.createElement("h3");

    title.textContent =
        "My Task Status";


    const total =
        data.total_tasks || 0;

    const pending =
        data.pending_tasks || 0;

    const inProgress =
        data.in_progress_tasks || 0;

    const completed =
        data.completed_tasks || 0;


    const donut =
        document.createElement("div");

    donut.className =
        "employee-task-donut";


    if (total > 0) {

        const pendingPercent =
            (pending / total) * 100;

        const progressPercent =
            (inProgress / total) * 100;

        const completedPercent =
            (completed / total) * 100;


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
                #e2e8f0 ${completedEnd}% 100%
            )`;

    } else {

        donut.style.background =
            "#e2e8f0";
    }


    const centre =
        document.createElement("div");

    centre.className =
        "employee-donut-centre";


    centre.innerHTML = `
        <strong>
            ${data.completion_percentage || 0}%
        </strong>

        <span>
            Complete
        </span>
    `;


    donut.appendChild(
        centre
    );


    const legend =
        document.createElement("div");

    legend.className =
        "chart-legend";


    legend.innerHTML = `

        <div>
            <span
                class="legend-dot pending-dot"
            ></span>

            Pending: ${pending}
        </div>

        <div>
            <span
                class="legend-dot progress-dot"
            ></span>

            In Progress: ${inProgress}
        </div>

        <div>
            <span
                class="legend-dot completed-dot"
            ></span>

            Completed: ${completed}
        </div>

        <div>
            <span
                class="legend-dot overdue-dot"
            ></span>

            Overdue: ${data.overdue_tasks || 0}
        </div>
    `;


    chartCard.appendChild(title);
    chartCard.appendChild(donut);
    chartCard.appendChild(legend);

    chartArea.appendChild(
        chartCard
    );
}

async function loadEmployeeMeetings() {

    try {

        const meetings =
            await getAccessibleMeetings();


        employeeMeetingList.innerHTML = "";


        if (meetings.length === 0) {

            employeeMeetingList.textContent =
                "No published meetings available.";

            return;
        }


        meetings.forEach(function (meeting) {

            const meetingCard =
                document.createElement("div");

            meetingCard.className =
                "meeting-card employee-meeting-card";


            // Meeting title
            const title =
                document.createElement("h3");

            title.textContent =
                meeting.title;


            // Meeting ID
            const meetingId =
                document.createElement("p");

            meetingId.className =
                "meeting-id";

            meetingId.textContent =
                "Meeting ID: " +
                meeting.id;


            // Meeting date
            const meetingDate =
                document.createElement("p");

            meetingDate.className =
                "employee-meeting-date";

            meetingDate.textContent =
                "Date: " +
                (
                    meeting.meeting_date
                        ? new Date(
                            meeting.meeting_date
                        ).toLocaleDateString()
                        : "Not provided"
                );


            // Buttons
            const actions =
                document.createElement("div");

            actions.className =
                "meeting-card-actions";


            const summaryButton =
                document.createElement("button");

            summaryButton.className =
                "secondary-action";

            summaryButton.textContent =
                "Meeting Summary";


            const decisionsButton =
                document.createElement("button");

            decisionsButton.className =
                "secondary-action";

            decisionsButton.textContent =
                "Decisions";


            const notesButton =
                document.createElement("button");

            notesButton.className =
                "secondary-action";

            notesButton.textContent =
                "Extracted Meeting Notes";


            // -----------------------------------
            // Summary popup
            // -----------------------------------

            summaryButton.onclick =
                function () {

                    openEmployeeMeetingModal(
                        meeting.title +
                        " — Meeting Summary",

                        `
                            <p>
                                ${
                                    escapeHtml(
                                        meeting.ai_summary ||
                                        "No summary available."
                                    )
                                }
                            </p>
                        `
                    );
                };


            // -----------------------------------
            // Decisions popup
            // -----------------------------------

            decisionsButton.onclick =
                function () {

                    let decisionHtml =
                        "<p>No decisions available.</p>";


                    if (
                        meeting.decisions &&
                        meeting.decisions.length > 0
                    ) {

                        decisionHtml =
                            meeting.decisions
                                .map(
                                    function (decision) {

                                        return (
                                            "<p>• " +
                                            escapeHtml(
                                                decision.decision_text
                                            ) +
                                            "</p>"
                                        );
                                    }
                                )
                                .join("");
                    }


                    openEmployeeMeetingModal(
                        meeting.title +
                        " — Decisions",

                        decisionHtml
                    );
                };


            // -----------------------------------
            // Extracted notes popup
            // -----------------------------------

            notesButton.onclick =
                function () {

                    openEmployeeMeetingModal(
                        meeting.title +
                        " — Extracted Meeting Notes",

                        `
                            <pre class="modal-notes">${
                                escapeHtml(
                                    meeting.raw_text ||
                                    "No extracted meeting notes available."
                                )
                            }</pre>
                        `
                    );
                };


            actions.appendChild(
                summaryButton
            );

            actions.appendChild(
                decisionsButton
            );

            actions.appendChild(
                notesButton
            );


            meetingCard.appendChild(
                title
            );

            meetingCard.appendChild(
                meetingId
            );

            meetingCard.appendChild(
                meetingDate
            );

            meetingCard.appendChild(
                actions
            );


            employeeMeetingList.appendChild(
                meetingCard
            );
        });


    } catch (error) {

        console.error(
            "Employee meetings error:",
            error
        );

        employeeMeetingList.textContent =
            "Unable to load meeting information.";
    }
}

function openEmployeeMeetingModal(
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


    const headingRow =
        document.createElement("div");

    headingRow.className =
        "employee-modal-heading";


    const heading =
        document.createElement("h2");

    heading.textContent =
        title;


    const closeButton =
        document.createElement("button");

    closeButton.type =
        "button";

    closeButton.className =
        "employee-modal-close";

    closeButton.textContent =
        "×";


    const contentBox =
        document.createElement("div");

    contentBox.className =
        "meeting-modal-content";

    contentBox.innerHTML =
        content;


    function closeModal() {

        if (document.body.contains(overlay)) {

            document.body.removeChild(
                overlay
            );
        }
    }


    closeButton.onclick =
        closeModal;


    overlay.onclick =
        function (event) {

            if (event.target === overlay) {

                closeModal();
            }
        };


    headingRow.appendChild(
        heading
    );

    headingRow.appendChild(
        closeButton
    );


    modal.appendChild(
        headingRow
    );

    modal.appendChild(
        contentBox
    );


    overlay.appendChild(
        modal
    );


    document.body.appendChild(
        overlay
    );
}

function escapeHtml(value) {

    const div =
        document.createElement("div");

    div.textContent =
        value;

    return div.innerHTML;
}


async function loadTaskHistory(
    taskId,
    container
) {

    try {

        const response = await fetch(
            "/tasks/" +
            taskId +
            "/updates",
            {
                headers: {
                    "Authorization":
                        "Bearer " + token
                }
            }
        );

        if (!response.ok) {
            container.textContent =
                "Could not load task history.";
            return;
        }

        const updates =
            await response.json();

        container.innerHTML = "";

        if (updates.length === 0) {
            container.textContent =
                "No progress history yet.";
            return;
        }

        updates.forEach(
            function (update) {

                const item =
                    document.createElement("div");

                const status =
                    document.createElement("p");

                status.textContent =
                    "Status: " +
                    update.status;


                const progress =
                    document.createElement("p");

                progress.textContent =
                    "Progress: " +
                    update.progress_percentage +
                    "%";


                const comment =
                    document.createElement("p");

                comment.textContent =
                    "Comment: " +
                    (
                        update.comment ||
                        "No comment"
                    );


                const date =
                    document.createElement("p");

                date.textContent =
                    "Updated: " +
                    new Date(
                        update.created_at
                    ).toLocaleString();


                item.appendChild(status);
                item.appendChild(progress);
                item.appendChild(comment);
                item.appendChild(date);

                item.appendChild(
                    document.createElement("hr")
                );

                container.appendChild(item);
            }
        );

    } catch (error) {

        console.error(
            "Task history error:",
            error
        );

        container.textContent =
            "Unable to load task history.";
    }
}

refreshTasks.addEventListener(
    "click",
    loadTasks
);


showTaskHistory.addEventListener(
    "click",
    async function () {

        if (
            taskHistoryList.style.display ===
            "none"
        ) {
            taskHistoryList.style.display =
                "block";

            await loadCompletedTasks();

            showTaskHistory.textContent =
                "Hide Task History";

        } else {

            taskHistoryList.style.display =
                "none";

            showTaskHistory.textContent =
                "Task History";
        }
    }
);

// Load assigned tasks automatically
// when the employee dashboard opens.
async function startEmployeeDashboard() {

    await checkEmployee();

    await loadTasks();

    await loadEmployeeAnalytics();

    await loadEmployeeMeetings();
}

startEmployeeDashboard();