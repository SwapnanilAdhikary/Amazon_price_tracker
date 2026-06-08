# E-Commerce Price Tracker & AI Assistant

Welcome to the repository! This project is a collaborative effort to build an intelligent price tracking system that integrates directly into e-commerce platforms (like Amazon, Flipkart, etc.) via a browser extension, enhanced by an AI analysis layer.

The long-term goal is to build an intelligent shopping assistant that not only tracks prices but also uses AI to provide buying recommendations, price predictions, and market insights.

---

## 🤝 Collaboration Workflow (How We Work)

To keep our main code stable and avoid merge conflicts, we will use a **Feature Branch Workflow**. Please follow these steps for every new change:

1. **Pull the latest changes:** Always start by ensuring your local `main` branch is up to date.
   ```bash
   git checkout main
   git pull origin main

2. **Create a feature branch:** Name your branch descriptively (e.g., feature/scraper-amazon, feature/popup-ui).
   ```bash
   git checkout -b feature/your-feature-name

3. **Commit your work:** Make clear, concise commit messages.
   ```bash
   git commit -m "Add basic scraping logic for Amazon product pages"

4. **Push and Open a Pull Request (PR):** Push your branch to GitHub and open a PR for review. Do not merge directly into main without a quick review from the other collaborator!
   ```bash
   git push origin feature/your-feature-name
