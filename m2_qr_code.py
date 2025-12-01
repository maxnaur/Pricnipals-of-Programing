import qrcode
import os
import customtkinter as ctk
from PIL import Image, ImageTk

def Display_QR_code(self):
    """Make and display a QR of the User ID so others can send crypto to the wallet."""
    qr_image = qrcode.make(self.userID)
    
    qrLocation = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'user_wallet_qr.png')
    qr_image.save(qrLocation)

    img = Image.open(qrLocation)
    img = img.resize((800, 800))
    img_tk = ImageTk.PhotoImage(img)

    qrcode_win = ctk.CTkToplevel(self.main)
    qrcode_win.title("QR Code of User ID")
    lbl = ctk.CTkLabel(qrcode_win, image=img_tk, text="")
    lbl.image = img_tk
    lbl.pack(pady=10)