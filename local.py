from doc_editor.editor import DocumentEditor


editor = DocumentEditor("doc_editor/tests/test_data/Lorem Ipsum.docx")
editor.load_config("doc_editor/tests/test_data/formatConfig.yaml")
editor.apply_config()
editor.save("output.docx")
