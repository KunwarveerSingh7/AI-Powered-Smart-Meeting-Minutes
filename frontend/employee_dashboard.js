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

        if (tasks.length === 0) {
            taskList.textContent =
                "No tasks assigned to you.";
            return;
        }

        tasks.forEach(function (task) {

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

taskList.appendChild(taskBox);
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

            taskBox.appendChild(
                document.createElement("hr")
            );

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

    } catch (error) {

        console.error(
            "Employee analytics loading error:",
            error
        );
    }
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

showMeetingNotes.addEventListener(
    "click",
    async function () {

        try {

            const meetings =
                await getAccessibleMeetings();

            meetingNotesBox.innerHTML = "";

            if (meetings.length === 0) {

                meetingNotesBox.textContent =
                    "No published meeting notes available.";

                meetingNotesBox.style.display =
                    "block";

                return;
            }

            meetings.forEach(
                function (meeting) {

                    const meetingBox =
                        document.createElement("div");

                    const title =
                        document.createElement("h3");

                    title.textContent =
                        meeting.title +
                        " (Meeting ID: " +
                        meeting.id +
                        ")";

                    const notes =
                        document.createElement("pre");

                    notes.textContent =
                        meeting.raw_text ||
                        "No extracted meeting notes available.";

                    meetingBox.appendChild(title);
                    meetingBox.appendChild(notes);

                    meetingBox.appendChild(
                        document.createElement("hr")
                    );

                    meetingNotesBox.appendChild(
                        meetingBox
                    );
                }
            );

            meetingNotesBox.style.display =
                "block";

        } catch (error) {

            console.error(
                "Meeting notes error:",
                error
            );

            meetingNotesBox.textContent =
                error.message;

            meetingNotesBox.style.display =
                "block";
        }
    }
);

showMeetingSummary.addEventListener(
    "click",
    async function () {

        try {

            const meetings =
                await getAccessibleMeetings();

            meetingSummaryBox.innerHTML = "";

            if (meetings.length === 0) {
                meetingSummaryBox.textContent =
                    "No published meeting summaries available.";

                meetingSummaryBox.style.display =
                    "block";

                return;
            }

            meetings.forEach(
                function (meeting) {

                    const meetingBox =
                        document.createElement("div");

                    const title =
                        document.createElement("h3");

                    title.textContent =
                        meeting.title +
                        " (Meeting ID: " +
                        meeting.id +
                        ")";

                    const summary =
                        document.createElement("p");

                    summary.textContent =
                        meeting.ai_summary ||
                        "No summary available.";

                    meetingBox.appendChild(title);
                    meetingBox.appendChild(summary);

                    meetingBox.appendChild(
                        document.createElement("hr")
                    );

                    meetingSummaryBox.appendChild(
                        meetingBox
                    );
                }
            );

            meetingSummaryBox.style.display =
                "block";

        } catch (error) {

            meetingSummaryBox.textContent =
                error.message;

            meetingSummaryBox.style.display =
                "block";
        }
    }
);


showMeetingSummary.addEventListener(
    "click",
    async function () {

        try {

            const meetings =
                await getAccessibleMeetings();

            meetingSummaryBox.innerHTML = "";

            if (meetings.length === 0) {
                meetingSummaryBox.textContent =
                    "No published meeting summaries available.";

                meetingSummaryBox.style.display =
                    "block";

                return;
            }

            meetings.forEach(
                function (meeting) {

                    const meetingBox =
                        document.createElement("div");

                    const title =
                        document.createElement("h3");

                    title.textContent =
                        meeting.title +
                        " (Meeting ID: " +
                        meeting.id +
                        ")";

                    const summary =
                        document.createElement("p");

                    summary.textContent =
                        meeting.ai_summary ||
                        "No summary available.";

                    meetingBox.appendChild(title);
                    meetingBox.appendChild(summary);

                    meetingBox.appendChild(
                        document.createElement("hr")
                    );

                    meetingSummaryBox.appendChild(
                        meetingBox
                    );
                }
            );

            meetingSummaryBox.style.display =
                "block";

        } catch (error) {

            meetingSummaryBox.textContent =
                error.message;

            meetingSummaryBox.style.display =
                "block";
        }
    }
);

showDecisions.addEventListener(
    "click",
    async function () {

        try {

            const meetings =
                await getAccessibleMeetings();

            decisionsBox.innerHTML = "";

            if (meetings.length === 0) {

                decisionsBox.textContent =
                    "No published meeting decisions available.";

                decisionsBox.style.display =
                    "block";

                return;
            }

            meetings.forEach(
                function (meeting) {

                    const meetingBox =
                        document.createElement("div");

                    const title =
                        document.createElement("h3");

                    title.textContent =
                        meeting.title +
                        " (Meeting ID: " +
                        meeting.id +
                        ")";

                    meetingBox.appendChild(title);

                    if (
                        meeting.decisions &&
                        meeting.decisions.length > 0
                    ) {

                        meeting.decisions.forEach(
                            function (decision) {

                                const item =
                                    document.createElement("p");

                                item.textContent =
                                    "• " +
                                    decision.decision_text;

                                meetingBox.appendChild(
                                    item
                                );
                            }
                        );

                    } else {

                        const noDecision =
                            document.createElement("p");

                        noDecision.textContent =
                            "No decisions available.";

                        meetingBox.appendChild(
                            noDecision
                        );
                    }

                    meetingBox.appendChild(
                        document.createElement("hr")
                    );

                    decisionsBox.appendChild(
                        meetingBox
                    );
                }
            );

            decisionsBox.style.display =
                "block";

        } catch (error) {

            decisionsBox.textContent =
                error.message;

            decisionsBox.style.display =
                "block";
        }
    }
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
}

startEmployeeDashboard();