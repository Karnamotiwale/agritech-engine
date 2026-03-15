# pyre-ignore-all-errors
# type: ignore
"""
Carbon Footprint Calculation Service
Calculates farm emissions from multiple agricultural activity sources.
"""

# Emission factors (standard agricultural emission coefficients)
ELECTRICITY_FACTOR = 0.82    # kg CO2 per kWh
FERTILIZER_FACTOR = 6.3      # kg CO2e per kg of nitrogen fertilizer
DIESEL_FACTOR = 2.68         # kg CO2 per liter of diesel
RESIDUE_FACTOR = 1.5         # kg CO2e per kg of crop residue burned


def calculate_carbon_footprint(
    electricity_kwh: float = 0,
    fertilizer_kg: float = 0,
    diesel_liters: float = 0,
    residue_kg: float = 0,
    farm_area_hectare: float = 1.0
) -> dict:
    """
    Calculate carbon emissions from agricultural activities.

    Returns structured emission result with breakdown and per-hectare metrics.
    """
    electricity_emission = round(electricity_kwh * ELECTRICITY_FACTOR, 2)
    fertilizer_emission = round(fertilizer_kg * FERTILIZER_FACTOR, 2)
    fuel_emission = round(diesel_liters * DIESEL_FACTOR, 2)
    residue_emission = round(residue_kg * RESIDUE_FACTOR, 2)

    total_carbon = round(
        electricity_emission + fertilizer_emission + fuel_emission + residue_emission, 2
    )

    area = max(farm_area_hectare, 0.01)  # Prevent division by zero
    carbon_per_hectare = round(total_carbon / area, 2)

    # Emission percentages for recommendation logic
    total_safe = max(total_carbon, 0.01)
    electricity_pct = (electricity_emission / total_safe) * 100
    fertilizer_pct = (fertilizer_emission / total_safe) * 100
    fuel_pct = (fuel_emission / total_safe) * 100
    residue_pct = (residue_emission / total_safe) * 100

    # Sustainability recommendations
    suggestions = _generate_suggestions(
        electricity_kwh, electricity_pct,
        fertilizer_pct,
        diesel_liters, fuel_pct,
        residue_kg, residue_pct,
        carbon_per_hectare
    )

    return {
        "total_carbon": total_carbon,
        "carbon_per_hectare": carbon_per_hectare,
        "electricity_emission": electricity_emission,
        "fertilizer_emission": fertilizer_emission,
        "fuel_emission": fuel_emission,
        "residue_emission": residue_emission,
        "emission_breakdown": {
            "electricity_pct": round(electricity_pct, 1),
            "fertilizer_pct": round(fertilizer_pct, 1),
            "fuel_pct": round(fuel_pct, 1),
            "residue_pct": round(residue_pct, 1),
        },
        "suggestions": suggestions,
        "unit": "kg CO2e"
    }


def _generate_suggestions(
    electricity_kwh, electricity_pct,
    fertilizer_pct,
    diesel_liters, fuel_pct,
    residue_kg, residue_pct,
    carbon_per_hectare
) -> list:
    """Generate sustainability suggestions based on emission profile."""
    suggestions = []

    if fertilizer_pct > 40:
        suggestions.append("Reduce nitrogen fertilizer usage — switch to organic compost or nitrification inhibitors.")

    if electricity_pct > 30 or electricity_kwh > 100:
        suggestions.append("Install solar-powered irrigation pumps to reduce grid electricity dependence.")

    if fuel_pct > 25 or diesel_liters > 50:
        suggestions.append("Replace diesel tractors and pumps with electric or solar farm equipment.")

    if residue_kg > 10:
        suggestions.append("Use composting or mulching instead of burning crop residues.")

    if carbon_per_hectare > 100:
        suggestions.append("Adopt precision farming techniques to optimize resource usage per hectare.")

    if not suggestions:
        suggestions.append("Great work! Your farm's carbon footprint is within sustainable limits. Consider adopting agroforestry for further improvement.")

    suggestions.append("Adopt drip irrigation to reduce water and energy consumption.")
    suggestions.append("Track and benchmark your annual emissions to monitor improvement over time.")

    return suggestions
