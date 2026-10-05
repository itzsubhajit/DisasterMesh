/* ============================================================
   DisasterMesh Dashboard — Complete Frontend JavaScript
   Steps 1-30
============================================================ */

/* =========================
   DEMO USERS
========================= */

const demoUsers = [
    {
        username: "operator",
        password: "operator123",
        name: "Rescue Operator",
        role: "OPERATOR"
    },
    {
        username: "admin",
        password: "admin123",
        name: "System Administrator",
        role: "ADMIN"
    }
];


/* =========================
   APPLICATION STATE
========================= */

let currentUser = null;
let selectedIncidentId = null;
let selectedNodeId = null;
let selectedMessageId = null;

let currentMapFilter = "ALL";

let map = null;
let nodeLayer = null;
let incidentLayer = null;

const nodeMarkers = {};
const incidentMarkers = {};

const currentFilters = {
    priority: "ALL",
    category: "ALL"
};

const nodeFilters = {
    search: "",
    status: "ALL",
    battery: "ALL"
};


/* =========================
   INCIDENT DATA
========================= */

const incidents = [

    {
        id: "INC-001",
        category: "Trapped Person",
        priority: "CRITICAL",
        message:
            "Person trapped inside building. Immediate rescue required.",
        node: "DM-001",
        location: "22.5726, 88.3639",
        latitude: 22.5726,
        longitude: 88.3639,
        status: "NEW",
        assignedTeam: "",
        confidence: 0.94,
        safetyRuleTriggered: true,
        reviewRequired: true,
        reviewed: false,
        time: "2 min ago"
    },

    {
        id: "INC-002",
        category: "Medical Emergency",
        priority: "CRITICAL",
        message:
            "Injured person requires immediate medical assistance.",
        node: "DM-003",
        location: "22.5734, 88.3652",
        latitude: 22.5734,
        longitude: 88.3652,
        status: "ACKNOWLEDGED",
        assignedTeam: "",
        confidence: 0.58,
        safetyRuleTriggered: false,
        reviewRequired: true,
        reviewed: true,
        time: "5 min ago"
    },

    {
        id: "INC-003",
        category: "Building Collapse",
        priority: "CRITICAL",
        message:
            "Collapsed structure reported near the field relay node.",
        node: "DM-004",
        location: "22.5718, 88.3627",
        latitude: 22.5718,
        longitude: 88.3627,
        status: "ASSIGNED",
        assignedTeam: "Rescue Team Alpha",
        confidence: 0.91,
        safetyRuleTriggered: true,
        reviewRequired: true,
        reviewed: true,
        time: "8 min ago"
    },

    {
        id: "INC-004",
        category: "Missing Person",
        priority: "HIGH",
        message:
            "Child reported missing after evacuation.",
        node: "DM-005",
        location: "22.5742, 88.3645",
        latitude: 22.5742,
        longitude: 88.3645,
        status: "IN_PROGRESS",
        assignedTeam: "Rescue Team Bravo",
        confidence: 0.87,
        safetyRuleTriggered: false,
        reviewRequired: false,
        reviewed: false,
        time: "11 min ago"
    },

    {
        id: "INC-005",
        category: "Rescue Required",
        priority: "HIGH",
        message:
            "Immediate rescue team assistance requested.",
        node: "DM-002",
        location: "22.5750, 88.3661",
        latitude: 22.5750,
        longitude: 88.3661,
        status: "NEW",
        assignedTeam: "",
        confidence: 0.82,
        safetyRuleTriggered: true,
        reviewRequired: false,
        reviewed: false,
        time: "14 min ago"
    }

];


/* =========================
   NODE DATA
========================= */

const nodes = [

    {
        id: "DM-001",
        status: "ONLINE",
        battery: 87,
        rssi: -61,
        gps: "22.5726, 88.3639",
        gpsValid: true,
        latitude: 22.5726,
        longitude: 88.3639,
        lastSeen: "10 sec ago"
    },

    {
        id: "DM-002",
        status: "ONLINE",
        battery: 74,
        rssi: -68,
        gps: "22.5731, 88.3650",
        gpsValid: true,
        latitude: 22.5731,
        longitude: 88.3650,
        lastSeen: "15 sec ago"
    },

    {
        id: "DM-003",
        status: "ONLINE",
        battery: 62,
        rssi: -72,
        gps: "22.5734, 88.3652",
        gpsValid: true,
        latitude: 22.5734,
        longitude: 88.3652,
        lastSeen: "21 sec ago"
    },

    {
        id: "DM-004",
        status: "ONLINE",
        battery: 91,
        rssi: -59,
        gps: "22.5718, 88.3627",
        gpsValid: true,
        latitude: 22.5718,
        longitude: 88.3627,
        lastSeen: "8 sec ago"
    },

    {
        id: "DM-005",
        status: "ONLINE",
        battery: 56,
        rssi: -76,
        gps: "22.5742, 88.3645",
        gpsValid: true,
        latitude: 22.5742,
        longitude: 88.3645,
        lastSeen: "28 sec ago"
    },

    {
        id: "DM-006",
        status: "OFFLINE",
        battery: 42,
        rssi: null,
        gps: "Unavailable",
        gpsValid: false,
        latitude: null,
        longitude: null,
        lastKnownLatitude: 22.5738,
        lastKnownLongitude: 88.3637,
        lastSeen: "2 min ago"
    }

];


/* =========================
   ROUTES
========================= */

const routes = [

    {
        source: "DM-001",
        destination: "GATEWAY",
        nextHop: "DM-002",
        hopCount: 3,
        quality: "Excellent",
        status: "ACTIVE"
    },

    {
        source: "DM-001",
        destination: "GATEWAY",
        nextHop: "DM-004",
        hopCount: 3,
        quality: "Good",
        status: "STANDBY"
    },

    {
        source: "DM-005",
        destination: "GATEWAY",
        nextHop: "DM-004",
        hopCount: 3,
        quality: "Good",
        status: "ACTIVE"
    },

    {
        source: "DM-006",
        destination: "GATEWAY",
        nextHop: "--",
        hopCount: 0,
        quality: "Unavailable",
        status: "STALE"
    }

];


/* =========================
   MESSAGE DATA
========================= */

const messages = [

    {
        id: "DM001-00017",
        sender: "DM-001",
        category: "Trapped Person",
        priority: "CRITICAL",
        hopCount: 3,
        ttl: 2,
        status: "DELIVERED",
        time: "2 min ago",
        content:
            "Person trapped inside building. Immediate rescue required.",
        routePath: [
            "DM-001",
            "DM-002",
            "DM-003",
            "GATEWAY"
        ],
        ack: true,
        integrity: "VALID",
        duplicate: false
    },

    {
        id: "DM003-00014",
        sender: "DM-003",
        category: "Medical Emergency",
        priority: "CRITICAL",
        hopCount: 2,
        ttl: 3,
        status: "DELIVERED",
        time: "5 min ago",
        content:
            "Injured person requires immediate medical assistance.",
        routePath: [
            "DM-003",
            "DM-004",
            "GATEWAY"
        ],
        ack: true,
        integrity: "VALID",
        duplicate: false
    },

    {
        id: "DM004-00011",
        sender: "DM-004",
        category: "Building Collapse",
        priority: "CRITICAL",
        hopCount: 2,
        ttl: 3,
        status: "FORWARDED",
        time: "8 min ago",
        content:
            "Collapsed structure reported near the field relay node.",
        routePath: [
            "DM-004",
            "DM-003",
            "GATEWAY"
        ],
        ack: false,
        integrity: "VALID",
        duplicate: false
    },

    {
        id: "DM005-00009",
        sender: "DM-005",
        category: "Missing Person",
        priority: "HIGH",
        hopCount: 3,
        ttl: 2,
        status: "DELIVERED",
        time: "11 min ago",
        content:
            "Child reported missing after evacuation.",
        routePath: [
            "DM-005",
            "DM-004",
            "DM-003",
            "GATEWAY"
        ],
        ack: true,
        integrity: "VALID",
        duplicate: false
    },

    {
        id: "DM002-00007",
        sender: "DM-002",
        category: "Rescue Required",
        priority: "HIGH",
        hopCount: 2,
        ttl: 3,
        status: "QUEUED",
        time: "14 min ago",
        content:
            "Immediate rescue team assistance requested.",
        routePath: [
            "DM-002",
            "QUEUE"
        ],
        ack: false,
        integrity: "VALID",
        duplicate: false
    },

    {
        id: "DM006-00003",
        sender: "DM-006",
        category: "General Information",
        priority: "LOW",
        hopCount: 0,
        ttl: 5,
        status: "FAILED",
        time: "18 min ago",
        content:
            "General information packet from an unavailable node.",
        routePath: [
            "DM-006",
            "NO ROUTE"
        ],
        ack: false,
        integrity: "VALID",
        duplicate: false
    }

];


/* =========================
   PACKET QUEUE
========================= */

const packetQueue = [

    {
        id: "DM002-00007",
        sender: "DM-002",
        priority: "HIGH",
        category: "Rescue Required",
        status: "QUEUED",
        retryCount: 1,
        maxRetries: 5,
        age: "14 min",
        reason:
            "Waiting for a usable forwarding route",
        nextRetry:
            "In 24 sec"
    },

    {
        id: "DM006-00003",
        sender: "DM-006",
        priority: "LOW",
        category: "General Information",
        status: "FAILED",
        retryCount: 3,
        maxRetries: 3,
        age: "18 min",
        reason:
            "Source node offline; retry limit reached",
        nextRetry:
            "Not scheduled"
    }

];


/* =========================
   SYSTEM HEALTH
========================= */

const systemHealth = [

    {
        service: "LoRa Mesh",
        state: "UP",
        description:
            "Field nodes are exchanging packets.",
        metricLabel: "Active routes",
        metricValue: "3"
    },

    {
        service: "Gateway",
        state: "UP",
        description:
            "LoRa-to-backend bridge is reachable.",
        metricLabel: "Last packet",
        metricValue: "8 sec ago"
    },

    {
        service: "Backend API",
        state: "UP",
        description:
            "REST API is accepting dashboard requests.",
        metricLabel: "Response",
        metricValue: "42 ms"
    },

    {
        service: "Database",
        state: "UP",
        description:
            "SQLite datastore is available.",
        metricLabel: "Records",
        metricValue: "184"
    },

    {
        service: "AI Classifier",
        state: "UP",
        description:
            "Emergency classification service is ready.",
        metricLabel: "Model",
        metricValue: "TF-IDF + LR"
    },

    {
        service: "GPS Services",
        state: "UP",
        description:
            "GPS coordinates are available on active nodes.",
        metricLabel: "Valid fixes",
        metricValue: "5 / 6"
    },

    {
        service: "Packet Queue",
        state: "WARNING",
        description:
            "One or more packets are waiting for delivery.",
        metricLabel: "Queued",
        metricValue: "1"
    },

    {
        service: "System Logging",
        state: "UP",
        description:
            "Security and network events are being recorded.",
        metricLabel: "Events",
        metricValue: "62"
    }

];


/* =========================
   GATEWAY STATE
========================= */

const gatewayState = {

    gateway: {
        state: "UP",
        lastPacket: "8 sec ago"
    },

    backend: {
        state: "UP",
        response: "42 ms"
    },

    database: {
        state: "UP",
        records: "184"
    },

    sync: {
        state: "PENDING",
        pending: 1
    }

};


/* =========================
   AUDIT LOGS
========================= */

const auditLogs = [

    {
        timestamp: "Just now",
        eventType: "AUTH",
        severity: "INFO",
        actor: "System Administrator",
        nodeId: "--",
        event: "Session active",
        description:
            "Administrator dashboard session is active."
    },

    {
        timestamp: "2 min ago",
        eventType: "INCIDENT",
        severity: "CRITICAL",
        actor: "Rescue Operator",
        nodeId: "DM-001",
        event: "Incident created",
        description:
            "Critical trapped-person request entered the response queue."
    },

    {
        timestamp: "3 min ago",
        eventType: "NODE",
        severity: "WARNING",
        actor: "SYSTEM",
        nodeId: "DM-006",
        event: "Node offline",
        description:
            "Heartbeat timeout detected for DM-006."
    },

    {
        timestamp: "5 min ago",
        eventType: "MESSAGE",
        severity: "INFO",
        actor: "SYSTEM",
        nodeId: "DM-003",
        event: "Message delivered",
        description:
            "Emergency packet delivered through the mesh to the gateway."
    },

    {
        timestamp: "8 min ago",
        eventType: "NETWORK",
        severity: "INFO",
        actor: "SYSTEM",
        nodeId: "DM-004",
        event: "Route selected",
        description:
            "Active forwarding path selected through DM-004."
    },

    {
        timestamp: "11 min ago",
        eventType: "INCIDENT",
        severity: "INFO",
        actor: "Rescue Operator",
        nodeId: "DM-005",
        event: "Incident assigned",
        description:
            "Missing-person incident assigned to Rescue Team Bravo."
    },

    {
        timestamp: "14 min ago",
        eventType: "MESSAGE",
        severity: "WARNING",
        actor: "SYSTEM",
        nodeId: "DM-002",
        event: "Packet queued",
        description:
            "Emergency message waiting for a usable forwarding route."
    },

    {
        timestamp: "18 min ago",
        eventType: "AUTH",
        severity: "INFO",
        actor: "System Administrator",
        nodeId: "--",
        event: "Administrator session",
        description:
            "Administrator dashboard session authenticated successfully."
    }

];

const logFilter = {
    eventType: "ALL",
    severity: "ALL"
};
/* ============================================================
   STEP 27 - ALERT CENTER
============================================================ */
const alerts = [
    { id: "ALT-001", title: "Node DM-006 Offline", severity: "CRITICAL", source: "DM-006", time: "3 min ago", status: "UNREAD", description: "Heartbeat timeout detected. Node is unavailable and has no active forwarding route." },
    { id: "ALT-002", title: "Packet Waiting for Route", severity: "WARNING", source: "DM-002", time: "14 min ago", status: "UNREAD", description: "Emergency packet remains in the store-and-forward queue until a usable route is available." },
    { id: "ALT-003", title: "Critical Incident Awaiting Review", severity: "CRITICAL", source: "INC-001", time: "2 min ago", status: "UNREAD", description: "Critical trapped-person incident requires mandatory human review before workflow advancement." },
    { id: "ALT-004", title: "Gateway Synchronization Pending", severity: "WARNING", source: "GATEWAY", time: "1 min ago", status: "READ", description: "One queued packet is waiting for successful backend synchronization." },
    { id: "ALT-005", title: "Emergency Packet Delivered", severity: "INFO", source: "DM-003", time: "5 min ago", status: "READ", description: "Critical medical emergency packet reached the gateway successfully." },
    { id: "ALT-006", title: "Alternate Route Available", severity: "INFO", source: "NETWORK", time: "8 min ago", status: "READ", description: "A standby path through DM-004 is available for route recovery." }
];

/* ============================================================
   STEP 28 - ANALYTICS & PERFORMANCE
============================================================ */
const analyticsMetrics = {
    deliveryRate: 94,
    latency: 42,
    routeRecovery: 2.8,
    duplicateRate: 1.7,
    aiAccuracy: 92,
    dashboardLatency: 580
};

/* ============================================================
   STEP 29 - USER MANAGEMENT
============================================================ */
const managedUsers = [
    { username: "operator", password: "operator123", name: "Rescue Operator", role: "OPERATOR", status: "ACTIVE", created: "Prototype setup" },
    { username: "admin", password: "admin123", name: "System Administrator", role: "ADMIN", status: "ACTIVE", created: "Prototype setup" }
];

/* ============================================================
   STEP 30 - SYSTEM READINESS
============================================================ */
const readinessChecks = [
    { id: "AUTH", title: "Dashboard authentication", description: "Login screen, session state and role-based access are available.", state: "PASS" },
    { id: "INCIDENTS", title: "Emergency incident workflow", description: "Incident review, acknowledgement, assignment and resolution workflow is available.", state: "PASS" },
    { id: "NODES", title: "Node monitoring", description: "Node health, battery, signal, GPS and registration controls are available.", state: "PASS" },
    { id: "MESH", title: "Mesh topology and routes", description: "Current and standby routes can be visualized and inspected.", state: "PASS" },
    { id: "MESSAGES", title: "Packet inspection", description: "Message payload, route path, ACK, integrity, duplicate and TTL states can be inspected.", state: "PASS" },
    { id: "QUEUE", title: "Store-and-forward queue", description: "Queued packets and retry handling are available.", state: "PASS" },
    { id: "GATEWAY", title: "Gateway operations", description: "Gateway, backend, database and synchronization states are represented.", state: "PASS" },
    { id: "LOGS", title: "Audit and security logging", description: "Operational and security events are recorded and filterable.", state: "PASS" },
    { id: "ALERTS", title: "Operational alert center", description: "Critical, warning and informational alerts can be reviewed.", state: "PASS" },
    { id: "ANALYTICS", title: "Performance analytics", description: "Network delivery, latency, route recovery, duplicate rate and AI metrics are available.", state: "PASS" },
    { id: "USERS", title: "Administrative user management", description: "Administrator can manage dashboard identities and role assignments.", state: "PASS" },
    { id: "BACKEND", title: "Backend integration", description: "REST API and database integration are pending the backend implementation phase.", state: "PENDING" },
    { id: "HARDWARE", title: "LoRa hardware integration", description: "Physical node and gateway integration are pending the hardware implementation phase.", state: "PENDING" }
];



/* =========================
   TOPOLOGY POSITIONS
========================= */

const topologyPositions = {

    "DM-001": {
        x: 12,
        y: 50
    },

    "DM-002": {
        x: 32,
        y: 28
    },

    "DM-003": {
        x: 55,
        y: 28
    },

    "DM-004": {
        x: 32,
        y: 72
    },

    "DM-005": {
        x: 55,
        y: 72
    },

    "DM-006": {
        x: 32,
        y: 92
    },

    GATEWAY: {
        x: 84,
        y: 50
    }

};


/* =========================
   VIEW INFORMATION
========================= */

const viewInformation = {

    dashboard: [
        "RESCUE OPERATIONS",
        "Command Dashboard",
        "Monitor incidents, field nodes and network activity."
    ],

    incidents: [
        "RESPONSE MANAGEMENT",
        "Incident Management",
        "Review and manage emergency requests."
    ],

    nodes: [
        "FIELD INFRASTRUCTURE",
        "Node Management",
        "Monitor registered field and relay nodes."
    ],

    network: [
        "MESH NETWORK",
        "Network Operations",
        "Monitor routes, connectivity and recovery activity."
    ],

    messages: [
        "MESSAGE TRAFFIC",
        "Message History",
        "Inspect delivery, routing and packet state."
    ],

    queue: [
        "STORE-AND-FORWARD",
        "Packet Queue",
        "Monitor queued messages, retries and synchronization state."
    ],

    gateway: [
        "EDGE CONNECTIVITY",
        "Gateway Operations",
        "Monitor the LoRa gateway, backend bridge and synchronization."
    ],

    logs: [
        "AUDIT & SECURITY",
        "Audit Logs",
        "Review authentication, node, message and network events."
    ],

    settings: [
        "SYSTEM CONFIGURATION",
        "Settings",
        "Dashboard and operator configuration."
    ]

};


/* =========================
   HELPERS
========================= */

const $ = id =>
    document.getElementById(id);


function setText(id, value) {

    const element = $(id);

    if (element) {
        element.textContent = value;
    }

}


function setVisible(id, value) {

    const element = $(id);

    if (element) {
        element.classList.toggle(
            "visible",
            value
        );
    }

}


function escapeHtml(value) {

    return String(value ?? "")
        .replaceAll(
            "&",
            "&amp;"
        )
        .replaceAll(
            "<",
            "&lt;"
        )
        .replaceAll(
            ">",
            "&gt;"
        )
        .replaceAll(
            '"',
            "&quot;"
        )
        .replaceAll(
            "'",
            "&#039;"
        );

}


function statusText(value) {

    return String(
        value || ""
    ).replaceAll(
        "_",
        " "
    );

}


function getPriorityClass(priority) {

    return {

        CRITICAL: "priority-critical",
        HIGH: "priority-high",
        MEDIUM: "priority-medium",
        LOW: "priority-low"

    }[priority] || "";

}


function getStatusClass(status) {

    return {

        NEW: "status-new",
        ACKNOWLEDGED: "status-acknowledged",
        ASSIGNED: "status-assigned",
        IN_PROGRESS: "status-in-progress",
        RESOLVED: "status-resolved",
        CANCELLED: "status-cancelled"

    }[status] || "";

}


function getNodeStatusClass(status) {

    return status === "ONLINE"
        ? "node-online"
        : "node-offline";

}


function getMessageStatusClass(status) {

    if (status === "DELIVERED") {
        return "message-delivered";
    }

    if (status === "QUEUED") {
        return "message-queued";
    }

    if (status === "FORWARDED") {
        return "message-forwarded";
    }

    return "message-failed";

}


function getNodeCondition(node) {

    if (node.status === "OFFLINE") {
        return "Offline — requires attention";
    }

    if (node.battery < 50) {
        return "Low battery — requires attention";
    }

    if (
        node.rssi !== null &&
        node.rssi <= -75
    ) {
        return "Weak signal — monitor connectivity";
    }

    return "Healthy";

}


function getSignalDescription(node) {

    if (node.rssi === null) {
        return "Unavailable";
    }

    if (node.rssi >= -65) {
        return "Excellent";
    }

    if (node.rssi >= -75) {
        return "Good";
    }

    return "Weak";

}


function showToast(
    message,
    type = "success"
) {

    const container =
        $("toastContainer");

    if (!container) {
        return;
    }

    const toast =
        document.createElement(
            "div"
        );

    toast.className =
        `toast toast-${type}`;

    toast.textContent =
        message;

    container.appendChild(
        toast
    );

    setTimeout(
        () => toast.remove(),
        3200
    );

}


/* =========================
   AUDIT LOGGING
========================= */

function addAuditLog(
    eventType,
    severity,
    actor,
    nodeId,
    event,
    description
) {

    auditLogs.unshift({

        timestamp: "Just now",

        eventType,

        severity,

        actor:
            actor ||
            currentUser?.name ||
            "SYSTEM",

        nodeId:
            nodeId ||
            "--",

        event,

        description

    });

    renderAuditLogs();

    updateLogSummary();

}


/* =========================
   AUTHENTICATION
========================= */

function saveSession(user) {

    sessionStorage.setItem(
        "disasterMeshSession",
        JSON.stringify(user)
    );

}


function getSavedSession() {

    try {

        return (
            JSON.parse(
                sessionStorage.getItem(
                    "disasterMeshSession"
                )
            ) || null
        );

    } catch {

        return null;

    }

}


function clearSession() {

    sessionStorage.removeItem(
        "disasterMeshSession"
    );

}


function authenticateUser(
    username,
    password
) {

    const user =
        demoUsers.find(
            item =>
                item.username === username &&
                item.password === password
        ) || null;

    if (!user) {
        return null;
    }

    const managed =
        typeof managedUsers !== "undefined"
            ? managedUsers.find(
                item =>
                    item.username === user.username
            )
            : null;

    if (
        managed &&
        managed.status !== "ACTIVE"
    ) {
        return null;
    }

    return user;

}


function applyRolePermissions() {

    document
        .querySelectorAll(
            ".admin-only"
        )
        .forEach(
            element =>
                element.classList.toggle(
                    "admin-visible",
                    !!currentUser &&
                    currentUser.role === "ADMIN"
                )
        );

    if (!currentUser) {
        return;
    }

    setText(
        "currentUserName",
        currentUser.name
    );

    setText(
        "currentUserRole",
        currentUser.role === "ADMIN"
            ? "Administrator"
            : "Rescue Operator"
    );

    setText(
        "settingsUserName",
        currentUser.name
    );

    setText(
        "settingsUserRole",
        currentUser.role === "ADMIN"
            ? "Administrator"
            : "Rescue Operator"
    );

}


function showApplication() {

    $("authScreen")?.classList.add(
        "hidden"
    );

    $("application")?.classList.add(
        "visible"
    );

    document.body.classList.add(
        "authenticated"
    );

    applyRolePermissions();

    if (map) {

        setTimeout(
            () =>
                map.invalidateSize(),
            50
        );

    }

}


function showAuthentication() {

    $("application")?.classList.remove(
        "visible"
    );

    $("authScreen")?.classList.remove(
        "hidden"
    );

    document.body.classList.remove(
        "authenticated"
    );

}


function setupAuthentication() {

    const form =
        $("loginForm");

    if (!form) {
        return;
    }

    const button =
        $("loginButton");

    const error =
        $("authError");

    form.addEventListener(
        "submit",
        event => {

            event.preventDefault();

            const username =
                $("username")
                    ?.value
                    .trim() || "";

            const password =
                $("password")
                    ?.value || "";

            if (error) {
                error.textContent =
                    "";
            }

            if (button) {

                button.disabled =
                    true;

                button.classList.add(
                    "loading"
                );

                button.textContent =
                    "Signing In...";

            }

            setTimeout(
                () => {

                    const user =
                        authenticateUser(
                            username,
                            password
                        );

                    if (!user) {

                        if (error) {

                            error.textContent =
                                "Invalid username or password.";

                        }

                        if (button) {

                            button.disabled =
                                false;

                            button.classList.remove(
                                "loading"
                            );

                            button.textContent =
                                "Sign In";

                        }

                        addAuditLog(
                            "AUTH",
                            "WARNING",
                            username ||
                                "Unknown user",
                            "--",
                            "Login failed",
                            "Failed dashboard authentication attempt."
                        );

                        showToast(
                            "Login failed.",
                            "error"
                        );

                        return;

                    }

                    currentUser = {

                        username:
                            user.username,

                        name:
                            user.name,

                        role:
                            user.role

                    };

                    saveSession(
                        currentUser
                    );

                    if (button) {

                        button.disabled =
                            false;

                        button.classList.remove(
                            "loading"
                        );

                        button.textContent =
                            "Sign In";

                    }

                    showApplication();

                    addAuditLog(
                        "AUTH",
                        "INFO",
                        user.name,
                        "--",
                        "Login successful",
                        `${user.name} authenticated as ${user.role}.`
                    );

                    showToast(
                        `Welcome, ${user.name}.`
                    );

                    form.reset();

                },
                350
            );

        }
    );

}


function logout() {

    if (currentUser) {

        addAuditLog(
            "AUTH",
            "INFO",
            currentUser.name,
            "--",
            "Logout",
            "Dashboard session ended by the active user."
        );

    }

    clearSession();

    currentUser = null;

    closeAllModals();

    showAuthentication();

    showToast(
        "Session ended."
    );

}


/* =========================
   NAVIGATION
========================= */

function switchView(
    viewName
) {

    const target =
        $(`view-${viewName}`);

    if (!target) {
        return;
    }

    document
        .querySelectorAll(
            ".page-view"
        )
        .forEach(
            view =>
                view.classList.remove(
                    "active-view"
                )
        );

    target.classList.add(
        "active-view"
    );

    document
        .querySelectorAll(
            ".nav-item"
        )
        .forEach(
            item =>
                item.classList.toggle(
                    "active",
                    item.dataset.view ===
                        viewName
                )
        );

    const info =
        viewInformation[
            viewName
        ];

    if (info) {

        setText(
            "pageEyebrow",
            info[0]
        );

        setText(
            "pageTitle",
            info[1]
        );

        setText(
            "pageDescription",
            info[2]
        );

    }

    if (
        viewName === "dashboard" &&
        map
    ) {

        setTimeout(
            () =>
                map.invalidateSize(),
            60
        );

    }

    if (
        viewName === "incidents"
    ) {
        renderIncidentManagement();
    }

    if (
        viewName === "nodes"
    ) {
        renderFullNodeTable();
    }

    if (
        viewName === "network"
    ) {
        renderNetworkView();
    }

    if (
        viewName === "messages"
    ) {
        renderFullMessageTable();
    }

    if (
        viewName === "queue"
    ) {
        renderPacketQueue();
    }

    if (
        viewName === "gateway"
    ) {
        renderGatewayView();
    }

    if (
        viewName === "logs"
    ) {
        renderAuditLogs();
    }

    if (
        viewName === "alerts"
    ) {
        renderAlertCenter();
    }

    if (
        viewName === "analytics"
    ) {
        renderAnalytics();
    }

    if (
        viewName === "users"
    ) {
        renderUserManagement();
    }

    if (
        viewName === "readiness"
    ) {
        renderSystemReadiness();
    }

}


function setupNavigation() {

    document
        .querySelectorAll(
            ".nav-item"
        )
        .forEach(
            item =>
                item.addEventListener(
                    "click",
                    event => {

                        event.preventDefault();

                        switchView(
                            item.dataset.view
                        );

                    }
                )
        );

}


/* =========================
   DASHBOARD STATISTICS
========================= */

function updateStatistics() {

    const active =
        nodes.filter(
            node =>
                node.status ===
                    "ONLINE"
        ).length;

    const offline =
        nodes.filter(
            node =>
                node.status ===
                    "OFFLINE"
        ).length;

    const critical =
        incidents.filter(
            incident =>
                incident.priority ===
                    "CRITICAL" &&
                ![
                    "RESOLVED",
                    "CANCELLED"
                ].includes(
                    incident.status
                )
        ).length;

    const high =
        incidents.filter(
            incident =>
                incident.priority ===
                    "HIGH" &&
                ![
                    "RESOLVED",
                    "CANCELLED"
                ].includes(
                    incident.status
                )
        ).length;

    setText(
        "activeNodes",
        String(active).padStart(
            2,
            "0"
        )
    );

    setText(
        "offlineNodes",
        String(offline).padStart(
            2,
            "0"
        )
    );

    setText(
        "criticalIncidents",
        String(
            critical
        ).padStart(
            2,
            "0"
        )
    );

    setText(
        "highPriority",
        String(
            high
        ).padStart(
            2,
            "0"
        )
    );

    setText(
        "totalMessages",
        String(
            messages.length
        ).padStart(
            2,
            "0"
        )
    );

}


/* =========================
   INCIDENT WORKFLOW
========================= */

function shouldRequireReview(
    incident
) {

    return (
        incident.priority ===
            "CRITICAL" ||
        incident.confidence <
            0.70 ||
        incident.reviewRequired
    );

}


function getNextStatus(
    status
) {

    return {

        NEW:
            "ACKNOWLEDGED",

        ACKNOWLEDGED:
            "ASSIGNED",

        ASSIGNED:
            "IN_PROGRESS",

        IN_PROGRESS:
            "RESOLVED"

    }[
        status
    ] || null;

}


function getStatusActionText(
    status
) {

    return {

        NEW:
            "Acknowledge Incident",

        ACKNOWLEDGED:
            "Assign Incident",

        ASSIGNED:
            "Start Response",

        IN_PROGRESS:
            "Resolve Incident"

    }[
        status
    ] || "No Further Action";

}


function updateWorkflow(
    status
) {

    const order = [

        "NEW",
        "ACKNOWLEDGED",
        "ASSIGNED",
        "IN_PROGRESS",
        "RESOLVED"

    ];

    const index =
        order.indexOf(
            status
        );

    document
        .querySelectorAll(
            ".workflow-step"
        )
        .forEach(
            (
                step,
                stepIndex
            ) => {

                step.classList.remove(
                    "completed",
                    "current",
                    "cancelled"
                );

                if (
                    status ===
                    "CANCELLED"
                ) {

                    step.classList.add(
                        "cancelled"
                    );

                    return;

                }

                if (
                    stepIndex <
                    index
                ) {

                    step.classList.add(
                        "completed"
                    );

                }

                if (
                    stepIndex ===
                    index
                ) {

                    step.classList.add(
                        status ===
                            "RESOLVED"
                            ? "completed"
                            : "current"
                    );

                }

            }
        );

    document
        .querySelectorAll(
            ".workflow-line"
        )
        .forEach(
            (
                line,
                lineIndex
            ) => {

                line.classList.toggle(
                    "completed",
                    index >
                        lineIndex
                );

            }
        );

}


function renderIncidents() {

    const container =
        $("incidentList");

    if (!container) {
        return;
    }

    const filtered =
        incidents.filter(
            incident => {

                const priorityMatch =
                    currentFilters.priority ===
                        "ALL" ||
                    incident.priority ===
                        currentFilters.priority;

                const categoryMatch =
                    currentFilters.category ===
                        "ALL" ||
                    incident.category ===
                        currentFilters.category;

                return (
                    priorityMatch &&
                    categoryMatch
                );

            }
        );

    setText(
        "incidentCount",
        String(
            filtered.length
        ).padStart(
            2,
            "0"
        )
    );

    container.innerHTML =
        "";

    if (!filtered.length) {

        container.innerHTML =
            `<div class="no-incidents">
                No incidents match the selected filters.
            </div>`;

        return;

    }

    filtered.forEach(
        incident => {

            const item =
                document.createElement(
                    "div"
                );

            item.className =
                "incident-item";

            item.innerHTML = `

                <div class="incident-top">

                    <span class="priority-badge ${getPriorityClass(
                        incident.priority
                    )}">
                        ${escapeHtml(
                            incident.priority
                        )}
                    </span>

                    <span class="incident-time">
                        ${escapeHtml(
                            incident.time
                        )}
                    </span>

                </div>

                <div class="incident-title">
                    ${escapeHtml(
                        incident.category
                    )}
                </div>

                <div class="incident-message">
                    ${escapeHtml(
                        incident.message
                    )}
                </div>

                <div class="incident-meta">

                    <span>
                        ID:
                        ${escapeHtml(
                            incident.id
                        )}
                    </span>

                    <span>
                        Node:
                        ${escapeHtml(
                            incident.node
                        )}
                    </span>

                    <span>
                        Team:
                        ${escapeHtml(
                            incident.assignedTeam ||
                            "Unassigned"
                        )}
                    </span>

                </div>

                <div class="incident-status ${getStatusClass(
                    incident.status
                )}">
                    ${escapeHtml(
                        statusText(
                            incident.status
                        )
                    )}
                </div>

            `;

            item.addEventListener(
                "click",
                () =>
                    openIncidentModal(
                        incident.id
                    )
            );

            container.appendChild(
                item
            );

        }
    );

}


function renderIncidentManagement() {

    const container =
        $("incidentManagementList");

    if (!container) {
        return;
    }

    container.innerHTML =
        "";

    incidents.forEach(
        incident => {

            const item =
                document.createElement(
                    "div"
                );

            item.className =
                "incident-item";

            item.innerHTML = `

                <div class="incident-top">

                    <span class="priority-badge ${getPriorityClass(
                        incident.priority
                    )}">
                        ${escapeHtml(
                            incident.priority
                        )}
                    </span>

                    <span class="incident-time">
                        ${escapeHtml(
                            incident.time
                        )}
                    </span>

                </div>

                <div class="incident-title">
                    ${escapeHtml(
                        incident.category
                    )}
                </div>

                <div class="incident-message">
                    ${escapeHtml(
                        incident.message
                    )}
                </div>

                <div class="incident-meta">

                    <span>
                        ID:
                        ${escapeHtml(
                            incident.id
                        )}
                    </span>

                    <span>
                        Node:
                        ${escapeHtml(
                            incident.node
                        )}
                    </span>

                    <span>
                        Team:
                        ${escapeHtml(
                            incident.assignedTeam ||
                            "Unassigned"
                        )}
                    </span>

                </div>

                <div class="incident-status ${getStatusClass(
                    incident.status
                )}">
                    ${escapeHtml(
                        statusText(
                            incident.status
                        )
                    )}
                </div>

            `;

            item.addEventListener(
                "click",
                () =>
                    openIncidentModal(
                        incident.id
                    )
            );

            container.appendChild(
                item
            );

        }
    );

}


function openIncidentModal(
    incidentId
) {

    const incident =
        incidents.find(
            item =>
                item.id ===
                    incidentId
        );

    if (!incident) {
        return;
    }

    selectedIncidentId =
        incidentId;

    incident.reviewRequired =
        shouldRequireReview(
            incident
        );

    setText(
        "modalIncidentCategory",
        incident.category
    );

    const priority =
        $("modalPriority");

    if (priority) {

        priority.textContent =
            incident.priority;

        priority.className =
            `priority-badge ${getPriorityClass(
                incident.priority
            )}`;

    }

    const status =
        $("modalStatus");

    if (status) {

        status.textContent =
            statusText(
                incident.status
            );

        status.className =
            `incident-status ${getStatusClass(
                incident.status
            )}`;

    }

    setText(
        "modalMessage",
        incident.message
    );

    setText(
        "modalClassification",
        incident.category
    );

    setText(
        "modalConfidence",
        `${Math.round(
            incident.confidence *
                100
        )}%`
    );

    setText(
        "modalSafetyRule",
        incident.safetyRuleTriggered
            ? "Triggered"
            : "Not Triggered"
    );

    setText(
        "modalReviewState",
        incident.reviewed
            ? "Completed"
            : "Required"
    );

    setText(
        "modalId",
        incident.id
    );

    setText(
        "modalNode",
        incident.node
    );

    setText(
        "modalLocation",
        incident.location
    );

    setText(
        "modalTime",
        incident.time
    );

    const assignedTeam =
        $("assignedTeam");

    if (assignedTeam) {

        assignedTeam.value =
            incident.assignedTeam ||
            "Rescue Team Alpha";

    }

    const reviewWarning =
        $("reviewWarning");

    const reviewText =
        $("reviewWarningText");

    const reviewButton =
        $("reviewButton");

    const needsReview =
        incident.reviewRequired &&
        !incident.reviewed;

    if (reviewWarning) {

        reviewWarning.classList.add(
            "visible"
        );

    }

    if (reviewText) {

        reviewText.textContent =
            needsReview
                ? incident.confidence <
                  0.70

                    ? "AI confidence is below the review threshold. Human verification is required before status advancement."

                    : "Critical-priority incidents require operator verification before status advancement."

                : "Operator review has been completed. Status advancement is enabled.";

    }

    if (reviewButton) {

        reviewButton.textContent =
            incident.reviewed
                ? "Review Completed"
                : "Mark as Reviewed";

        reviewButton.classList.toggle(
            "reviewed",
            incident.reviewed
        );

        reviewButton.disabled =
            incident.reviewed;

    }

    updateWorkflow(
        incident.status
    );

    setText(
        "statusActionButton",
        getStatusActionText(
            incident.status
        )
    );

    const actionButton =
        $("statusActionButton");

    if (actionButton) {

        actionButton.disabled =
            !getNextStatus(
                incident.status
            );

    }

    setVisible(
        "incidentModal",
        true
    );

    document.body.classList.add(
        "modal-open"
    );

}


function closeIncidentModal() {

    setVisible(
        "incidentModal",
        false
    );

    selectedIncidentId =
        null;

    if (
        !document.querySelector(
            ".modal-overlay.visible"
        )
    ) {

        document.body.classList.remove(
            "modal-open"
        );

    }

}


function reviewSelectedIncident() {

    const incident =
        incidents.find(
            item =>
                item.id ===
                    selectedIncidentId
        );

    if (
        !incident ||
        incident.reviewed
    ) {

        return;

    }

    incident.reviewed =
        true;

    addAuditLog(
        "INCIDENT",
        "INFO",
        currentUser?.name,
        incident.node,
        "Human review completed",
        `${incident.id} was manually reviewed before status advancement.`
    );

    renderIncidents();

    renderIncidentManagement();

    updateStatistics();

    openIncidentModal(
        incident.id
    );

    showToast(
        `Operator review completed for ${incident.id}.`
    );

}


function advanceIncidentStatus() {

    const incident =
        incidents.find(
            item =>
                item.id ===
                    selectedIncidentId
        );

    if (!incident) {
        return;
    }

    if (
        shouldRequireReview(
            incident
        ) &&
        !incident.reviewed
    ) {

        showToast(
            "Operator review is required before advancing this incident.",
            "warning"
        );

        return;

    }

    const next =
        getNextStatus(
            incident.status
        );

    if (!next) {
        return;
    }

    if (next === "ASSIGNED") {

        incident.assignedTeam =
            $("assignedTeam")
                ?.value ||
            incident.assignedTeam ||
            "Rescue Team Alpha";

    }

    incident.status =
        next;

    if (
        next === "RESOLVED"
    ) {

        incident.resolvedAt =
            new Date().toISOString();

    }

    addAuditLog(
        "INCIDENT",
        "INFO",
        currentUser?.name,
        incident.node,
        `Status changed to ${next}`,
        `${incident.id} moved to ${statusText(
            next
        )}.`
    );

    renderIncidents();

    renderIncidentManagement();

    updateStatistics();

    openIncidentModal(
        incident.id
    );

    showToast(
        `${incident.id} moved to ${statusText(
            next
        )}.`
    );

}


function cancelIncident() {

    const incident =
        incidents.find(
            item =>
                item.id ===
                    selectedIncidentId
        );

    if (!incident) {
        return;
    }

    incident.status =
        "CANCELLED";

    addAuditLog(
        "INCIDENT",
        "WARNING",
        currentUser?.name,
        incident.node,
        "Incident cancelled",
        `${incident.id} was cancelled from the operator dashboard.`
    );

    renderIncidents();

    renderIncidentManagement();

    updateStatistics();

    openIncidentModal(
        incident.id
    );

    showToast(
        `${incident.id} cancelled.`,
        "warning"
    );

}


function setupIncidentFilters() {

    const priority =
        $("priorityFilter");

    const category =
        $("categoryFilter");

    priority?.addEventListener(
        "change",
        () => {

            currentFilters.priority =
                priority.value;

            renderIncidents();

        }
    );

    category?.addEventListener(
        "change",
        () => {

            currentFilters.category =
                category.value;

            renderIncidents();

        }
    );

    $("resetFilters")
        ?.addEventListener(
            "click",
            () => {

                currentFilters.priority =
                    "ALL";

                currentFilters.category =
                    "ALL";

                if (priority) {
                    priority.value =
                        "ALL";
                }

                if (category) {
                    category.value =
                        "ALL";
                }

                renderIncidents();

            }
        );

}


function setupIncidentModal() {

    const modal =
        $("incidentModal");

    $("closeModal")
        ?.addEventListener(
            "click",
            closeIncidentModal
        );

    $("modalCloseButton")
        ?.addEventListener(
            "click",
            closeIncidentModal
        );

    $("reviewButton")
        ?.addEventListener(
            "click",
            reviewSelectedIncident
        );

    $("statusActionButton")
        ?.addEventListener(
            "click",
            advanceIncidentStatus
        );

    $("cancelIncidentButton")
        ?.addEventListener(
            "click",
            cancelIncident
        );

    $("assignedTeam")
        ?.addEventListener(
            "change",
            event => {

                const incident =
                    incidents.find(
                        item =>
                            item.id ===
                                selectedIncidentId
                    );

                if (incident) {

                    incident.assignedTeam =
                        event.target.value;

                    addAuditLog(
                        "INCIDENT",
                        "INFO",
                        currentUser?.name,
                        incident.node,
                        "Team assignment updated",
                        `${incident.id} team changed to ${incident.assignedTeam}.`
                    );

                    renderIncidentManagement();

                }

            }
        );

    modal?.addEventListener(
        "click",
        event => {

            if (
                event.target ===
                modal
            ) {

                closeIncidentModal();

            }

        }
    );

}


/* =========================
   LEAFLET MAP
========================= */

function initializeMap() {

    if (
        typeof L ===
        "undefined"
    ) {

        return;

    }

    if (map) {
        return;
    }

    if (!$("map")) {
        return;
    }

    map =
        L.map(
            "map"
        ).setView(
            [
                22.5735,
                88.3645
            ],
            16
        );

    L.tileLayer(
        "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
        {
            maxZoom: 19,
            attribution:
                "&copy; OpenStreetMap contributors"
        }
    ).addTo(
        map
    );

    nodeLayer =
        L.layerGroup().addTo(
            map
        );

    incidentLayer =
        L.layerGroup().addTo(
            map
        );

    nodes.forEach(
        addNodeMarker
    );

    incidents.forEach(
        addIncidentMarker
    );

    setMapFilter(
        currentMapFilter
    );

    fitAllMapObjects();

}


function getNodeMapCoordinates(
    node
) {

    if (
        Number.isFinite(
            node.latitude
        ) &&
        Number.isFinite(
            node.longitude
        )
    ) {

        return {
            latitude:
                node.latitude,
            longitude:
                node.longitude,
            lastKnown:
                !node.gpsValid
        };

    }

    if (
        Number.isFinite(
            node.lastKnownLatitude
        ) &&
        Number.isFinite(
            node.lastKnownLongitude
        )
    ) {

        return {
            latitude:
                node.lastKnownLatitude,
            longitude:
                node.lastKnownLongitude,
            lastKnown:
                true
        };

    }

    return null;

}


function addNodeMarker(
    node
) {

    if (!map) {
        return;
    }

    nodeMarkers[
        node.id
    ]?.remove();

    const coordinates =
        getNodeMapCoordinates(
            node
        );

    if (!coordinates) {
        return;
    }

    const online =
        node.status ===
        "ONLINE";

    const marker =
        L.circleMarker(
            [
                coordinates.latitude,
                coordinates.longitude
            ],
            {
                radius:
                    online
                        ? 8
                        : 9,

                color:
                    online
                        ? "#16a34a"
                        : "#dc2626",

                fillColor:
                    online
                        ? "#16a34a"
                        : "#dc2626",

                fillOpacity:
                    online
                        ? 0.9
                        : 0.95,

                weight:
                    2
            }
        );

    marker.bindPopup(
        `
            <strong>
                ${escapeHtml(
                    node.id
                )}
            </strong>

            <br>

            Status:
            ${escapeHtml(
                node.status
            )}

            <br>

            Battery:
            ${escapeHtml(
                node.battery
            )}%

            <br>

            RSSI:
            ${
                node.rssi === null
                    ? "Unavailable"
                    : `${escapeHtml(
                        node.rssi
                    )} dBm`
            }

            <br>

            GPS:
            ${
                node.gpsValid
                    ? escapeHtml(
                        node.gps
                    )
                    : "Unavailable — last known position shown"
            }
        `
    );

    marker.on(
        "click",
        () =>
            openNodeDetailsModal(
                node.id
            )
    );

    marker.addTo(
        nodeLayer
    );

    nodeMarkers[
        node.id
    ] = marker;

}

function addIncidentMarker(
    incident
) {

    if (!map) {
        return;
    }

    incidentMarkers[
        incident.id
    ]?.remove();

    const marker =
        L.circleMarker(
            [
                incident.latitude,
                incident.longitude
            ],
            {
                radius: 10,
                color:
                    "#dc2626",
                fillColor:
                    "#dc2626",
                fillOpacity:
                    0.82,
                weight: 3
            }
        );

    marker.bindPopup(
        `
            <strong>
                ${escapeHtml(
                    incident.category
                )}
            </strong>

            <br>

            Priority:
            ${escapeHtml(
                incident.priority
            )}

            <br>

            Confidence:
            ${Math.round(
                incident.confidence *
                    100
            )}%

            <br>

            Node:
            ${escapeHtml(
                incident.node
            )}
        `
    );

    marker.on(
        "click",
        () =>
            openIncidentModal(
                incident.id
            )
    );

    marker.addTo(
        incidentLayer
    );

    incidentMarkers[
        incident.id
    ] = marker;

}


function setMapFilter(
    filter
) {

    currentMapFilter =
        filter;

    document
        .querySelectorAll(
            ".map-control"
        )
        .forEach(
            button =>
                button.classList.toggle(
                    "active",
                    button.dataset.mapFilter ===
                        filter
                )
        );

    if (!map) {
        return;
    }

    if (
        filter ===
        "ALL"
    ) {

        nodeLayer.addTo(
            map
        );

        incidentLayer.addTo(
            map
        );

        return;

    }

    if (
        filter ===
        "NODES"
    ) {

        map.removeLayer(
            incidentLayer
        );

        nodeLayer.addTo(
            map
        );

        return;

    }

    map.removeLayer(
        nodeLayer
    );

    incidentLayer.addTo(
        map
    );

}


function setupMap() {

    document
        .querySelectorAll(
            ".map-control"
        )
        .forEach(
            button =>
                button.addEventListener(
                    "click",
                    () =>
                        setMapFilter(
                            button.dataset.mapFilter
                        )
                )
        );

    $("viewFullMapButton")
        ?.addEventListener(
            "click",
            () => {

                if (!map) {
                    return;
                }

                map.invalidateSize();

                fitAllMapObjects();

            }
        );

}


function fitAllMapObjects() {

    if (!map) {
        return;
    }

    const points = [];

    nodes.forEach(
        node => {

            const coordinates =
                getNodeMapCoordinates(
                    node
                );

            if (coordinates) {

                points.push(
                    [
                        coordinates.latitude,
                        coordinates.longitude
                    ]
                );

            }

        }
    );

    incidents.forEach(
        incident => {

            if (
                Number.isFinite(
                    incident.latitude
                ) &&
                Number.isFinite(
                    incident.longitude
                )
            ) {

                points.push(
                    [
                        incident.latitude,
                        incident.longitude
                    ]
                );

            }

        }
    );

    if (!points.length) {
        return;
    }

    map.fitBounds(
        points,
        {
            padding: [
                30,
                30
            ]
        }
    );

}

function focusMapOnNode(
    node
) {

    if (
        !map ||
        !node
    ) {
        return;
    }

    const coordinates =
        getNodeMapCoordinates(
            node
        );

    if (!coordinates) {

        showToast(
            "No known location is available for this node.",
            "error"
        );

        return;

    }

    switchView(
        "dashboard"
    );

    setTimeout(
        () => {

            map.invalidateSize();

            map.setView(
                [
                    coordinates.latitude,
                    coordinates.longitude
                ],
                18,
                {
                    animate: true
                }
            );

            nodeMarkers[
                node.id
            ]?.openPopup();

        },
        80
    );

}

function focusMapOnIncident(
    incident
) {

    if (!map) {
        return;
    }

    switchView(
        "dashboard"
    );

    setTimeout(
        () => {

            map.invalidateSize();

            map.setView(
                [
                    incident.latitude,
                    incident.longitude
                ],
                18,
                {
                    animate: true
                }
            );

            incidentMarkers[
                incident.id
            ]?.openPopup();

        },
        80
    );

}


/* =========================
   NODE TABLES
========================= */

function renderNodeRows(
    targetId
) {

    const body =
        $(targetId);

    if (!body) {
        return;
    }

    let list =
        nodes;

    if (
        targetId ===
        "fullNodeTableBody"
    ) {

        list =
            nodes.filter(
                node => {

                    const search =
                        nodeFilters.search
                            .trim()
                            .toLowerCase();

                    const searchMatch =
                        !search ||
                        node.id
                            .toLowerCase()
                            .includes(
                                search
                            ) ||
                        node.gps
                            .toLowerCase()
                            .includes(
                                search
                            );

                    const statusMatch =
                        nodeFilters.status ===
                            "ALL" ||
                        node.status ===
                            nodeFilters.status;

                    const batteryMatch =
                        nodeFilters.battery ===
                            "ALL" ||
                        (
                            nodeFilters.battery ===
                                "LOW"
                                ? node.battery <
                                    50
                                : node.battery >=
                                    50
                        );

                    return (
                        searchMatch &&
                        statusMatch &&
                        batteryMatch
                    );

                }
            );

    }

    body.innerHTML =
        "";

    if (!list.length) {

        body.innerHTML =
            `
                <tr>
                    <td colspan="6">
                        <div class="no-incidents">
                            No nodes match the selected filters.
                        </div>
                    </td>
                </tr>
            `;

        return;

    }

    list.forEach(
        node => {

            const row =
                document.createElement(
                    "tr"
                );

            const gpsDisplay =
                node.gpsValid
                    ? "Available"
                    : "Unavailable";

            const gpsClass =
                node.gpsValid
                    ? "gps-valid"
                    : "gps-unavailable";

            const rssi =
                node.rssi === null
                    ? "--"
                    : `${node.rssi} dBm`;

            row.innerHTML =
                `

                    <td>
                        <span class="node-id">
                            ${escapeHtml(
                                node.id
                            )}
                        </span>
                    </td>

                    <td>
                        <span class="node-status ${getNodeStatusClass(
                            node.status
                        )}">
                            <span class="node-status-dot"></span>
                            ${escapeHtml(
                                node.status
                            )}
                        </span>
                    </td>

                    <td>

                        <div class="battery-wrapper">

                            <div class="battery-bar">

                                <div
                                    class="battery-level ${
                                        node.battery <
                                        50
                                            ? "battery-low"
                                            : ""
                                    }"
                                    style="
                                        width:
                                            ${Math.max(
                                                0,
                                                Math.min(
                                                    100,
                                                    node.battery
                                                )
                                            )}%
                                    "
                                ></div>

                            </div>

                            <span>
                                ${escapeHtml(
                                    node.battery
                                )}%
                            </span>

                        </div>

                    </td>

                    <td>

                        <span class="rssi-value">
                            ${escapeHtml(
                                rssi
                            )}
                        </span>

                    </td>

                    <td>

                        <span class="${gpsClass}">
                            ${gpsDisplay}
                        </span>

                    </td>

                    <td>

                        <span class="last-seen">
                            ${escapeHtml(
                                node.lastSeen
                            )}
                        </span>

                    </td>

                `;

            row.addEventListener(
                "click",
                () =>
                    openNodeDetailsModal(
                        node.id
                    )
            );

            body.appendChild(
                row
            );

        }
    );

}


function renderNodes() {

    renderNodeRows(
        "nodeTableBody"
    );

}


function renderFullNodeTable() {

    renderNodeRows(
        "fullNodeTableBody"
    );

}


function setupNodeFilters() {

    const searchInput =
        $("nodeSearchInput");

    const statusFilter =
        $("nodeStatusFilter");

    const batteryFilter =
        $("nodeBatteryFilter");

    const refresh =
        () => {

            nodeFilters.search =
                searchInput
                    ?.value ||
                "";

            nodeFilters.status =
                statusFilter
                    ?.value ||
                "ALL";

            nodeFilters.battery =
                batteryFilter
                    ?.value ||
                "ALL";

            renderFullNodeTable();

        };

    searchInput?.addEventListener(
        "input",
        refresh
    );

    statusFilter?.addEventListener(
        "change",
        refresh
    );

    batteryFilter?.addEventListener(
        "change",
        refresh
    );

    $("resetNodeFilters")
        ?.addEventListener(
            "click",
            () => {

                if (searchInput) {
                    searchInput.value =
                        "";
                }

                if (statusFilter) {
                    statusFilter.value =
                        "ALL";
                }

                if (batteryFilter) {
                    batteryFilter.value =
                        "ALL";
                }

                nodeFilters.search =
                    "";

                nodeFilters.status =
                    "ALL";

                nodeFilters.battery =
                    "ALL";

                renderFullNodeTable();

            }
        );

}


/* =========================
   NODE DETAILS
========================= */

function getNodeRelatedRoutes(
    nodeId
) {

    return routes.filter(
        route =>
            route.source ===
                nodeId ||
            route.nextHop ===
                nodeId
    );

}


function getNodeRelatedIncidents(
    nodeId
) {

    return incidents.filter(
        incident =>
            incident.node ===
                nodeId
    );

}


function renderNodeRelatedRoutes(
    node
) {

    const container =
        $("nodeModalRoutes");

    if (!container) {
        return;
    }

    const related =
        getNodeRelatedRoutes(
            node.id
        );

    container.innerHTML =
        "";

    if (!related.length) {

        container.innerHTML =
            `
                <div class="related-empty">
                    No route records are associated with this node.
                </div>
            `;

        return;

    }

    related.forEach(
        route => {

            const item =
                document.createElement(
                    "div"
                );

            item.className =
                "related-item";

            const routeClass =
                route.status ===
                    "ACTIVE"
                    ? "route-active"
                    : route.status ===
                        "STANDBY"
                        ? "route-standby"
                        : "route-stale";

            item.innerHTML =
                `

                    <div class="related-item-main">

                        <strong>
                            ${escapeHtml(
                                route.source
                            )}
                            →
                            ${escapeHtml(
                                route.destination
                            )}
                        </strong>

                        <span>
                            Next hop:
                            ${escapeHtml(
                                route.nextHop
                            )}
                            ·
                            ${route.hopCount}
                            hops
                            ·
                            ${escapeHtml(
                                route.quality
                            )}
                        </span>

                    </div>

                    <span class="route-status ${routeClass}">
                        ${escapeHtml(
                            route.status
                        )}
                    </span>

                `;

            container.appendChild(
                item
            );

        }
    );

}


function renderNodeRelatedIncidents(
    node
) {

    const container =
        $("nodeModalIncidents");

    if (!container) {
        return;
    }

    const related =
        getNodeRelatedIncidents(
            node.id
        );

    container.innerHTML =
        "";

    if (!related.length) {

        container.innerHTML =
            `
                <div class="related-empty">
                    No incidents are currently linked to this node.
                </div>
            `;

        return;

    }

    related.forEach(
        incident => {

            const item =
                document.createElement(
                    "div"
                );

            item.className =
                "related-item";

            item.innerHTML =
                `

                    <div class="related-item-main">

                        <strong>
                            ${escapeHtml(
                                incident.id
                            )}
                            —
                            ${escapeHtml(
                                incident.category
                            )}
                        </strong>

                        <span>
                            ${escapeHtml(
                                incident.priority
                            )}
                            ·
                            ${escapeHtml(
                                statusText(
                                    incident.status
                                )
                            )}
                        </span>

                    </div>

                    <button
                        class="related-item-action"
                        type="button"
                    >
                        Open
                    </button>

                `;

            item
                .querySelector(
                    "button"
                )
                ?.addEventListener(
                    "click",
                    event => {

                        event.stopPropagation();

                        closeNodeDetailsModal();

                        openIncidentModal(
                            incident.id
                        );

                    }
                );

            container.appendChild(
                item
            );

        }
    );

}


function openNodeDetailsModal(
    nodeId
) {

    const node =
        nodes.find(
            item =>
                item.id ===
                    nodeId
        );

    if (!node) {
        return;
    }

    selectedNodeId =
        node.id;

    const status =
        $("nodeModalStatus");

    if (status) {

        status.className =
            `node-status ${getNodeStatusClass(
                node.status
            )}`;

        status.innerHTML =
            `
                <span class="node-status-dot"></span>
                ${escapeHtml(
                    node.status
                )}
            `;

    }

    setText(
        "nodeModalTitle",
        node.id
    );

    setText(
        "nodeModalId",
        node.id
    );

    setText(
        "nodeModalBattery",
        `${node.battery}%`
    );

    setText(
        "nodeModalSignal",
        node.rssi === null
            ? "Unavailable"
            : `${node.rssi} dBm (${getSignalDescription(
                node
            )})`
    );

    setText(
        "nodeModalGpsStatus",
        node.gpsValid
            ? "Available"
            : "Unavailable"
    );

    setText(
        "nodeModalLastSeen",
        node.lastSeen
    );

    setText(
        "nodeModalLocation",
        node.gps
    );

    setText(
        "nodeModalCondition",
        getNodeCondition(
            node
        )
    );

    renderNodeRelatedRoutes(
        node
    );

    renderNodeRelatedIncidents(
        node
    );

    setVisible(
        "nodeDetailsModal",
        true
    );

    document.body.classList.add(
        "modal-open"
    );

}


function closeNodeDetailsModal() {

    setVisible(
        "nodeDetailsModal",
        false
    );

    selectedNodeId =
        null;

    if (
        !document.querySelector(
            ".modal-overlay.visible"
        )
    ) {

        document.body.classList.remove(
            "modal-open"
        );

    }

}


function setupNodeDetails() {

    $("closeNodeModal")
        ?.addEventListener(
            "click",
            closeNodeDetailsModal
        );

    $("nodeModalCloseButton")
        ?.addEventListener(
            "click",
            closeNodeDetailsModal
        );

    $("nodeViewMapButton")
        ?.addEventListener(
            "click",
            () => {

                const node =
                    nodes.find(
                        item =>
                            item.id ===
                                selectedNodeId
                    );

                if (node) {
                    focusMapOnNode(
                        node
                    );
                }

                closeNodeDetailsModal();

            }
        );

    $("nodeViewNetworkButton")
        ?.addEventListener(
            "click",
            () => {

                const node =
                    nodes.find(
                        item =>
                            item.id ===
                                selectedNodeId
                    );

                if (!node) {
                    return;
                }

                closeNodeDetailsModal();

                switchView(
                    "network"
                );

                showToast(
                    `${node.id} network information opened.`
                );

            }
        );

    $("nodeDetailsModal")
        ?.addEventListener(
            "click",
            event => {

                if (
                    event.target ===
                    $("nodeDetailsModal")
                ) {

                    closeNodeDetailsModal();

                }

            }
        );

}


/* =========================
   NODE REGISTRATION
========================= */

function ensureTopologyPosition(
    nodeId
) {

    if (
        topologyPositions[
            nodeId
        ]
    ) {

        return;

    }

    const index =
        Object.keys(
            topologyPositions
        ).length -
        1;

    topologyPositions[
        nodeId
    ] = {

        x:
            15 +
            (
                index *
                14
            ) %
                55,

        y:
            18 +
            (
                index *
                17
            ) %
                70

    };

}


function openNodeRegistrationModal() {

    if (
        currentUser?.role !==
        "ADMIN"
    ) {

        showToast(
            "Administrator access is required to register a node.",
            "warning"
        );

        return;

    }

    $("nodeRegistrationForm")
        ?.reset();

    if (
        $("registerNodeBattery")
    ) {

        $("registerNodeBattery")
            .value =
            "100";

    }

    if (
        $("nodeRegistrationError")
    ) {

        $("nodeRegistrationError")
            .textContent =
            "";

    }

    setVisible(
        "nodeRegistrationModal",
        true
    );

    document.body.classList.add(
        "modal-open"
    );

}


function closeNodeRegistrationModal() {

    setVisible(
        "nodeRegistrationModal",
        false
    );

    if (
        !document.querySelector(
            ".modal-overlay.visible"
        )
    ) {

        document.body.classList.remove(
            "modal-open"
        );

    }

}


function setupNodeRegistration() {

    $("registerNodeButton")
        ?.addEventListener(
            "click",
            openNodeRegistrationModal
        );

    $("closeNodeRegistrationModal")
        ?.addEventListener(
            "click",
            closeNodeRegistrationModal
        );

    $("cancelNodeRegistrationButton")
        ?.addEventListener(
            "click",
            closeNodeRegistrationModal
        );

    $("manageNodesButton")
        ?.addEventListener(
            "click",
            () =>
                switchView(
                    "nodes"
                )
        );

    $("nodeRegistrationForm")
        ?.addEventListener(
            "submit",
            event => {

                event.preventDefault();

                if (
                    currentUser?.role !==
                    "ADMIN"
                ) {

                    showToast(
                        "Administrator access is required.",
                        "warning"
                    );

                    return;

                }

                const error =
                    $("nodeRegistrationError");

                const id =
                    $("registerNodeId")
                        ?.value
                        .trim()
                        .toUpperCase() ||
                    "";

                const status =
                    $("registerNodeStatus")
                        ?.value ||
                    "ONLINE";

                const battery =
                    Number(
                        $(
                            "registerNodeBattery"
                        )?.value
                    );

                const rssiText =
                    $("registerNodeRssi")
                        ?.value
                        .trim() ||
                    "";

                const rssi =
                    rssiText === ""
                        ? null
                        : Number(
                            rssiText
                        );

                const latitude =
                    Number(
                        $(
                            "registerNodeLatitude"
                        )?.value
                    );

                const longitude =
                    Number(
                        $(
                            "registerNodeLongitude"
                        )?.value
                    );

                const fail =
                    message => {

                        if (error) {

                            error.textContent =
                                message;

                        }

                    };

                if (error) {

                    error.textContent =
                        "";

                }

                if (
                    !/^DM-\d{3,}$/.test(
                        id
                    )
                ) {

                    return fail(
                        "Node ID must follow the format DM-007."
                    );

                }

                if (
                    nodes.some(
                        node =>
                            node.id ===
                                id
                    )
                ) {

                    return fail(
                        "This node ID is already registered."
                    );

                }

                if (
                    !Number.isFinite(
                        battery
                    ) ||
                    battery <
                        0 ||
                    battery >
                        100
                ) {

                    return fail(
                        "Battery must be between 0 and 100 percent."
                    );

                }

                if (
                    rssi !== null &&
                    (
                        !Number.isFinite(
                            rssi
                        ) ||
                        rssi <
                            -120 ||
                        rssi >
                            0
                    )
                ) {

                    return fail(
                        "RSSI must be between -120 and 0 dBm."
                    );

                }

                if (
                    !Number.isFinite(
                        latitude
                    ) ||
                    latitude <
                        -90 ||
                    latitude >
                        90
                ) {

                    return fail(
                        "Enter a valid latitude between -90 and 90."
                    );

                }

                if (
                    !Number.isFinite(
                        longitude
                    ) ||
                    longitude <
                        -180 ||
                    longitude >
                        180
                ) {

                    return fail(
                        "Enter a valid longitude between -180 and 180."
                    );

                }

                const newNode = {

                    id,

                    status,

                    battery,

                    rssi,

                    gps:
                        `${latitude.toFixed(
                            4
                        )}, ${longitude.toFixed(
                            4
                        )}`,

                    gpsValid:
                        true,

                    latitude,

                    longitude,

                    lastSeen:
                        "Just now"

                };

                nodes.push(
                    newNode
                );

                ensureTopologyPosition(
                    newNode.id
                );

                addNodeMarker(
                    newNode
                );

                renderNodes();

                renderFullNodeTable();

                renderTopology();

                renderNetworkView();

                updateStatistics();

                addAuditLog(
                    "NODE",
                    "INFO",
                    currentUser.name,
                    newNode.id,
                    "Node registered",
                    `${newNode.id} was registered and added to the trusted mesh.`
                );

                closeNodeRegistrationModal();

                showToast(
                    `${newNode.id} registered successfully and added to the trusted mesh.`
                );

                openNodeDetailsModal(
                    newNode.id
                );

            }
        );

}


/* =========================
   ROUTES / TOPOLOGY
========================= */

function renderRouteRows(
    targetId
) {

    const body =
        $(targetId);

    if (!body) {
        return;
    }

    body.innerHTML =
        "";

    routes.forEach(
        route => {

            const row =
                document.createElement(
                    "tr"
                );

            const routeClass =
                route.status ===
                    "ACTIVE"
                    ? "route-active"
                    : route.status ===
                        "STANDBY"
                        ? "route-standby"
                        : "route-stale";

            row.innerHTML =
                `

                    <td>
                        <strong>
                            ${escapeHtml(
                                route.source
                            )}
                        </strong>
                    </td>

                    <td>
                        ${escapeHtml(
                            route.destination
                        )}
                    </td>

                    <td>
                        ${escapeHtml(
                            route.nextHop
                        )}
                    </td>

                    <td>
                        ${route.hopCount}
                    </td>

                    <td>

                        <span class="route-quality">
                            ${escapeHtml(
                                route.quality
                            )}
                        </span>

                    </td>

                    <td>

                        <span class="route-status ${routeClass}">
                            ${escapeHtml(
                                route.status
                            )}
                        </span>

                    </td>

                `;

            body.appendChild(
                row
            );

        }
    );

}


function renderRoutes() {

    renderRouteRows(
        "routeTableBody"
    );

}


function renderNetworkView() {

    renderRouteRows(
        "networkRouteTableBody"
    );

    drawTopology(
        "networkTopologySvg",
        "networkTopologyNodes"
    );

}


function renderTopology() {

    drawTopology(
        "topologySvg",
        "topologyNodes"
    );

}


function drawTopology(
    svgId,
    containerId
) {

    const svg =
        $(svgId);

    const container =
        $(containerId);

    if (
        !svg ||
        !container
    ) {
        return;
    }

    const width =
        1000;

    const height =
        520;

    svg.setAttribute(
        "viewBox",
        `0 0 ${width} ${height}`
    );

    svg.setAttribute(
        "preserveAspectRatio",
        "none"
    );

    svg.innerHTML =
        "";

    container.innerHTML =
        "";

    nodes.forEach(
        node =>
            ensureTopologyPosition(
                node.id
            )
    );

    const links = [

        [
            "DM-001",
            "DM-002",
            "active"
        ],

        [
            "DM-002",
            "DM-003",
            "active"
        ],

        [
            "DM-003",
            "GATEWAY",
            "active"
        ],

        [
            "DM-001",
            "DM-004",
            "standby"
        ],

        [
            "DM-004",
            "DM-003",
            "standby"
        ],

        [
            "DM-005",
            "DM-004",
            "active"
        ],

        [
            "DM-006",
            "DM-004",
            "offline"
        ]

    ];

    links.forEach(
        (
            [
                fromId,
                toId,
                state
            ]
        ) => {

            const from =
                topologyPositions[
                    fromId
                ];

            const to =
                topologyPositions[
                    toId
                ];

            if (
                !from ||
                !to
            ) {
                return;
            }

            const line =
                document.createElementNS(
                    "http://www.w3.org/2000/svg",
                    "line"
                );

            line.setAttribute(
                "x1",
                (
                    from.x /
                    100
                ) * width
            );

            line.setAttribute(
                "y1",
                (
                    from.y /
                    100
                ) * height
            );

            line.setAttribute(
                "x2",
                (
                    to.x /
                    100
                ) * width
            );

            line.setAttribute(
                "y2",
                (
                    to.y /
                    100
                ) * height
            );

            line.classList.add(
                "route-line",
                state
            );

            svg.appendChild(
                line
            );

        }
    );

    nodes.forEach(
        node => {

            const position =
                topologyPositions[
                    node.id
                ];

            if (!position) {
                return;
            }

            const element =
                document.createElement(
                    "div"
                );

            const online =
                node.status ===
                "ONLINE";

            element.className =
                `topology-node ${
                    online
                        ? "active"
                        : "offline"
                }`;

            element.style.left =
                `${position.x}%`;

            element.style.top =
                `${position.y}%`;

            element.innerHTML =
                `
                    <span class="topology-node-id">
                        ${escapeHtml(
                            node.id
                        )}
                    </span>

                    <span class="topology-node-status">

                        <span class="topology-node-dot ${
                            online
                                ? "online"
                                : "offline"
                        }"></span>

                        ${escapeHtml(
                            node.status
                        )}

                    </span>
                `;

            element.addEventListener(
                "click",
                () =>
                    openNodeDetailsModal(
                        node.id
                    )
            );

            container.appendChild(
                element
            );

        }
    );

    const gateway =
        topologyPositions.GATEWAY;

    if (gateway) {

        const element =
            document.createElement(
                "div"
            );

        element.className =
            "topology-node gateway-node";

        element.style.left =
            `${gateway.x}%`;

        element.style.top =
            `${gateway.y}%`;

        element.innerHTML =
            `
                <span class="topology-node-id gateway-label">
                    GATEWAY
                </span>

                <span class="topology-node-status">
                    LoRa Bridge
                </span>
            `;

        container.appendChild(
            element
        );

    }

}

/* =========================
   MESSAGE HISTORY
========================= */

function renderMessageRows(
    targetId
) {

    const body =
        $(targetId);

    if (!body) {
        return;
    }

    body.innerHTML =
        "";

    messages.forEach(
        message => {

            const row =
                document.createElement(
                    "tr"
                );

            row.innerHTML =
                `

                    <td>
                        <span class="message-id">
                            ${escapeHtml(
                                message.id
                            )}
                        </span>
                    </td>

                    <td>
                        ${escapeHtml(
                            message.sender
                        )}
                    </td>

                    <td>
                        ${escapeHtml(
                            message.category
                        )}
                    </td>

                    <td>

                        <span class="priority-badge ${getPriorityClass(
                            message.priority
                        )}">
                            ${escapeHtml(
                                message.priority
                            )}
                        </span>

                    </td>

                    <td>
                        ${message.hopCount}
                    </td>

                    <td>
                        ${message.ttl}
                    </td>

                    <td>

                        <span class="message-status ${getMessageStatusClass(
                            message.status
                        )}">
                            ${escapeHtml(
                                message.status
                            )}
                        </span>

                    </td>

                    <td>
                        ${escapeHtml(
                            message.time
                        )}
                    </td>

                `;

            row.addEventListener(
                "click",
                () =>
                    showMessageDetails(
                        message
                    )
            );

            body.appendChild(
                row
            );

        }
    );

}


function renderMessages() {

    renderMessageRows(
        "messageTableBody"
    );

    setText(
        "messageCount",
        String(
            messages.length
        ).padStart(
            2,
            "0"
        )
    );

}


function renderFullMessageTable() {

    renderMessageRows(
        "fullMessageTableBody"
    );

}


/* =========================
   MESSAGE DETAIL
========================= */

function renderPacketRoute(
    routePath
) {

    const container =
        $("packetRoutePath");

    if (!container) {
        return;
    }

    container.innerHTML =
        "";

    routePath.forEach(
        (
            step,
            index
        ) => {

            const node =
                document.createElement(
                    "span"
                );

            node.className =
                `packet-route-node ${
                    step ===
                    "GATEWAY"
                        ? "gateway"
                        : ""
                }`;

            node.textContent =
                step;

            container.appendChild(
                node
            );

            if (
                index <
                routePath.length -
                    1
            ) {

                const arrow =
                    document.createElement(
                        "span"
                    );

                arrow.className =
                    "packet-route-arrow";

                arrow.textContent =
                    "→";

                container.appendChild(
                    arrow
                );

            }

        }
    );

}


function showMessageDetails(
    message
) {

    if (!message) {
        return;
    }

    selectedMessageId =
        message.id;

    const delivered =
        message.status ===
        "DELIVERED";

    const queued =
        message.status ===
        "QUEUED";

    setText(
        "messageDetailTitle",
        `${message.category} · ${message.id}`
    );

    setText(
        "messageDetailIcon",
        message.priority ===
            "CRITICAL"
            ? "!"
            : "P"
    );

    setText(
        "messageDetailId",
        message.id
    );

    setText(
        "messageDetailStatus",
        message.status
    );

    setText(
        "packetMessageId",
        message.id
    );

    setText(
        "packetSender",
        message.sender
    );

    setText(
        "packetCategory",
        message.category
    );

    setText(
        "packetPriority",
        message.priority
    );

    setText(
        "packetHops",
        message.hopCount
    );

    setText(
        "packetTtl",
        message.ttl
    );

    setText(
        "packetStatus",
        message.status
    );

    setText(
        "packetTime",
        message.time
    );

    setText(
        "packetContent",
        message.content
    );

    setText(
        "messageDeliveryState",
        delivered
            ? "DELIVERED"
            : queued
                ? "QUEUED"
                : message.status
    );

    setText(
        "messageDeliveryDescription",
        delivered
            ? "Packet reached the gateway successfully."
            : queued
                ? "Packet is retained locally until a usable route becomes available."
                : "Packet has not yet reached the final delivery state."
    );

    const deliveryDot =
        $("messageDeliveryDot");

    if (deliveryDot) {

        deliveryDot.className =
            `message-delivery-dot ${
                delivered
                    ? "packet-state-good"
                    : queued
                        ? "packet-state-warning"
                        : "packet-state-critical"
            }`;

    }

    setText(
        "packetAckState",
        message.ack
            ? "ACK RECEIVED"
            : queued
                ? "ACK PENDING"
                : "NO ACK"
    );

    setText(
        "packetAckDescription",
        message.ack
            ? "Acknowledgement was recorded for the packet."
            : queued
                ? "Acknowledgement will be completed after a usable route is available."
                : "No acknowledgement has been recorded for this packet."
    );

    setText(
        "packetIntegrityState",
        message.integrity ||
            "VALID"
    );

    setText(
        "packetIntegrityDescription",
        "Packet integrity check is valid in this frontend demonstration state."
    );

    setText(
        "packetDuplicateState",
        message.duplicate
            ? "DUPLICATE DETECTED"
            : "NOT DETECTED"
    );

    setText(
        "packetDuplicateDescription",
        message.duplicate
            ? "Duplicate suppression should discard repeated delivery attempts."
            : "No duplicate message ID has been observed."
    );

    setText(
        "packetTtlState",
        message.ttl > 0
            ? "WITHIN LIMIT"
            : "EXPIRED"
    );

    setText(
        "packetTtlDescription",
        message.ttl > 0
            ? "TTL is still available for forwarding."
            : "TTL has reached zero and the packet must be discarded."
    );

    renderPacketRoute(
        message.routePath ||
        [
            message.sender,
            "GATEWAY"
        ]
    );

    setVisible(
        "messageDetailModal",
        true
    );

    document.body.classList.add(
        "modal-open"
    );

}


function closeMessageDetailModal() {

    setVisible(
        "messageDetailModal",
        false
    );

    selectedMessageId =
        null;

    if (
        !document.querySelector(
            ".modal-overlay.visible"
        )
    ) {

        document.body.classList.remove(
            "modal-open"
        );

    }

}


function setupMessageDetails() {

    /* Header X button */
    $("closeMessageDetailModal")
        ?.addEventListener(
            "click",
            closeMessageDetailModal
        );

    /* Footer Close button */
    $("messageDetailCloseButton")
        ?.addEventListener(
            "click",
            closeMessageDetailModal
        );

    $("messageViewSenderNodeButton")
        ?.addEventListener(
            "click",
            () => {

                const message =
                    messages.find(
                        item =>
                            item.id ===
                                selectedMessageId
                    );

                const node =
                    nodes.find(
                        item =>
                            item.id ===
                                message?.sender
                    );

                closeMessageDetailModal();

                if (node) {

                    openNodeDetailsModal(
                        node.id
                    );

                }

            }
        );

    $("messageViewNetworkButton")
        ?.addEventListener(
            "click",
            () => {

                closeMessageDetailModal();

                switchView(
                    "network"
                );

            }
        );

    $("messageDetailModal")
        ?.addEventListener(
            "click",
            event => {

                if (
                    event.target ===
                    $("messageDetailModal")
                ) {

                    closeMessageDetailModal();

                }

            }
        );

}


/* =========================
   PACKET QUEUE
========================= */

function renderPacketQueue() {

    const body =
        $("packetQueueTableBody");

    if (body) {

        body.innerHTML =
            "";

        packetQueue.forEach(
            packet => {

                const row =
                    document.createElement(
                        "tr"
                    );

                row.className =
                    "packet-queue-row";

                const statusClass =
                    packet.status ===
                        "QUEUED"
                        ? "queued"
                        : packet.status ===
                            "RETRY_READY"
                            ? "retry"
                            : packet.status ===
                                "FAILED"
                                ? "failed"
                                : "ready";

                row.innerHTML =
                    `

                        <td>

                            <span class="message-id">
                                ${escapeHtml(
                                    packet.id
                                )}
                            </span>

                        </td>

                        <td>
                            ${escapeHtml(
                                packet.sender
                            )}
                        </td>

                        <td>

                            <span class="priority-badge ${getPriorityClass(
                                packet.priority
                            )}">
                                ${escapeHtml(
                                    packet.priority
                                )}
                            </span>

                        </td>

                        <td>
                            ${escapeHtml(
                                packet.category
                            )}
                        </td>

                        <td>

                            <span class="queue-status ${statusClass}">
                                ${escapeHtml(
                                    statusText(
                                        packet.status
                                    )
                                )}
                            </span>

                        </td>

                        <td>
                            ${packet.retryCount}
                            /
                            ${packet.maxRetries}
                        </td>

                        <td>
                            ${escapeHtml(
                                packet.age
                            )}
                        </td>

                        <td>
                            ${escapeHtml(
                                packet.reason
                            )}
                        </td>

                    `;

                row.addEventListener(
                    "click",
                    () => {

                        const message =
                            messages.find(
                                item =>
                                    item.id ===
                                        packet.id
                            );

                        if (message) {

                            showMessageDetails(
                                message
                            );

                        }

                    }
                );

                body.appendChild(
                    row
                );

            }
        );

    }

    const queued =
        packetQueue.filter(
            packet =>
                packet.status ===
                    "QUEUED"
        ).length;

    const retry =
        packetQueue.filter(
            packet =>
                packet.status ===
                    "RETRY_READY"
        ).length;

    const pending =
        queued +
        retry;

    setText(
        "queuedPacketCount",
        String(
            queued
        ).padStart(
            2,
            "0"
        )
    );

    setText(
        "retryPacketCount",
        String(
            retry
        ).padStart(
            2,
            "0"
        )
    );

    setText(
        "oldestPacketAge",
        packetQueue[0]
            ?.age ||
            "0 min"
    );

    setText(
        "queueDeliveryState",
        packetQueue.length
            ? "WAITING FOR ROUTE"
            : "CLEAR"
    );

    setText(
        "queueSyncStatus",
        pending
            ? `${pending} packet(s) awaiting delivery`
            : "Queue synchronized"
    );

    setText(
        "syncPendingCount",
        pending
    );

}


function retryQueuedPackets() {

    let changed =
        0;

    packetQueue.forEach(
        packet => {

            if (
                packet.status ===
                "QUEUED"
            ) {

                packet.status =
                    "RETRY_READY";

                packet.retryCount =
                    Math.min(
                        packet.retryCount +
                            1,
                        packet.maxRetries
                    );

                packet.nextRetry =
                    "Ready now";

                changed +=
                    1;

            }

        }
    );

    if (!changed) {

        showToast(
            "No queued packets are currently eligible for retry.",
            "warning"
        );

        return;

    }

    addAuditLog(
        "MESSAGE",
        "INFO",
        currentUser?.name,
        "--",
        "Queue retry requested",
        `${changed} queued packet(s) moved to retry state.`
    );

    renderPacketQueue();

    renderGatewayView();

    showToast(
        `${changed} queued packet(s) prepared for retry.`
    );

}


function setupQueue() {

    $("retryQueuedPacketsButton")
        ?.addEventListener(
            "click",
            retryQueuedPackets
        );

}


/* =========================
   GATEWAY OPERATIONS
========================= */

function renderGatewayView() {

    setText(
        "gatewayState",
        gatewayState.gateway.state
    );

    setText(
        "gatewayLastPacket",
        gatewayState.gateway.lastPacket
    );

    setText(
        "backendState",
        gatewayState.backend.state
    );

    setText(
        "backendResponseTime",
        gatewayState.backend.response
    );

    setText(
        "databaseState",
        gatewayState.database.state
    );

    setText(
        "databaseRecords",
        gatewayState.database.records
    );

    const pending =
        packetQueue.filter(
            packet =>
                [
                    "QUEUED",
                    "RETRY_READY"
                ].includes(
                    packet.status
                )
        ).length;

    setText(
        "syncState",
        pending
            ? "PENDING"
            : "SYNCED"
    );

    setText(
        "syncPendingCount",
        pending
    );

    setText(
        "queueSyncStatus",
        pending
            ? `${pending} packet(s) awaiting delivery`
            : "Queue synchronized"
    );

    gatewayState.sync.state =
        pending
            ? "PENDING"
            : "SYNCED";

    gatewayState.sync.pending =
        pending;

}


/* =========================
   AUDIT LOGS
========================= */

function renderAuditLogs() {

    const body =
        $("auditLogTableBody");

    if (!body) {
        return;
    }

    const filtered =
        auditLogs.filter(
            log => {

                const eventMatch =
                    logFilter.eventType ===
                        "ALL" ||
                    log.eventType ===
                        logFilter.eventType;

                const severityMatch =
                    logFilter.severity ===
                        "ALL" ||
                    log.severity ===
                        logFilter.severity;

                return (
                    eventMatch &&
                    severityMatch
                );

            }
        );

    if (!filtered.length) {

        body.innerHTML =
            `
                <tr>
                    <td colspan="7">

                        <div class="no-incidents">
                            No audit events match the selected filters.
                        </div>

                    </td>
                </tr>
            `;

        updateLogSummary();

        return;

    }

    body.innerHTML =
        "";

    filtered.forEach(
        log => {

            const row =
                document.createElement(
                    "tr"
                );

            row.innerHTML =
                `

                    <td>
                        ${escapeHtml(
                            log.timestamp
                        )}
                    </td>

                    <td>

                        <span class="log-event-type">
                            ${escapeHtml(
                                log.eventType
                            )}
                        </span>

                    </td>

                    <td>

                        <span class="log-severity log-severity-${log.severity.toLowerCase()}">
                            ${escapeHtml(
                                log.severity
                            )}
                        </span>

                    </td>

                    <td>

                        <span class="log-actor">
                            ${escapeHtml(
                                log.actor
                            )}
                        </span>

                    </td>

                    <td>
                        ${escapeHtml(
                            log.nodeId
                        )}
                    </td>

                    <td>
                        ${escapeHtml(
                            log.event
                        )}
                    </td>

                    <td>

                        <span class="log-description">
                            ${escapeHtml(
                                log.description
                            )}
                        </span>

                    </td>

                `;

            body.appendChild(
                row
            );

        }
    );

    updateLogSummary();

}


function updateLogSummary() {

    setText(
        "loginEventCount",
        String(
            auditLogs.filter(
                log =>
                    log.eventType ===
                        "AUTH"
            ).length
        ).padStart(
            2,
            "0"
        )
    );

    setText(
        "adminEventCount",
        String(
            auditLogs.filter(
                log =>
                    log.actor ===
                        "System Administrator"
            ).length
        ).padStart(
            2,
            "0"
        )
    );

    setText(
        "securityWarningCount",
        String(
            auditLogs.filter(
                log =>
                    [
                        "WARNING",
                        "CRITICAL"
                    ].includes(
                        log.severity
                    )
            ).length
        ).padStart(
            2,
            "0"
        )
    );

    setText(
        "loggingState",
        "ACTIVE"
    );

}


function setupAuditLogs() {

    $("logEventFilter")
        ?.addEventListener(
            "change",
            event => {

                logFilter.eventType =
                    event.target.value;

                renderAuditLogs();

            }
        );

    $("logSeverityFilter")
        ?.addEventListener(
            "change",
            event => {

                logFilter.severity =
                    event.target.value;

                renderAuditLogs();

            }
        );

    $("resetLogFilters")
        ?.addEventListener(
            "click",
            () => {

                logFilter.eventType =
                    "ALL";

                logFilter.severity =
                    "ALL";

                if (
                    $("logEventFilter")
                ) {

                    $("logEventFilter")
                        .value =
                        "ALL";

                }

                if (
                    $("logSeverityFilter")
                ) {

                    $("logSeverityFilter")
                        .value =
                        "ALL";

                }

                renderAuditLogs();

            }
        );

    $("exportLogsButton")
        ?.addEventListener(
            "click",
            exportAuditLogs
        );

    $("clearLogsControl")
        ?.addEventListener(
            "click",
            clearAuditLogs
        );

}


function exportAuditLogs() {

    if (
        currentUser?.role !==
        "ADMIN"
    ) {

        showToast(
            "Administrator access is required to export audit logs.",
            "warning"
        );

        return;

    }

    addAuditLog(
        "AUTH",
        "INFO",
        currentUser.name,
        "--",
        "Audit log exported",
        "Administrator exported dashboard audit logs."
    );

    const header =
        "Timestamp,Event Type,Severity,Actor,Node,Event,Description";

    const lines =
        auditLogs.map(
            log =>
                [
                    log.timestamp,
                    log.eventType,
                    log.severity,
                    log.actor,
                    log.nodeId,
                    log.event,
                    log.description
                ]
                    .map(
                        value =>
                            `"${String(
                                value
                            ).replaceAll(
                                '"',
                                '""'
                            )}"`
                    )
                    .join(",")
        );

    const blob =
        new Blob(
            [
                [
                    header,
                    ...lines
                ].join(
                    "\n"
                )
            ],
            {
                type:
                    "text/csv;charset=utf-8"
            }
        );

    const url =
        URL.createObjectURL(
            blob
        );

    const anchor =
        document.createElement(
            "a"
        );

    anchor.href =
        url;

    anchor.download =
        "DisasterMesh_Audit_Logs.csv";

    document.body.appendChild(
        anchor
    );

    anchor.click();

    anchor.remove();

    URL.revokeObjectURL(
        url
    );

    showToast(
        "Audit log export prepared."
    );

}


function clearAuditLogs() {

    if (
        currentUser?.role !==
        "ADMIN"
    ) {

        showToast(
            "Administrator access is required to clear audit logs.",
            "warning"
        );

        return;

    }

    const confirmed =
        window.confirm(
            "Clear the demo audit log? This only clears the frontend demonstration data."
        );

    if (!confirmed) {
        return;
    }

    auditLogs.splice(
        0,
        auditLogs.length
    );

    addAuditLog(
        "AUTH",
        "WARNING",
        currentUser.name,
        "--",
        "Audit log cleared",
        "Administrator cleared the frontend demonstration audit log."
    );

    showToast(
        "Demo audit log cleared.",
        "warning"
    );

}


/* =========================
   SYSTEM HEALTH
========================= */

function renderSystemHealth() {

    const container =
        $("systemHealthGrid");

    if (!container) {
        return;
    }

    container.innerHTML =
        "";

    systemHealth.forEach(
        service => {

            const card =
                document.createElement(
                    "div"
                );

            const stateClass =
                service.state ===
                    "UP"
                    ? "health-up"
                    : service.state ===
                        "WARNING"
                        ? "health-warning"
                        : "health-down";

            card.className =
                "health-card";

            card.innerHTML =
                `

                    <div class="health-card-top">

                        <span class="health-service">
                            ${escapeHtml(
                                service.service
                            )}
                        </span>

                        <span class="health-state ${stateClass}">

                            <span class="health-state-dot"></span>

                            ${escapeHtml(
                                service.state
                            )}

                        </span>

                    </div>

                    <p class="health-description">
                        ${escapeHtml(
                            service.description
                        )}
                    </p>

                    <div class="health-metric">

                        <span class="health-metric-label">
                            ${escapeHtml(
                                service.metricLabel
                            )}
                        </span>

                        <span class="health-metric-value">
                            ${escapeHtml(
                                service.metricValue
                            )}
                        </span>

                    </div>

                `;

            container.appendChild(
                card
            );

        }
    );

}


/* =========================
   SETTINGS / UTILITY BUTTONS
========================= */

function setupUtilityButtons() {

    $("dashboardLogoutButton")
        ?.addEventListener(
            "click",
            logout
        );

    $("logoutButton")
        ?.addEventListener(
            "click",
            logout
        );

    $("viewAllNodesButton")
        ?.addEventListener(
            "click",
            () =>
                switchView(
                    "nodes"
                )
        );

    $("manageLogsButton")
        ?.addEventListener(
            "click",
            () =>
                switchView(
                    "logs"
                )
        );

    $("settingsLogsButton")
        ?.addEventListener(
            "click",
            () =>
                switchView(
                    "logs"
                )
        );

    $("settingsManageNodesButton")
        ?.addEventListener(
            "click",
            () =>
                switchView(
                    "nodes"
                )
        );

    document
        .querySelectorAll(
            ".settings-row .panel-button"
        )
        .forEach(
            button => {

                const text =
                    button.textContent
                        .trim();

                if (
                    text ===
                    "View Logs"
                ) {

                    button.addEventListener(
                        "click",
                        () =>
                            switchView(
                                "logs"
                            )
                    );

                }

                if (
                    text ===
                    "Manage Nodes"
                ) {

                    button.addEventListener(
                        "click",
                        () =>
                            switchView(
                                "nodes"
                            )
                    );

                }

            }
        );

    $("settingsAlertsButton")
        ?.addEventListener(
            "click",
            () =>
                switchView(
                    "alerts"
                )
        );

    $("settingsAnalyticsButton")
        ?.addEventListener(
            "click",
            () =>
                switchView(
                    "analytics"
                )
        );

    $("settingsManageUsersButton")
        ?.addEventListener(
            "click",
            () =>
                switchView(
                    "users"
                )
        );

    $("settingsReadinessButton")
        ?.addEventListener(
            "click",
            () =>
                switchView(
                    "readiness"
                )
        );

    $("autoRefreshToggle")
        ?.addEventListener(
            "change",
            event =>
                showToast(
                    event.target.checked
                        ? "Auto refresh enabled."
                        : "Auto refresh disabled."
                )
        );

    $("mapAnimationToggle")
        ?.addEventListener(
            "change",
            event =>
                showToast(
                    event.target.checked
                        ? "Map animations enabled."
                        : "Map animations disabled."
                )
        );

}


/* ============================================================
   STEPS 27-30
   ALERTS / ANALYTICS / USER MANAGEMENT / READINESS
============================================================ */

function getAlertSeverityClass(severity) {
    if (severity === "CRITICAL") return "alert-critical";
    if (severity === "WARNING") return "alert-warning";
    return "alert-info";
}

function renderAlertCenter() {
    const body = $("alertTableBody");
    if (!body) return;

    const filter = $("alertFilter")?.value || "ALL";
    const filtered = alerts.filter(alert => {
        if (filter === "ALL") return true;
        if (filter === "UNREAD") return alert.status === "UNREAD";
        return alert.severity === filter;
    });

    const critical = alerts.filter(alert => alert.severity === "CRITICAL").length;
    const warning = alerts.filter(alert => alert.severity === "WARNING").length;
    const info = alerts.filter(alert => alert.severity === "INFO").length;
    const unread = alerts.filter(alert => alert.status === "UNREAD").length;

    setText("alertsCriticalCount", String(critical).padStart(2, "0"));
    setText("alertsWarningCount", String(warning).padStart(2, "0"));
    setText("alertsInfoCount", String(info).padStart(2, "0"));
    setText("alertsUnreadCount", String(unread).padStart(2, "0"));

    body.innerHTML = "";

    if (!filtered.length) {
        body.innerHTML = `<tr><td colspan="6"><div class="alerts-empty">No alerts match the selected filter.</div></td></tr>`;
        return;
    }

    filtered.forEach(alert => {
        const row = document.createElement("tr");
        row.className = `alert-row ${alert.status === "UNREAD" ? "alert-unread" : ""}`;

        row.innerHTML = `
            <td><span class="alert-title">${escapeHtml(alert.title)}</span></td>
            <td><span class="alert-severity ${getAlertSeverityClass(alert.severity)}"><span class="alert-severity-dot"></span>${escapeHtml(alert.severity)}</span></td>
            <td><span class="alert-source">${escapeHtml(alert.source)}</span></td>
            <td><span class="alert-time">${escapeHtml(alert.time)}</span></td>
            <td><span class="alert-status ${alert.status === "UNREAD" ? "unread" : "read"}">${escapeHtml(alert.status)}</span></td>
            <td><span class="alert-description">${escapeHtml(alert.description)}</span></td>
        `;

        row.addEventListener("click", () => {
            if (alert.status !== "UNREAD") return;

            alert.status = "READ";

            addAuditLog(
                "SYSTEM",
                "INFO",
                currentUser?.name,
                alert.source.startsWith("DM-") || alert.source.startsWith("INC-") ? alert.source : "--",
                "Alert reviewed",
                `${alert.title} was marked as read.`
            );

            renderAlertCenter();
            showToast("Alert marked as read.", "success");
        });

        body.appendChild(row);
    });
}

function markAllAlertsRead() {
    let changed = 0;

    alerts.forEach(alert => {
        if (alert.status === "UNREAD") {
            alert.status = "READ";
            changed += 1;
        }
    });

    if (!changed) {
        showToast("There are no unread alerts.", "warning");
        return;
    }

    addAuditLog(
        "SYSTEM",
        "INFO",
        currentUser?.name,
        "--",
        "Alerts reviewed",
        `${changed} alert(s) marked as read.`
    );

    renderAlertCenter();
    showToast(`${changed} alert(s) marked as read.`, "success");
}

function setupAlertEvents() {
    $("alertFilter")?.addEventListener("change", renderAlertCenter);
    $("markAllAlertsReadButton")?.addEventListener("click", markAllAlertsRead);
}

/* ============================================================
   STEP 28 - ANALYTICS & PERFORMANCE
============================================================ */
function renderAnalytics() {
    setText("analyticsDeliveryRate", `${analyticsMetrics.deliveryRate}%`);
    setText("analyticsLatency", `${analyticsMetrics.latency} ms`);
    setText("analyticsRouteRecovery", `${analyticsMetrics.routeRecovery} s`);
    setText("analyticsDuplicateRate", `${analyticsMetrics.duplicateRate}%`);
    setText("analyticsAiAccuracy", `${analyticsMetrics.aiAccuracy}%`);
    setText("analyticsDashboardLatency", `${analyticsMetrics.dashboardLatency} ms`);

    const body = $("analyticsMetricTableBody");
    if (!body) return;

    body.innerHTML = "";

    const metrics = [
        ["Packet Delivery Ratio", `${analyticsMetrics.deliveryRate}%`, "≥ 90%", analyticsMetrics.deliveryRate >= 90, "Controlled-test prototype target."],
        ["Dashboard / Gateway Latency", `${analyticsMetrics.latency} ms`, "Few seconds", analyticsMetrics.latency < 1000, "Representative prototype value."],
        ["Route Recovery", `${analyticsMetrics.routeRecovery} s`, "Within a few seconds", analyticsMetrics.routeRecovery <= 5, "Small controlled-mesh demonstration value."],
        ["Duplicate Delivery Rate", `${analyticsMetrics.duplicateRate}%`, "< 5%", analyticsMetrics.duplicateRate < 5, "Representative normal-operation value."],
        ["AI Classification Accuracy", `${analyticsMetrics.aiAccuracy}%`, "Measured on held-out set", analyticsMetrics.aiAccuracy >= 90, "Frontend placeholder until backend model integration."]
    ];

    metrics.forEach(metric => {
        const row = document.createElement("tr");
        row.className = "analytics-row";

        row.innerHTML = `
            <td><span class="analytics-metric">${escapeHtml(metric[0])}</span></td>
            <td><span class="analytics-current">${escapeHtml(metric[1])}</span></td>
            <td><span class="analytics-target">${escapeHtml(metric[2])}</span></td>
            <td><span class="metric-state ${metric[3] ? "metric-good" : "metric-warning"}">${metric[3] ? "PASS" : "WARNING"}</span></td>
            <td><span class="analytics-note">${escapeHtml(metric[4])}</span></td>
        `;

        body.appendChild(row);
    });
}

function exportAnalyticsSummary() {
    const range = $("analyticsRangeFilter")?.value || "CURRENT";

    const lines = [
        "DisasterMesh Analytics Summary",
        `Evaluation Window,${range}`,
        `Packet Delivery Ratio,${analyticsMetrics.deliveryRate}%`,
        `End-to-End Latency,${analyticsMetrics.latency} ms`,
        `Route Recovery,${analyticsMetrics.routeRecovery} s`,
        `Duplicate Rate,${analyticsMetrics.duplicateRate}%`,
        `AI Accuracy,${analyticsMetrics.aiAccuracy}%`,
        `Dashboard Latency,${analyticsMetrics.dashboardLatency} ms`
    ];

    const blob = new Blob(
        [lines.join("\n")],
        { type: "text/plain;charset=utf-8" }
    );

    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");

    anchor.href = url;
    anchor.download = "DisasterMesh_Analytics_Summary.txt";

    document.body.appendChild(anchor);
    anchor.click();
    anchor.remove();

    URL.revokeObjectURL(url);

    addAuditLog(
        "SYSTEM",
        "INFO",
        currentUser?.name,
        "--",
        "Analytics exported",
        "Performance summary exported from the dashboard."
    );

    showToast("Analytics summary exported.", "success");
}

function setupAnalyticsEvents() {
    $("analyticsRangeFilter")?.addEventListener("change", renderAnalytics);
    $("analyticsExportButton")?.addEventListener("click", exportAnalyticsSummary);
}

/* ============================================================
   STEP 29 - USER MANAGEMENT
============================================================ */
function renderUserManagement() {
    const body = $("userTableBody");
    if (!body) return;

    const search = ($( "userSearchInput" )?.value || "").trim().toLowerCase();
    const role = $("userRoleFilter")?.value || "ALL";

    const filtered = managedUsers.filter(user => {
        const searchMatch = !search ||
            user.name.toLowerCase().includes(search) ||
            user.username.toLowerCase().includes(search);

        const roleMatch = role === "ALL" || user.role === role;
        return searchMatch && roleMatch;
    });

    setText("userCount", String(managedUsers.length).padStart(2, "0"));
    setText("adminUserCount", String(managedUsers.filter(user => user.role === "ADMIN").length).padStart(2, "0"));
    setText("operatorUserCount", String(managedUsers.filter(user => user.role === "OPERATOR").length).padStart(2, "0"));
    setText("userManagementState", currentUser?.role === "ADMIN" ? "ACTIVE" : "LOCKED");

    body.innerHTML = "";

    if (!filtered.length) {
        body.innerHTML = `<tr><td colspan="6"><div class="users-empty">No users match the selected filters.</div></td></tr>`;
        return;
    }

    filtered.forEach(user => {
        const row = document.createElement("tr");
        row.className = "user-row";

        row.innerHTML = `
            <td><span class="user-name">${escapeHtml(user.name)}</span></td>
            <td><span class="user-username">${escapeHtml(user.username)}</span></td>
            <td><span class="user-role ${user.role === "ADMIN" ? "admin" : "operator"}">${user.role === "ADMIN" ? "ADMINISTRATOR" : "OPERATOR"}</span></td>
            <td><span class="user-state ${user.status === "ACTIVE" ? "user-active" : "user-inactive"}"><span class="user-state-dot"></span>${escapeHtml(user.status)}</span></td>
            <td>${escapeHtml(user.created)}</td>
            <td><div class="user-action-group"><button class="user-action" data-user-action="toggle" data-username="${escapeHtml(user.username)}">${user.status === "ACTIVE" ? "Disable" : "Enable"}</button><button class="user-action" data-user-action="role" data-username="${escapeHtml(user.username)}">Change Role</button></div></td>
        `;

        row.querySelectorAll("[data-user-action]").forEach(button => {
            button.addEventListener("click", event => {
                event.stopPropagation();
                performUserAction(button.dataset.userAction, button.dataset.username);
            });
        });

        body.appendChild(row);
    });
}

function performUserAction(action, username) {
    if (!currentUser || currentUser.role !== "ADMIN") {
        showToast("Administrator access is required.", "warning");
        return;
    }

    const user = managedUsers.find(item => item.username === username);
    if (!user) return;

    if (user.username === currentUser.username && action === "toggle") {
        showToast("The active administrator session cannot be disabled.", "warning");
        return;
    }

    if (action === "toggle") {
        user.status = user.status === "ACTIVE" ? "INACTIVE" : "ACTIVE";

        addAuditLog(
            "AUTH",
            "INFO",
            currentUser.name,
            "--",
            "User status changed",
            `${user.username} is now ${user.status}.`
        );

        renderUserManagement();
        showToast(`${user.username} is now ${user.status.toLowerCase()}.`, "success");
        return;
    }

    if (action === "role") {
        if (user.username === currentUser.username) {
            showToast("The active session role cannot be changed in the demo.", "warning");
            return;
        }

        user.role = user.role === "ADMIN" ? "OPERATOR" : "ADMIN";

        const authUser = demoUsers.find(item => item.username === user.username);
        if (authUser) authUser.role = user.role;

        addAuditLog(
            "AUTH",
            "WARNING",
            currentUser.name,
            "--",
            "User role changed",
            `${user.username} role changed to ${user.role}.`
        );

        renderUserManagement();
        showToast(`${user.username} role changed to ${user.role}.`, "success");
    }
}

function openUserModal() {
    if (!currentUser || currentUser.role !== "ADMIN") {
        showToast("Administrator access is required.", "warning");
        return;
    }

    $("userForm")?.reset();
    if ($("userFormError")) $("userFormError").textContent = "";

    setVisible("userModal", true);
    document.body.classList.add("modal-open");
}

function closeUserModal() {
    setVisible("userModal", false);
    document.body.classList.remove("modal-open");
}

function createManagedUser(event) {
    event.preventDefault();

    if (!currentUser || currentUser.role !== "ADMIN") {
        showToast("Administrator access is required.", "warning");
        return;
    }

    const name = $("userName")?.value.trim() || "";
    const username = $("userUsername")?.value.trim() || "";
    const role = $("userRole")?.value || "OPERATOR";
    const password = $("userPassword")?.value || "";
    const error = $("userFormError");

    if (error) error.textContent = "";

    if (name.length < 2 || username.length < 3 || password.length < 6) {
        if (error) error.textContent = "Enter a valid name, username and password of at least 6 characters.";
        return;
    }

    if (managedUsers.some(user => user.username.toLowerCase() === username.toLowerCase())) {
        if (error) error.textContent = "That username already exists.";
        return;
    }

    managedUsers.push({
        username,
        password,
        name,
        role,
        status: "ACTIVE",
        created: "Just now"
    });

    demoUsers.push({
        username,
        password,
        name,
        role
    });

    addAuditLog(
        "AUTH",
        "INFO",
        currentUser.name,
        "--",
        "User registered",
        `${name} (${username}) was created with role ${role}.`
    );

    renderUserManagement();
    closeUserModal();
    showToast(`User ${username} created.`, "success");
}

function setupUserManagementEvents() {
    $("userSearchInput")?.addEventListener("input", renderUserManagement);
    $("userRoleFilter")?.addEventListener("change", renderUserManagement);

    $("resetUserFilters")?.addEventListener("click", () => {
        if ($("userSearchInput")) $("userSearchInput").value = "";
        if ($("userRoleFilter")) $("userRoleFilter").value = "ALL";
        renderUserManagement();
    });

    $("addUserButton")?.addEventListener("click", openUserModal);
    $("closeUserModal")?.addEventListener("click", closeUserModal);
    $("cancelUserModal")?.addEventListener("click", closeUserModal);
    $("userForm")?.addEventListener("submit", createManagedUser);

    $("userModal")?.addEventListener("click", event => {
        if (event.target === $("userModal")) closeUserModal();
    });
}

/* ============================================================
   STEP 30 - SYSTEM READINESS
============================================================ */
function getReadinessStateClass(state) {
    if (state === "PASS") return "pass";
    if (state === "FAIL") return "fail";
    return "pending";
}

function renderSystemReadiness() {
    const container = $("readinessChecklist");
    if (!container) return;

    container.innerHTML = "";

    let passed = 0;

    readinessChecks.forEach(check => {
        if (check.state === "PASS") passed += 1;

        const item = document.createElement("div");
        item.className = `readiness-item ${getReadinessStateClass(check.state)}`;

        item.innerHTML = `
            <div class="readiness-main">
                <div class="readiness-check-icon">
                    ${check.state === "PASS" ? "✓" : check.state === "FAIL" ? "!" : "•"}
                </div>
                <div class="readiness-main-content">
                    <strong>${escapeHtml(check.title)}</strong>
                    <span>${escapeHtml(check.description)}</span>
                </div>
            </div>
            <span class="readiness-state ${getReadinessStateClass(check.state)}">
                ${escapeHtml(check.state)}
            </span>
        `;

        container.appendChild(item);
    });

    const total = readinessChecks.length;
    const score = Math.round((passed / total) * 100);
    const pending = readinessChecks.filter(check => check.state === "PENDING").length;
    const failed = readinessChecks.filter(check => check.state === "FAIL").length;

    setText("readinessScore", `${score}%`);
    setText("readinessState", failed ? "BLOCKED" : pending ? "READY*" : "READY");
    setText("readinessLastCheck", new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }));

    renderDemoScenario();
}

function renderDemoScenario() {
    const body = $("demoScenarioTableBody");
    if (!body) return;

    const steps = [
        ["01", "Field emergency created", "Emergency request receives a unique ID, category, GPS and timestamp.", true],
        ["02", "Mesh forwarding", "Packet travels through available multi-hop routes with TTL and duplicate checks.", true],
        ["03", "Gateway reception", "Gateway validates and forwards the packet toward the backend.", true],
        ["04", "Dashboard incident", "Critical incident becomes visible with location and classification details.", true],
        ["05", "Operator response", "Operator reviews, acknowledges, assigns and advances the incident.", true],
        ["06", "Route recovery", "Alternate path can be selected when an intermediate node fails.", true],
        ["07", "Store-and-forward", "Queued packet can be retained and retried after connectivity returns.", true],
        ["08", "Backend / hardware integration", "Live API, database, gateway and LoRa hardware must be integrated and tested.", false]
    ];

    body.innerHTML = "";
    let complete = 0;

    steps.forEach(step => {
        if (step[3]) complete += 1;

        const row = document.createElement("tr");
        row.className = "demo-scenario-row";

        row.innerHTML = `
            <td><span class="demo-step-number">${step[0]}</span></td>
            <td><span class="demo-stage">${escapeHtml(step[1])}</span></td>
            <td><span class="demo-expected">${escapeHtml(step[2])}</span></td>
            <td><span class="demo-state ${step[3] ? "complete" : "pending"}">${step[3] ? "READY" : "PENDING"}</span></td>
        `;

        body.appendChild(row);
    });

    setText("demoProgress", `${Math.round((complete / steps.length) * 100)}%`);
}

function runReadinessCheck() {
    renderSystemReadiness();

    addAuditLog(
        "SYSTEM",
        "INFO",
        currentUser?.name,
        "--",
        "Readiness check executed",
        "Frontend readiness and demonstration checkpoints were validated."
    );

    showToast("System readiness check completed.", "success");
}

function resetReadinessCheck() {
    readinessChecks.forEach(check => {
        check.state = (check.id === "BACKEND" || check.id === "HARDWARE") ? "PENDING" : "PASS";
    });

    renderSystemReadiness();
    showToast("Readiness checklist reset.", "success");
}

function setupReadinessEvents() {
    $("runReadinessCheckButton")?.addEventListener("click", runReadinessCheck);
    $("resetReadinessButton")?.addEventListener("click", resetReadinessCheck);
}

/* =========================
   MODAL / GLOBAL EVENTS
========================= */

/* =========================
   GLOBAL MODAL CONTROL
========================= */

function closeAllModals() {

    [
        "incidentModal",
        "nodeDetailsModal",
        "nodeRegistrationModal",
        "messageDetailModal",
        "userModal"
    ].forEach(
        id =>
            setVisible(
                id,
                false
            )
    );

    selectedIncidentId =
        null;

    selectedNodeId =
        null;

    selectedMessageId =
        null;

    document.body.classList.remove(
        "modal-open"
    );

}


function setupGlobalKeyboard() {

    document.addEventListener(
        "keydown",
        event => {

            if (
                event.key !==
                "Escape"
            ) {

                return;

            }

            if (
                $("messageDetailModal")
                    ?.classList.contains(
                        "visible"
                    )
            ) {

                closeMessageDetailModal();

                return;

            }

            if (
                $("nodeRegistrationModal")
                    ?.classList.contains(
                        "visible"
                    )
            ) {

                closeNodeRegistrationModal();

                return;

            }

            if (
                $("nodeDetailsModal")
                    ?.classList.contains(
                        "visible"
                    )
            ) {

                closeNodeDetailsModal();

                return;

            }

            if (
                $("userModal")
                    ?.classList.contains(
                        "visible"
                    )
            ) {

                closeUserModal();

                return;

            }

            if (
                $("incidentModal")
                    ?.classList.contains(
                        "visible"
                    )
            ) {

                closeIncidentModal();

            }

        }
    );

}


/* =========================
   INITIALIZATION
========================= */

function initializeDashboard() {

    setupAuthentication();

    setupNavigation();

    setupIncidentFilters();

    setupIncidentModal();

    setupMap();

    setupNodeFilters();

    setupNodeDetails();

    setupNodeRegistration();

    setupMessageDetails();

    setupQueue();

    setupAuditLogs();

    setupAlertEvents();

    setupAnalyticsEvents();

    setupUserManagementEvents();

    setupReadinessEvents();

    setupUtilityButtons();

    setupGlobalKeyboard();


    currentUser =
        getSavedSession();


    if (currentUser) {

        showApplication();

    } else {

        showAuthentication();

    }


    updateStatistics();

    renderIncidents();

    renderIncidentManagement();

    renderNodes();

    renderFullNodeTable();

    renderRoutes();

    renderTopology();

    renderNetworkView();

    renderMessages();

    renderFullMessageTable();

    renderPacketQueue();

    renderGatewayView();

    renderAuditLogs();

    renderAlertCenter();

    renderAnalytics();

    renderUserManagement();

    renderSystemReadiness();

    renderSystemHealth();

    initializeMap();

    applyRolePermissions();


    console.log(
        "DisasterMesh dashboard initialized — Steps 1-30."
    );

}


if (
    document.readyState ===
    "loading"
) {

    document.addEventListener(
        "DOMContentLoaded",
        initializeDashboard,
        {
            once: true
        }
    );

} else {

    initializeDashboard();

}