const eventName = document.getElementById("event-name");
const eventMeta = document.getElementById("event-meta");
const slotOptions = document.getElementById("slot-options");
const form = document.getElementById("availability-form");
const formMessage = document.getElementById("form-message");
const noneAvailable = document.getElementById("none-available");
const resultsLink = document.getElementById("results-link");


function getEventId() {
  const parts = window.location.pathname.split("/");
  return parts[2];
}


function formatTime(startTime) {
  const start = new Date(startTime);

  const end = new Date(
    start.getTime() + 60 * 60 * 1000
  );

  const dateText = start.toLocaleDateString(
    undefined,
    {
      weekday: "long",
      month: "short",
      day: "numeric",
    }
  );

  const startText = start.toLocaleTimeString(
    undefined,
    {
      hour: "numeric",
      minute: "2-digit",
    }
  );

  const endText = end.toLocaleTimeString(
    undefined,
    {
      hour: "numeric",
      minute: "2-digit",
    }
  );

  return `${dateText} · ${startText}–${endText}`;
}


async function loadEvent() {
  const eventId = getEventId();

  resultsLink.href =
    `/events/${eventId}/results`;

  try {
    const response =
      await fetch(`/api/events/${eventId}`);

    const data = await response.json();

    if (!response.ok) {
      throw new Error(
        data.error?.message || "Could not load event."
      );
    }

    eventName.textContent = data.event_name;
    eventMeta.textContent =
      `Created by ${data.creator_name}`;

    slotOptions.replaceChildren();

    for (const slot of data.time_slots) {
      const label =
        document.createElement("label");

      label.className = "check-option";

      const checkbox =
        document.createElement("input");

      checkbox.type = "checkbox";
      checkbox.name = "slot";
      checkbox.value = slot.slot_id;

      checkbox.addEventListener("change", () => {
        if (checkbox.checked) {
          noneAvailable.checked = false;
        }
      });

      const text =
        document.createElement("span");

      text.textContent =
        formatTime(slot.start_time);

      label.append(checkbox, text);
      slotOptions.append(label);
    }
  } catch (error) {
    eventName.textContent = "Unable to load event";
    formMessage.textContent = error.message;
    console.error(error);
  }
}


async function submitAvailability(event) {
  event.preventDefault();

  formMessage.textContent = "";

  const eventId = getEventId();

  const participantName =
    document.getElementById(
      "participant-name"
    ).value;

  const selectedSlotIds = [];

  if (!noneAvailable.checked) {
    const checkedSlots =
      document.querySelectorAll(
        'input[name="slot"]:checked'
      );

    for (const checkbox of checkedSlots) {
      selectedSlotIds.push(
        Number(checkbox.value)
      );
    }
  }

  const requestBody = {
    participant_name: participantName,
    selected_slot_ids: selectedSlotIds,
  };

  try {
    const response = await fetch(
      `/api/events/${eventId}/availability`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(requestBody),
      }
    );

    const data = await response.json();

    if (!response.ok) {
      throw new Error(
        data.error?.message ||
        "Could not submit availability."
      );
    }

    window.location.href =
      `/events/${eventId}/results`;
  } catch (error) {
    formMessage.textContent = error.message;
    console.error(error);
  }
}


noneAvailable.addEventListener(
  "change",
  () => {
    if (noneAvailable.checked) {
      const slotCheckboxes =
        document.querySelectorAll(
          'input[name="slot"]'
        );

      for (const checkbox of slotCheckboxes) {
        checkbox.checked = false;
      }
    }
  }
);


form.addEventListener(
  "submit",
  submitAvailability
);

loadEvent();