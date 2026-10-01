const $ = (id) => document.getElementById(id);
let currentTicket = null;

async function api(path, options = {}) {
  const response = await fetch(path, {
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    ...options,
  });

  let data = null;
  const text = await response.text();
  if (text) {
    try { data = JSON.parse(text); } catch { data = text; }
  }

  if (!response.ok) {
    const detail = data?.detail || data || `HTTP ${response.status}`;
    throw new Error(detail);
  }
  return data;
}

function metric(label, value) {
  return `<div class="metric"><small>${label}</small><strong>${value ?? "—"}</strong></div>`;
}

function renderSnapshot(ticket) {
  $("ticketId").textContent = `Ticket #${ticket.id}`;
  $("snapshot").innerHTML = [
    metric("Status", ticket.status),
    metric("Category", ticket.category),
    metric("Urgency", ticket.urgency),
    metric("Priority", ticket.priority),
    metric("SLA", `${ticket.sla_hours}h`),
    metric("AI source", ticket.classification_source),
  ].join("");

  $("automation").textContent =
    `Automation: ${ticket.automation_status} • attempts: ${ticket.automation_attempts}`;
}

async function refreshTicket() {
  if (!currentTicket) return;
  currentTicket = await api(`/api/v1/tickets/${currentTicket.id}`);
  renderSnapshot(currentTicket);
}

$("sampleBtn").addEventListener("click", () => {
  $("customerName").value = "Sarah Miller";
  $("customerEmail").value = "sarah@example.com";
  $("subject").value = "Cannot access my account";
  $("message").value = "I reset my password but I still cannot sign in.";
});

$("seedBtn").addEventListener("click", async () => {
  const articles = [
    {
      title: "Account login troubleshooting",
      content: "For account login problems, use the password reset link and then retry sign in using a new browser session.",
      category: "account",
      source: "support-handbook",
    },
    {
      title: "Duplicate charge refund policy",
      content: "Duplicate billing charges should be reviewed by the billing team. Refund requests are handled according to the verified billing policy.",
      category: "billing",
      source: "billing-policy",
    },
  ];

  try {
    for (const article of articles) {
      await api("/api/v1/knowledge", {
        method: "POST",
        body: JSON.stringify(article),
      });
    }
    $("formStatus").textContent = "Demo knowledge added.";
  } catch (error) {
    $("formStatus").textContent = error.message;
  }
});

$("ticketForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  $("formStatus").textContent = "Creating...";

  try {
    currentTicket = await api("/api/v1/tickets", {
      method: "POST",
      body: JSON.stringify({
        customer_name: $("customerName").value,
        customer_email: $("customerEmail").value,
        subject: $("subject").value,
        message: $("message").value,
      }),
    });

    $("workspace").classList.remove("hidden");
    $("formStatus").textContent = "Ticket created.";
    renderSnapshot(currentTicket);
    await refreshAudit();
  } catch (error) {
    $("formStatus").textContent = error.message;
  }
});

$("knowledgeBtn").addEventListener("click", async () => {
  if (!currentTicket) return;
  $("knowledge").textContent = "Retrieving...";

  try {
    const result = await api(`/api/v1/tickets/${currentTicket.id}/knowledge`);
    if (!result.matches.length) {
      $("knowledge").textContent = "No verified knowledge matched this ticket.";
      return;
    }

    $("knowledge").innerHTML = result.matches.map((item) => `
      <div class="knowledge-item">
        <strong>${item.title}</strong>
        <p>${item.excerpt}</p>
        <p>source: ${item.source} • score: ${item.score}</p>
      </div>
    `).join("");
  } catch (error) {
    $("knowledge").textContent = error.message;
  }
});

$("draftBtn").addEventListener("click", async () => {
  if (!currentTicket) return;
  $("draftMeta").textContent = "Generating...";

  try {
    const result = await api(`/api/v1/tickets/${currentTicket.id}/draft`, {
      method: "POST",
    });

    $("draftText").value = result.reply;
    $("draftMeta").textContent =
      `source: ${result.source} • confidence: ${result.confidence} • human review: ${result.needs_human_review}`;
    await refreshTicket();
    await refreshAudit();
  } catch (error) {
    $("draftMeta").textContent = error.message;
  }
});

$("approveBtn").addEventListener("click", async () => {
  if (!currentTicket) return;
  $("reviewStatus").textContent = "Approving...";

  try {
    const payload = {
      reviewed_by: $("reviewer").value,
      note: $("reviewNote").value,
      approved_reply: $("draftText").value || null,
    };

    const result = await api(`/api/v1/tickets/${currentTicket.id}/approve`, {
      method: "POST",
      body: JSON.stringify(payload),
    });

    $("reviewStatus").textContent = `Approved by ${result.reviewed_by}.`;
    $("automation").textContent =
      `Automation: ${result.automation_status} • attempts: ${result.automation_attempts}`;
    await refreshTicket();
    await refreshAudit();
  } catch (error) {
    $("reviewStatus").textContent = error.message;
  }
});

$("rejectBtn").addEventListener("click", async () => {
  if (!currentTicket) return;
  $("reviewStatus").textContent = "Rejecting...";

  try {
    const result = await api(`/api/v1/tickets/${currentTicket.id}/reject`, {
      method: "POST",
      body: JSON.stringify({
        reviewed_by: $("reviewer").value,
        note: $("reviewNote").value,
      }),
    });

    $("reviewStatus").textContent = `Rejected by ${result.reviewed_by}.`;
    await refreshTicket();
    await refreshAudit();
  } catch (error) {
    $("reviewStatus").textContent = error.message;
  }
});

async function refreshAudit() {
  if (!currentTicket) return;

  try {
    const events = await api(`/api/v1/tickets/${currentTicket.id}/audit`);
    $("audit").innerHTML = events.length
      ? events.map((event) => `
          <div class="event">
            <strong>${event.event_type}</strong>
            <span>${event.actor} • ${new Date(event.created_at).toLocaleString()}</span>
          </div>
        `).join("")
      : `<span class="muted">No audit events yet.</span>`;
  } catch (error) {
    $("audit").innerHTML = `<span class="muted">${error.message}</span>`;
  }
}

$("refreshAuditBtn").addEventListener("click", refreshAudit);
