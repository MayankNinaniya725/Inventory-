from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import sqlite3
import uvicorn
import os

app = FastAPI()
templates = Jinja2Templates(directory="templates")
DB_FILE = r"D:\Inventory\inventory.db"

def get_conn():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM inventory")
    inventory_items = cur.fetchall()
    cur.execute("SELECT * FROM purchase_list")
    purchase_items = cur.fetchall()
    conn.close()
    return templates.TemplateResponse("index.html", {
        "request": request,
        "inventory": inventory_items,
        "purchase_list": purchase_items,
        "message": ""
    })

@app.post("/scan_item/", response_class=HTMLResponse)
def scan_item(request: Request, item_id: int = Form(...)):
    conn = get_conn()
    cur = conn.cursor()
    
    # Check item exists
    cur.execute("SELECT * FROM inventory WHERE id = ?", (item_id,))
    item = cur.fetchone()
    if not item:
        message = f"Item ID {item_id} not found!"
    elif item["quantity"] <= 0 or item["status"] == "out_of_stock":
        message = f"Item {item['name']} is out of stock!"
    else:
        # Reduce inventory
        new_quantity = item["quantity"] - 1
        new_status = "out_of_stock" if new_quantity <= 0 else "in_stock"
        
        cur.execute("UPDATE inventory SET quantity = ?, status = ? WHERE id = ?", 
                   (new_quantity, new_status, item_id))
        
        # Add to purchase list
        cur.execute("INSERT INTO purchase_list (id, name, quantity, price) VALUES (?, ?, 1, ?)",
                    (item["id"], item["name"], item["price"]))
        conn.commit()
        
        status_msg = " (Now out of stock!)" if new_status == "out_of_stock" else f" (Remaining: {new_quantity})"
        message = f"Item {item['name']} added to purchase list.{status_msg}"
    
    # Refresh lists
    cur.execute("SELECT * FROM inventory")
    inventory_items = cur.fetchall()
    cur.execute("SELECT * FROM purchase_list")
    purchase_items = cur.fetchall()
    conn.close()
    
    return templates.TemplateResponse("index.html", {
        "request": request,
        "inventory": inventory_items,
        "purchase_list": purchase_items,
        "message": message
    })

@app.post("/search_item/", response_class=HTMLResponse)
def search_item(request: Request, search_query: str = Form(...)):
    conn = get_conn()
    cur = conn.cursor()
    
    # Try to search by ID first (if it's a number), then by name
    try:
        item_id = int(search_query)
        cur.execute("SELECT * FROM inventory WHERE id = ?", (item_id,))
        item = cur.fetchone()
    except ValueError:
        # Search by name (partial match)
        cur.execute("SELECT * FROM inventory WHERE name LIKE ?", (f"%{search_query}%",))
        item = cur.fetchone()
    
    if not item:
        message = f"Item '{search_query}' not found in inventory!"
    elif item["quantity"] <= 0 or item["status"] == "out_of_stock":
        message = f"Item {item['name']} (ID: {item['id']}) is out of stock!"
    else:
        # Move entire remaining quantity to purchase list
        cur.execute("INSERT INTO purchase_list (id, name, quantity, price) VALUES (?, ?, ?, ?)",
                    (item["id"], item["name"], item["quantity"], item["price"]))
        
        # Set inventory to out of stock
        cur.execute("UPDATE inventory SET quantity = 0, status = 'out_of_stock' WHERE id = ?", 
                   (item["id"],))
        conn.commit()
        
        message = f"Item {item['name']} (ID: {item['id']}) moved to purchase list. Quantity: {item['quantity']}"
    
    # Refresh lists
    cur.execute("SELECT * FROM inventory")
    inventory_items = cur.fetchall()
    cur.execute("SELECT * FROM purchase_list")
    purchase_items = cur.fetchall()
    conn.close()
    
    return templates.TemplateResponse("index.html", {
        "request": request,
        "inventory": inventory_items,
        "purchase_list": purchase_items,
        "message": message
    })

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8001)
