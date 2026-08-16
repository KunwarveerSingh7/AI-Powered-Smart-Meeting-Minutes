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
            taskBox.appendChild(priority);
            taskBox.appendChild(status);
            taskBox.appendChild(deadline);

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


refreshTasks.addEventListener(
    "click",
    loadTasks
);


// Load assigned tasks automatically
// when the employee dashboard opens.
async function startEmployeeDashboard() {
    await checkEmployee();
    await loadTasks();
}

startEmployeeDashboard();