import io
from markitdown import MarkItDown

md = MarkItDown()

class FileExtractor:

    @classmethod
    def parse_docx_bytes(cls, data: bytes) -> str:
        result = md.convert(io.BytesIO(data), mime_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
        return result.text_content

    @classmethod
    def parse_pdf_bytes(cls, data: bytes) -> str:
        result = md.convert(io.BytesIO(data), mime_type="application/pdf")
        return result.text_content



    @classmethod
    def parse_text_bytes(cls, data: bytes, encoding: str = "utf-8") -> str:
        result = md.convert(io.BytesIO(data), mime_type="text/plain")
        return result.text_content



if __name__ == "__main__":
    with open("/Users/dylan/给城市合伙人的调研问卷.docx", "rb") as f:
        data = f.read()
        print(FileExtractor.parse_docx_bytes(data))

    with open("/Users/dylan/schema registry api文档.pdf", "rb") as f:
        data = f.read()
        print(FileExtractor.parse_pdf_bytes(data))

    with open("/Users/dylan/不动产登记和公证处.txt", "rb") as f:
        data = f.read()
        print(FileExtractor.parse_pdf_bytes(data))
