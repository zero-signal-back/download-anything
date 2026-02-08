from PIL import Image, ImageDraw, ImageFont
import os
import random
import string
from datetime import datetime

class FakeIDGenerator:
    def __init__(self):
        self.output_folder = 'generated'
        os.makedirs(self.output_folder, exist_ok=True)
    
    def generate_random_number(self, length=12):
        return ''.join(random.choices(string.digits, k=length))
    
    def generate_aadhar(self, name, dob, gender, address, photo=None):
        """Generate fake Aadhar card"""
        # Create image (850x550 - Aadhar size)
        img = Image.new('RGB', (850, 550), color='white')
        draw = ImageDraw.Draw(img)
        
        # Try to load fonts, fallback to default
        try:
            title_font = ImageFont.truetype("arial.ttf", 32)
            heading_font = ImageFont.truetype("arial.ttf", 20)
            text_font = ImageFont.truetype("arial.ttf", 16)
        except:
            title_font = ImageFont.load_default()
            heading_font = ImageFont.load_default()
            text_font = ImageFont.load_default()
        
        # Header background (Indian flag colors)
        draw.rectangle([0, 0, 850, 80], fill='#FF9933')
        
        # Title
        draw.text((300, 25), "आधार", font=title_font, fill='white')
        
        # Aadhar number
        aadhar_num = f"{self.generate_random_number(4)} {self.generate_random_number(4)} {self.generate_random_number(4)}"
        draw.text((50, 120), f"Aadhar Number: {aadhar_num}", font=heading_font, fill='#000080')
        
        # Photo placeholder
        draw.rectangle([50, 170, 200, 350], outline='black', width=2)
        draw.text((80, 250), "PHOTO", font=text_font, fill='gray')
        
        # Details
        y_pos = 170
        draw.text((250, y_pos), f"Name: {name}", font=text_font, fill='black')
        y_pos += 40
        draw.text((250, y_pos), f"DOB: {dob}", font=text_font, fill='black')
        y_pos += 40
        draw.text((250, y_pos), f"Gender: {gender}", font=text_font, fill='black')
        y_pos += 40
        draw.text((250, y_pos), f"Address: {address[:40]}", font=text_font, fill='black')
        if len(address) > 40:
            y_pos += 30
            draw.text((250, y_pos), address[40:80], font=text_font, fill='black')
        
        # Watermark
        draw.text((300, 480), "SAMPLE - NOT VALID - FOR TESTING ONLY", font=text_font, fill='red')
        
        # Save
        filename = f"aadhar_{int(datetime.now().timestamp())}.png"
        filepath = os.path.join(self.output_folder, filename)
        img.save(filepath)
        
        return filename
    
    def generate_pan(self, name, father_name, dob, pan_number=None):
        """Generate fake PAN card"""
        # Create image (850x550)
        img = Image.new('RGB', (850, 550), color='#FFF8DC')
        draw = ImageDraw.Draw(img)
        
        try:
            title_font = ImageFont.truetype("arial.ttf", 28)
            heading_font = ImageFont.truetype("arialbd.ttf", 18)
            text_font = ImageFont.truetype("arial.ttf", 16)
        except:
            title_font = ImageFont.load_default()
            heading_font = ImageFont.load_default()
            text_font = ImageFont.load_default()
        
        # Header
        draw.rectangle([0, 0, 850, 70], fill='#000080')
        draw.text((250, 20), "INCOME TAX DEPARTMENT", font=title_font, fill='white')
        
        # PAN Number
        if not pan_number:
            pan_number = f"{random.choice(string.ascii_uppercase)}{random.choice(string.ascii_uppercase)}{random.choice(string.ascii_uppercase)}{random.choice(string.ascii_uppercase)}{random.choice(string.ascii_uppercase)}{self.generate_random_number(4)}{random.choice(string.ascii_uppercase)}"
        
        draw.text((50, 100), "Permanent Account Number", font=heading_font, fill='#000080')
        draw.rectangle([50, 140, 400, 190], outline='black', width=2)
        draw.text((120, 155), pan_number, font=title_font, fill='#000080')
        
        # Photo placeholder
        draw.rectangle([600, 120, 750, 300], outline='black', width=2)
        draw.text((640, 200), "PHOTO", font=text_font, fill='gray')
        
        # Details
        y_pos = 220
        draw.text((50, y_pos), f"Name: {name.upper()}", font=text_font, fill='black')
        y_pos += 40
        draw.text((50, y_pos), f"Father's Name: {father_name.upper()}", font=text_font, fill='black')
        y_pos += 40
        draw.text((50, y_pos), f"Date of Birth: {dob}", font=text_font, fill='black')
        
        # Signature
        draw.line([50, 400, 300, 400], fill='black', width=1)
        draw.text((50, 410), "Signature", font=text_font, fill='gray')
        
        # Watermark
        draw.text((250, 480), "SAMPLE - NOT VALID - FOR TESTING ONLY", font=text_font, fill='red')
        
        # Save
        filename = f"pan_{int(datetime.now().timestamp())}.png"
        filepath = os.path.join(self.output_folder, filename)
        img.save(filepath)
        
        return filename
    
    def generate_certificate(self, name, course, date, cert_type='completion'):
        """Generate fake certificate"""
        # Create image (1200x850 - landscape)
        img = Image.new('RGB', (1200, 850), color='white')
        draw = ImageDraw.Draw(img)
        
        try:
            title_font = ImageFont.truetype("arial.ttf", 48)
            heading_font = ImageFont.truetype("arialbd.ttf", 32)
            text_font = ImageFont.truetype("arial.ttf", 24)
        except:
            title_font = ImageFont.load_default()
            heading_font = ImageFont.load_default()
            text_font = ImageFont.load_default()
        
        # Border
        draw.rectangle([20, 20, 1180, 830], outline='#FFD700', width=10)
        draw.rectangle([40, 40, 1160, 810], outline='#FF6347', width=3)
        
        # Title
        draw.text((350, 100), "CERTIFICATE", font=title_font, fill='#000080')
        draw.text((400, 160), f"of {cert_type.title()}", font=heading_font, fill='#4B0082')
        
        # Content
        draw.text((200, 280), "This is to certify that", font=text_font, fill='black')
        draw.text((400, 340), name.upper(), font=heading_font, fill='#000080')
        draw.line([350, 380, 850, 380], fill='black', width=2)
        
        draw.text((200, 420), f"has successfully completed the course", font=text_font, fill='black')
        draw.text((450, 480), course, font=heading_font, fill='#4B0082')
        
        # Date
        draw.text((200, 600), f"Date: {date}", font=text_font, fill='black')
        
        # Signature
        draw.line([800, 650, 1050, 650], fill='black', width=1)
        draw.text((850, 660), "Authorized Signature", font=text_font, fill='gray')
        
        # Watermark
        draw.text((400, 750), "SAMPLE - NOT VALID - FOR TESTING ONLY", font=text_font, fill='red')
        
        # Save
        filename = f"certificate_{int(datetime.now().timestamp())}.png"
        filepath = os.path.join(self.output_folder, filename)
        img.save(filepath)
        
        return filename
