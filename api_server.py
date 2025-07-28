from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict
import random
import time
from datetime import datetime
import os

app = FastAPI(
    title="Currency Strength Widget API",
    description="API for currency strength data used by Android widget",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class DemoDataGenerator:
    def __init__(self):
        self.currencies = ["USD", "EUR", "GBP", "CHF", "CAD", "AUD", "JPY", "NZD"]
        self.pairs = [
            "EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCAD", "USDCHF",
            "EURGBP", "EURJPY", "GBPJPY", "AUDJPY", "CADJPY", "CHFJPY",
            "EURAUD", "GBPAUD", "AUDCAD", "AUDCHF", "CADCHF", "EURCAD",
            "GBPCAD", "GBPCHF", "EURNZD", "GBPNZD", "AUDNZD", "CADNZD",
            "CHFNZD", "JPYNZD"
        ]
        self.last_update = None
        self.cached_data = None

    def generate_demo_strength_data(self):
        strength_data = {}
        for pair in self.pairs:
            base_strength = random.uniform(3.0, 7.0)
            strength_data[pair] = round(base_strength, 1)
        return strength_data

    def aggregate_currencies(self, strength_data):
        currency_scores = {}
        currency_counts = {}
        
        for currency in self.currencies:
            currency_scores[currency] = 0.0
            currency_counts[currency] = 0
        
        for pair, strength in strength_data.items():
            if len(pair) == 6:
                base_currency = pair[:3]
                quote_currency = pair[3:6]
                
                if base_currency in self.currencies and quote_currency in self.currencies:
                    currency_scores[base_currency] += strength
                    currency_counts[base_currency] += 1
                    currency_scores[quote_currency] -= strength
                    currency_counts[quote_currency] += 1
        
        currency_averages = {}
        for currency in self.currencies:
            if currency_counts[currency] > 0:
                currency_averages[currency] = round(
                    currency_scores[currency] / currency_counts[currency], 2
                )
            else:
                currency_averages[currency] = 0.0
        
        return {
            "scores": currency_scores,
            "counts": currency_counts,
            "averages": currency_averages
        }

    def get_strength_data(self):
        current_time = time.time()
        
        if (self.cached_data is None or 
            self.last_update is None or 
            current_time - self.last_update > 300):
            
            strength_data = self.generate_demo_strength_data()
            currency_aggregates = self.aggregate_currencies(strength_data)
            
            self.cached_data = {
                "timestamp": datetime.now().isoformat(),
                "strength_data": strength_data,
                "currency_aggregates": currency_aggregates
            }
            self.last_update = current_time
        
        return self.cached_data

demo_generator = DemoDataGenerator()

class CurrencyStrengthResponse(BaseModel):
    timestamp: str
    strength_data: Dict[str, float]
    currency_aggregates: Dict[str, Dict]

class StatusResponse(BaseModel):
    status: str
    timestamp: str
    version: str

@app.get("/", response_model=StatusResponse)
async def root():
    return StatusResponse(
        status="Currency Strength Widget API is running",
        timestamp=datetime.now().isoformat(),
        version="1.0.0"
    )

@app.get("/api/v1/status", response_model=StatusResponse)
async def health_check():
    return StatusResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        version="1.0.0"
    )

@app.get("/api/v1/strength", response_model=CurrencyStrengthResponse)
async def get_currency_strength():
    try:
        data = demo_generator.get_strength_data()
        return CurrencyStrengthResponse(**data)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating strength data: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=port,
        reload=False
    )
