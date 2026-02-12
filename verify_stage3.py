#!/usr/bin/env python3
"""Quick verification script for Phase 2 Stage 3 implementation."""

import sys
sys.path.insert(0, '/Users/kirill/Desktop/vniim/formatingDocx')

print("=" * 70)
print("PHASE 2 STAGE 3: Verification Script")
print("=" * 70)

# Test 1: Import processors
print("\n[1/3] Testing imports...")
try:
    from doc_editor.processors import PrefaceProcessor, AppendixProcessor
    print("  ✓ PrefaceProcessor imported")
    print("  ✓ AppendixProcessor imported")
except ImportError as e:
    print(f"  ✗ Import failed: {e}")
    sys.exit(1)

# Test 2: Instantiate processors
print("\n[2/3] Testing instantiation...")
try:
    from doc_editor.models.config import DocumentConfig, DocumentStructureConfig, PrefaceConfig, AppendixConfig, StyleConfig
    
    config = DocumentConfig(
        structure=DocumentStructureConfig(
            document_structure=type('obj', (object,), {
                'preface': PrefaceConfig(enabled=True, content='Test preface'),
                'appendix': AppendixConfig(enabled=True, numbering_style='letters')
            })(),
        ),
        styles=StyleConfig(),
    )
    
    preface = PrefaceProcessor(config)
    appendix = AppendixProcessor(config)
    
    print("  ✓ PrefaceProcessor instantiated")
    print("  ✓ AppendixProcessor instantiated")
except Exception as e:
    print(f"  ✗ Instantiation failed: {e}")
    sys.exit(1)

# Test 3: Verify methods
print("\n[3/3] Testing methods...")
try:
    # PrefaceProcessor methods
    assert hasattr(preface, 'add_preface')
    print("  ✓ PrefaceProcessor.add_preface() exists")
    
    # AppendixProcessor methods
    assert hasattr(appendix, 'process_appendices')
    print("  ✓ AppendixProcessor.process_appendices() exists")
    assert hasattr(appendix, '_find_appendix_headings')
    print("  ✓ AppendixProcessor._find_appendix_headings() exists")
    assert hasattr(appendix, '_get_appendix_letter')
    print("  ✓ AppendixProcessor._get_appendix_letter() exists")
    
    # Test letter generation
    letters = [appendix._get_appendix_letter(i) for i in range(5)]
    print(f"  ✓ Letter generation: {letters}")
    
except AssertionError as e:
    print(f"  ✗ Method check failed: {e}")
    sys.exit(1)

print("\n" + "=" * 70)
print("✓ All verifications passed!")
print("=" * 70)
