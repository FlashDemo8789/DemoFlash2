#!/usr/bin/env python3
"""
Clean up FLASH project - remove old files and organize
"""
import os
import shutil

def cleanup_flash_project():
    """Remove old files and organize the project."""
    
    # Directories to completely remove
    dirs_to_remove = [
        'flashcamp',  # Old project directory
        'models/v3',  # Old model attempt
        'data/training',  # Intermediate training data
        'examples',  # Old examples
        'docs',  # Old documentation
        'pipelines',  # Old pipelines
        'reports',  # Old reports
        'tests',  # Old tests
        'notebooks',  # Old notebooks
        'scripts',  # Old scripts
        '.git',  # Old git history
    ]
    
    # Files to remove
    files_to_remove = [
        'create_training_dataset.py',  # Old dataset creator
        'train_models.py',  # Old training script
        'DOCKER_README.md',
        'IMPLEMENTATION_PLAN.md',
        'IMPLEMENTATION_PLAN_BACKEND.md',
        'IMPLEMENTATION_SUMMARY.md',
        'README_old.md',
        'env.template',
        'docker-compose.yml',
        'Dockerfile.backend',
        'Dockerfile.frontend',
        '.gitignore',
        'data/hybrid_100k_companies.csv',  # Intermediate dataset
        'data/hybrid_sample_1000.csv',  # Intermediate sample
    ]
    
    # Count items before cleanup
    total_size_before = 0
    for root, dirs, files in os.walk('.'):
        for f in files:
            fp = os.path.join(root, f)
            if os.path.exists(fp):
                total_size_before += os.path.getsize(fp)
    
    print("FLASH 2.0 Project Cleanup")
    print("=" * 50)
    
    # Remove directories
    for dir_path in dirs_to_remove:
        if os.path.exists(dir_path):
            try:
                shutil.rmtree(dir_path)
                print(f"✓ Removed directory: {dir_path}")
            except Exception as e:
                print(f"✗ Error removing {dir_path}: {e}")
    
    # Remove files
    for file_path in files_to_remove:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"✓ Removed file: {file_path}")
            except Exception as e:
                print(f"✗ Error removing {file_path}: {e}")
    
    # Create clean README
    readme_content = """# FLASH 2.0 - AI-Powered Startup Success Prediction

## Overview
FLASH 2.0 uses advanced machine learning to predict startup success across 4 key pillars (CAMP):
- **C**apital: Financial health and efficiency
- **A**dvantage: Competitive moat and differentiation  
- **M**arket: TAM and growth dynamics
- **P**eople: Team quality and experience

## Quick Start

1. **Start the API server:**
   ```bash
   python3 api_server.py
   ```

2. **Start the React frontend:**
   ```bash
   cd flash-frontend
   npm start
   ```

3. **Access the application:**
   - Frontend: http://localhost:3000
   - API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

## Architecture

- **Models**: CatBoost ensemble with 77% AUC
- **API**: FastAPI with automatic validation
- **Frontend**: React with Apple/OpenAI-inspired design
- **Dataset**: 100k companies with 45 features

## Project Structure
```
FLASH/
├── api_server.py           # FastAPI inference server
├── train_flash_v2.py       # Model training pipeline
├── models/                 # Trained ML models
│   ├── v2/                # Base CatBoost models
│   └── v2_enhanced/       # Ensemble models
├── data/                  # Datasets
│   └── final_100k_dataset_45features.csv
├── flash-frontend/        # React application
└── requirements.txt       # Python dependencies
```

## Performance
- **Test AUC**: 77.3%
- **Inference Time**: <150ms
- **Models**: 11 total (4 base + 7 ensemble)

Built with ❤️ using CatBoost, FastAPI, and React.
"""
    
    with open('README.md', 'w') as f:
        f.write(readme_content)
    print("\n✓ Created clean README.md")
    
    # Count items after cleanup
    total_size_after = 0
    file_count = 0
    for root, dirs, files in os.walk('.'):
        # Skip node_modules
        if 'node_modules' in root:
            continue
        for f in files:
            fp = os.path.join(root, f)
            if os.path.exists(fp):
                total_size_after += os.path.getsize(fp)
                file_count += 1
    
    # Summary
    print("\n" + "=" * 50)
    print("Cleanup Summary:")
    print(f"Space freed: {(total_size_before - total_size_after) / 1024 / 1024:.1f} MB")
    print(f"Remaining files: {file_count} (excluding node_modules)")
    print("\nProject is now clean and organized!")
    print("\nKept:")
    print("- Models: /models/v2/ and /models/v2_enhanced/")
    print("- Dataset: /data/final_100k_dataset_45features.csv")
    print("- Code: api_server.py, training scripts, React app")
    
if __name__ == "__main__":
    response = input("This will delete old project files. Continue? (yes/no): ")
    if response.lower() == 'yes':
        cleanup_flash_project()
    else:
        print("Cleanup cancelled.")