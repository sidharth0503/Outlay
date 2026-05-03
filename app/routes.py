"""Outlay – Advanced API route definitions (v1.1.0).

Production-grade expense-tracking endpoints backed by in-memory data
structures.  Supports full CRUD for bills, category-based budgeting,
and real-time analytics with budget-variance calculations.
"""

from flask import render_template, jsonify, request

from app import app

# ---------------------------------------------------------------------------
# In-memory data stores
# ---------------------------------------------------------------------------

bills = [
    {
        "id": 1,
        "name": "Netflix",
        "amount": 15.99,
        "dueDate": "2026-05-15",
        "category": "Entertainment",
        "status": "pending",
    },
    {
        "id": 2,
        "name": "Electric Bill",
        "amount": 120.00,
        "dueDate": "2026-05-01",
        "category": "Utilities",
        "status": "paid",
    },
    {
        "id": 3,
        "name": "Rent",
        "amount": 1400.00,
        "dueDate": "2026-05-01",
        "category": "Housing",
        "status": "pending",
    },
    {
        "id": 4,
        "name": "Spotify",
        "amount": 9.99,
        "dueDate": "2026-05-20",
        "category": "Entertainment",
        "status": "paid",
    },
]

budgets = {
    "Utilities": 200.00,
    "Entertainment": 50.00,
    "Housing": 1500.00,
}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _next_bill_id():
    """Return the next available bill ID."""
    return max(b["id"] for b in bills) + 1 if bills else 1


def _find_bill(bill_id):
    """Look up a bill by its integer ID.

    Returns
    -------
    tuple[dict | None, int | None]
        The bill dict and its list index, or (None, None) when not found.
    """
    for idx, bill in enumerate(bills):
        if bill["id"] == bill_id:
            return bill, idx
    return None, None


# ---------------------------------------------------------------------------
# Routes – Health-check
# ---------------------------------------------------------------------------


@app.route("/", methods=["GET"])
def index():
    """Serve the Outlay dashboard frontend."""
    return render_template("index.html")


@app.route("/api/health", methods=["GET"])
def health_check():
    """Return a simple health-check response with the current API version."""
    return jsonify({"status": "Outlay API is running", "version": "1.1.0"}), 200


# ---------------------------------------------------------------------------
# Routes – Bills CRUD
# ---------------------------------------------------------------------------


@app.route("/api/bills", methods=["GET"])
def get_bills():
    """Return all bills, optionally filtered by query parameters.

    Supported query parameters
    --------------------------
    - **category** – exact-match filter on bill category.
    - **status**   – exact-match filter on bill status (``pending`` | ``paid``).

    Both filters may be combined.
    """
    result = bills

    category = request.args.get("category")
    if category:
        result = [b for b in result if b["category"].lower() == category.lower()]

    status = request.args.get("status")
    if status:
        result = [b for b in result if b["status"].lower() == status.lower()]

    return jsonify(result), 200


@app.route("/api/bills", methods=["POST"])
def add_bill():
    """Add a new bill from a JSON payload.

    Required fields
    ----------------
    - **name**     (str):   Human-readable bill / subscription name.
    - **amount**   (float): Dollar amount due.
    - **dueDate**  (str):   ISO-formatted due date (e.g. ``2026-06-01``).
    - **category** (str):   Spending category (e.g. ``Utilities``).

    Optional fields
    ----------------
    - **status** (str): Defaults to ``"pending"`` if omitted.

    Returns
    -------
    201 Created  – with the newly added bill.
    400 Bad Request – if any required field is missing or body is invalid.
    """
    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": "Request body must be valid JSON"}), 400

    required = ("name", "amount", "dueDate", "category")
    missing = [f for f in required if f not in data]
    if missing:
        return (
            jsonify({"error": f"Missing required field(s): {', '.join(missing)}"}),
            400,
        )

    new_bill = {
        "id": _next_bill_id(),
        "name": data["name"],
        "amount": data["amount"],
        "dueDate": data["dueDate"],
        "category": data["category"],
        "status": data.get("status", "pending"),
    }

    bills.append(new_bill)
    return jsonify(new_bill), 201


@app.route("/api/bills/<int:bill_id>", methods=["PUT"])
def update_bill(bill_id):
    """Fully update an existing bill.

    The request body should contain **all** bill fields that need updating.
    Fields not supplied will retain their current values.

    Returns
    -------
    200 OK       – with the updated bill.
    404 Not Found – if no bill matches the given ID.
    400 Bad Request – if body is invalid JSON.
    """
    bill, _ = _find_bill(bill_id)

    if bill is None:
        return jsonify({"error": f"Bill with id {bill_id} not found"}), 404

    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Request body must be valid JSON"}), 400

    updatable = ("name", "amount", "dueDate", "category", "status")
    for field in updatable:
        if field in data:
            bill[field] = data[field]

    return jsonify(bill), 200


@app.route("/api/bills/<int:bill_id>/pay", methods=["PATCH"])
def pay_bill(bill_id):
    """Mark a bill as paid.

    This is a dedicated, intent-specific endpoint that sets the bill's
    ``status`` to ``"paid"``.  No request body is required.

    Returns
    -------
    200 OK       – with the updated bill.
    404 Not Found – if no bill matches the given ID.
    """
    bill, _ = _find_bill(bill_id)

    if bill is None:
        return jsonify({"error": f"Bill with id {bill_id} not found"}), 404

    bill["status"] = "paid"
    return jsonify(bill), 200


@app.route("/api/bills/<int:bill_id>", methods=["DELETE"])
def delete_bill(bill_id):
    """Delete a bill by ID.

    Returns
    -------
    200 OK       – confirmation message with the deleted bill.
    404 Not Found – if no bill matches the given ID.
    """
    bill, idx = _find_bill(bill_id)

    if bill is None:
        return jsonify({"error": f"Bill with id {bill_id} not found"}), 404

    bills.pop(idx)
    return jsonify({"message": f"Bill {bill_id} deleted", "bill": bill}), 200


# ---------------------------------------------------------------------------
# Routes – Budgets
# ---------------------------------------------------------------------------


@app.route("/api/budgets", methods=["GET"])
def get_budgets():
    """Return all category budget limits."""
    return jsonify(budgets), 200


@app.route("/api/budgets", methods=["POST"])
def set_budget():
    """Add or update a category budget limit.

    Required fields
    ----------------
    - **category** (str):  The spending category name.
    - **limit**    (float): The maximum spending limit.

    Returns
    -------
    200 OK          – if an existing category limit was updated.
    201 Created     – if a new category limit was added.
    400 Bad Request – if required fields are missing or body is invalid.
    """
    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": "Request body must be valid JSON"}), 400

    missing = [f for f in ("category", "limit") if f not in data]
    if missing:
        return (
            jsonify({"error": f"Missing required field(s): {', '.join(missing)}"}),
            400,
        )

    category = data["category"]
    is_update = category in budgets
    budgets[category] = data["limit"]

    status_code = 200 if is_update else 201
    action = "updated" if is_update else "created"
    return (
        jsonify({
            "message": f"Budget for '{category}' {action}",
            "budgets": budgets,
        }),
        status_code,
    )


# ---------------------------------------------------------------------------
# Routes – Analytics
# ---------------------------------------------------------------------------


@app.route("/api/analytics", methods=["GET"])
def get_analytics():
    """Return real-time financial analytics across all bills and budgets.

    Response fields
    ----------------
    - **total_spend**      – Sum of every bill's ``amount``.
    - **unpaid_balance**   – Sum of amounts where ``status == "pending"``.
    - **budget_variance**  – Per-category breakdown containing:
        - *limit*:            The budgeted spending cap.
        - *current_spend*:    Actual spend in the category.
        - *remaining_budget*: ``limit - current_spend`` (negative = over budget).
    """
    total_spend = sum(b["amount"] for b in bills)
    unpaid_balance = sum(b["amount"] for b in bills if b["status"] == "pending")

    # Build per-category actual spend from bills.
    category_spend = {}
    for bill in bills:
        cat = bill["category"]
        category_spend[cat] = category_spend.get(cat, 0.0) + bill["amount"]

    # Compute variance for every budgeted category.
    budget_variance = {}
    for cat, limit in budgets.items():
        spent = category_spend.get(cat, 0.0)
        budget_variance[cat] = {
            "limit": limit,
            "current_spend": round(spent, 2),
            "remaining_budget": round(limit - spent, 2),
        }

    return (
        jsonify({
            "total_spend": round(total_spend, 2),
            "unpaid_balance": round(unpaid_balance, 2),
            "budget_variance": budget_variance,
        }),
        200,
    )
