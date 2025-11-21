# app.py
import os
import uvicorn
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from optimized_pipeline import main
from utils.data_points import (
    cyber_data_points,
    general_liability_data_points,
    business_owner_data_points,
    comercial_auto_data_points
)
from utils.queryy import (
    prompt_template_cyber,
    prompt_template_general,
    prompt_template_commercial_auto,
    prompt_template_general_liability,
    prompt_template_property,
    prompt_template_business_owner,
    prompt_template_package
)

app = FastAPI(title="Insurance Extraction API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mapping
prompt_map = {
    "cyber": prompt_template_cyber,
    "general": prompt_template_general,
    "comercial_auto": prompt_template_commercial_auto,
    "general_liability": prompt_template_general_liability,
    "property": prompt_template_property,
    "business_owner": prompt_template_business_owner,
    "package": prompt_template_business_owner
}

data_points_map = {
    "cyber": cyber_data_points,
    "general": business_owner_data_points,
    "comercial_auto": comercial_auto_data_points,
    "general_liability": general_liability_data_points,
    "property": cyber_data_points,
    "business_owner": business_owner_data_points,
    "package": business_owner_data_points
}

# ----------------------------
#       API ENDPOINT
# ----------------------------

@app.post("/extract/")
async def extract_api(
    business: str = Form(...),
    file: UploadFile = File(...)
):
    try:
        # Save temporarily
        os.makedirs("uploads", exist_ok=True)
        file_path = f"uploads/{file.filename}"

        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())

        if business not in data_points_map:
            return JSONResponse({"error": "Invalid business type"}, status_code=400)

        # Run main pipeline
        extracted_result = main(file_path, business, data_points_map, prompt_map)

        return JSONResponse({
            "status": "success",
            "file": file.filename,
            "business": business,
            "extracted_data": extracted_result
        })

    except Exception as e:
        return JSONResponse({
            "status": "error",
            "message": str(e)
        }, status_code=500)


@app.get("/")
def root():
    return {"message": "Insurance Extraction API Running"}


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000)
