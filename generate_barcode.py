import os
import pandas as pd
import barcode
from barcode.writer import ImageWriter
import qrcode

# Load Excel
df = pd.read_excel(r"D:\Inventory\Paint Stock Working - Issue Slip Entry 28.8.25.xlsx")

# Define output directories
barcode_dir = r"D:\Inventory\bar_codes"
qrcode_dir = r"D:\Inventory\qr_codes"

# Create directories if they don't exist
os.makedirs(barcode_dir, exist_ok=True)
os.makedirs(qrcode_dir, exist_ok=True)

# Writer options for barcode
barcode_options = {
    'write_text': True,
    'font_size': 14,
    'text_distance': 5,
    'module_height': 15
}

# Loop through rows and generate both codes
for idx, row in df.iterrows():
    combo = f"{row['ICD']}-{row['Batch No']}"

    # === Generate Barcode ===
    code128 = barcode.get('code128', combo, writer=ImageWriter())
    barcode_path = os.path.join(barcode_dir, combo)


    # === Generate QR Code with custom message ===
    code128.save(barcode_path, options=barcode_options)
    message = f"Scan to verify product: {combo}"
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        border=4,
        box_size=10,
    )
    qr.add_data(message)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    qrcode_path = os.path.join(qrcode_dir, f"{combo}.png")
    img.save(qrcode_path)

print(f"✅ All barcodes and QR codes saved to:\n- {barcode_dir}\n- {qrcode_dir}")
