# Breakfast Dashboard and Coefficient Calculator

This set of tools helps analyze breakfast consumption data and calculate coefficients (consumption per breakfast) for each product on a monthly basis.

## What We've Accomplished

1. **Data Analysis**: Analyzed breakfast attendance and product consumption data to calculate consumption coefficients for each product and month.
2. **Excel Dashboard**: Created a comprehensive Excel dashboard that includes:

   - Monthly breakfast attendance summaries
   - Detailed product consumption data for each month
   - Coefficient calculations (consumption per breakfast attendee)
   - Combined view across all months
3. **Flexible Tools**: Developed Python scripts that allow:

   - Calculating and viewing coefficients for all months
   - Updating the standard file with coefficients from any specific month
   - Creating visualizations in Excel format

## Files

### Input Data

- `standard - Standard .csv`: The original product list with empty coefficient column
- `colazionigiornalierecount2024.csv`: Daily breakfast attendance data
- `unified_consumi_data.csv`: Monthly product consumption data

### Python Scripts

- `calculate_coefficients.py`: Script to calculate coefficients and output them to a CSV file
- `create_dashboard.py`: Script to create an Excel dashboard with monthly coefficients
- `update_standard_coefficients.py`: Script to update the standard file with coefficients from a specific month

### Output Files

- `standard_with_coefficients.csv`: Output of calculate_coefficients.py (combined coefficients)
- `standard_updated.csv`: Output of update_standard_coefficients.py (coefficients from a specific month)
- `breakfast_dashboard.xlsx`: Output of create_dashboard.py (Excel dashboard)

## How to Use

### 1. Calculate Coefficients and Generate CSV

Run the following command:

```bash
python calculate_coefficients.py
```

This will:

- Calculate monthly breakfast attendance totals
- Calculate coefficients for each product and month
- Generate a CSV file (`standard_with_coefficients.csv`) with coefficients listed for each product

### 2. Create Excel Dashboard

Run the following command:

```bash
python create_dashboard.py
```

This will:

- Calculate monthly breakfast attendance totals
- Calculate coefficients for each product and month
- Create an Excel dashboard (`breakfast_dashboard.xlsx`) with the following sheets:
  - Summary: Monthly breakfast attendance totals
  - Monthly sheets (e.g., Aprile, Maggio): Coefficients for each product for that month
  - Coefficienti Mensili: Combined view of coefficients for all months

### 3. Update Standard File with Specific Month

Run the following command:

```bash
python update_standard_coefficients.py
```

You'll be prompted to select a month. Alternatively, you can specify the month directly:

```bash
python update_standard_coefficients.py 5  # For May
```

This will:

- Load coefficients for the selected month from the dashboard Excel file
- Update the standard file with these coefficients
- Generate an updated CSV file (`standard_updated.csv`)

## Understanding the Data

- **Coefficient**: Represents the quantity of a product consumed per breakfast attendee

  - Formula: Quantity Consumed in Month / Total Breakfast Attendance in Month
  - Example: If 100 croissants were consumed in a month with 500 breakfast attendees, the coefficient would be 0.2 (meaning 0.2 croissants per person on average)
- **Monthly Breakfasts**: The total number of breakfast attendees for each month, calculated from the daily data

## Requirements

Python 3.

pandas

openpyxl (for Excel operations)

Install requirements:

```bash
pip install pandas openpyxl
```

## Dashboard Structure

The Excel dashboard includes:

1. **Summary sheet**: Shows the total breakfast attendance for each month
2. **Monthly sheets**: One sheet per month showing:
   - Product details (category, name, article code, unit of measure)
   - Quantity consumed that month
   - Coefficient (consumption per breakfast)
3. **Combined coefficients sheet**: Shows coefficients for all products across all months in a matrix format
# dasboardcolazioni
