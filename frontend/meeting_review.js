//Source 1
//https://javascript.info/fetch
// fetch request and recieve data from backend
//Source 2
//https://javascript.info/modifying-document
// creating and understanding the html elements
//Source 3
//https://www.w3schools.com/js/js_htmldom_methods.asp
//reference to createElemnt
// Source 4
// https://auth0.com/docs/secure/security-guidance/data-security/token-storage
//how access token is being used


// file strcuture
// async functions in order
// loadEmployees()
//loadMeetings()
//saveSummary()
//saveDecision()
//saveTasks()
// publishMeeting()
//startReviewPage

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
        ) {
        
        meeting.decisions.forEach(
        
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

        // check if the meeting has any recorded tasks
        if (meeting.tasks &&
            meeting.tasks.length > 0) {

        // for all the generated tasks
        meeting.tasks.forEach(function (task) {
        // create a box to display the tasks
        const taskBox = document.createElement("div");
        taskBox.className = "task-review";
        // create the top section of task
        const taskHeader = document.createElement("div");
        taskHeader.className = "task-review-header";
        // create labl for ai-genrtated tasks
        const taskNumber = document.createElement("span");
        taskNumber.className = "task-number";
        taskNumber.textContent =  "AI-Generated Task";

        // create badge for priority fo the tasks
        const priorityBadge = document.createElement("span");

        priorityBadge.className = "priority-badge priority-" + task.priority;
        // use medium if priority is missing (display in capital)
        priorityBadge.textContent = (task.priority || "medium").toUpperCase() + " PRIORITY";

        // add label and prioruty to the header
        taskHeader.appendChild(taskNumber);
        taskHeader.appendChild(priorityBadge);
        taskBox.appendChild(taskHeader);


        // Title for the tasks
        const titleLabel = document.createElement("p");

        titleLabel.className ="task-field-label";
        titleLabel.textContent = "Task Title:";
        //editable task title
        const titleInput = document.createElement("input");
        titleInput.className ="task-input";

        titleInput.type = "text";
        titleInput.value = task.title;
        titleInput.style.width = "100%";

        taskBox.appendChild(titleLabel);
        taskBox.appendChild(titleInput);

        // task description
        const descriptionLabel = document.createElement("p");
        descriptionLabel.className = "task-field-label";
        descriptionLabel.textContent = "Description:";
        // textarea to allow manager to edit the description
        const descriptionInput = document.createElement("textarea");
        descriptionInput.className ="task-input";

        descriptionInput.rows = 3;
        descriptionInput.style.width = "100%";
        // leave empty if no description given by ai
        descriptionInput.value = task.description || "";

        taskBox.appendChild(descriptionLabel);
        taskBox.appendChild(descriptionInput);

        // deadline for the task
        const deadlineLabel = document.createElement("p");
        deadlineLabel.className = "task-field-label";
        deadlineLabel.textContent ="Deadline:";

        // date input for the deadline
        const deadlineInput = document.createElement("input");
        deadlineInput.className = "task-input";
        deadlineInput.type = "date";
        // only set if ai find a deadline date
        if (task.due_date) {deadlineInput.value = task.due_date.split("T")[0];
        }

        // priority of the task
        const priorityLabel = document.createElement("p");
        priorityLabel.className ="task-field-label";
        priorityLabel.textContent ="Priority:";

        // dropdown to review and chnage tje priority
        const prioritySelect = document.createElement("select");
        prioritySelect.className = "task-input";
        // three priority options
        ["low", "medium", "high"].forEach(
            function (priorityValue) {
                const option = document.createElement("option");

                option.value = priorityValue;
                option.textContent =priorityValue;
                // select the priority given by ai
                if (task.priority ===priorityValue) {
                    option.selected = true;
                }

                prioritySelect.appendChild(option);
            }
        );
        
        // put deadline and priority on the same row
        const taskDetailsRow = document.createElement("div");
        taskDetailsRow.className ="task-details-row";

        // group's deadline label + input
        const deadlineGroup = document.createElement("div");

        deadlineGroup.className ="task-field-group";
        deadlineGroup.appendChild(deadlineLabel);
        deadlineGroup.appendChild(deadlineInput);

        //group's priority label and dropdown
        const priorityGroup = document.createElement("div");
        priorityGroup.className = "task-field-group";
        priorityGroup.appendChild(priorityLabel);
        priorityGroup.appendChild(prioritySelect);

        // add both th groups to details row
        taskDetailsRow.appendChild(deadlineGroup  );
        taskDetailsRow.appendChild(priorityGroup);
        // add the detials row to task box
        taskBox.appendChild(taskDetailsRow);

        // employee assignment
        const employeeLabel = document.createElement("p");
        employeeLabel.className = "task-field-label";
        employeeLabel.textContent = "Assign Employee:";
        
        // dropdown to assign the available employees to the task
        const employeeSelect = document.createElement("select");
        employeeSelect.className = "task-input employee-assignment";

        employeeSelect.multiple = true;
        //add all employees to the dropdown
        employeeList.forEach(
            function (employee) {

                const option =document.createElement("option");
                option.value = employee.id;
                //show employees name and positipn
                option.textContent =(employee.name || employee.email) +(employee.position? " — " + employee.position: "");

                //keep already assigned employees selected
                if (task.assigned_user_ids && task.assigned_user_ids.includes(
                        employee.id)
                    ) {
                    option.selected = true;}

                employeeSelect.appendChild(option);
            }
        );

        //add employeee section to taskbox
        taskBox.appendChild(employeeLabel);
        taskBox.appendChild(employeeSelect);


        // warning messages
        // if task has no deadline
        if (!task.due_date) {

            const warning = document.createElement("p");
            warning.textContent =  "⚠️ Manager review required: deadline is missing.";
            warning.className = "manager-review-warning";

            taskBox.appendChild(warning);
        }

        //show the warning message if no employee is assigned
        if (!task.assigned_user_ids ||
            task.assigned_user_ids.length === 0) {

        const assignmentWarning =document.createElement("p");

        assignmentWarning.className ="manager-review-warning";

        assignmentWarning.textContent = "⚠️ Manager review required: employee assignment has not been confirmed.";

        taskBox.appendChild(assignmentWarning);}

        //  sabe button
        const saveButton = document.createElement("button");
        saveButton.textContent = "Save Task";
        saveButton.className ="primary-action task-save-button";    
        // meesage after saving
        const message = document.createElement("p");
        message.className = "task-save-message";    

        saveButton.onclick =
            async function () {
                // get id of the slelected employees
                const assignedIds =
                    Array.from(
                        employeeSelect
                            .selectedOptions
                    ).map(
                        option =>
                            Number(option.value)
                    );
                // send the updated task details to the backend
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

        // add save button and the messages to the taskBox and task box to the page
        taskBox.appendChild(saveButton);
        taskBox.appendChild(message);
        tasksContainer.appendChild(taskBox);
        });
        } 
    
        else {tasksContainer.textContent ="No tasks identified.";}

    } 
    
    catch (error) {

        console.error("Meeting review error:", error);
    }
}

//save the edited meeting summary
async function saveSummary() {

    // get the meeting id from page url
    const parts =window.location.pathname.split("/");
    const meetingId = parts[parts.length - 1];
    // get the current summary from text area
    const summary =document.getElementById("aiSummary").value;

    try {
        //send the updates to backend upon changes
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

                body: JSON.stringify({ai_summary: summary})
            }
        );

        //message if not saved
        if (!response.ok) {document.getElementById("summaryMessage"
            ).textContent ="Could not save summary.";
            return;
        }

        //confirm the summary was save
        document.getElementById("summaryMessage").textContent =
            "Summary saved successfully.";

    } 
    
    catch (error) {
        console.error("Summary update error:", error);
    }
}

// saved th e changes to decision
async function saveDecision(
    decisionId,decisionText) {

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

        // show error if decision could not be saved
        if (!response.ok) {document.getElementById("decisionMessage").textContent =
                "Could not save decision.";
            return;
        }

        document.getElementById(
            "decisionMessage"
        ).textContent =
            "Decision saved successfully.";

    } 
    catch (error) {
        console.error(
            "Decision update error:",
            error);
    }
}

// save updated task info
async function saveTask(
    taskId,
    taskData,
    messageElement) {

    try {
        //update the selected task in backend
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

        const data =await response.json();
        // show the error if update no happen
        if (!response.ok) {
            messageElement.textContent =
                data.detail ||
                "Could not save task.";
            return;
        }

        messageElement.textContent ="Task saved successfully.";

    } 
    
    catch (error) {
        console.error(
            "Task update error:",
            error
        );

        messageElement.textContent = "Unable to save task.";
    }
}

// publisj the meeting after manager review
async function publishMeeting() {
    // get the meeting id from url
    const parts = window.location.pathname.split("/");
    const meetingId = parts[parts.length - 1];
    const message =document.getElementById("publishMessage");

    try {
        // request backend to publish meeting
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

        const data =await response.json();
        // error message
        if (!response.ok) {
            message.textContent =data.detail || "Could not publish meeting.";
            return;
        }

        message.textContent ="Meeting published successfully.";

    } 
    catch (error) {
        console.error(
            "Meeting publish error:",
            error
        );

        message.textContent ="Unable to publish meeting.";
    }
}

// manager return to dash
function goBack() {
    window.location.href ="/manager-dashboard";
}

// load all informatio when review page opens
async function startReviewPage() {
    await loadEmployees();
    await loadMeeting();
}

// start the meeting review page
startReviewPage();
