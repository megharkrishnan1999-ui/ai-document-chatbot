const API_URL = "http://127.0.0.1:8000";


// =============================
// TAB SWITCHING
// =============================

function openTab(tabId, button) {

    document.querySelectorAll(".tab-content")
        .forEach(tab => {

            tab.classList.remove("active");

        });


    document.querySelectorAll(".tab-button")
        .forEach(btn => {

            btn.classList.remove("active");

        });


    document.getElementById(tabId)
        .classList.add("active");


    button.classList.add("active");
}


// =============================
// FILE SELECTION
// =============================

const pdfInput =
    document.getElementById("pdfFile");


pdfInput.addEventListener("change", function () {

    const selectedFile =
        document.getElementById("selectedFile");


    if (!this.files.length) {

        selectedFile.innerHTML = "";

        return;
    }


    const file = this.files[0];


    if (file.type !== "application/pdf") {

        selectedFile.innerHTML =
            "❌ Please select a PDF file.";

        this.value = "";

        return;
    }


    selectedFile.innerHTML =
        `📄 ${file.name}`;

});


// =============================
// DRAG & DROP
// =============================

const dropZone =
    document.getElementById("dropZone");


dropZone.addEventListener(
    "dragover",
    function (event) {

        event.preventDefault();

        dropZone.classList.add("dragging");

    }
);


dropZone.addEventListener(
    "dragleave",
    function () {

        dropZone.classList.remove("dragging");

    }
);


dropZone.addEventListener(
    "drop",
    function (event) {

        event.preventDefault();

        dropZone.classList.remove("dragging");


        const files =
            event.dataTransfer.files;


        if (!files.length) {

            return;
        }


        const file = files[0];


        if (file.type !== "application/pdf") {

            alert("Only PDF files are supported.");

            return;
        }


        /*
         * Assign the dropped file to the
         * file input.
         */

        const dataTransfer =
            new DataTransfer();

        dataTransfer.items.add(file);

        pdfInput.files =
            dataTransfer.files;


        document.getElementById("selectedFile")
            .innerHTML =
            `📄 ${file.name}`;

    }
);


// =============================
// UPLOAD PDF
// =============================

async function uploadPDF() {

    const fileInput =
        document.getElementById("pdfFile");

    const status =
        document.getElementById("uploadStatus");

    const documentInfo =
        document.getElementById("documentInfo");


    if (!fileInput.files.length) {

        status.innerHTML =
            "⚠️ Please select a PDF file.";

        return;
    }


    const file =
        fileInput.files[0];


    if (file.type !== "application/pdf") {

        status.innerHTML =
            "❌ Only PDF files are supported.";

        return;
    }


    const formData =
        new FormData();

    formData.append("file", file);


    status.innerHTML =
        "⏳ Processing document...";


    documentInfo.classList.add("hidden");


    try {

        const response =
            await fetch(
                `${API_URL}/documents/upload`,
                {
                    method: "POST",
                    body: formData
                }
            );


        const data =
            await response.json();


        if (!response.ok) {

            status.innerHTML =
                `❌ ${data.detail || "Upload failed."}`;

            return;
        }


        status.innerHTML =
            "✓ Document processed successfully.";


        documentInfo.classList.remove("hidden");


        document.getElementById(
            "documentDetails"
        ).innerText =
            `${data.filename} • ${data.chunk_count} chunks indexed`;
        loadDocuments();

    }

    catch (error) {

        console.error(error);

        status.innerHTML =
            "❌ Could not connect to the backend.";

    }
}


// =============================
// ASK QUESTION
// =============================

async function askQuestion() {

    const input =
        document.getElementById("question");


    const question =
        input.value.trim();


    if (!question) {

        return;
    }


    const chatMessages =
        document.getElementById("chatMessages");


    // USER MESSAGE

    chatMessages.innerHTML += `

        <div class="user-message">

            <div class="message">

                ${escapeHtml(question)}

            </div>

        </div>

    `;


    input.value = "";


    // LOADING

    const loadingId =
        "loading-" + Date.now();


    chatMessages.innerHTML += `

        <div
            class="ai-message"
            id="${loadingId}">

            <div class="message">

                🤖 Thinking...

            </div>

        </div>

    `;


    scrollChat();


    try {

        const response =
            await fetch(
                `${API_URL}/chat`,
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({
                        question: question
                    })
                }
            );


        const data =
            await response.json();


        const loading =
            document.getElementById(loadingId);


        if (!response.ok) {

            loading.innerHTML = `

                <div class="message">

                    ❌ Something went wrong.

                </div>

            `;

            return;
        }


        // =========================
        // SOURCES
        // =========================

        let sourcesHTML = "";


        if (
            data.metadata &&
            data.metadata.length > 0
        ) {

            sourcesHTML = `

                <div class="sources">

                    <div class="sources-title">
                        📚 Sources
                    </div>

                    ${data.metadata.map(
                        (source, index) => `

                        <div class="source-item">

                            📄
                            <strong>
                                ${escapeHtml(
                                    source.filename
                                )}
                            </strong>

                            <span>
                                — Chunk
                                ${source.chunk_id}
                            </span>

                        </div>

                    `).join("")}

                </div>

            `;

        }


        // =========================
        // ANSWER
        // =========================

        loading.innerHTML = `

            <div class="message">

                <strong>
                    🤖 AI Assistant
                </strong>

                <p>
                    ${formatAnswer(data.answer)}
                </p>

                ${sourcesHTML}

            </div>

        `;


    }

    catch (error) {

        console.error(error);


        const loading =
            document.getElementById(loadingId);


        loading.innerHTML = `

            <div class="message">

                ❌ Could not connect to the backend.

            </div>

        `;

    }


    scrollChat();
}


// =============================
// ENTER KEY
// =============================

function handleEnter(event) {

    if (event.key === "Enter") {

        event.preventDefault();

        askQuestion();

    }

}


// =============================
// CLEAR CHAT
// =============================

function clearChat() {

    const chatMessages =
        document.getElementById("chatMessages");


    chatMessages.innerHTML = `

        <div class="welcome-message">

            <div class="welcome-icon">
                🤖
            </div>

            <div>

                <h3>
                    AI Document Assistant
                </h3>

                <p>
                    Ask me anything about
                    your uploaded document.
                </p>

            </div>

        </div>

    `;

}


// =============================
// SCROLL CHAT
// =============================

function scrollChat() {

    const chatMessages =
        document.getElementById("chatMessages");


    chatMessages.scrollTop =
        chatMessages.scrollHeight;

}


// =============================
// SECURITY HELPER
// =============================

function escapeHtml(text) {

    const div =
        document.createElement("div");


    div.textContent = text;


    return div.innerHTML;

}


// =============================
// FORMAT ANSWER
// =============================

function formatAnswer(text) {

    if (!text) {

        return "No answer was generated.";

    }


    return escapeHtml(text)
        .replace(/\n/g, "<br>");

}

// =============================
// LOAD DOCUMENTS
// =============================

async function loadDocuments() {

    const documentList =
        document.getElementById("documentList");

    documentList.innerHTML = `
        <div class="document-loading">
            ⏳ Loading documents...
        </div>
    `;

    try {

        const response =
            await fetch(
                `${API_URL}/documents`
            );

        const data =
            await response.json();

        if (!response.ok) {

            documentList.innerHTML = `
                <div class="document-error">
                    ❌ Could not load documents.
                </div>
            `;

            return;
        }

        const documents =
            data.documents || [];

        if (documents.length === 0) {

            documentList.innerHTML = `
                <div class="empty-documents">

                    <div class="empty-icon">
                        📂
                    </div>

                    <strong>
                        No documents uploaded yet
                    </strong>

                    <p>
                        Upload a PDF to get started.
                    </p>

                </div>
            `;

            return;
        }


        documentList.innerHTML =
            documents.map(document => {

                const statusClass =
                    document.exists
                        ? "available"
                        : "missing";

                const statusText =
                    document.exists
                        ? "Available"
                        : "PDF file missing";

                return `

                    <div class="document-item">

                        <div class="document-icon">
                            📄
                        </div>


                        <div class="document-details">

                            <strong>
                                ${escapeHtml(
                                    document.filename
                                )}
                            </strong>

                            <div class="document-meta">

                                <span>
                                    ${document.chunk_count}
                                    chunks
                                </span>

                                <span class="${statusClass}">
                                    ${statusText}
                                </span>

                            </div>

                        </div>


                        <button
                            class="delete-document-button"
                            onclick="deleteDocument(
                                '${escapeHtml(
                                    document.filename
                                )}'
                            )">

                            🗑

                        </button>

                    </div>

                `;

            }).join("");

    }

    catch (error) {

        console.error(error);

        documentList.innerHTML = `
            <div class="document-error">
                ❌ Could not connect to the backend.
            </div>
        `;
    }
}

// =============================
// DELETE DOCUMENT
// =============================

async function deleteDocument(filename) {

    const confirmed =
        confirm(
            `Delete "${filename}"?\n\nThis will remove the document from the chatbot's knowledge base.`
        );

    if (!confirmed) {
        return;
    }


    try {

        const response =
            await fetch(
                `${API_URL}/documents/${encodeURIComponent(filename)}`,
                {
                    method: "DELETE"
                }
            );


        const data =
            await response.json();


        if (!response.ok) {

            alert(
                data.detail ||
                "Could not delete the document."
            );

            return;
        }


        alert(
            "Document deleted successfully."
        );


        // Refresh document list
        loadDocuments();

    }

    catch (error) {

        console.error(error);

        alert(
            "Could not connect to the backend."
        );

    }
}

// =============================
// INITIALIZE DOCUMENT LIBRARY
// =============================

loadDocuments();