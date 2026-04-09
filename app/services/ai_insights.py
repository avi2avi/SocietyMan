from collections import defaultdict


def generate_financial_insights(expenses: list[dict], collections: list[dict]) -> dict:
    category_totals = defaultdict(float)
    for expense in expenses:
        category_totals[expense["category"]] += float(expense["amount"])

    total_expense = sum(category_totals.values())
    total_collection = sum(float(x["amount"]) for x in collections)

    suggestions = []
    for category, amount in category_totals.items():
        if total_expense and amount / total_expense > 0.25:
            suggestions.append(f"Review {category} contracts, high expense share detected")

    return {
        "total_collection": total_collection,
        "total_expense": total_expense,
        "savings_suggestions": suggestions,
    }
