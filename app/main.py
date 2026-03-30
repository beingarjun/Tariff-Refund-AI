from __future__ import annotations

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import HTMLResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles

from app.engine import analyze_refunds
from app.parser import ParseError, parse_exclusions, parse_shipments, parse_tariff_rates
from app.reporting import build_report_csv

app = FastAPI(title="Tariff Refund AI", version="1.0.0")
app.mount("/static", StaticFiles(directory="app/static"), name="static")


def _decode_upload(file: UploadFile) -> str:
    try:
        content = file.file.read()
        return content.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise HTTPException(status_code=400, detail=f"Invalid file encoding for {file.filename}") from exc


@app.get("/", response_class=HTMLResponse)
def root() -> str:
    with open("app/static/index.html", "r", encoding="utf-8") as handle:
        return handle.read()


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/api/analyze")
def analyze(
    shipments: UploadFile = File(...),
    tariff_rates: UploadFile = File(...),
    exclusions: UploadFile | None = File(default=None),
) -> dict:
    try:
        shipment_text = _decode_upload(shipments)
        rates_text = _decode_upload(tariff_rates)
        exclusions_text = _decode_upload(exclusions) if exclusions else None

        shipment_rows = parse_shipments(shipment_text)
        rate_rows = parse_tariff_rates(rates_text)
        exclusion_rows = parse_exclusions(exclusions_text) if exclusions_text else []
        return analyze_refunds(shipment_rows, rate_rows, exclusion_rows)
    except ParseError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/api/analyze/report", response_class=PlainTextResponse)
def analyze_report(
    shipments: UploadFile = File(...),
    tariff_rates: UploadFile = File(...),
    exclusions: UploadFile | None = File(default=None),
) -> PlainTextResponse:
    try:
        shipment_text = _decode_upload(shipments)
        rates_text = _decode_upload(tariff_rates)
        exclusions_text = _decode_upload(exclusions) if exclusions else None

        shipment_rows = parse_shipments(shipment_text)
        rate_rows = parse_tariff_rates(rates_text)
        exclusion_rows = parse_exclusions(exclusions_text) if exclusions_text else []
        analysis = analyze_refunds(shipment_rows, rate_rows, exclusion_rows)
        report_csv = build_report_csv(analysis)
    except ParseError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    headers = {"Content-Disposition": 'attachment; filename="tariff_refund_report.csv"'}
    return PlainTextResponse(content=report_csv, media_type="text/csv", headers=headers)

