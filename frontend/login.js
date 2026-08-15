// javaspring.net/blog/can-t-get-response-status-code-with-javascript-fetch/
// source code for this login form

const loginForm = document.getElementById("loginForm");
const errorMessage = document.getElementById("errorMessage");

loginForm.addEventListener("submit", async function (event) {
    event.preventDefault();

    errorMessage.textContent = "";

    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;

    try {
        const response = await fetch("/login", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                email: email,
                password: password
            })
        });

        const data = await response.json();

        if (!response.ok) {
            errorMessage.textContent = data.detail || "Login failed.";
            return;
        }

        // Save the JWT token returned by FastAPI.
        localStorage.setItem("access_token", data.access_token);

        // Get the logged-in user's role.
        const profileResponse = await fetch("/me", {
            method: "GET",
            headers: {
                "Authorization": "Bearer " + data.access_token
            }
        });

        const user = await profileResponse.json();

        if (!profileResponse.ok) {
            errorMessage.textContent = "Could not load user details.";
            return;
        }

        // Send the user to the correct dashboard.
        if (user.role === "manager") {
            window.location.href = "/manager-dashboard";
        } else if (user.role === "employee") {
            window.location.href = "/employee-dashboard";
        } else {
            errorMessage.textContent = "Unknown user role.";
        }

    } catch (error) {
        console.error(error);
        errorMessage.textContent = "Unable to connect to the server.";
    }
});
