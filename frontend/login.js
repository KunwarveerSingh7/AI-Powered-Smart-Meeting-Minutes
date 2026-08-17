// Source 1
// https://www.geeksforgeeks.org/javascript/design-a-responsive-sliding-login-registration-form-using-html-css-javascript/
// login form html, css and js idea
//Source 2
// javaspring.net/blog/can-t-get-response-status-code-with-javascript-fetch/
// checking unsuccessful fetch resrponses
//Source 3
// https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API/Using_Fetch
// understand fetch request and response
//Source 4
// https://stackoverflow.com/questions/68389117/using-fetch-api-to-create-a-login-form/79563467
// use of fetch api to create a login form



// get the login form and error message from basic_html
const loginForm = document.getElementById("loginForm");
const errorMessage = document.getElementById("errorMessage");

// run login form when user press submit button
loginForm.addEventListener("submit", async function (event) {
    event.preventDefault();
    //clear an error message from previous login attempt
    errorMessage.textContent = "";

    //get the email and password entered by the user
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;

    try {

        //send the login details entered by the user to FastAPI
        const response = await fetch("/login", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },

            // convert email and password into JSON before sending
            body: JSON.stringify({
                email: email,
                password: password
            })
        });


        // convert response from server into javascript data
        const data = await response.json();

        // error message from unsuccessful login
        if (!response.ok) {
            errorMessage.textContent = data.detail || "Login failed.";
            return;
        }

        // Save the JWT token returned by FastAPI.
        localStorage.setItem("access_token", data.access_token);

        // ask backend for information about the logged in user
        const profileResponse = await fetch("/me", {
            method: "GET",
            headers: {
                "Authorization": "Bearer " + data.access_token
            }
        });

        // read the user infor returned from /me
        const user = await profileResponse.json();

        // error message if user details not loaded
        if (!profileResponse.ok) {
            errorMessage.textContent = "Could not load user details.";
            return;
        }

        // Send the user to the correct dashboard.
        if (user.role === "manager") {
            window.location.href = "/manager-dashboard";
        } else if (user.role === "employee") {
            window.location.href = "/employee-dashboard";
        // this should only happen when user's role is not defined
        } else {
            errorMessage.textContent = "Unknown user role.";
        }

    // error handler if backend server is not connected 
    } catch (error) {
        console.error(error);
        errorMessage.textContent = "Unable to connect to the server.";
    }
});
