const token =
    localStorage.getItem("access_token");


async function loadMeeting() {

    if (!token) {
        window.location.href = "/login-page";
        return;
    }

    const parts =
        window.location.pathname.split("/");

    const meetingId =
        parts[parts.length - 1];

    try {

        const response = await fetch(
            "/meetings/" + meetingId,
            {
                headers: {
                    "Authorization":
                        "Bearer " + token
                }
            }
        );

        if (!response.ok) {
            document.getElementById(
                "meetingText"
            ).textContent =
                "Could not load meeting.";

            return;
        }

        const meeting =
            await response.json();

        document.getElementById(
            "meetingTitle"
        ).textContent =
            meeting.title;

        document.getElementById(
            "meetingFile"
        ).textContent =
            "File: " + meeting.original_filename;

        document.getElementById(
            "meetingText"
        ).textContent =
            meeting.raw_text;

    } catch (error) {

        console.error(
            "Meeting review error:",
            error
        );
    }
}


function goBack() {
    window.location.href =
        "/manager-dashboard";
}


loadMeeting();