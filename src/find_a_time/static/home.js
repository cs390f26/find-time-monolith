async function loadEvents() {
    const eventList = document.getElementById("event-list");
    const pageMessage = document.getElementById("page-message");
  
    try {
      const response = await fetch("/api/events");
      const data = await response.json();
  
      if (!response.ok) {
        throw new Error(
          data.error?.message || "Could not load events."
        );
      }
  
      eventList.replaceChildren();
  
      if (data.events.length === 0) {
        pageMessage.textContent = "No events yet.";
        return;
      }
  
      pageMessage.textContent = "";
  
      for (const event of data.events) {
        const row = document.createElement("li");
        row.className = "event-row";
  
        const eventMain = document.createElement("div");
        eventMain.className = "event-main";
  
        const eventName = document.createElement("p");
        eventName.className = "event-name";
        eventName.textContent = event.event_name;
  
        const eventMeta = document.createElement("span");
        eventMeta.className = "event-meta";
  
        const responseWord =
          event.response_count === 1 ? "response" : "responses";
  
        eventMeta.textContent =
          `Created by ${event.creator_name} · ` +
          `${event.response_count} ${responseWord}`;
  
        eventMain.append(eventName, eventMeta);
  
        const actions = document.createElement("div");
        actions.className = "event-actions";
  
        const availabilityLink = document.createElement("a");
        availabilityLink.className = "btn btn-primary";
        availabilityLink.textContent = "Availability";
        availabilityLink.href =
          `/events/${event.event_id}/availability`;
  
        const resultsLink = document.createElement("a");
        resultsLink.className = "btn btn-primary";
        resultsLink.textContent = "Results";
        resultsLink.href =
          `/events/${event.event_id}/results`;
  
        actions.append(availabilityLink, resultsLink);
        row.append(eventMain, actions);
        eventList.append(row);
      }
    } catch (error) {
      pageMessage.textContent =
        "Unable to load events. Please try again.";
      console.error(error);
    }
  }
  
  loadEvents();