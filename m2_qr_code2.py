import qrcode
import os
import customtkinter as ctk
from PIL import Image, ImageTk

class set_Up_QR_Code:
    """Display User QR code GUI"""
    def __init__(self, Menu, userID):
        """set up GUI"""
        self.Menu = Menu
        self.userID = userID
        self.display_QR_code()

        # make QR code and save to file
        qr_image = qrcode.make(self.userID)
        self.qrLocation = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'user_wallet_qr.png')
        qr_image.save(self.qrLocation)


    def display_QR_code(self):
        """Display userID QR code and option to interprate what an other QR code contains"""
        # Create header
        ctk.CTkLabel(
            self.Menu,
            text="QR code",
            font=ctk.CTkFont(family='Consolas', size=15)
        ).pack(pady=14)

        # Display QR code
        qr_image = Image.open(self.qrLocation)
        qr_image = qr_image.resize((600, 600))
        qr_photo = ImageTk.PhotoImage(qr_image)
        ctk.CTkLabel(
            self.Menu,
            image=qr_photo,
            text=""
        ).pack(pady=10)

        # Button to read QR code from file
        read_qr_btn = ctk.CTkButton(
            self.Menu,
            text="Read QR Code from file",
            command=self.read_QR_code
        ).pack(pady=10)

    def read_QR_code(self):
        """Read and display data from a QR code image file"""
        




def Display_QR_code(self):
    """Make and display a QR of the User ID so others can send crypto to the wallet."""
    qrLocation = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'user_wallet_qr.png')

    img = Image.open(qrLocation)
    img = img.resize((600, 600))
    img_tk = ImageTk.PhotoImage(img)

    qrcode_win = ctk.CTkToplevel(self.Menu)
    qrcode_win.title("QR Code of User ID")
    lbl = ctk.CTkLabel(qrcode_win, image=img_tk, text="")
    lbl.image = img_tk
    lbl.pack(pady=10)