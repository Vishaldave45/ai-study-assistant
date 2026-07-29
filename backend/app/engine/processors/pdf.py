import logging
import fitz  # PyMuPDF
from pathlib import Path
from typing import Union
from app.engine.base import BaseDocumentProcessor
from app.engine.schemas import PageObject, ImageMetadata
from app.engine.utils.pdf import safe_open_pdf

logger = logging.getLogger(__name__)


class PDFDocumentProcessor(BaseDocumentProcessor):
    """
    PyMuPDF-powered PDF Processor converting raw PDFs into structured PageObjects
    containing clean text blocks and bounding-box image metadata.
    """

    def process(self, file_source: Union[Path, bytes]) -> list[PageObject]:
        if isinstance(file_source, bytes):
            doc = safe_open_pdf(file_source)
        else:
            with open(file_source, "rb") as f:
                doc = safe_open_pdf(f.read())

        pages: list[PageObject] = []

        try:
            for page_num, page in enumerate(doc, start=1):
                # 1. Extract text
                text = page.get_text("text").strip()

                # 2. Extract image bounding boxes & metadata
                images: list[ImageMetadata] = []
                image_list = page.get_images(full=True)

                for img_info in image_list:
                    xref = img_info[0]
                    try:
                        base_image = doc.extract_image(xref)
                        if base_image:
                            width = base_image.get("width", 0)
                            height = base_image.get("height", 0)
                            ext = base_image.get("ext", "png")

                            # Get image bounding box on page rect if available
                            rects = page.get_image_rects(xref)
                            bbox = list(rects[0]) if rects else []

                            images.append(
                                ImageMetadata(
                                    page_number=page_num,
                                    bbox=bbox,
                                    mime_type=f"image/{ext}",
                                    width=width,
                                    height=height,
                                )
                            )
                    except Exception as img_err:
                        logger.debug(f"Failed extracting image xref {xref} on page {page_num}: {img_err}")

                pages.append(
                    PageObject(
                        page_number=page_num,
                        text=text,
                        images=images,
                        tables=[],
                        diagrams=[],
                        equations=[],
                    )
                )
        finally:
            doc.close()

        return pages
