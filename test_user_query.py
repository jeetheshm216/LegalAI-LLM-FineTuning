
import sys
sys.path.insert(0, '/home/sece2026-student07/legalai-finetuning')
from src.api.server import pipeline
from src.legal_knowledge.retrieval.pipeline import GeneralIndianLegalKnowledgePipeline

pipe = GeneralIndianLegalKnowledgePipeline(
    db_path='/home/sece2026-student07/legalai-finetuning/data/legalai_indian_legal_knowledge.db',
    base_pipeline=pipeline
)
q = 'A person was murdered by a group of 6 people because of his caste on 15 August 2024. Which provision of the Bharatiya Nyaya Sanhita, 2023 applies, specifically under Section 103(1) or 103(2)? Also, if the same incident had occurred on 15 June 2024, would BNS still apply, or would the IPC apply? Explain the relevance of Article 20(1) of the Constitution.'
res = pipe.query(q)
print('--- CURRENT ANSWER ---')
print(res['answer'])
print('--- END ANSWER ---')
