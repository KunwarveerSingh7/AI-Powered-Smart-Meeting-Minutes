

const token = localStorage.getItem("access_token");
// employee info stored here are after loading
let employeeList = [];


// Load employees for task assignment by manager
async function loadEmployees() {
    try {
        // authorisation request to get employes
        const response = await fetch("/employees",{
            headers: {"Authorization":"Bearer " + token}
        });
        // stop here if informatiom not laoaded
        if (!response.ok) {
            console.error("Could not load employees.");
            return;}

        employeeList = await response.json();
        
    //error message
    } catch (error) {
        console.error("Employee loading error:", error);}
}

// load the selected meeting and pass ist functions
async function loadMeeting() {
    //user without the access token cannot access
    if (!token) {window.location.href = "/login-page";
    return;
    }
    // get metting id
    const parts = window.location.pathname.split("/");
    const meetingId = parts[parts.length - 1];

    try {
        // upon getting the meeting id, ask backend for that
        const response = await fetch("/meetings/" + meetingId, {
                headers: {"Authorization": "Bearer " + token }
        });
        //show error on page if meeting not loaded
        if (!response.ok) {
            document.getElementById("meetingText").textContent =
                "Could not load meeting.";
            return;
        }
        // backend send meeting info as json
        const meeting =
            await response.json();

        //add meeting title to the page
        document.getElementById("meetingTitle").textContent =
        meeting.title;
        //show the file name for the uploaded doc
        document.getElementById("meetingFile").textContent =
        "File: " + meeting.original_filename;
        //raw text contain original text extracted using file_handler.py
        document.getElementById("meetingText").textContent =
            meeting.raw_text;
        // put ai genereted text summary in the text area
        document.getElementById("aiSummary").value =
        meeting.ai_summary || "";

        // Display decisions
        const decisionsContainer = document.getElementById("decisions");
        decisionsContainer.innerHTML = "";

        //check if the meeting has any recorded decisions
        if (
        meeting.decisions &&
        meeting.decisions.length > 0
        ) 
        
        {meeting.decisions.forEach(
        
        function (decision) {

            //create editable area for each decision
            const decisionBox = document.createElement("div");
            const input = document.createElement("textarea");

            input.rows = 3;
            input.style.width = "100%";
            input.value = decision.decision_text;
            //save button for each decision
            const button = document.createElement("button");

            button.textContent = "Save Decision";

            button.onclick = function () {
                saveDecision(decision.id, input.value);
            };

            decisionBox.appendChild(input);
            decisionBox.appendChild(button);

            decisionsContainer.appendChild(decisionBox);
        });
        } 
        else {decisionsContainer.textContent =
            "No decisions identified.";
        }


        // Display AI-generated tasks
        const tasksContainer = document.getElementById("tasks");
        tasksContainer.innerHTML = "";

        if (meeting.tasks &&
            meeting.tasks.length > 0) {
    meeting.tasks.forEach(function (task) {

        const taskBox =
            document.createElement("div");

        taskBox.className = "task-review";

        const taskHeader =
    document.createElement("div");

taskHeader.className =
    "task-review-header";


const taskNumber =
    document.createElement("span");

taskNumber.className =
    "task-number";

taskNumber.textContent =
    "AI-Generated Task";


const priorityBadge =
    document.createElement("span");

priorityBadge.className =
    "priority-badge priority-" +
    task.priority;

priorityBadge.textContent =
    (task.priority || "medium")
        .toUpperCase() +
    " PRIORITY";


taskHeader.appendChild(taskNumber);
taskHeader.appendChild(priorityBadge);

taskBox.appendChild(taskHeader);


        // -------------------------
        // Task title
        // -------------------------

        const titleLabel =
            document.createElement("p");

            titleLabel.className =
    "task-field-label";

        titleLabel.textContent = "Task Title:";

        const titleInput =
            document.createElement("input");

            titleInput.className =
    "task-input";

        titleInput.type = "text";
        titleInput.value = task.title;
        titleInput.style.width = "100%";

        taskBox.appendChild(titleLabel);
        taskBox.appendChild(titleInput);


        // -------------------------
        // Description
        // -------------------------

        const descriptionLabel =
            document.createElement("p");

        descriptionLabel.className =
            "task-field-label";

        descriptionLabel.textContent =
            "Description:";


        const descriptionInput =
            document.createElement("textarea");

        descriptionInput.className =
            "task-input";

        descriptionInput.rows = 3;
        descriptionInput.style.width = "100%";
        descriptionInput.value =
            task.description || "";

        taskBox.appendChild(
            descriptionLabel
        );

        taskBox.appendChild(
            descriptionInput
        );


        // -------------------------
        // Deadline
        // -------------------------

        const deadlineLabel =
            document.createElement("p");

        deadlineLabel.className =
            "task-field-label";

        deadlineLabel.textContent =
            "Deadline:";


        const deadlineInput =
            document.createElement("input");

        deadlineInput.className =
            "task-input";

        deadlineInput.type = "date";

        if (task.due_date) {
            deadlineInput.value =
                task.due_date.split("T")[0];
        }


        // -------------------------
        // Priority
        // -------------------------

        const priorityLabel =
            document.createElement("p");

        priorityLabel.className =
            "task-field-label";

        priorityLabel.textContent =
            "Priority:";


        const prioritySelect =
            document.createElement("select");

        prioritySelect.className =
            "task-input";

        ["low", "medium", "high"].forEach(
            function (priorityValue) {

                const option =
                    document.createElement(
                        "option"
                    );

                option.value =
                    priorityValue;

                option.textContent =
                    priorityValue;

                if (
                    task.priority ===
                    priorityValue
                ) {
                    option.selected = true;
                }

                prioritySelect.appendChild(
                    option
                );
            }
        );

        const taskDetailsRow =
    document.createElement("div");

taskDetailsRow.className =
    "task-details-row";


const deadlineGroup =
    document.createElement("div");

deadlineGroup.className =
    "task-field-group";

deadlineGroup.appendChild(
    deadlineLabel
);

deadlineGroup.appendChild(
    deadlineInput
);


const priorityGroup =
    document.createElement("div");

priorityGroup.className =
    "task-field-group";

priorityGroup.appendChild(
    priorityLabel
);

priorityGroup.appendChild(
    prioritySelect
);


taskDetailsRow.appendChild(
    deadlineGroup
);

taskDetailsRow.appendChild(
    priorityGroup
);

taskBox.appendChild(
    taskDetailsRow
);

        // -------------------------
        // Employee assignment
        // -------------------------

        const employeeLabel =
            document.createElement("p");

        employeeLabel.className =
            "task-field-label";

        employeeLabel.textContent =
            "Assign Employee:";


        const employeeSelect =
            document.createElement("select");

        employeeSelect.className =
            "task-input employee-assignment";

        employeeSelect.multiple = true;

        employeeList.forEach(
            function (employee) {

                const option =
                    document.createElement(
                        "option"
                    );

                option.value =
                    employee.id;

                option.textContent =
                (employee.name || employee.email) +
                (
                    employee.position
                    ? " — " + employee.position
                    : ""
                    );

                if (
                    task.assigned_user_ids &&
                    task.assigned_user_ids.includes(
                        employee.id
                    )
                ) {
                    option.selected = true;
                }

                employeeSelect.appendChild(
                    option
                );
            }
        );

        taskBox.appendChild(
            employeeLabel
        );

        taskBox.appendChild(
            employeeSelect
        );


        // -------------------------
        // Warning
        // -------------------------

        if (!task.due_date) {

            const warning =
                document.createElement("p");

            warning.textContent =
                "⚠️ Manager review required: deadline is missing.";

                warning.className = "manager-review-warning";

            taskBox.appendChild(
                warning
            );
        }


        if (!task.assigned_user_ids ||
            task.assigned_user_ids.length === 0
        ) {

        const assignmentWarning =
            document.createElement("p");

        assignmentWarning.className =
            "manager-review-warning";

        assignmentWarning.textContent =
            "⚠️ Manager review required: employee assignment has not been confirmed.";

        taskBox.appendChild(
            assignmentWarning
        );
        }


        // -------------------------
        // Save button
        // -------------------------

        const saveButton =
            document.createElement("button");

        saveButton.textContent =
            "Save Task";

        saveButton.className =
            "primary-action task-save-button";    

        const message =
            document.createElement("p");

        message.className =
            "task-save-message";    

        saveButton.onclick =
            async function () {

                const assignedIds =
                    Array.from(
                        employeeSelect
                            .selectedOptions
                    ).map(
                        option =>
                            Number(option.value)
                    );

                await saveTask(
                    task.id,
                    {
                        title:
                            titleInput.value,

                        description:
                            descriptionInput.value,

                        due_date:
                            deadlineInput.value
                                ? deadlineInput.value +
                                  "T00:00:00"
                                : null,

                        priority:
                            prioritySelect.value,

                        assigned_user_ids:
                            assignedIds
                    },
                    message
                );
            };

        taskBox.appendChild(
            saveButton
        );

        taskBox.appendChild(
            message
        );


        tasksContainer.appendChild(
            taskBox
        );
    });

} else {

    tasksContainer.textContent =
        "No tasks identified.";
}

    } catch (error) {

        console.error(
            "Meeting review error:",
            error
        );
    }
}

async function saveSummary() {

    const parts =
        window.location.pathname.split("/");

    const meetingId =
        parts[parts.length - 1];

    const summary =
        document.getElementById(
            "aiSummary"
        ).value;

    try {
        const response = await fetch(
            "/meetings/" +
            meetingId +
            "/summary",
            {
                method: "PUT",

                headers: {
                    "Authorization":
                        "Bearer " + token,

                    "Content-Type":
                        "application/json"
                },

                body: JSON.stringify({
                    ai_summary: summary
                })
            }
        );

        if (!response.ok) {
            document.getElementById(
                "summaryMessage"
            ).textContent =
                "Could not save summary.";
            return;
        }

        document.getElementById(
            "summaryMessage"
        ).textContent =
            "Summary saved successfully.";

    } catch (error) {
        console.error(
            "Summary update error:",
            error
        );
    }
}


async function saveDecision(
    decisionId,
    decisionText
) {

    try {
        const response = await fetch(
            "/decisions/" + decisionId,
            {
                method: "PUT",

                headers: {
                    "Authorization":
                        "Bearer " + token,

                    "Content-Type":
                        "application/json"
                },

                body: JSON.stringify({
                    decision_text:
                        decisionText
                })
            }
        );

        if (!response.ok) {
            document.getElementById(
                "decisionMessage"
            ).textContent =
                "Could not save decision.";
            return;
        }

        document.getElementById(
            "decisionMessage"
        ).textContent =
            "Decision saved successfully.";

    } catch (error) {
        console.error(
            "Decision update error:",
            error
        );
    }
}


async function saveTask(
    taskId,
    taskData,
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

                body: JSON.stringify(
                    taskData
                )
            }
        );

        const data =
            await response.json();

        if (!response.ok) {
            messageElement.textContent =
                data.detail ||
                "Could not save task.";

            return;
        }

        messageElement.textContent =
            "Task saved successfully.";

    } catch (error) {

        console.error(
            "Task update error:",
            error
        );

        messageElement.textContent =
            "Unable to save task.";
    }
}

async function publishMeeting() {

    const parts =
        window.location.pathname.split("/");

    const meetingId =
        parts[parts.length - 1];

    const message =
        document.getElementById(
            "publishMessage"
        );

    try {

        const response = await fetch(
            "/meetings/" +
            meetingId +
            "/publish",
            {
                method: "PUT",

                headers: {
                    "Authorization":
                        "Bearer " + token
                }
            }
        );

        const data =
            await response.json();

        if (!response.ok) {

            message.textContent =
                data.detail ||
                "Could not publish meeting.";

            return;
        }

        message.textContent =
            "Meeting published successfully.";

    } catch (error) {

        console.error(
            "Meeting publish error:",
            error
        );

        message.textContent =
            "Unable to publish meeting.";
    }
}


function goBack() {
    window.location.href =
        "/manager-dashboard";
}


async function startReviewPage() {
    await loadEmployees();
    await loadMeeting();
}


startReviewPage();
