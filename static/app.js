// Global App State
let forecastChart = null;
let currentProduct = "";
let inventoryData = [];
let cart = [];

// Initialize App
document.addEventListener("DOMContentLoaded", () => {
    // 1. Fetch initial dashboard data
    fetchDashboardData();
    
    // 2. Bind Refresh Button
    document.getElementById("refresh-btn").addEventListener("click", fetchDashboardData);
    
    // 3. Bind Product Select Dropdown for Forecasting
    document.getElementById("product-select").addEventListener("change", (e) => {
        loadForecast(e.target.value);
        highlightActiveItem(e.target.value);
    });

    // 4. Tab Navigation click handlers
    const tabButtons = document.querySelectorAll(".tab-btn");
    const tabPanes = document.querySelectorAll(".tab-pane");

    tabButtons.forEach(btn => {
        btn.addEventListener("click", () => {
            // Toggle active classes
            tabButtons.forEach(b => b.classList.remove("active"));
            tabPanes.forEach(p => p.classList.remove("active"));
            
            btn.classList.add("active");
            const targetTab = btn.getAttribute("data-tab");
            document.getElementById(targetTab).classList.add("active");
        });
    });

    // 5. Wire up POS Pay Button
    const payBtn = document.getElementById("pay-btn");
    if (payBtn) {
        payBtn.addEventListener("click", handleCheckout);
    }

    // 6. Wire up Receipt Modal Close Button
    const closeReceiptBtn = document.getElementById("close-receipt-btn");
    if (closeReceiptBtn) {
        closeReceiptBtn.addEventListener("click", () => {
            document.getElementById("receipt-modal").classList.remove("active");
        });
    }

    // 7. Wire up Restock Form Submit
    const restockForm = document.getElementById("restock-form");
    if (restockForm) {
        restockForm.addEventListener("submit", handleRestock);
    }
});

// Main data fetching orchestrator
async function fetchDashboardData() {
    try {
        await fetchSummary();
        await fetchInventory();
    } catch (error) {
        console.error("Error refreshing dashboard data:", error);
    }
}

// Fetch general store statistics
async function fetchSummary() {
    try {
        const response = await fetch("/api/summary");
        if (!response.ok) throw new Error("Summary API failed");
        const data = await response.json();
        
        // Update DOM
        document.getElementById("stat-revenue").textContent = `₹${data.total_revenue.toLocaleString()}`;
        document.getElementById("stat-top-product").textContent = data.top_selling_product;
        document.getElementById("stat-total-products").textContent = data.total_products;
        
        const alertVal = document.getElementById("stat-alerts");
        alertVal.textContent = data.low_stock_alerts;
        
        // Add flashing effect to container if low stock exists
        const alertCard = document.getElementById("alert-card-container");
        if (data.low_stock_alerts > 0) {
            alertCard.classList.add("critical");
        } else {
            alertCard.classList.remove("critical");
        }
    } catch (e) {
        console.error("Error fetching summary:", e);
    }
}

// Fetch detailed inventory statuses
async function fetchInventory() {
    const listContainer = document.getElementById("inventory-list-container");
    const selectDropdown = document.getElementById("product-select");
    
    try {
        const response = await fetch("/api/inventory");
        if (!response.ok) throw new Error("Inventory API failed");
        const items = await response.json();
        
        // Save items to global state
        inventoryData = items;
        
        listContainer.innerHTML = "";
        
        // Save current selection to restore it
        const previousSelection = selectDropdown.value;
        selectDropdown.innerHTML = "";
        
        items.forEach((item, idx) => {
            // Add option to dropdown
            const option = document.createElement("option");
            option.value = item.product_name;
            option.textContent = item.product_name;
            selectDropdown.appendChild(option);
            
            // Build inventory list card
            const itemCard = document.createElement("div");
            itemCard.className = `inventory-item ${item.product_name === currentProduct ? "active" : ""}`;
            itemCard.dataset.product = item.product_name;
            
            // Calculate progress bar fill (capped at 100)
            const ratio = item.current_stock / item.reorder_level;
            const progressPct = Math.min(100, Math.max(5, Math.round(ratio * 50)));
            
            const statusClass = item.status.toLowerCase();
            
            itemCard.innerHTML = `
                <div class="item-top">
                    <span class="item-name">${item.product_name}</span>
                    <span class="status-tag ${statusClass}">${item.status}</span>
                </div>
                <div class="progress-container">
                    <div class="progress-bar ${statusClass}" style="width: ${progressPct}%"></div>
                </div>
                <div class="item-details">
                    <span>Stock: <strong>${item.current_stock}</strong> / Reorder: ${item.reorder_level}</span>
                    <span>Est. Run Out: <strong>${item.days_remaining} days</strong></span>
                </div>
            `;
            
            // Add click listener
            itemCard.addEventListener("click", () => {
                selectDropdown.value = item.product_name;
                loadForecast(item.product_name);
                highlightActiveItem(item.product_name);
            });
            
            listContainer.appendChild(itemCard);
        });
        
        // Handle initial default load or restore selection
        if (items.length > 0) {
            if (previousSelection && items.some(i => i.product_name === previousSelection)) {
                selectDropdown.value = previousSelection;
                currentProduct = previousSelection;
            } else {
                selectDropdown.selectedIndex = 0;
                currentProduct = items[0].product_name;
            }
            loadForecast(currentProduct);
            highlightActiveItem(currentProduct);
        }
        
        // Update all related UI views
        renderPOSCatalog();
        renderManagerTab();
        
    } catch (e) {
        listContainer.innerHTML = `<div class="loading">Failed to load inventory data: ${e.message}</div>`;
    }
}

// Highlight the active inventory item card on left panel
function highlightActiveItem(productName) {
    currentProduct = productName;
    const cards = document.querySelectorAll(".inventory-item");
    cards.forEach(card => {
        if (card.dataset.product === productName) {
            card.classList.add("active");
        } else {
            card.classList.remove("active");
        }
    });
}

// Fetch forecast calculations and draw/update charts
async function loadForecast(productName) {
    try {
        const response = await fetch(`/api/forecast/${encodeURIComponent(productName)}`);
        if (!response.ok) throw new Error("Forecast API failed");
        const data = await response.json();
        
        // 1. Update Forecast HUD Stats
        const sumForecast = data.forecast.reduce((acc, curr) => acc + curr.quantity, 0);
        document.getElementById("forecast-total").textContent = `${Math.round(sumForecast)} units`;
        
        const trendBadge = document.getElementById("forecast-trend");
        trendBadge.className = `trend-badge ${data.trend.toLowerCase()}`;
        trendBadge.textContent = data.trend;
        
        const slopeVal = document.getElementById("forecast-slope");
        const sign = data.slope > 0 ? "+" : "";
        slopeVal.textContent = `${sign}${data.slope.toFixed(2)} units / day`;
        
        // 2. Prepare Data arrays for Chart.js
        const historyDates = data.history.map(h => formatDate(h.date));
        const forecastDates = data.forecast.map(f => formatDate(f.date));
        const allLabels = [...historyDates, ...forecastDates];
        
        // Build History Series (null for future dates)
        const historySeries = data.history.map(h => h.quantity);
        const historyPadding = Array(data.forecast.length).fill(null);
        const actualsDataset = [...historySeries, ...historyPadding];
        
        // Build Forecast Series (starts at the last historical date to connect lines)
        const forecastSeries = data.forecast.map(f => f.quantity);
        const forecastPadding = Array(data.history.length - 1).fill(null);
        const lastHistoricalValue = historySeries[historySeries.length - 1] || 0;
        const forecastDataset = [...forecastPadding, lastHistoricalValue, ...forecastSeries];
        
        // Render Chart.js
        renderChart(allLabels, actualsDataset, forecastDataset, productName);
        
    } catch (e) {
        console.error("Error loading forecast stats:", e);
    }
}

// Utility to format date strings for clean chart labels
function formatDate(dateStr) {
    const d = new Date(dateStr);
    return d.toLocaleDateString("en-US", { month: "short", day: "numeric" });
}

// Render or Update Chart.js Instance
function renderChart(labels, actualData, forecastData, productName) {
    const ctx = document.getElementById("forecastChart").getContext("2d");
    
    if (forecastChart) {
        forecastChart.destroy();
    }
    
    const actualGradient = ctx.createLinearGradient(0, 0, 0, 300);
    actualGradient.addColorStop(0, "rgba(0, 242, 254, 0.3)");
    actualGradient.addColorStop(1, "rgba(0, 242, 254, 0.0)");
    
    const forecastGradient = ctx.createLinearGradient(0, 0, 0, 300);
    forecastGradient.addColorStop(0, "rgba(255, 184, 0, 0.2)");
    forecastGradient.addColorStop(1, "rgba(255, 184, 0, 0.0)");
    
    forecastChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Actual Sales (90 Days)',
                    data: actualData,
                    borderColor: '#00f2fe',
                    borderWidth: 2,
                    backgroundColor: actualGradient,
                    fill: true,
                    tension: 0.3,
                    pointRadius: 0,
                    pointHoverRadius: 5,
                    pointHitRadius: 10
                },
                {
                    label: 'ML Forecast (Next 7 Days)',
                    data: forecastData,
                    borderColor: '#ffb800',
                    borderWidth: 2,
                    borderDash: [5, 5],
                    backgroundColor: forecastGradient,
                    fill: true,
                    tension: 0.3,
                    pointRadius: 0,
                    pointHoverRadius: 5,
                    pointHitRadius: 10
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    labels: {
                        color: '#9a98af',
                        font: { family: 'Inter', size: 11 }
                    }
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                    backgroundColor: '#161427',
                    titleColor: '#f5f5fa',
                    bodyColor: '#9a98af',
                    borderColor: 'rgba(255, 255, 255, 0.1)',
                    borderWidth: 1
                }
            },
            scales: {
                x: {
                    grid: { color: 'rgba(255, 255, 255, 0.03)' },
                    ticks: {
                        color: '#9a98af',
                        font: { family: 'Inter', size: 10 },
                        maxTicksLimit: 12
                    }
                },
                y: {
                    grid: { color: 'rgba(255, 255, 255, 0.03)' },
                    ticks: {
                        color: '#9a98af',
                        font: { family: 'Inter', size: 10 }
                    },
                    title: {
                        display: true,
                        text: 'Units Sold',
                        color: '#9a98af',
                        font: { family: 'Inter', size: 11 }
                    }
                }
            }
        }
    });
}

// Render POS Product Catalog Cards
function renderPOSCatalog() {
    const catalogContainer = document.getElementById("pos-catalog-container");
    if (!catalogContainer) return;
    
    catalogContainer.innerHTML = "";
    
    inventoryData.forEach(item => {
        const isOutOfStock = item.current_stock <= 0;
        const isLowStock = item.current_stock <= item.reorder_level;
        
        let stockClass = "pos-item-stock";
        let stockText = `Stock: ${item.current_stock} units`;
        if (isOutOfStock) {
            stockClass += " out-warn";
            stockText = "Out of Stock";
        } else if (isLowStock) {
            stockClass += " low-warn";
            stockText = `Low Stock: ${item.current_stock} units`;
        }
        
        const card = document.createElement("div");
        card.className = "pos-item-card glass";
        card.innerHTML = `
            <div>
                <div class="pos-item-name">${item.product_name}</div>
                <div class="${stockClass}">${stockText}</div>
            </div>
            <div class="pos-item-price">₹${item.unit_price.toFixed(2)}</div>
            <button class="pos-add-btn" ${isOutOfStock ? "disabled" : ""}>
                ${isOutOfStock ? "Out of stock" : "Add to Cart"}
            </button>
        `;
        
        // Add to Cart handler
        const addBtn = card.querySelector(".pos-add-btn");
        addBtn.addEventListener("click", () => {
            addToCart(item);
        });
        
        catalogContainer.appendChild(card);
    });
}

// Add an item to the shopping cart
function addToCart(item) {
    const existingItem = cart.find(c => c.product_name === item.product_name);
    const cartQty = existingItem ? existingItem.quantity : 0;
    
    if (cartQty + 1 > item.current_stock) {
        alert(`Insufficient stock. Only ${item.current_stock} units available.`);
        return;
    }
    
    if (existingItem) {
        existingItem.quantity += 1;
    } else {
        cart.push({
            product_name: item.product_name,
            quantity: 1,
            unit_price: item.unit_price
        });
    }
    
    renderCart();
}

// Render cart item rows & calculate totals
function renderCart() {
    const cartContainer = document.getElementById("cart-items-container");
    if (!cartContainer) return;
    
    cartContainer.innerHTML = "";
    
    if (cart.length === 0) {
        cartContainer.innerHTML = `<div class="empty-cart-message">Your shopping cart is empty. Click catalog products to add them.</div>`;
        document.getElementById("pay-btn").disabled = true;
        document.getElementById("cart-subtotal").textContent = "₹0.00";
        document.getElementById("cart-tax").textContent = "₹0.00";
        document.getElementById("cart-total").textContent = "₹0.00";
        return;
    }
    
    let subtotal = 0;
    
    cart.forEach((item, index) => {
        const itemTotal = item.quantity * item.unit_price;
        subtotal += itemTotal;
        
        const invItem = inventoryData.find(i => i.product_name === item.product_name);
        const maxStock = invItem ? invItem.current_stock : 999;
        
        const row = document.createElement("div");
        row.className = "cart-item-row";
        row.innerHTML = `
            <div class="c-item-info">
                <span class="c-item-name">${item.product_name}</span>
                <span class="c-item-price">₹${item.unit_price.toFixed(2)} each</span>
            </div>
            <div class="c-item-controls">
                <button class="cart-qty-btn decrease">-</button>
                <span class="c-item-qty">${item.quantity}</span>
                <button class="cart-qty-btn increase" ${item.quantity >= maxStock ? "disabled" : ""}>+</button>
                <span class="c-item-total">₹${itemTotal.toFixed(2)}</span>
                <button class="c-item-remove">❌</button>
            </div>
        `;
        
        // Decrease quantity
        row.querySelector(".decrease").addEventListener("click", () => {
            if (item.quantity > 1) {
                item.quantity -= 1;
            } else {
                cart.splice(index, 1);
            }
            renderCart();
        });
        
        // Increase quantity
        row.querySelector(".increase").addEventListener("click", () => {
            if (item.quantity < maxStock) {
                item.quantity += 1;
                renderCart();
            } else {
                alert(`Insufficient stock. Only ${maxStock} units of ${item.product_name} are available.`);
            }
        });
        
        // Remove item
        row.querySelector(".c-item-remove").addEventListener("click", () => {
            cart.splice(index, 1);
            renderCart();
        });
        
        cartContainer.appendChild(row);
    });
    
    const tax = subtotal * 0.05;
    const total = subtotal + tax;
    
    document.getElementById("cart-subtotal").textContent = `₹${subtotal.toFixed(2)}`;
    document.getElementById("cart-tax").textContent = `₹${tax.toFixed(2)}`;
    document.getElementById("cart-total").textContent = `₹${total.toFixed(2)}`;
    
    document.getElementById("pay-btn").disabled = false;
}

// Handle cart payment & invoice generation
async function handleCheckout() {
    if (cart.length === 0) return;
    
    const payBtn = document.getElementById("pay-btn");
    
    let subtotal = cart.reduce((sum, item) => sum + (item.quantity * item.unit_price), 0);
    const tax = subtotal * 0.05;
    const totalPaid = subtotal + tax;
    
    const payload = {
        items: cart.map(item => ({
            product_name: item.product_name,
            quantity: item.quantity
        })),
        total_paid: parseFloat(totalPaid.toFixed(2))
    };
    
    try {
        payBtn.disabled = true;
        payBtn.textContent = "Processing Checkout...";
        
        const response = await fetch("/api/checkout", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });
        
        if (!response.ok) {
            const errData = await response.json();
            throw new Error(errData.detail || "Checkout server request failed");
        }
        
        const result = await response.json();
        
        // Display receipt popup
        showReceipt(result, cart, subtotal, tax, totalPaid);
        
        // Reset local cart
        cart = [];
        renderCart();
        
        // Refresh the backend dashboard data (automatically updates stocks in POS UI too)
        await fetchDashboardData();
        
    } catch (error) {
        console.error("Checkout transaction error:", error);
        alert("Transaction Failed: " + error.message);
    } finally {
        payBtn.textContent = "💵 Pay & Generate Receipt";
        payBtn.disabled = cart.length === 0;
    }
}

// Populate and Display Receipt Modal
function showReceipt(result, items, subtotal, tax, total) {
    const modal = document.getElementById("receipt-modal");
    if (!modal) return;
    
    document.getElementById("r-date").textContent = result.timestamp;
    document.getElementById("r-invoice").textContent = result.invoice_id;
    
    const itemsContainer = document.getElementById("r-items-container");
    itemsContainer.innerHTML = "";
    
    items.forEach(item => {
        const itemRow = document.createElement("div");
        itemRow.className = "r-item";
        
        const qtyPart = `${item.quantity}x`;
        const namePart = item.product_name;
        const totalCost = `₹${(item.quantity * item.unit_price).toFixed(2)}`;
        
        itemRow.innerHTML = `
            <span>${qtyPart} ${namePart}</span>
            <span>${totalCost}</span>
        `;
        itemsContainer.appendChild(itemRow);
    });
    
    document.getElementById("r-subtotal").textContent = `₹${subtotal.toFixed(2)}`;
    document.getElementById("r-tax").textContent = `₹${tax.toFixed(2)}`;
    document.getElementById("r-total").textContent = `₹${total.toFixed(2)}`;
    
    modal.classList.add("active");
}

// Render Manager restock dropdown selection & quick inventory checklist
function renderManagerTab() {
    const restockSelect = document.getElementById("restock-product-select");
    const quickStockBody = document.getElementById("quick-stock-tbody");
    
    if (!restockSelect || !quickStockBody) return;
    
    // 1. Populate product dropdown
    const previousSelection = restockSelect.value;
    restockSelect.innerHTML = "";
    
    const defaultOpt = document.createElement("option");
    defaultOpt.value = "";
    defaultOpt.textContent = "-- Select Product to Add --";
    defaultOpt.disabled = true;
    defaultOpt.selected = !previousSelection;
    restockSelect.appendChild(defaultOpt);
    
    inventoryData.forEach(item => {
        const opt = document.createElement("option");
        opt.value = item.product_name;
        opt.textContent = item.product_name;
        if (item.product_name === previousSelection) {
            opt.selected = true;
        }
        restockSelect.appendChild(opt);
    });
    
    // 2. Populate Quick Stock Table rows
    quickStockBody.innerHTML = "";
    
    inventoryData.forEach(item => {
        const row = document.createElement("tr");
        const statusClass = item.status.toLowerCase();
        
        row.innerHTML = `
            <td><strong>${item.product_name}</strong></td>
            <td>${item.current_stock} units</td>
            <td>${item.reorder_level} units</td>
            <td><span class="status-tag ${statusClass}">${item.status}</span></td>
        `;
        quickStockBody.appendChild(row);
    });
}

// Handle restock form submit
async function handleRestock(e) {
    e.preventDefault();
    
    const productSelect = document.getElementById("restock-product-select");
    const qtyInput = document.getElementById("restock-qty");
    
    const productName = productSelect.value;
    const quantity = parseInt(qtyInput.value);
    
    if (!productName || isNaN(quantity) || quantity <= 0) {
        alert("Please select a valid product and input quantity.");
        return;
    }
    
    const form = document.getElementById("restock-form");
    const submitBtn = form.querySelector(".submit-btn");
    
    try {
        submitBtn.disabled = true;
        submitBtn.textContent = "Updating stock...";
        
        const response = await fetch("/api/inventory/add", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                product_name: productName,
                quantity: quantity
            })
        });
        
        if (!response.ok) {
            const errData = await response.json();
            throw new Error(errData.detail || "Restock API error");
        }
        
        const result = await response.json();
        alert(`Stock logged successfully:\n${result.message}`);
        
        // Reset quantity input
        qtyInput.value = "";
        
        // Refresh all store analytics and stock counts
        await fetchDashboardData();
        
    } catch (err) {
        console.error("Restock failed:", err);
        alert("Restock error: " + err.message);
    } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = "📥 Log Inventory Inbound";
    }
}
