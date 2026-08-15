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

checkEmployee();