import unittest
import os
from pathlib import Path
from doc_editor.editor import DocumentEditor, format_document


class TestDocumentEditor(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_dir = Path(__file__).parent / 'test_data'
        cls.sample_doc = cls.test_dir / 'sample.docx'
        cls.sample_config = cls.test_dir / 'sample_config.yaml'
        cls.output_doc = cls.test_dir / 'output.docx'

        # Создаем тестовый документ если его нет
        if not cls.sample_doc.exists():
            doc = Document()
            doc.add_paragraph("Test document")
            doc.save(cls.sample_doc)

    def test_load_config(self):
        editor = DocumentEditor(self.sample_doc)
        editor.load_config(self.sample_config)
        self.assertIsNotNone(editor.config)

    def test_apply_margins(self):
        editor = DocumentEditor(self.sample_doc)
        editor.load_config(self.sample_config)
        editor._apply_margins()

        # Проверяем что поля установились
        section = editor.doc.sections[0]
        self.assertAlmostEqual(section.left_margin.inches, 1.0, places=2)

    def test_format_document_function(self):
        # Проверяем работу оберточной функции
        format_document(
            input_path=self.sample_doc,
            config_path=self.sample_config,
            output_path=self.output_doc
        )
        self.assertTrue(self.output_doc.exists())
        self.output_doc.unlink()  # Удаляем после теста


if __name__ == '__main__':
    unittest.main()