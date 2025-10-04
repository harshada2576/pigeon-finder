"""
Unit Tests for File Scanner
"""

import unittest
import tempfile
import os
from pathlib import Path
import sys

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.file_scanner import FileScanner
from core.hashing import FileHasher

class TestFileScanner(unittest.TestCase):
    """Test cases for FileScanner"""
    
    def setUp(self):
        """Set up test environment"""
        self.scanner = FileScanner()
        self.test_dir = tempfile.mkdtemp()
        
        # Create test files
        self.create_test_files()
    
    def tearDown(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.test_dir)
    
    def create_test_files(self):
        """Create test files for scanning"""
        # Create some duplicate files
        content1 = b"This is test content 1"
        content2 = b"This is test content 2"
        
        # File 1 (original)
        with open(os.path.join(self.test_dir, "file1.txt"), "wb") as f:
            f.write(content1)
        
        # File 2 (duplicate of file1)
        with open(os.path.join(self.test_dir, "file2.txt"), "wb") as f:
            f.write(content1)
        
        # File 3 (different content)
        with open(os.path.join(self.test_dir, "file3.txt"), "wb") as f:
            f.write(content2)
        
        # Create subdirectory with more files
        subdir = os.path.join(self.test_dir, "subdir")
        os.makedirs(subdir)
        
        with open(os.path.join(subdir, "file4.txt"), "wb") as f:
            f.write(content1)
    
    def test_scan_directory(self):
        """Test directory scanning"""
        files = self.scanner.scan_directory(self.test_dir)
        
        # Should find all 4 files
        self.assertEqual(len(files), 4)
        
        # All files should have required attributes
        for file_info in files.values():
            self.assertIn('size', file_info)
            self.assertIn('path', file_info)
            self.assertIn('name', file_info)
    
    def test_size_grouping(self):
        """Test file grouping by size"""
        files = self.scanner.scan_directory(self.test_dir)
        size_groups = self.scanner.get_file_groups_by_size()
        
        # Should have groups for each unique file size
        self.assertGreaterEqual(len(size_groups), 1)
        
        # Each group should have files of same size
        for size, file_list in size_groups.items():
            for file_path in file_list:
                actual_size = os.path.getsize(file_path)
                self.assertEqual(actual_size, size)
    
    def test_extension_filter(self):
        """Test file extension filtering"""
        files = self.scanner.scan_directory(self.test_dir, extensions=['.txt'])
        self.assertEqual(len(files), 4)  # All files are .txt
        
        files = self.scanner.scan_directory(self.test_dir, extensions=['.jpg'])
        self.assertEqual(len(files), 0)  # No .jpg files
    
    def test_size_filter(self):
        """Test file size filtering"""
        # Get size of one file
        test_file = os.path.join(self.test_dir, "file1.txt")
        file_size = os.path.getsize(test_file)
        
        # Test min size filter
        files = self.scanner.scan_directory(self.test_dir, min_size=file_size + 1)
        self.assertEqual(len(files), 0)
        
        # Test max size filter
        files = self.scanner.scan_directory(self.test_dir, max_size=file_size - 1)
        self.assertEqual(len(files), 0)

class TestFileHasher(unittest.TestCase):
    """Test cases for FileHasher"""
    
    def setUp(self):
        self.hasher = FileHasher()
        self.test_file = tempfile.NamedTemporaryFile(delete=False)
        self.test_content = b"Test content for hashing"
        self.test_file.write(self.test_content)
        self.test_file.close()
    
    def tearDown(self):
        os.unlink(self.test_file.name)
    
    def test_hash_calculation(self):
        """Test hash calculation"""
        file_hash = self.hasher.calculate_hash(self.test_file.name)
        
        # Hash should be consistent
        self.assertEqual(len(file_hash), 32)  # MD5 hash length
        self.assertEqual(file_hash, self.hasher.calculate_hash(self.test_file.name))
    
    def test_quick_comparison(self):
        """Test quick file comparison"""
        # Create another file with same content
        test_file2 = tempfile.NamedTemporaryFile(delete=False)
        test_file2.write(self.test_content)
        test_file2.close()
        
        try:
            # Files should be considered equal in quick comparison
            result = self.hasher.quick_hash_comparison(self.test_file.name, test_file2.name)
            self.assertTrue(result)
        finally:
            os.unlink(test_file2.name)

if __name__ == '__main__':
    unittest.main()