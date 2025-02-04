from fastapi import FastAPI
from langchain_community.document_loaders import PyPDFLoader

app = FastAPI()

@app.get("/test_pdf")
def test_pdf():
    file_path = 'D:/visualstudiocode/project/eufeedbackapp/src/download/AGRI/(05.09.22) IRV-CIP opinion sent on amendments to EU Reg. 2018-273.pdf'
    try:
        pdf_reader = PyPDFLoader(file_path)
        pages = pdf_reader.load_and_split()
        return {"first_page_content": pages[0]}
    except ImportError as e:
        return {"error": f"ImportError: {str(e)}"}
    except Exception as e:
        return {"error": f"General Exception: {str(e)}"}

@app.get("/check_environment")
def check_environment():
    import sys
    return {"python_path": sys.executable}
