# Neo4j Data Import Script

This Python script facilitates the import of data from an Excel file into a Neo4j graph database. The data includes information about Acceleration Programs, Startups, and Founders, along with relationships between them.

## Prerequisites

- [Neo4j](https://neo4j.com/download/) installed and running.
- [Python](https://www.python.org/downloads/) installed.
- Required Python libraries installed:
  ```bash
  pip install pandas neo4j tqdm
  ```

## Configuration

Before running the script, configure the Neo4j connection details in the `config.py` file:

```python
# config.py

NEO4J_URI = "bolt://localhost:7687"  # Update with your Neo4j server URI
NEO4J_USER = "your_username"         # Update with your Neo4j username
NEO4J_PASSWORD = "your_password"     # Update with your Neo4j password
```

## Usage

1. Create a cleaned CSV file from your Excel data and update the `excel_file_path` variable in the script accordingly.

2. Execute the script:
   ```bash
   python your_script_name.py
   ```

3. Monitor the progress using the tqdm progress bar, and view the processed rows count at the end.

## Data Model

The script uses the following data model:

- **AccelerationProgram:** Represents an Acceleration Program with properties such as name, city, country, and average_founding.

- **Startup:** Represents a Startup with properties like name, industry, description, headquarters, website, year_founded, and employees. Connected to AccelerationProgram via the PARTICIPATED_IN relationship.

- **Founder:** Represents a Founder with properties including name, tech_skills, founded_before, managing_experience, gender, and profile_link. Connected to Startup via the FOUNDED relationship.

- **Relationships:**
  - **PARTICIPATED_IN:** Connects a Startup to an AccelerationProgram with a property 'year'.
  - **FOUNDED:** Connects a Founder to a Startup.

## Note

Feel free to adapt the script and data model according to your specific requirements.