- name: 📚 Generate README_AUTO.md
  run: |
    source .venv/bin/activate
    python scripts/gen_docs.py
