import os
import pickle
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
from app.models import Job, Company
from app import db

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
VECDB_JOB_PATH = "ml/job_vectors.faiss"
VECDB_JOB_META = "ml/job_vectors_meta.pkl"
VECDB_COMPANY_PATH = "ml/company_vectors.faiss"
VECDB_COMPANY_META = "ml/company_vectors_meta.pkl"

model = None
job_index = None
job_meta = None
company_index = None
company_meta = None

def get_model():
    global model
    if model is None:
        model = SentenceTransformer(MODEL_NAME)
    return model

def build_job_vector_db():
    jobs = Job.query.all()
    texts = []
    ids = []
    for job in jobs:
        # Kết hợp các trường chính
        fields = [
            str(job.title or ""),
            str(job.company_name or ""),
            str(job.sort_addresses or ""),
            str(job.full_addresses or ""),
            str(job.experience or ""),
            str(job.level or ""),
            str(job.job_type or ""),
            str(job.skills or ""),
            str(job.content or ""),
            str(job.requirements or ""),
            str(job.responsibilities or ""),
        ]
        text = " | ".join(fields)
        texts.append(text)
        ids.append(job.id)
    model = get_model()
    embeddings = model.encode(texts, show_progress_bar=True, convert_to_numpy=True)
    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(embeddings)
    with open(VECDB_JOB_META, "wb") as f:
        pickle.dump(ids, f)
    faiss.write_index(index, VECDB_JOB_PATH)

def build_company_vector_db():
    companies = Company.query.all()
    texts = []
    ids = []
    for comp in companies:
        fields = [
            str(comp.name or ""),
            str(comp.industry or ""),
            str(comp.size or ""),
            str(comp.nationality or ""),
            str(comp.tech_stack or ""),
            str(comp.short_address or ""),
            str(comp.address or ""),
            str(comp.description or ""),
            str(comp.shortdescription or ""),
        ]
        text = " | ".join(fields)
        texts.append(text)
        ids.append(comp.id)
    model = get_model()
    embeddings = model.encode(texts, show_progress_bar=True, convert_to_numpy=True)
    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(embeddings)
    with open(VECDB_COMPANY_META, "wb") as f:
        pickle.dump(ids, f)
    faiss.write_index(index, VECDB_COMPANY_PATH)

def load_job_vector_db():
    global job_index, job_meta
    if not (os.path.exists(VECDB_JOB_PATH) and os.path.exists(VECDB_JOB_META)):
        build_job_vector_db()
    job_index = faiss.read_index(VECDB_JOB_PATH)
    with open(VECDB_JOB_META, "rb") as f:
        job_meta = pickle.load(f)

def load_company_vector_db():
    global company_index, company_meta
    if not (os.path.exists(VECDB_COMPANY_PATH) and os.path.exists(VECDB_COMPANY_META)):
        build_company_vector_db()
    company_index = faiss.read_index(VECDB_COMPANY_PATH)
    with open(VECDB_COMPANY_META, "rb") as f:
        company_meta = pickle.load(f)

def search_jobs(query, top_k=10):
    if job_index is None or job_meta is None:
        load_job_vector_db()
    model = get_model()
    emb = model.encode([query], convert_to_numpy=True)
    D, I = job_index.search(emb, top_k)
    results = []
    for idx in I[0]:
        if idx < len(job_meta):
            results.append(job_meta[idx])
    return results

def search_companies(query, top_k=10):
    if company_index is None or company_meta is None:
        load_company_vector_db()
    model = get_model()
    emb = model.encode([query], convert_to_numpy=True)
    D, I = company_index.search(emb, top_k)
    results = []
    for idx in I[0]:
        if idx < len(company_meta):
            results.append(company_meta[idx])
    return results

def init_vector_dbs():
    load_job_vector_db()
    load_company_vector_db()
