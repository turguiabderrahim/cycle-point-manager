# Bicycle Rental Point Management System

A Python-based management and analytics tool for bicycle rental networks. This system allows administrators to track fleet health, calculate inventory value, and analyze bicycle usage across multiple rental locations using data-driven insights.

## ✨ Features

- **Multi-Point Data Loading**: Import rental point data from separate `.txt` files automatically or via command-line arguments.
- **Fleet Analytics**:
  - Categorize bicycles as "Usable" or "Unusable" based on a customizable maximum age.
  - Calculate total inventory value and average age per rental point.
  - Identify specific bicycle types (e.g., City bikes) across the network.
- **Global Insights**: Find the oldest bicycle in the entire fleet and view a combined summary of all rental points.
- **Robust Error Handling**: Skips malformed data rows and provides warnings without crashing the system.

## 🛠️ Technical Implementation

The system is built using Object-Oriented Programming (OOP) principles:
- **`Bicycle` Class**: Stores manufacturer, manufacturing year, price, and purpose. It includes methods for age calculation and usability checks.
- **`Point` Class**: Manages a collection of bicycles, handles file I/O via class methods, and generates detailed statistical reports.

## 🚀 Getting Started

### Prerequisites
- Python 3.7 or higher

### Data Format
Each rental point requires a `.txt` file following this structure:
```text
[Point Name]
[Manufacturer],[Year],[Price],[Purpose]
