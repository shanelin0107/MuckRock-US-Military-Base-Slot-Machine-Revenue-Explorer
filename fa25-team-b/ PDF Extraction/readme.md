
<h1 align="center">
  <br>
  <a href="https://www.bu.edu/spark/" target="_blank"><img src="https://www.bu.edu/spark/files/2023/08/logo.png" alt="BUSpark" width="200"></a>
  <br>
  Project README Template <change to project name>
  <br>
</h1>

<h4 align="center">A template for the project readme file. </h4> <change to repo short description>

# 1. Detailed Data Extraction Procedure
### 1.1. Asset Report

### 1.2. Marine Revenue

### 1.3. Navy Revenue Report

### 1.4. Financial Statements
The Financial Statements pdf required a bit of expirimentation for both OCR tools as well as formatted text extraction. Due to the size of the document, some extraction libraries and most online tools for OCR would not process the file. For text extraction, we ended up using poppler-utils, which had the best balance between quality of the table formatting during extraction alongside time to extract. For OCR, we initially tried using python libraries, but none worked particularly well or quickly. To solve this, we ended up splitting the document into chunks, running them through Adobe Express's OCR tool, then recombining them into one pdf. This was a successful approach, and the rest of the work done was in cleaning minor issues in extraction/formatting before loading data into our CSV files.
### 1.5. District Revenue
