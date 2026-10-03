/* =========================================
   DisasterMesh Dashboard
   Phase 1 - Steps 13, 14 and 15
========================================= */


/* =========================================
   CURRENT SESSION
========================================= */

const currentUser = {

    name: "Rescue Operator",

    role: "OPERATOR"

};


/* =========================================
   INCIDENT DATA
========================================= */

const incidents = [

    {
        id: "INC-001",
        category: "Trapped Person",
        priority: "CRITICAL",
        message: "Person trapped inside building. Immediate rescue required.",
        node: "DM-001",
        location: "22.5726, 88.3639",
        latitude: 22.5726,
        longitude: 88.3639,
        status: "NEW",
        assignedTeam: "",
        time: "2 min ago"
    },

    {
        id: "INC-002",
        category: "Medical Emergency",
        priority: "CRITICAL",
        message: "Injured person requires immediate medical assistance.",
        node: "DM-003",
        location: "22.5734, 88.3652",
        latitude: 22.5734,
        longitude: 88.3652,
        status: "ACKNOWLEDGED",
        assignedTeam: "",
        time: "5 min ago"
    },

    {
        id: "INC-003",
        category: "Building Collapse",
        priority: "CRITICAL",
        message: "Collapsed structure reported near the field relay node.",
        node: "DM-004",
        location: "22.5718, 88.3627",
        latitude: 22.5718,
        longitude: 88.3627,
        status: "ASSIGNED",
        assignedTeam: "Rescue Team Alpha",
        time: "8 min ago"
    },

    {
        id: "INC-004",
        category: "Missing Person",
        priority: "HIGH",
        message: "Child reported missing after evacuation.",
        node: "DM-005",
        location: "22.5742, 88.3645",
        latitude: 22.5742,
        longitude: 88.3645,
        status: "IN_PROGRESS",
        assignedTeam: "Rescue Team Bravo",
        time: "11 min ago"
    },

    {
        id: "INC-005",
        category: "Rescue Required",
        priority: "HIGH",
        message: "Immediate rescue team assistance requested.",
        node: "DM-002",
        location: "22.5750, 88.3661",
        latitude: 22.5750,
        longitude: 88.3661,
        status: "NEW",
        assignedTeam: "",
        time: "14 min ago"
    }

];


/* =========================================
   NODE DATA
========================================= */

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
        lastSeen: "2 min ago"
    }

];


/* =========================================
   ROUTE DATA
========================================= */

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


/* =========================================
   MESSAGE DATA
========================================= */

const messages = [

    {
        id: "DM001-00017",
        sender: "DM-001",
        category: "Trapped Person",
        priority: "CRITICAL",
        hopCount: 3,
        ttl: 2,
        status: "DELIVERED",
        time: "2 min ago"
    },

    {
        id: "DM003-00014",
        sender: "DM-003",
        category: "Medical Emergency",
        priority: "CRITICAL",
        hopCount: 2,
        ttl: 3,
        status: "DELIVERED",
        time: "5 min ago"
    },

    {
        id: "DM004-00011",
        sender: "DM-004",
        category: "Building Collapse",
        priority: "CRITICAL",
        hopCount: 2,
        ttl: 3,
        status: "FORWARDED",
        time: "8 min ago"
    },

    {
        id: "DM005-00009",
        sender: "DM-005",
        category: "Missing Person",
        priority: "HIGH",
        hopCount: 3,
        ttl: 2,
        status: "DELIVERED",
        time: "11 min ago"
    },

    {
        id: "DM002-00007",
        sender: "DM-002",
        category: "Rescue Required",
        priority: "HIGH",
        hopCount: 2,
        ttl: 3,
        status: "QUEUED",
        time: "14 min ago"
    },

    {
        id: "DM006-00003",
        sender: "DM-006",
        category: "General Information",
        priority: "LOW",
        hopCount: 0,
        ttl: 5,
        status: "FAILED",
        time: "18 min ago"
    }

];


/* =========================================
   SYSTEM HEALTH DATA
========================================= */

const systemHealth = [

    {
        service: "LoRa Mesh",
        state: "UP",
        description: "Field nodes are exchanging packets.",
        metricLabel: "Active routes",
        metricValue: "3"
    },

    {
        service: "Gateway",
        state: "UP",
        description: "LoRa-to-backend bridge is reachable.",
        metricLabel: "Last packet",
        metricValue: "8 sec ago"
    },

    {
        service: "Backend API",
        state: "UP",
        description: "REST API is accepting dashboard requests.",
        metricLabel: "Response",
        metricValue: "42 ms"
    },

    {
        service: "Database",
        state: "UP",
        description: "SQLite datastore is available.",
        metricLabel: "Records",
        metricValue: "184"
    },

    {
        service: "AI Classifier",
        state: "UP",
        description: "Emergency classification service is ready.",
        metricLabel: "Model",
        metricValue: "TF-IDF + LR"
    },

    {
        service: "GPS Services",
        state: "UP",
        description: "GPS coordinates are available on active nodes.",
        metricLabel: "Valid fixes",
        metricValue: "5 / 6"
    },

    {
        service: "Packet Queue",
        state: "WARNING",
        description: "One message is waiting for a usable route.",
        metricLabel: "Queued",
        metricValue: "1"
    },

    {
        service: "System Logging",
        state: "UP",
        description: "Security and network events are being recorded.",
        metricLabel: "Events",
        metricValue: "62"
    }

];


/* =========================================
   APPLICATION STATE
========================================= */

let selectedIncidentId = null;

let currentFilters = {

    priority: "ALL",

    category: "ALL"

};

let currentMapFilter = "ALL";

let map = null;

let nodeMarkers = {};

let incidentMarkers = {};

let nodeLayer = null;

let incidentLayer = null;


/* =========================================
   NAVIGATION DATA
========================================= */

const viewInformation = {

    dashboard: {

        eyebrow: "RESCUE OPERATIONS",

        title: "Command Dashboard",

        description:
            "Monitor incidents, field nodes and network activity."

    },

    incidents: {

        eyebrow: "RESPONSE MANAGEMENT",

        title: "Incident Management",

        description:
            "Review and manage emergency requests."

    },

    nodes: {

        eyebrow: "FIELD INFRASTRUCTURE",

        title: "Node Management",

        description:
            "Monitor registered field and relay nodes."

    },

    network: {

        eyebrow: "MESH NETWORK",

        title: "Network Operations",

        description:
            "Monitor routes, connectivity and recovery activity."

    },

    messages: {

        eyebrow: "MESSAGE TRAFFIC",

        title: "Message History",

        description:
            "Inspect delivery, routing and packet state."

    },

    settings: {

        eyebrow: "SYSTEM CONFIGURATION",

        title: "Settings",

        description:
            "Dashboard and operator configuration."

    }

};


/* =========================================
   ROLE-BASED ACCESS
========================================= */

function applyRolePermissions() {

    const adminElements =
        document.querySelectorAll(
            ".admin-only"
        );


    adminElements.forEach(element => {

        if (
            currentUser.role ===
            "ADMIN"
        ) {

            element.classList.add(
                "admin-visible"
            );

        } else {

            element.classList.remove(
                "admin-visible"
            );

        }

    });


    document.getElementById(
        "currentUserName"
    ).textContent =
        currentUser.name;


    document.getElementById(
        "currentUserRole"
    ).textContent =
        currentUser.role === "ADMIN"
            ? "Administrator"
            : "Rescue Operator";


    document.getElementById(
        "settingsUserName"
    ).textContent =
        currentUser.name;


    document.getElementById(
        "settingsUserRole"
    ).textContent =
        currentUser.role === "ADMIN"
            ? "Administrator"
            : "Rescue Operator";

}


/* =========================================
   NAVIGATION
========================================= */

function switchView(viewName) {

    const targetView =
        document.getElementById(
            `view-${viewName}`
        );


    if (!targetView) {
        return;
    }


    document
        .querySelectorAll(
            ".page-view"
        )
        .forEach(view => {

            view.classList.remove(
                "active-view"
            );

        });


    targetView.classList.add(
        "active-view"
    );


    document
        .querySelectorAll(
            ".nav-item"
        )
        .forEach(item => {

            item.classList.toggle(
                "active",
                item.dataset.view ===
                    viewName
            );

        });


    const info =
        viewInformation[viewName];


    if (info) {

        document.getElementById(
            "pageEyebrow"
        ).textContent =
            info.eyebrow;


        document.getElementById(
            "pageTitle"
        ).textContent =
            info.title;


        document.getElementById(
            "pageDescription"
        ).textContent =
            info.description;

    }


    if (viewName === "nodes") {

        renderFullNodeTable();

    }


    if (viewName === "network") {

        renderNetworkView();

    }


    if (viewName === "messages") {

        renderFullMessageTable();

    }


    if (viewName === "incidents") {

        renderIncidentManagement();

    }

}


function setupNavigation() {

    document
        .querySelectorAll(
            ".nav-item"
        )
        .forEach(item => {

            item.addEventListener(
                "click",
                event => {

                    event.preventDefault();

                    switchView(
                        item.dataset.view
                    );

                }
            );

        });

}


/* =========================================
   NODE COUNTS
========================================= */

function getActiveNodeCount() {

    return nodes.filter(
        node =>
            node.status ===
            "ONLINE"
    ).length;

}


function getOfflineNodeCount() {

    return nodes.filter(
        node =>
            node.status ===
            "OFFLINE"
    ).length;

}


/* =========================================
   INCIDENT COUNTS
========================================= */

function getCriticalIncidentCount() {

    return incidents.filter(
        incident =>
            incident.priority ===
                "CRITICAL" &&
            incident.status !==
                "RESOLVED" &&
            incident.status !==
                "CANCELLED"
    ).length;

}


function getHighPriorityCount() {

    return incidents.filter(
        incident =>
            incident.priority ===
                "HIGH" &&
            incident.status !==
                "RESOLVED" &&
            incident.status !==
                "CANCELLED"
    ).length;

}


/* =========================================
   UPDATE STATISTICS
========================================= */

function updateStatistics() {

    document.getElementById(
        "activeNodes"
    ).textContent =
        String(
            getActiveNodeCount()
        ).padStart(
            2,
            "0"
        );


    document.getElementById(
        "offlineNodes"
    ).textContent =
        String(
            getOfflineNodeCount()
        ).padStart(
            2,
            "0"
        );


    document.getElementById(
        "criticalIncidents"
    ).textContent =
        String(
            getCriticalIncidentCount()
        ).padStart(
            2,
            "0"
        );


    document.getElementById(
        "highPriority"
    ).textContent =
        String(
            getHighPriorityCount()
        ).padStart(
            2,
            "0"
        );


    document.getElementById(
        "totalMessages"
    ).textContent =
        String(
            messages.length
        ).padStart(
            2,
            "0"
        );

}


/* =========================================
   HELPERS
========================================= */

function getPriorityClass(
    priority
) {

    return `priority-${
        priority.toLowerCase()
    }`;

}


function getStatusClass(
    status
) {

    return `status-${
        status
            .toLowerCase()
            .replaceAll(
                " ",
                "-"
            )
    }`;

}


function getNodeStatusClass(
    status
) {

    return status === "ONLINE"
        ? "node-online"
        : "node-offline";

}


/* =========================================
   INCIDENT FILTERING
========================================= */

function getFilteredIncidents() {

    return incidents.filter(
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

}


/* =========================================
   RENDER INCIDENT QUEUE
========================================= */

function renderIncidents() {

    const incidentList =
        document.getElementById(
            "incidentList"
        );


    const incidentCount =
        document.getElementById(
            "incidentCount"
        );


    const filteredIncidents =
        getFilteredIncidents();


    incidentCount.textContent =
        String(
            filteredIncidents.length
        ).padStart(
            2,
            "0"
        );


    incidentList.innerHTML = "";


    if (
        filteredIncidents.length ===
        0
    ) {

        incidentList.innerHTML = `
            <div class="no-incidents">
                No incidents match the selected filters.
            </div>
        `;

        return;

    }


    filteredIncidents.forEach(
        incident => {

            const element =
                document.createElement(
                    "div"
                );


            element.className =
                "incident-item";


            element.innerHTML = `

                <div class="incident-top">

                    <span class="priority-badge ${getPriorityClass(
                        incident.priority
                    )}">
                        ${incident.priority}
                    </span>

                    <span class="incident-time">
                        ${incident.time}
                    </span>

                </div>

                <div class="incident-title">
                    ${incident.category}
                </div>

                <div class="incident-message">
                    ${incident.message}
                </div>

                <div class="incident-meta">

                    <span>
                        Node: ${incident.node}
                    </span>

                    <span>
                        GPS: ${incident.location}
                    </span>

                </div>

                <div class="incident-status ${getStatusClass(
                    incident.status
                )}">
                    ${incident.status.replaceAll(
                        "_",
                        " "
                    )}
                </div>

            `;


            element.addEventListener(
                "click",
                () =>
                    openIncidentModal(
                        incident.id
                    )
            );


            incidentList.appendChild(
                element
            );

        }
    );

}


/* =========================================
   FILTER EVENTS
========================================= */

function updateFilters() {

    currentFilters.priority =
        document.getElementById(
            "priorityFilter"
        ).value;


    currentFilters.category =
        document.getElementById(
            "categoryFilter"
        ).value;


    renderIncidents();

}


function resetFilters() {

    currentFilters.priority =
        "ALL";


    currentFilters.category =
        "ALL";


    document.getElementById(
        "priorityFilter"
    ).value =
        "ALL";


    document.getElementById(
        "categoryFilter"
    ).value =
        "ALL";


    renderIncidents();

}


function setupFilterEvents() {

    document.getElementById(
        "priorityFilter"
    ).addEventListener(
        "change",
        updateFilters
    );


    document.getElementById(
        "categoryFilter"
    ).addEventListener(
        "change",
        updateFilters
    );


    document.getElementById(
        "resetFilters"
    ).addEventListener(
        "click",
        resetFilters
    );

}


/* =========================================
   INCIDENT WORKFLOW
========================================= */

function getNextStatus(
    status
) {

    const workflow = {

        NEW:
            "ACKNOWLEDGED",

        ACKNOWLEDGED:
            "ASSIGNED",

        ASSIGNED:
            "IN_PROGRESS",

        IN_PROGRESS:
            "RESOLVED"

    };


    return workflow[status] ||
        null;

}


function getStatusActionText(
    status
) {

    const actions = {

        NEW:
            "Acknowledge Incident",

        ACKNOWLEDGED:
            "Assign Incident",

        ASSIGNED:
            "Start Response",

        IN_PROGRESS:
            "Resolve Incident"

    };


    return actions[status] ||
        "";

}


/* =========================================
   WORKFLOW DISPLAY
========================================= */

function updateWorkflow(
    status
) {

    const steps =
        document.querySelectorAll(
            ".workflow-step"
        );


    const lines =
        document.querySelectorAll(
            ".workflow-line"
        );


    const order = [

        "NEW",

        "ACKNOWLEDGED",

        "ASSIGNED",

        "IN_PROGRESS",

        "RESOLVED"

    ];


    steps.forEach(
        step => {

            step.classList.remove(
                "completed",
                "current",
                "cancelled"
            );

        }
    );


    lines.forEach(
        line => {

            line.classList.remove(
                "completed"
            );

        }
    );


    if (
        status ===
        "CANCELLED"
    ) {

        steps.forEach(
            step =>
                step.classList.add(
                    "cancelled"
                )
        );

        return;

    }


    const index =
        order.indexOf(
            status
        );


    steps.forEach(
        (step, stepIndex) => {

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


    lines.forEach(
        (line, lineIndex) => {

            if (
                lineIndex <
                index
            ) {

                line.classList.add(
                    "completed"
                );

            }

        }
    );

}


/* =========================================
   OPEN INCIDENT MODAL
========================================= */

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


    document.getElementById(
        "modalIncidentCategory"
    ).textContent =
        incident.category;


    const priority =
        document.getElementById(
            "modalPriority"
        );


    priority.textContent =
        incident.priority;


    priority.className =
        `priority-badge ${getPriorityClass(
            incident.priority
        )}`;


    const status =
        document.getElementById(
            "modalStatus"
        );


    status.textContent =
        incident.status.replaceAll(
            "_",
            " "
        );


    status.className =
        `incident-status ${getStatusClass(
            incident.status
        )}`;


    document.getElementById(
        "modalMessage"
    ).textContent =
        incident.message;


    document.getElementById(
        "modalId"
    ).textContent =
        incident.id;


    document.getElementById(
        "modalNode"
    ).textContent =
        incident.node;


    document.getElementById(
        "modalLocation"
    ).textContent =
        incident.location;


    document.getElementById(
        "modalTime"
    ).textContent =
        incident.time;


    const assignment =
        document.getElementById(
            "assignmentGroup"
        );


    assignment.style.display =
        incident.status === "NEW"
            ? "none"
            : "flex";


    document.getElementById(
        "assignedTeam"
    ).value =
        incident.assignedTeam ||
        "Rescue Team Alpha";


    const actionButton =
        document.getElementById(
            "statusActionButton"
        );


    const cancelButton =
        document.getElementById(
            "cancelIncidentButton"
        );


    if (
        incident.status ===
            "RESOLVED" ||
        incident.status ===
            "CANCELLED"
    ) {

        actionButton.style.display =
            "none";

        cancelButton.style.display =
            "none";

    } else {

        actionButton.style.display =
            "block";

        cancelButton.style.display =
            "block";

        actionButton.textContent =
            getStatusActionText(
                incident.status
            );

    }


    updateWorkflow(
        incident.status
    );


    document.getElementById(
        "incidentModal"
    ).classList.add(
        "visible"
    );


    document.body.classList.add(
        "modal-open"
    );


    focusMapOnIncident(
        incident
    );

}


/* =========================================
   CLOSE MODAL
========================================= */

function closeIncidentModal() {

    document.getElementById(
        "incidentModal"
    ).classList.remove(
        "visible"
    );


    document.body.classList.remove(
        "modal-open"
    );


    selectedIncidentId =
        null;

}


/* =========================================
   ADVANCE INCIDENT STATUS
========================================= */

function advanceIncidentStatus() {

    if (!selectedIncidentId) {
        return;
    }


    const incident =
        incidents.find(
            item =>
                item.id ===
                selectedIncidentId
        );


    if (!incident) {
        return;
    }


    const nextStatus =
        getNextStatus(
            incident.status
        );


    if (!nextStatus) {
        return;
    }


    if (
        nextStatus ===
        "ASSIGNED"
    ) {

        incident.assignedTeam =
            document.getElementById(
                "assignedTeam"
            ).value;

    }


    incident.status =
        nextStatus;


    renderIncidents();

    renderIncidentManagement();

    updateStatistics();

    openIncidentModal(
        incident.id
    );

}


/* =========================================
   CANCEL INCIDENT
========================================= */

function cancelIncident() {

    if (!selectedIncidentId) {
        return;
    }


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


    renderIncidents();

    renderIncidentManagement();

    updateStatistics();

    openIncidentModal(
        incident.id
    );

}


/* =========================================
   MODAL EVENTS
========================================= */

function setupModalEvents() {

    document.getElementById(
        "closeModal"
    ).addEventListener(
        "click",
        closeIncidentModal
    );


    document.getElementById(
        "modalCloseButton"
    ).addEventListener(
        "click",
        closeIncidentModal
    );


    document.getElementById(
        "statusActionButton"
    ).addEventListener(
        "click",
        advanceIncidentStatus
    );


    document.getElementById(
        "cancelIncidentButton"
    ).addEventListener(
        "click",
        cancelIncident
    );


    document.getElementById(
        "assignedTeam"
    ).addEventListener(
        "change",
        event => {

            if (!selectedIncidentId) {
                return;
            }


            const incident =
                incidents.find(
                    item =>
                        item.id ===
                        selectedIncidentId
                );


            if (incident) {

                incident.assignedTeam =
                    event.target.value;

            }

        }
    );


    document.getElementById(
        "incidentModal"
    ).addEventListener(
        "click",
        event => {

            if (
                event.target.id ===
                "incidentModal"
            ) {

                closeIncidentModal();

            }

        }
    );


    document.addEventListener(
        "keydown",
        event => {

            if (
                event.key ===
                "Escape"
            ) {

                closeIncidentModal();

            }

        }
    );

}


/* =========================================
   MAP
========================================= */

function initializeMap() {

    map =
        L.map(
            "map"
        );


    map.setView(
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


    createNodeMarkers();

    createIncidentMarkers();

    fitAllMapObjects();

}


/* =========================================
   NODE MARKERS
========================================= */

function createNodeMarkers() {

    nodes.forEach(
        node => {

            if (
                !node.gpsValid
            ) {
                return;
            }


            const online =
                node.status ===
                "ONLINE";


            const marker =
                L.circleMarker(
                    [
                        node.latitude,
                        node.longitude
                    ],
                    {

                        radius: 8,

                        color:
                            online
                                ? "#16a34a"
                                : "#dc2626",

                        fillColor:
                            online
                                ? "#16a34a"
                                : "#dc2626",

                        fillOpacity:
                            0.9,

                        weight: 2

                    }
                );


            marker.bindPopup(`
                <div class="map-node-tooltip">

                    <strong>
                        ${node.id}
                    </strong>

                    <br>

                    Status:
                    <strong>
                        ${node.status}
                    </strong>

                    <br>

                    Battery:
                    ${node.battery}%

                    <br>

                    RSSI:
                    ${
                        node.rssi !== null
                            ? `${node.rssi} dBm`
                            : "--"
                    }

                    <br>

                    GPS:
                    ${node.gps}

                </div>
            `);


            marker.on(
                "click",
                () =>
                    focusMapOnNode(
                        node
                    )
            );


            marker.addTo(
                nodeLayer
            );


            nodeMarkers[
                node.id
            ] =
                marker;

        }
    );

}


/* =========================================
   INCIDENT MARKERS
========================================= */

function createIncidentMarkers() {

    incidents.forEach(
        incident => {

            const marker =
                L.circleMarker(
                    [
                        incident.latitude,
                        incident.longitude
                    ],
                    {

                        radius: 10,

                        color: "#dc2626",

                        fillColor:
                            "#dc2626",

                        fillOpacity:
                            0.82,

                        weight: 3

                    }
                );


            marker.bindPopup(`
                <div class="map-node-tooltip">

                    <strong>
                        ${incident.category}
                    </strong>

                    <br>

                    Priority:
                    <strong>
                        ${incident.priority}
                    </strong>

                    <br>

                    Node:
                    ${incident.node}

                    <br>

                    ${incident.message}

                </div>
            `);


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
            ] =
                marker;

        }
    );

}


/* =========================================
   MAP FILTERS
========================================= */

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
            button => {

                button.classList.toggle(
                    "active",
                    button.dataset.mapFilter ===
                        filter
                );

            }
        );


    if (
        filter ===
        "ALL"
    ) {

        if (
            !map.hasLayer(
                nodeLayer
            )
        ) {

            nodeLayer.addTo(
                map
            );

        }


        if (
            !map.hasLayer(
                incidentLayer
            )
        ) {

            incidentLayer.addTo(
                map
            );

        }

    }


    if (
        filter ===
        "NODES"
    ) {

        if (
            map.hasLayer(
                incidentLayer
            )
        ) {

            map.removeLayer(
                incidentLayer
            );

        }


        if (
            !map.hasLayer(
                nodeLayer
            )
        ) {

            nodeLayer.addTo(
                map
            );

        }

    }


    if (
        filter ===
        "INCIDENTS"
    ) {

        if (
            map.hasLayer(
                nodeLayer
            )
        ) {

            map.removeLayer(
                nodeLayer
            );

        }


        if (
            !map.hasLayer(
                incidentLayer
            )
        ) {

            incidentLayer.addTo(
                map
            );

        }

    }

}


function setupMapFilterEvents() {

    document
        .querySelectorAll(
            ".map-control"
        )
        .forEach(
            button => {

                button.addEventListener(
                    "click",
                    () =>
                        setMapFilter(
                            button.dataset.mapFilter
                        )
                );

            }
        );

}


/* =========================================
   MAP FIT / FOCUS
========================================= */

function fitAllMapObjects() {

    const points = [];


    nodes.forEach(
        node => {

            if (
                node.gpsValid
            ) {

                points.push(
                    [
                        node.latitude,
                        node.longitude
                    ]
                );

            }

        }
    );


    incidents.forEach(
        incident => {

            points.push(
                [
                    incident.latitude,
                    incident.longitude
                ]
            );

        }
    );


    if (
        points.length ===
        0
    ) {
        return;
    }


    map.fitBounds(
        L.latLngBounds(
            points
        ),
        {
            padding:
                [30, 30]
        }
    );

}


function focusMapOnIncident(
    incident
) {

    if (!map) {
        return;
    }


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


    const marker =
        incidentMarkers[
            incident.id
        ];


    if (marker) {

        marker.openPopup();

    }

}


function focusMapOnNode(
    node
) {

    if (
        !map ||
        !node.gpsValid
    ) {
        return;
    }


    map.setView(
        [
            node.latitude,
            node.longitude
        ],
        18,
        {
            animate: true
        }
    );


    const marker =
        nodeMarkers[
            node.id
        ];


    if (marker) {

        marker.openPopup();

    }

}


function setupMapButton() {

    document.getElementById(
        "viewFullMapButton"
    ).addEventListener(
        "click",
        () => {

            map.invalidateSize();

            fitAllMapObjects();

        }
    );

}


/* =========================================
   NODE TABLE
========================================= */

function buildNodeRows(
    targetId
) {

    const body =
        document.getElementById(
            targetId
        );


    if (!body) {
        return;
    }


    body.innerHTML = "";


    nodes.forEach(
        node => {

            const row =
                document.createElement(
                    "tr"
                );


            const batteryClass =
                node.battery <
                50
                    ? "battery-low"
                    : "";


            const gpsDisplay =
                node.gpsValid
                    ? "Available"
                    : "Unavailable";


            const gpsClass =
                node.gpsValid
                    ? "gps-valid"
                    : "gps-unavailable";


            const rssiDisplay =
                node.rssi !== null
                    ? `${node.rssi} dBm`
                    : "--";


            row.innerHTML = `

                <td>

                    <span class="node-id">
                        ${node.id}
                    </span>

                </td>


                <td>

                    <span class="node-status ${getNodeStatusClass(
                        node.status
                    )}">

                        <span class="node-status-dot"></span>

                        ${node.status}

                    </span>

                </td>


                <td>

                    <div class="battery-wrapper">

                        <div class="battery-bar">

                            <div
                                class="battery-level ${batteryClass}"
                                style="width: ${node.battery}%"
                            ></div>

                        </div>

                        <span>
                            ${node.battery}%
                        </span>

                    </div>

                </td>


                <td>

                    <span class="rssi-value">
                        ${rssiDisplay}
                    </span>

                </td>


                <td>

                    <span class="${gpsClass}">
                        ${gpsDisplay}
                    </span>

                </td>


                <td>

                    <span class="last-seen">
                        ${node.lastSeen}
                    </span>

                </td>

            `;


            row.addEventListener(
                "click",
                () =>
                    focusMapOnNode(
                        node
                    )
            );


            body.appendChild(
                row
            );

        }
    );

}


function renderNodes() {

    buildNodeRows(
        "nodeTableBody"
    );

}


function renderFullNodeTable() {

    buildNodeRows(
        "fullNodeTableBody"
    );

}


/* =========================================
   ROUTES
========================================= */

function renderRouteRows(
    targetId
) {

    const body =
        document.getElementById(
            targetId
        );


    if (!body) {
        return;
    }


    body.innerHTML = "";


    routes.forEach(
        route => {

            const row =
                document.createElement(
                    "tr"
                );


            const statusClass =
                route.status ===
                "ACTIVE"
                    ? "route-active"
                    : route.status ===
                      "STANDBY"
                        ? "route-standby"
                        : "route-stale";


            row.innerHTML = `

                <td>
                    <strong>
                        ${route.source}
                    </strong>
                </td>

                <td>
                    ${route.destination}
                </td>

                <td>
                    ${route.nextHop}
                </td>

                <td>
                    ${route.hopCount}
                </td>

                <td>
                    <span class="route-quality">
                        ${route.quality}
                    </span>
                </td>

                <td>
                    <span class="route-status ${statusClass}">
                        ${route.status}
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


    renderNetworkTopology();

}


/* =========================================
   NETWORK TOPOLOGY
========================================= */

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

    "GATEWAY": {
        x: 84,
        y: 50
    }

};


function drawTopology(
    svgId,
    nodeContainerId
) {

    const svg =
        document.getElementById(
            svgId
        );


    const container =
        document.getElementById(
            nodeContainerId
        );


    if (
        !svg ||
        !container
    ) {
        return;
    }


    svg.innerHTML = "";

    container.innerHTML = "";


    const connections = [

        {
            from: "DM-001",
            to: "DM-002",
            state: "active"
        },

        {
            from: "DM-002",
            to: "DM-003",
            state: "active"
        },

        {
            from: "DM-003",
            to: "GATEWAY",
            state: "active"
        },

        {
            from: "DM-001",
            to: "DM-004",
            state: "standby"
        },

        {
            from: "DM-004",
            to: "DM-003",
            state: "standby"
        },

        {
            from: "DM-004",
            to: "DM-005",
            state: "standby"
        },

        {
            from: "DM-006",
            to: "DM-004",
            state: "offline"
        }

    ];


    connections.forEach(
        connection => {

            const from =
                topologyPositions[
                    connection.from
                ];


            const to =
                topologyPositions[
                    connection.to
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
                `${from.x}%`
            );


            line.setAttribute(
                "y1",
                `${from.y}%`
            );


            line.setAttribute(
                "x2",
                `${to.x}%`
            );


            line.setAttribute(
                "y2",
                `${to.y}%`
            );


            line.classList.add(
                "route-line"
            );


            if (
                connection.state ===
                "active"
            ) {

                line.classList.add(
                    "active"
                );

            }


            if (
                connection.state ===
                "offline"
            ) {

                line.classList.add(
                    "offline"
                );

            }


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


            element.innerHTML = `

                <span class="topology-node-id">
                    ${node.id}
                </span>

                <span class="topology-node-status">

                    <span class="topology-node-dot ${
                        online
                            ? "online"
                            : "offline"
                    }"></span>

                    ${node.status}

                </span>

            `;


            container.appendChild(
                element
            );

        }
    );


    const gateway =
        topologyPositions[
            "GATEWAY"
        ];


    const gatewayElement =
        document.createElement(
            "div"
        );


    gatewayElement.className =
        "topology-node gateway-node";


    gatewayElement.style.left =
        `${gateway.x}%`;


    gatewayElement.style.top =
        `${gateway.y}%`;


    gatewayElement.innerHTML = `

        <span class="topology-node-id gateway-label">
            GATEWAY
        </span>

        <span class="topology-node-status">
            LoRa Bridge
        </span>

    `;


    container.appendChild(
        gatewayElement
    );

}


function renderTopology() {

    drawTopology(
        "topologySvg",
        "topologyNodes"
    );

}


function renderNetworkTopology() {

    drawTopology(
        "networkTopologySvg",
        "networkTopologyNodes"
    );

}


/* =========================================
   MESSAGE TABLE
========================================= */

function getMessageStatusClass(
    status
) {

    if (
        status ===
        "DELIVERED"
    ) {

        return "message-delivered";

    }


    if (
        status ===
        "QUEUED"
    ) {

        return "message-queued";

    }


    if (
        status ===
        "FORWARDED"
    ) {

        return "message-forwarded";

    }


    return "message-failed";

}


function buildMessageRows(
    targetId
) {

    const body =
        document.getElementById(
            targetId
        );


    if (!body) {
        return;
    }


    body.innerHTML = "";


    messages.forEach(
        message => {

            const row =
                document.createElement(
                    "tr"
                );


            row.innerHTML = `

                <td>

                    <span class="message-id">
                        ${message.id}
                    </span>

                </td>

                <td>
                    ${message.sender}
                </td>

                <td>
                    ${message.category}
                </td>

                <td>

                    <span class="priority-badge ${getPriorityClass(
                        message.priority
                    )}">
                        ${message.priority}
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
                        ${message.status}
                    </span>

                </td>

                <td>
                    ${message.time}
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

    buildMessageRows(
        "messageTableBody"
    );


    document.getElementById(
        "messageCount"
    ).textContent =
        String(
            messages.length
        ).padStart(
            2,
            "0"
        );

}


function renderFullMessageTable() {

    buildMessageRows(
        "fullMessageTableBody"
    );

}


function showMessageDetails(
    message
) {

    alert(
        `Message ID: ${message.id}\n\n` +
        `Sender: ${message.sender}\n` +
        `Category: ${message.category}\n` +
        `Priority: ${message.priority}\n` +
        `Hop Count: ${message.hopCount}\n` +
        `TTL Remaining: ${message.ttl}\n` +
        `Status: ${message.status}\n` +
        `Time: ${message.time}`
    );

}


/* =========================================
   INCIDENT MANAGEMENT VIEW
========================================= */

function renderIncidentManagement() {

    const container =
        document.getElementById(
            "incidentManagementList"
        );


    if (!container) {
        return;
    }


    container.innerHTML = "";


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
                        ${incident.priority}
                    </span>

                    <span class="incident-time">
                        ${incident.time}
                    </span>

                </div>


                <div class="incident-title">
                    ${incident.category}
                </div>


                <div class="incident-message">
                    ${incident.message}
                </div>


                <div class="incident-meta">

                    <span>
                        ID: ${incident.id}
                    </span>

                    <span>
                        Node: ${incident.node}
                    </span>

                    <span>
                        Team:
                        ${
                            incident.assignedTeam
                                || "Unassigned"
                        }
                    </span>

                </div>


                <div class="incident-status ${getStatusClass(
                    incident.status
                )}">
                    ${incident.status.replaceAll(
                        "_",
                        " "
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


/* =========================================
   SYSTEM HEALTH
========================================= */

function renderSystemHealth() {

    const container =
        document.getElementById(
            "systemHealthGrid"
        );


    container.innerHTML = "";


    systemHealth.forEach(
        service => {

            const card =
                document.createElement(
                    "div"
                );


            let stateClass =
                "health-down";


            if (
                service.state ===
                "UP"
            ) {

                stateClass =
                    "health-up";

            }


            if (
                service.state ===
                "WARNING"
            ) {

                stateClass =
                    "health-warning";

            }


            card.className =
                "health-card";


            card.innerHTML = `

                <div class="health-card-top">

                    <span class="health-service">
                        ${service.service}
                    </span>

                    <span class="health-state ${stateClass}">

                        <span class="health-state-dot"></span>

                        ${service.state}

                    </span>

                </div>


                <p class="health-description">
                    ${service.description}
                </p>


                <div class="health-metric">

                    <span class="health-metric-label">
                        ${service.metricLabel}
                    </span>

                    <span class="health-metric-value">
                        ${service.metricValue}
                    </span>

                </div>

            `;


            container.appendChild(
                card
            );

        }
    );

}


/* =========================================
   INITIALIZE
========================================= */

document.addEventListener(
    "DOMContentLoaded",
    () => {

        applyRolePermissions();

        setupNavigation();

        updateStatistics();

        renderIncidents();

        renderNodes();

        renderRoutes();

        renderTopology();

        renderMessages();

        renderSystemHealth();

        setupFilterEvents();

        setupModalEvents();

        setupMapFilterEvents();

        setupMapButton();

        initializeMap();

        console.log(
            "DisasterMesh dashboard initialized."
        );

    }
);