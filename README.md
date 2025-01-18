Here's a concise summary of your Streamlit application:  

### **BizCardX: Business Card Data Extraction & Management**  

**Overview:**  
BizCardX is a Python-based Streamlit application that extracts, processes, and manages business card details using OCR (EasyOCR). It allows users to upload images, extract text, clean the data, modify entries, and manage records in a SQLite database.  

### **Key Features:**  

1. **Home**  
   - Displays technologies used: Python, EasyOCR, Streamlit, SQL, Pandas.  
   - Provides an overview of the application.  

2. **Upload & Modify**  
   - Users upload an image (PNG, JPG, JPEG).  
   - The system extracts text using EasyOCR.  
   - Extracted data is categorized (Name, Designation, Contact, Email, etc.).  
   - Data is stored in an SQLite database.  
   - Users can preview or modify existing records

3. **Cleaned Data**  
   - Displays all extracted and processed data in a structured format.  

4. **Delete**  
   - Allows users to select a record by Name and Designation.  
   - Users can delete specific records from the database.  

### **Technologies Used:**  
- **OCR:** EasyOCR for text extraction.  
- **Frontend:** Streamlit for UI.  
- **Database:** SQLite for storing business card details.  
- **Processing:** Pandas & NumPy for data handling.  

This application automates business card data extraction, ensuring easy storage and retrieval of contact details.
