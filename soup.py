import pdfplumber
import pandas as pd

# Function to truncate text to ensure it does not exceed the max length
def truncate_text(data, max_length=2000):
    # Truncate each string field if it exceeds max_length
    return {key: (value[:max_length] if isinstance(value, str) else value) for key, value in data.items()}

# Open the PDF file
with pdfplumber.open("Singapore_CSA_Cyber_Trust_mark_Cloud_Companion_Guide.pdf") as pdf:
    all_tables = []
    
    # Extract tables from pages 20 to 70 (0-indexed, so range is 19 to 69)
    for page_num in range(19, 70):
        page = pdf.pages[page_num]
        tables = page.extract_tables()
        
        # Append each table found to the list
        if tables:
            all_tables.extend(tables)

# Function to map first element as the header for each row in the table
def map_table_with_headers(table):
    header = ["Clause", "Controls", "Customers Considering"]
    mapped_table = []
    for i in range(1, len(table)):  # Starting from 1 to skip the header row if necessary
        row = table[i][:-1]  # Remove the last column from each row
        mapped_table.append(dict(zip(header, row)))
    return mapped_table

# Function to remove newline characters from each cell in the table
def remove_newlines_from_table(table):
    return [[cell.replace('\n', '') if isinstance(cell, str) else cell for cell in row] for row in table]

# Clean and map all tables
cleaned_tables = [remove_newlines_from_table(table) for table in all_tables]  # Clean newlines first
mapped_tables = [map_table_with_headers(table) for table in cleaned_tables]  # Map headers after cleaning

# Flatten the data and apply truncation to ensure no text exceeds the max length
flattened_data = []
for table in mapped_tables:
    for row in table:
        truncated_row = truncate_text(row)  # Truncate each row to fit varchar length
        flattened_data.append(truncated_row)

# Output the first row (for preview)
print(flattened_data[0])  # This will print the first row of the flattened data

# Convert the list of dictionaries to a DataFrame
df = pd.DataFrame(flattened_data)

# Write the DataFrame to an Excel file
output_file = "output.xlsx"
df.to_excel(output_file, index=False, engine='openpyxl')

print(f"Data has been written to {output_file}")
