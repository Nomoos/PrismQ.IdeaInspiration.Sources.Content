"""Tests for repository structure validation."""

from pathlib import Path


def test_src_directory_exists():
    """Test that src/ directory exists for core package."""
    src_dir = Path("src")
    assert src_dir.exists(), "src/ directory should exist"
    assert src_dir.is_dir(), "src/ should be a directory"


def test_mod_directory_exists():
    """Test that mod/ directory exists for business modules."""
    mod_dir = Path("mod")
    assert mod_dir.exists(), "mod/ directory should exist"
    assert mod_dir.is_dir(), "mod/ should be a directory"


def test_src_contains_core_files():
    """Test that src/ contains core infrastructure files."""
    src_dir = Path("src")
    
    # Core files that should exist in src/
    core_files = [
        "config.py",
        "logging_config.py",
        "main.py",
        "__init__.py",
    ]
    
    for filename in core_files:
        file_path = src_dir / filename
        assert file_path.exists(), f"src/{filename} should exist"


def test_mod_has_readme():
    """Test that mod/ directory has a README explaining its purpose."""
    mod_readme = Path("mod/README.md")
    assert mod_readme.exists(), "mod/README.md should exist"
    
    # Check that it explains the purpose
    content = mod_readme.read_text(encoding="utf-8")
    assert "business" in content.lower() or "domain" in content.lower(), \
        "mod/README.md should explain business/domain purpose"


def test_main_readme_documents_structure():
    """Test that main README documents the new structure."""
    readme = Path("README.md")
    content = readme.read_text(encoding="utf-8")
    
    # Should mention both src/ and mod/
    assert "src/" in content, "README should document src/ directory"
    assert "mod/" in content, "README should document mod/ directory"
    
    # Should explain the separation
    assert "core" in content.lower() or "infrastructure" in content.lower(), \
        "README should explain src/ is for core/infrastructure"
    assert "business" in content.lower() or "domain" in content.lower(), \
        "README should explain mod/ is for business/domain"


def test_pyproject_toml_packages_config():
    """Test that pyproject.toml correctly configures packages."""
    pyproject = Path("pyproject.toml")
    content = pyproject.read_text(encoding="utf-8")
    
    # Should include src in packages (flexible matching)
    assert "packages" in content and "src" in content, \
        "pyproject.toml should configure src in packages"
    
    # Should have a comment about mod/
    assert "mod/" in content, \
        "pyproject.toml should document mod/ directory purpose"


def test_doc_directory_exists():
    """Test that doc/ directory exists for documentation."""
    doc_dir = Path("doc")
    assert doc_dir.exists(), "doc/ directory should exist"
    assert doc_dir.is_dir(), "doc/ should be a directory"


def test_doc_sphinx_structure():
    """Test that doc/ has proper Sphinx structure."""
    doc_source = Path("doc/source")
    assert doc_source.exists(), "doc/source/ should exist"
    
    # Core Sphinx files
    sphinx_files = [
        "conf.py",
        "index.rst",
    ]
    
    for filename in sphinx_files:
        file_path = doc_source / filename
        assert file_path.exists(), f"doc/source/{filename} should exist"
    
    # Sphinx directories
    assert (doc_source / "_static").exists(), "doc/source/_static/ should exist"
    assert (doc_source / "_templates").exists(), "doc/source/_templates/ should exist"


def test_doc_conf_has_autodoc_path():
    """Test that doc/source/conf.py configures path for autodoc."""
    conf_py = Path("doc/source/conf.py")
    content = conf_py.read_text(encoding="utf-8")
    
    # Should configure sys.path for autodoc
    assert "sys.path.insert" in content, \
        "conf.py should configure sys.path for autodoc"
    assert "../../src" in content or "'../../src'" in content, \
        "conf.py should add ../../src to path for autodoc"
    
    # Should have autodoc extension
    assert "sphinx.ext.autodoc" in content, \
        "conf.py should include sphinx.ext.autodoc extension"

