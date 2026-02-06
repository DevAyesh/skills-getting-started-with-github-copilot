document.addEventListener("DOMContentLoaded", () => {
  const activitiesList = document.getElementById("activities-list");
  const activitySelect = document.getElementById("activity");
  const signupForm = document.getElementById("signup-form");
  const messageDiv = document.getElementById("message");

  // Function to fetch activities from API
  async function fetchActivities() {
    try {
      const response = await fetch("/activities");
      const activities = await response.json();

      // Clear loading message
      activitiesList.innerHTML = "";

      // Populate activities list
      Object.entries(activities).forEach(([name, details]) => {
        const activityCard = createActivityCard(details);

        activitiesList.appendChild(activityCard);

        // Add option to select dropdown
        const option = document.createElement("option");
        option.value = name;
        option.textContent = name;
        activitySelect.appendChild(option);
      });
    } catch (error) {
      activitiesList.innerHTML = "<p>Failed to load activities. Please try again later.</p>";
      console.error("Error fetching activities:", error);
    }
  }

  // Function to create activity cards
  function createActivityCard(activity) {
    const card = document.createElement("div");
    card.className = "activity-card";

    const participantsList = activity.participants && activity.participants.length > 0
      ? `<div class="participants-list">${activity.participants.map(p => `<div class="participant-item"><span>${p}</span><button class="delete-btn" data-email="${p}" data-activity="${activity.name}" title="Remove participant">✕</button></div>`).join('')}</div>`
      : `<p class="no-participants">No participants yet. Be the first to sign up!</p>`;

    card.innerHTML = `
      <h4>${activity.name}</h4>
      <p><strong>Description:</strong> ${activity.description}</p>
      <p><strong>Schedule:</strong> ${activity.schedule}</p>
      <div class="participants">
        <h5>Participants</h5>
        ${participantsList}
      </div>
    `;

    // Add event listeners to delete buttons
    card.querySelectorAll(".delete-btn").forEach(btn => {
      btn.addEventListener("click", handleDeleteParticipant);
    });

    return card;
  }

  // Function to handle participant deletion
  async function handleDeleteParticipant(event) {
    event.preventDefault();
    const email = event.target.getAttribute("data-email");
    const activityName = event.target.getAttribute("data-activity");

    if (!confirm(`Are you sure you want to remove ${email} from ${activityName}?`)) {
      return;
    }

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activityName)}/unregister?email=${encodeURIComponent(email)}`,
        {
          method: "DELETE",
        }
      );

      if (response.ok) {
        messageDiv.textContent = `${email} has been removed from ${activityName}`;
        messageDiv.className = "success";
        messageDiv.classList.remove("hidden");

        // Refresh the activities list
        fetchActivities();

        // Hide message after 5 seconds
        setTimeout(() => {
          messageDiv.classList.add("hidden");
        }, 5000);
      } else {
        const result = await response.json();
        messageDiv.textContent = result.detail || "Failed to remove participant";
        messageDiv.className = "error";
        messageDiv.classList.remove("hidden");
      }
    } catch (error) {
      messageDiv.textContent = "Failed to remove participant. Please try again.";
      messageDiv.className = "error";
      messageDiv.classList.remove("hidden");
      console.error("Error removing participant:", error);
    }
  }

  // Handle form submission
  signupForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = document.getElementById("email").value;
    const activity = document.getElementById("activity").value;

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activity)}/signup?email=${encodeURIComponent(email)}`,
        {
          method: "POST",
        }
      );

      const result = await response.json();

      if (response.ok) {
        messageDiv.textContent = result.message;
        messageDiv.className = "success";
        signupForm.reset();
        
        // Refresh the activities list
        fetchActivities();
      } else {
        messageDiv.textContent = result.detail || "An error occurred";
        messageDiv.className = "error";
      }

      messageDiv.classList.remove("hidden");

      // Hide message after 5 seconds
      setTimeout(() => {
        messageDiv.classList.add("hidden");
      }, 5000);
    } catch (error) {
      messageDiv.textContent = "Failed to sign up. Please try again.";
      messageDiv.className = "error";
      messageDiv.classList.remove("hidden");
      console.error("Error signing up:", error);
    }
  });

  // Initialize app
  fetchActivities();
});
