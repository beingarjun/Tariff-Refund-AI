# Tariff Refund AI

Tariff Refund AI is a full-stack tool that helps identify potentially overpaid import duties and estimate recoverable refund amounts from shipment records.

## Features

- CSV upload workflow for shipments, tariff rates, and optional exclusion rules
- Refund estimation engine with:
  - date-based tariff matching
  - optional exclusion handling
  - expected duty vs paid duty comparisons
- JSON API for integration with other systems
- Web UI for analysts to upload files and inspect results
- Downloadable CSV refund report
- Unit tests for core calculation logic

## Project Structure

```text
app/
  main.py          FastAPI app and routes
  models.py        Data models
  parser.py        CSV parsing and validation
  engine.py        Refund analysis logic
  reporting.py     CSV report builder
  static/          Frontend assets
tests/
  test_engine.py   Unit tests
sample_data/
  shipments.csv
  tariff_rates.csv
  exclusions.csv
```

## Input CSV Formats

### `shipments.csv` (required)

Columns:

- `entry_id`
- `importer`
- `import_date` (`YYYY-MM-DD`)
- `hts_code`
- `declared_value` (number)
- `country_of_origin`
- `duty_paid` (number)
- `quantity` (number)

### `tariff_rates.csv` (required)

Columns:

- `hts_code`
- `country_of_origin`
- `start_date` (`YYYY-MM-DD`)
- `end_date` (`YYYY-MM-DD`)
- `rate_percent` (number)

### `exclusions.csv` (optional)

Columns:

- `hts_code`
- `country_of_origin`
- `start_date` (`YYYY-MM-DD`)
- `end_date` (`YYYY-MM-DD`)
- `reason`

## Run Locally

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open: `http://127.0.0.1:8000`

## API Endpoints

- `GET /api/health`
- `POST /api/analyze` (multipart file upload, returns JSON)
- `POST /api/analyze/report` (multipart file upload, returns CSV report)

## Run Tests

```bash
python -m unittest discover -s tests -v
```

