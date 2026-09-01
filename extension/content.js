(() => {
    const BACKEND_URL = "http://127.0.0.1:8000/api/products";
    const SIDEBAR_ID = "smart-price-tracker-sidebar";
    let lastUrl = location.href;
    let checkTimeout = null;

    function getCleanAmazonUrl(href = window.location.href) {
        const source = String(href);
        const match = source.match(/https?:\/\/(?:[^/]+\.)?amazon\.in\/(?:dp|gp\/product)\/([A-Z0-9]{10})(?=\/|\?|#|$)/i);
        return match ? `https://www.amazon.in/dp/${match[1].toUpperCase()}` : null;
    }

    function getProductTitle() {
        const titleElement = document.getElementById("productTitle");
        if (titleElement && titleElement.innerText.trim()) {
            return titleElement.innerText.trim();
        }
        const fallbackTitle = document.querySelector("h1")?.innerText?.trim();
        return fallbackTitle || document.title.trim();
    }

    function createSidebar() {
        const cleanUrl = getCleanAmazonUrl();
        
        // If we navigated away from a product page, remove any lingering sidebar completely
        if (!cleanUrl) {
            document.getElementById(SIDEBAR_ID)?.remove();
            return;
        }

        // If the sidebar already exists for THIS specific product, do not recreate it
        const existingSidebar = document.getElementById(SIDEBAR_ID);
        if (existingSidebar) {
            const displayedUrl = existingSidebar.querySelector(".spt-url")?.getAttribute("title");
            if (displayedUrl === cleanUrl) {
                return; // Everything is up to date
            } else {
                // The URL changed! Strip the old sidebar out so we can re-render fresh product data
                existingSidebar.remove();
            }
        }

        const productTitle = getProductTitle();
        // If Amazon is still loading and hasn't drawn the title text yet, defer creation
        if (!productTitle || productTitle === "Amazon.in" || productTitle === "") return;

        const sidebar = document.createElement("div");
        sidebar.id = SIDEBAR_ID;
        sidebar.innerHTML = `
            <div class="spt-panel" role="dialog" aria-label="Smart Price Tracker">
                <div class="spt-header">
                    <div>
                        <div class="spt-kicker">Smart Price Tracker</div>
                        <h2 class="spt-title">Add product to tracker</h2>
                    </div>
                    <button class="spt-close" type="button" aria-label="Close panel">×</button>
                </div>
                <div class="spt-section">
                    <div class="spt-label">Clean URL</div>
                    <div class="spt-value spt-url" title="${cleanUrl}">${cleanUrl}</div>
                </div>
                <div class="spt-section">
                    <div class="spt-label">Product Title</div>
                    <div class="spt-value spt-title" title="${productTitle}">${productTitle}</div>
                </div>
                <div class="spt-section">
                    <label class="spt-label" for="spt-target-price">Target Price (₹)</label>
                    <input id="spt-target-price" class="spt-input" type="number" min="0" step="1" placeholder="Enter target price" />
                </div>
                <div class="spt-actions">
                    <button id="spt-add-button" class="spt-button" type="button">Add to Tracker</button>
                </div>
                <div id="spt-status" class="spt-status" aria-live="polite"></div>
            </div>
        `;

        const style = document.createElement("style");
        style.textContent = `
            #${SIDEBAR_ID} {
                position: fixed;
                top: 96px;
                right: 16px;
                z-index: 2147483647;
                width: 340px;
                max-width: calc(100vw - 32px);
                font-family: Inter, "Segoe UI", Arial, sans-serif;
                color: #172033;
            }
            #${SIDEBAR_ID} .spt-panel {
                background: rgba(255, 255, 255, 0.98);
                backdrop-filter: blur(10px);
                border: 1px solid rgba(23, 32, 51, 0.12);
                border-radius: 18px;
                box-shadow: 0 18px 48px rgba(16, 24, 40, 0.22);
                padding: 16px;
            }
            #${SIDEBAR_ID} .spt-header {
                display: flex;
                align-items: flex-start;
                justify-content: space-between;
                gap: 12px;
                padding-bottom: 12px;
                border-bottom: 1px solid rgba(23, 32, 51, 0.08);
                margin-bottom: 14px;
            }
            #${SIDEBAR_ID} .spt-kicker {
                font-size: 11px;
                font-weight: 700;
                letter-spacing: 0.08em;
                text-transform: uppercase;
                color: #1f6feb;
                margin-bottom: 4px;
            }
            #${SIDEBAR_ID} .spt-title { margin: 0; font-size: 18px; line-height: 1.25; }
            #${SIDEBAR_ID} .spt-close {
                appearance: none; border: 0; background: rgba(23, 32, 51, 0.08);
                color: #172033; width: 30px; height: 30px; border-radius: 999px;
                font-size: 18px; cursor: pointer;
            }
            #${SIDEBAR_ID} .spt-section { margin-bottom: 14px; }
            #${SIDEBAR_ID} .spt-label { display: block; margin-bottom: 6px; font-size: 12px; font-weight: 700; color: #5b667d; }
            #${SIDEBAR_ID} .spt-value { padding: 10px 12px; border: 1px solid rgba(23, 32, 51, 0.12); border-radius: 12px; background: #f8fafc; font-size: 13px; word-break: break-all; max-height: 80px; overflow-y: auto; }
            #${SIDEBAR_ID} .spt-input { width: 100%; padding: 11px 12px; border: 1px solid rgba(23, 32, 51, 0.14); border-radius: 12px; font-size: 14px; outline: none; }
            #${SIDEBAR_ID} .spt-input:focus { border-color: #1f6feb; box-shadow: 0 0 0 3px rgba(31, 111, 235, 0.14); }
            #${SIDEBAR_ID} .spt-button { width: 100%; border: 0; border-radius: 12px; padding: 12px 14px; background: linear-gradient(135deg, #1f6feb 0%, #1454c4 100%); color: #fff; font-size: 14px; font-weight: 700; cursor: pointer; }
            #${SIDEBAR_ID} .spt-status { min-height: 18px; margin-top: 12px; font-size: 12px; color: #5b667d; }
        `;

        document.documentElement.appendChild(style);
        document.body.appendChild(sidebar);

        const closeButton = sidebar.querySelector(".spt-close");
        const addButton = sidebar.querySelector("#spt-add-button");
        const targetPriceInput = sidebar.querySelector("#spt-target-price");
        const statusElement = sidebar.querySelector("#spt-status");

        const setStatus = (message, isError = false) => {
            statusElement.textContent = message;
            statusElement.style.color = isError ? "#b42318" : "#5b667d";
        };

        closeButton.addEventListener("click", () => sidebar.remove());

        addButton.addEventListener("click", async () => {
            const targetPrice = Number(targetPriceInput.value);
            if (!Number.isFinite(targetPrice) || targetPrice <= 0) {
                setStatus("Enter a valid target price greater than zero.", true);
                return;
            }

            const payload = { title: productTitle, url: cleanUrl, target_price: targetPrice };
            addButton.disabled = true;
            setStatus("Saving product to tracker...");

            try {
                const response = await fetch(BACKEND_URL, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(payload),
                });
                if (!response.ok) throw new Error();
                setStatus("Product added to tracker.");
                targetPriceInput.value = "";
            } catch (error) {
                setStatus("Could not connect to backend server. Make sure your FastAPI app is running.", true);
            } finally {
                addButton.disabled = false;
            }
        });
    }

    // 🚀 THE DEBOUNCED ENGINE: Gives Amazon's DOM 400ms to completely finish updating 
    const handlePageChange = () => {
        clearTimeout(checkTimeout);
        checkTimeout = setTimeout(() => {
            createSidebar();
        }, 400);
    };

    const observer = new MutationObserver(() => {
        if (location.href !== lastUrl) {
            lastUrl = location.href;
        }
        handlePageChange();
    });

    observer.observe(document, { subtree: true, childList: true });
    handlePageChange();
})();