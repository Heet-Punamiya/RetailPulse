import os
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from datetime import datetime, timedelta
import random

app = FastAPI(title="RetailPulse API", description="Data Analytics & Point-of-Sale System")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

TRANSACTIONS_FILE = os.path.join("data", "transactions.csv")
INVENTORY_FILE = os.path.join("data", "inventory.csv")

# Pydantic Schemas for JSON requests
class RestockRequest(BaseModel):
    product_name: str
    quantity: int

class CartItem(BaseModel):
    product_name: str
    quantity: int

class CheckoutRequest(BaseModel):
    items: List[CartItem]
    total_paid: float

def load_data():
    if not os.path.exists(TRANSACTIONS_FILE) or not os.path.exists(INVENTORY_FILE):
        raise HTTPException(status_code=500, detail="Data files not found.")
    
    tx_df = pd.read_csv(TRANSACTIONS_FILE)
    inv_df = pd.read_csv(INVENTORY_FILE)
    tx_df['timestamp'] = pd.to_datetime(tx_df['timestamp'])
    tx_df['date'] = tx_df['timestamp'].dt.date
    return tx_df, inv_df

@app.get("/api/summary")
def get_summary():
    tx_df, inv_df = load_data()
    tx_df['revenue'] = tx_df['quantity_sold'] * tx_df['unit_price']
    total_revenue = round(float(tx_df['revenue'].sum()), 2)
    
    if not tx_df.empty:
        top_selling = tx_df.groupby('product_name')['quantity_sold'].sum().idxmax()
    else:
        top_selling = "None"
        
    max_date = tx_df['timestamp'].max() if not tx_df.empty else datetime.now()
    cutoff_date = max_date - timedelta(days=14)
    recent_tx = tx_df[tx_df['timestamp'] >= cutoff_date]
    
    daily_rates = recent_tx.groupby('product_name')['quantity_sold'].sum() / 14.0 if not recent_tx.empty else pd.Series()
    
    low_stock_count = 0
    for idx, row in inv_df.iterrows():
        prod_name = row['product_name']
        current_stock = row['current_stock']
        reorder_level = row['reorder_level']
        
        rate = daily_rates.get(prod_name, 1.0)
        days_left = current_stock / rate if rate > 0 else 999
        
        if current_stock <= reorder_level or days_left < 3:
            low_stock_count += 1
            
    return {
        "total_revenue": total_revenue,
        "top_selling_product": top_selling,
        "low_stock_alerts": low_stock_count,
        "total_products": len(inv_df)
    }

@app.get("/api/inventory")
def get_inventory():
    tx_df, inv_df = load_data()
    max_date = tx_df['timestamp'].max() if not tx_df.empty else datetime.now()
    cutoff_date = max_date - timedelta(days=14)
    recent_tx = tx_df[tx_df['timestamp'] >= cutoff_date]
    
    daily_rates = recent_tx.groupby('product_name')['quantity_sold'].sum() / 14.0 if not recent_tx.empty else pd.Series()
    
    inventory_status = []
    for idx, row in inv_df.iterrows():
        prod_name = row['product_name']
        current_stock = int(row['current_stock'])
        price = float(row['unit_price'])
        reorder_level = int(row['reorder_level'])
        
        rate = float(daily_rates.get(prod_name, 0.0))
        days_left = float(current_stock / rate) if rate > 0 else 999.0
        
        if days_left < 3 or current_stock <= (reorder_level * 0.5):
            status = "CRITICAL"
        elif days_left < 7 or current_stock <= reorder_level:
            status = "WARNING"
        else:
            status = "HEALTHY"
            
        inventory_status.append({
            "product_name": prod_name,
            "current_stock": current_stock,
            "unit_price": price,
            "daily_sales_rate": round(rate, 2),
            "days_remaining": round(days_left, 1) if days_left < 999 else "N/A",
            "reorder_level": reorder_level,
            "status": status
        })
    return inventory_status

@app.get("/api/forecast/{product_name}")
def get_forecast(product_name: str):
    tx_df, inv_df = load_data()
    prod_tx = tx_df[tx_df['product_name'] == product_name]
    if prod_tx.empty:
        # If no transactions yet, return empty history
        return {
            "product_name": product_name,
            "trend": "STABLE",
            "slope": 0.0,
            "history": [],
            "forecast": []
        }
        
    daily_sales = prod_tx.groupby('date')['quantity_sold'].sum().reset_index()
    daily_sales = daily_sales.sort_values('date')
    daily_sales['day_index'] = np.arange(len(daily_sales))
    
    X = daily_sales[['day_index']].values
    y = daily_sales['quantity_sold'].values
    
    model = LinearRegression()
    model.fit(X, y)
    
    future_indices = np.arange(len(daily_sales), len(daily_sales) + 7).reshape(-1, 1)
    predictions = model.predict(future_indices)
    predictions = np.clip(predictions, 0, None)
    
    last_date = daily_sales['date'].max()
    forecast_dates = [last_date + timedelta(days=i) for i in range(1, 8)]
    
    historical_data = [
        {"date": str(row['date']), "quantity": int(row['quantity_sold'])}
        for _, row in daily_sales.iterrows()
    ]
    forecast_data = [
        {"date": str(date), "quantity": round(float(pred), 1)}
        for date, pred in zip(forecast_dates, predictions)
    ]
    
    slope = float(model.coef_[0])
    trend = "UPWARD" if slope > 0.1 else ("DOWNWARD" if slope < -0.1 else "STABLE")
    
    return {
        "product_name": product_name,
        "trend": trend,
        "slope": round(slope, 3),
        "history": historical_data,
        "forecast": forecast_data
    }

# ---------------- NEW INTERACTIVE ENDPOINTS ----------------

@app.post("/api/inventory/add")
def restock_inventory(payload: RestockRequest):
    tx_df, inv_df = load_data()
    
    # Check if product exists
    if not inv_df['product_name'].str.contains(payload.product_name).any():
        raise HTTPException(status_code=404, detail="Product not found in inventory")
        
    # Add stock
    inv_df.loc[inv_df['product_name'] == payload.product_name, 'current_stock'] += payload.quantity
    
    # Save back to CSV
    inv_df.to_csv(INVENTORY_FILE, index=False)
    
    updated_row = inv_df[inv_df['product_name'] == payload.product_name].iloc[0]
    return {
        "product_name": updated_row['product_name'],
        "current_stock": int(updated_row['current_stock']),
        "message": f"Successfully added {payload.quantity} units to stock"
    }

@app.post("/api/checkout")
def checkout_cart(payload: CheckoutRequest):
    tx_df, inv_df = load_data()
    
    # Validate items in stock
    for item in payload.items:
        product_rows = inv_df[inv_df['product_name'] == item.product_name]
        if product_rows.empty:
            raise HTTPException(status_code=404, detail=f"Product '{item.product_name}' not found")
        
        current_stock = int(product_rows.iloc[0]['current_stock'])
        if current_stock < item.quantity:
            raise HTTPException(
                status_code=400, 
                detail=f"Insufficient stock for '{item.product_name}'. Available: {current_stock}, Requested: {item.quantity}"
            )
            
    # Process deductions and append to transactions
    timestamp = datetime.now()
    invoice_id = f"INV-{timestamp.strftime('%Y%m%d%H%M%S')}-{random.randint(100, 999)}"
    
    # Read weather conditions from recent or simulate them
    is_rainy = random.choice([0, 0, 0, 0, 1])  # 20% rain chance
    temp = round(22.0 + random.random() * 8.0, 1) # 22-30 degrees
    
    new_transactions = []
    
    for item in payload.items:
        # Deduct inventory
        inv_df.loc[inv_df['product_name'] == item.product_name, 'current_stock'] -= item.quantity
        
        # Get price
        price = float(inv_df.loc[inv_df['product_name'] == item.product_name, 'unit_price'].iloc[0])
        
        # Track new transaction
        new_transactions.append({
            "timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "product_name": item.product_name,
            "quantity_sold": item.quantity,
            "unit_price": price,
            "is_rainy": is_rainy,
            "temperature": temp
        })
        
    # Save files
    inv_df.to_csv(INVENTORY_FILE, index=False)
    
    # Append transactions
    new_tx_df = pd.DataFrame(new_transactions)
    combined_tx_df = pd.concat([tx_df.drop(columns=['date'], errors='ignore'), new_tx_df], ignore_index=True)
    combined_tx_df.to_csv(TRANSACTIONS_FILE, index=False)
    
    return {
        "invoice_id": invoice_id,
        "timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
        "total_items": sum(item.quantity for item in payload.items),
        "total_paid": payload.total_paid,
        "message": "Checkout completed successfully and inventory updated."
    }

# Mount static files folder
app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("analytics:app", host="127.0.0.1", port=8000, reload=True)
