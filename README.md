## **P.02 AI Shopping Agent Team**

**Team:** Tom Everson, Sai Zayar Tun

---

### **General Description**
An AI-powered sales and recommendation agent built specifically for our e-commerce platform. The agent retrieves **live product data** directly from the platform via an **MCP (Model Context Protocol) server**, and engages users in a conversational interface to recommend, compare, and guide purchases based on their needs and preferences.

---

### **Core Features**
* **MCP Server Integration:** Direct access to the platform's product database.
* **Conversational Interface:** A natural language sales agent.
* **Personalization:** Product recommendations and user preference memory.
* **Comparison Engine:** Side-by-side product breakdowns.
* **Price Intelligence:** Tracking, deal alerts, and stock handling.
* **Post-Search Support:** Cart assistance and review summarization.

---

### **Product Requirements**

#### **Feature 1: Product Data Access via MCP**
* **PR.1.1. MCP Server Integration:** The platform exposes a dedicated MCP server. The agent calls MCP tools to fetch listings and details—no scraping or third-party APIs required.
* **PR.1.2. Available MCP Tools:**
    | Tool | Function |
    | :--- | :--- |
    | `search_products(query, filters)` | Returns matching products |
    | `get_product(id)` | Returns full product details |
    | `get_reviews(product_id)` | Returns customer reviews |
    | `check_availability(product_id)` | Returns stock status |
    | `get_categories()` | Returns the full category tree |

* **PR.1.3. Structured Product Schema:** Data follows a unified schema: `name`, `price`, `rating`, `review_count`, `availability`, `category`, `url`, `image_url`.
* **PR.1.4. Review Summarization:** The agent uses an LLM to condense reviews into a **2–3 sentence pros/cons summary**.

#### **Feature 2: Conversational Agent**
* **PR.2.1. Natural Language Understanding:** Parses intent (e.g., *"laptop under $800 for video editing"*) to call the appropriate MCP tools.
* **PR.2.2. Guided Clarification:** If a query is ambiguous, the agent asks up to **2 follow-up questions** to narrow preferences.
* **PR.2.3. Recommendation Format:** Returns a ranked list of **3–5 products** with a short justification for each.
* **PR.2.4. Comparison Mode:** Renders a side-by-side breakdown of specs, price, and review sentiment for multiple products.

#### **Feature 3: Personalization & Memory**
* **PR.3.1. Session Preference Tracking:** Remembers budget, brand, and feature preferences within a single session.
* **PR.3.2. Persistent User Profiles (Optional):** If logged in, history is stored to improve future recommendations across sessions.

#### **Feature 4: Price & Availability Intelligence**
* **PR.4.1. Price Drop Alerts:** Users can flag products; the agent notifies them when the price falls below a defined threshold.
* **PR.4.2. Out-of-Stock Handling:** If a product is unavailable, the agent automatically surfaces the closest alternative with a brief explanation.
