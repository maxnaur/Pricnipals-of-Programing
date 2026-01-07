import qrcode
import os
import customtkinter as ctk
from PIL import Image, ImageTk
from pyzbar.pyzbar import decode
from tkinter import filedialog # For file dialog


class set_Up_QR_Code:
    """Display User QR code GUI"""
    def __init__(self, Menu, userID):
        """set up GUI"""
        self.Menu = Menu
        self.userID = userID
        self.display_Menu()

    def display_Menu(self):
        """Display userID QR code and option to interprate what an other QR code contains"""
        # Create header
        ctk.CTkLabel(
            self.Menu,
            text="QR code",
            font=ctk.CTkFont(family='Consolas', size=15)
        ).pack(pady=14)

        self.display_QR_code()

        # Button to read QR code from file
        read_qr_btn = ctk.CTkButton(
            self.Menu,
            text="Read QR Code from file",
            command=self.read_QR_code
        ).pack(pady=10)


    def display_QR_code(self):
        """Make and display a QR of the User ID so others can send crypto to the wallet."""
        # make QR code and save to file
        qr_image = qrcode.make(self.userID)
        qrLocation = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'user_wallet_qr.png')
        qr_image.save(qrLocation)

        # Display QR code
        img = Image.open(qrLocation)
        img = img.resize((600, 600))
        img_tk = ImageTk.PhotoImage(img)
        ctk.CTkLabel(
            self.Menu,
            image=img_tk,
            text=""
        ).pack(pady=10)

    def read_QR_code(self):
        """Read and display data from a QR code image file"""
        # Open a file dialog to let the user select an image
        file_path = filedialog.askopenfilename(
            title="Select QR Code Image",
            filetypes=[("Image files", "*.png;*.jpg;*.jpeg")]  # Filter for common image types
        )

        if file_path: # Check if a file was selected
            decoded_text = self.read_file(file_path)

            if decoded_text:
                ressult = ctk.CTkLabel(self.Menu, text=f"Decoded QR Code:\n{decoded_text}").pack(pady=10)
            else:
                ressult = ctk.CTkLabel(self.Menu, text="No QR code found or error decoding.").pack(pady=10)

    def read_file(self, file_path):
        """Read and decode QR code from the given image file"""
        try:
            # Load the image using PIL (avoids needing OpenCV)
            img = Image.open(file_path).convert('RGB')

            # Decode the QR code using pyzbar (accepts PIL Image)
            decoded_objects = decode(img)

            if decoded_objects:
                # Return the data from the first decoded object
                return decoded_objects[0].data.decode('utf-8')
            else:
                return None
        except Exception as e:
            print(f"Error reading QR code: {e}")
            return None
