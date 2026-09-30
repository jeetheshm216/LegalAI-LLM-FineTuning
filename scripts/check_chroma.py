import os

chroma_dir = '/home/sece2026-student07/legalai-finetuning/data/chroma_db'
if os.path.exists(chroma_dir):
    print('Chroma files:', os.listdir(chroma_dir))
    import chromadb
    client = chromadb.PersistentClient(path=chroma_dir)
    print('Collections:', [c.name for c in client.list_collections()])
    for c in client.list_collections():
        print(f"Collection: {c.name} | Count: {c.count()}")
else:
    print('No chroma_db dir')

case_doc_dir = '/home/sece2026-student07/legalai-finetuning/data/case_documents'
if os.path.exists(case_doc_dir):
    print('Case doc dirs:', os.listdir(case_doc_dir))
