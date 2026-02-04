"""
Data Migration Script

Django 프로젝트에서 데이터 파일 복사
"""
import shutil
from pathlib import Path


def copy_data_files():
    """Copy data files from Django project to FastAPI workspace."""
    # Source and destination paths
    django_base = Path(__file__).parent.parent.parent / "web"
    fastapi_base = Path(__file__).parent.parent
    
    # HSKModel data files
    hskmodel_src = django_base / "hskmodel" / "data"
    hskmodel_dst = fastapi_base / "src" / "core" / "hskmodel" / "data"
    
    if hskmodel_src.exists():
        for file in hskmodel_src.glob("*.json"):
            print(f"Copying {file.name}...")
            shutil.copy2(file, hskmodel_dst / file.name)
        print(f"HSKModel data files copied to {hskmodel_dst}")
    else:
        print(f"Source directory not found: {hskmodel_src}")
    
    # Blog markdown files
    blog_src = django_base / "blog" / "blog_post"
    blog_dst = fastapi_base / "data" / "blog_posts"
    
    if blog_src.exists():
        blog_dst.mkdir(parents=True, exist_ok=True)
        for file in blog_src.glob("*.md"):
            print(f"Copying {file.name}...")
            shutil.copy2(file, blog_dst / file.name)
        # Copy meta_data.json if exists
        meta_file = blog_src / "meta_data.json"
        if meta_file.exists():
            shutil.copy2(meta_file, blog_dst / "meta_data.json")
        print(f"Blog post files copied to {blog_dst}")
    else:
        print(f"Source directory not found: {blog_src}")


if __name__ == "__main__":
    copy_data_files()
