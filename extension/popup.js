document.addEventListener("DOMContentLoaded", () => {
	const productList = document.getElementById("product-list");

	if (!productList) {
		return;
	}

	const renderError = () => {
		productList.innerHTML =
			'<p class="empty-state">Could not connect to backend server. Make sure your FastAPI app is running.</p>';
	};

	const createProductCard = (product) => {
		const card = document.createElement("article");
		card.className = "product-card";

		const icon = document.createElement("span");
		icon.className = "product-icon";
		icon.setAttribute("aria-hidden", "true");

		const details = document.createElement("div");
		details.className = "product-details";

		const title = document.createElement("h2");
		title.className = "product-title";
		title.textContent = Object.prototype.hasOwnProperty.call(product, "title") && product.title
			? product.title
			: "Untitled product";

		const meta = document.createElement("p");
		meta.className = "product-meta";
		const hasTargetPrice = Object.prototype.hasOwnProperty.call(product, "target_price");
		const targetPrice = hasTargetPrice ? Number(product.target_price) : Number.NaN;
		meta.textContent = Number.isFinite(targetPrice)
			? `Target price: ₹${targetPrice.toFixed(2)}`
			: "Target price: Not set";

		const aiKey = Object.prototype.hasOwnProperty.call(product, "ai_recommendation")
			? "ai_recommendation"
			: Object.prototype.hasOwnProperty.call(product, "ai_insight")
				? "ai_insight"
				: null;

		if (aiKey && product[aiKey]) {
			const badge = document.createElement("span");
			badge.className = "ai-badge";
			badge.textContent = "AI Recommendation";
			details.appendChild(badge);
		}

		details.append(title, meta);
		card.append(icon, details);

		return card;
	};

	fetch("http://127.0.0.1:8000/api/products")
		.then((response) => {
			if (!response.ok) {
				throw new Error(`Request failed with status ${response.status}`);
			}

			return response.json();
		})
		.then((products) => {
			if (!Array.isArray(products) || products.length === 0) {
				productList.innerHTML = '<p class="empty-state">No tracked products yet.</p>';
				return;
			}

			productList.innerHTML = "";
			products.forEach((product) => {
				productList.appendChild(createProductCard(product));
			});
		})
		.catch(() => {
			renderError();
		});
});
