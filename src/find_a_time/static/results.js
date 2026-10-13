const eventName = document.getElementById("event-name");
const eventMeta = document.getElementById("event-meta");
const resultsList = document.getElementById("results-list");

const noneAvailableSection =
  document.getElementById("none-available-section");

const noneAvailableNames =
  document.getElementById("none-available-names");

const resultsMessage =
  document.getElementById("results-message");

const availabilityLink =
  document.getElementById("availability-link");


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


function responseText(count) {
  return count === 1
    ? "1 response"
    : `${count} responses`;
}


function availableText(count) {
  return count === 1
    ? "1 available"
    : `${count} available`;
}


function createResultRow(result, responseCount) {
  const row = document.createElement("li");

  const resultTop = document.createElement("div");
  resultTop.className = "result-top";

  const resultInfo = document.createElement("div");

  const resultLabel = document.createElement("span");
  resultLabel.className = "result-label";
  resultLabel.textContent =
    formatTime(result.start_time);

  const resultNames = document.createElement("span");
  resultNames.className = "result-names";

  if (result.participants.length > 0) {
    resultNames.textContent =
      result.participants.join(", ");
  } else {
    resultNames.textContent =
      "No participants available";
  }

  const resultCount = document.createElement("span");
  resultCount.className = "result-count";
  resultCount.textContent =
    availableText(result.available_count);

  resultInfo.append(resultLabel, resultNames);

  resultTop.append(
    resultInfo,
    resultCount
  );

  const resultBar = document.createElement("div");
  resultBar.className = "result-bar";
  resultBar.setAttribute("aria-hidden", "true");

  const resultBarFill =
    document.createElement("span");

  resultBarFill.className = "result-bar-fill";

  let percentage = 0;

  if (responseCount > 0) {
    percentage =
      (result.available_count / responseCount) * 100;
  }

  resultBarFill.style.width = `${percentage}%`;

  resultBar.append(resultBarFill);

  row.append(resultTop, resultBar);

  return row;
}


function showBestTimes(results) {
  if (results.length === 0) {
    resultsMessage.textContent =
      "No time slots are available.";
    return;
  }

  let highestCount = 0;

  for (const result of results) {
    if (result.available_count > highestCount) {
      highestCount = result.available_count;
    }
  }

  if (highestCount === 0) {
    resultsMessage.textContent =
      "No participants are available for any time yet.";
    return;
  }

  const bestTimes = [];

  for (const result of results) {
    if (result.available_count === highestCount) {
      bestTimes.push(
        formatTime(result.start_time)
      );
    }
  }

  if (bestTimes.length === 1) {
    resultsMessage.textContent =
      `${bestTimes[0]} currently has the most availability.`;
  } else {
    resultsMessage.textContent =
      `${bestTimes.join(" and ")} currently have the most availability.`;
  }
}


async function loadResults() {
  const eventId = getEventId();

  availabilityLink.href =
    `/events/${eventId}/availability`;

  try {
    const response =
      await fetch(`/api/events/${eventId}/results`);

    const data = await response.json();

    if (!response.ok) {
      throw new Error(
        data.error?.message ||
        "Could not load results."
      );
    }

    eventName.textContent = data.event_name;

    eventMeta.textContent =
      `Created by ${data.creator_name} · ` +
      responseText(data.response_count);

    resultsList.replaceChildren();

    for (const result of data.results) {
      const row = createResultRow(
        result,
        data.response_count
      );

      resultsList.append(row);
    }

    if (data.none_available.length > 0) {
      noneAvailableSection.hidden = false;

      noneAvailableNames.textContent =
        data.none_available.join(", ");
    } else {
      noneAvailableSection.hidden = true;
    }

    showBestTimes(data.results);
  } catch (error) {
    eventName.textContent =
      "Unable to load results";

    resultsMessage.textContent =
      error.message;

    console.error(error);
  }
}


loadResults();