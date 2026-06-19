"""
Tests for PDFParser — run with:  pytest tests/test_parser.py -v
"""

import sys
from pathlib import Path

import pytest

# Make sure the project root is on sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

from parser.pdf_parser import PDFParser, ParsedDocument, TextBlock, TableBlock, ImageBlock

SAMPLE_PDF = "data/pdfs/sample.pdf.pdf"


class TestPDFParser:

    def setup_method(self):
        """Runs before each test — creates a fresh parser."""
        self.parser = PDFParser(output_dir="output/test")

    # ── Initialization ────────────────────────────────────────────────────────

    def test_parser_creates_output_dirs(self):
        """Parser should create output/ and output/images/ on init."""
        assert self.parser.output_dir.exists()
        assert self.parser.images_dir.exists()

    # ── Full parse ────────────────────────────────────────────────────────────

    def test_parse_returns_parsed_document(self):
        if not Path(SAMPLE_PDF).exists():
            pytest.skip("Sample PDF not found")

        result = self.parser.parse(SAMPLE_PDF)

        assert isinstance(result, ParsedDocument)
        assert result.total_pages > 0
        assert isinstance(result.texts, list)
        assert isinstance(result.tables, list)
        assert isinstance(result.images, list)

    # ── Text extraction ───────────────────────────────────────────────────────

    def test_text_blocks_have_required_fields(self):
        if not Path(SAMPLE_PDF).exists():
            pytest.skip("Sample PDF not found")

        result = self.parser.parse(SAMPLE_PDF)

        if result.texts:
            block = result.texts[0]
            assert isinstance(block, TextBlock)
            assert block.page_number >= 1
            assert isinstance(block.content, str)
            assert len(block.content) > 0
            assert block.block_type in ("text", "heading")

    # ── Table extraction ──────────────────────────────────────────────────────

    def test_table_blocks_have_required_fields(self):
        if not Path(SAMPLE_PDF).exists():
            pytest.skip("Sample PDF not found")

        result = self.parser.parse(SAMPLE_PDF)

        for table in result.tables:
            assert isinstance(table, TableBlock)
            assert table.page_number >= 1
            assert isinstance(table.headers, list)
            assert isinstance(table.rows, list)
            assert isinstance(table.raw_text, str)

    # ── Image extraction ──────────────────────────────────────────────────────

    def test_image_files_are_saved(self):
        if not Path(SAMPLE_PDF).exists():
            pytest.skip("Sample PDF not found")

        result = self.parser.parse(SAMPLE_PDF)

        for img in result.images:
            assert isinstance(img, ImageBlock)
            assert Path(img.image_path).exists(), f"Image not saved: {img.image_path}"
            assert img.width  > 0
            assert img.height > 0

    # ── JSON output ───────────────────────────────────────────────────────────

    def test_save_to_json_creates_file(self):
        if not Path(SAMPLE_PDF).exists():
            pytest.skip("Sample PDF not found")

        result = self.parser.parse(SAMPLE_PDF)
        path   = self.parser.save_to_json(result)

        assert Path(path).exists()
        assert path.endswith(".json")