const form = document.getElementById("create-event-form");
const timeInputs = document.getElementById("time-inputs");
const addTimeButton = document.getElementById("add-time");
const formMessage = document.getElementById("form-message");


function addTimeInput() {
  const currentInputs =
    document.querySelectorAll(".time-input");

  if (currentInputs.length >= 10) {
    formMessage.textContent =
      "An event can have at most 10 times.";
    return;
  }

  const field = document.createElement("div");
  field.className = "field field-with-action";

  const input = document.createElement("input");
  input.className = "time-input";
  input.type = "datetime-local";
  input.step = "3600";

  const removeButton = document.createElement("button");
  removeButton.className = "btn btn-primary btn-icon";
  removeButton.type = "button";
  removeButton.textContent = "−";
  removeButton.setAttribute("aria-label", "Remove time");

  removeButton.addEventListener("click", () => {
    field.remove();
    formMessage.textContent = "";
  });

  field.append(input, removeButton);
  timeInputs.append(field);

  formMessage.textContent = "";
}


async function createEvent(event) {
  event.preventDefault();

  formMessage.textContent = "";

  const eventName =
    document.getElementById("event-name").value;

  const creatorName =
    document.getElementById("creator-name").value;

  const inputs =
    document.querySelectorAll(".time-input");

  const timeSlots = [];

  for (const input of inputs) {
    if (input.value) {
      const date = new Date(input.value);
      timeSlots.push(date.toISOString());
    }
  }

  const requestBody = {
    event_name: eventName,
    creator_name: creatorName,
    time_slots: timeSlots,
  };

  try {
    const response = await fetch("/api/events", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(requestBody),
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(
        data.error?.message || "Could not create event."
      );
    }

    window.location.href =
      `/events/${data.event_id}/availability`;
  } catch (error) {
    formMessage.textContent = error.message;
    console.error(error);
  }
}


addTimeButton.addEventListener("click", addTimeInput);
form.addEventListener("submit", createEvent);