from sklearn.tree import DecisionTreeClassifier
from sklearn.preprocessing import LabelEncoder
import numpy as np

class DecisionTreeRecommender:
    def __init__(self):
        self.clf = None
        self.encoders = [LabelEncoder() for _ in range(3)]
        self.job_ids = []
        self.X_encoded = None

    def job_to_features(self, job):
        level = (job.level or '').lower()
        job_type = (job.job_type or '').lower()
        skills = ','.join(job.skills) if isinstance(job.skills, list) else (job.skills or '').lower()
        return [level, job_type, skills]

    def fit(self, jobs, current_job=None):
        X = []
        y = []
        job_ids = []
        for job in jobs:
            if current_job and job.id == current_job.id:
                continue
            X.append(self.job_to_features(job))
            y.append(1 if current_job and job.company_name == current_job.company_name else 0)
            job_ids.append(job.id)
        if not X or len(X) < 2:
            self.clf = None
            self.X_encoded = None
            self.job_ids = []
            return
        # Fit encoders
        for i in range(3):
            self.encoders[i].fit([row[i] for row in X])
        # Encode features
        self.X_encoded = np.array([
            [self.encoders[i].transform([row[i]])[0] if row[i] in self.encoders[i].classes_ else 0 for i in range(3)]
            for row in X
        ])
        self.clf = DecisionTreeClassifier(max_depth=3)
        self.clf.fit(self.X_encoded, y)
        self.job_ids = job_ids

    def recommend(self, current_job, jobs, n=5):
        if not self.clf or self.X_encoded is None:
            return []
        current_features = self.job_to_features(current_job)
        current_encoded = [
            self.encoders[i].transform([current_features[i]])[0]
            if current_features[i] in self.encoders[i].classes_ else 0
            for i in range(3)
        ]
        # Predict similarity score for all jobs
        probs = self.clf.predict_proba(self.X_encoded)
        if probs.shape[1] < 2:
            # Only one class present in training, cannot recommend
            return []
        probs = probs[:, 1]
        top_indices = np.argsort(probs)[-n:][::-1]
        recommended_ids = [self.job_ids[i] for i in top_indices]
        recommended_jobs = [job for job in jobs if job.id in recommended_ids]
        return recommended_jobs
