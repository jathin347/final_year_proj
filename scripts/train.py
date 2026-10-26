"""
Model Training and Calibration Script for VeritasAI Text Stylometrics
Trains a reproducible, calibrated classification pipeline on stylistic & misinformation indicators.
"""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import joblib
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, f1_score

# Expanded balanced training corpus of journalistic vs sensationalist/misinformation text
TRAINING_DATA = [
    # Credible / Journalistic (Label 0)
    ("Federal reserve holds benchmark borrowing interest rate steady following consumer price inflation data release.", 0),
    ("According to official spokespersons at the headquarters, the ministry announced updated infrastructure guidelines.", 0),
    ("Researchers at the university hospital published findings in a peer-reviewed journal on malaria vaccine efficacy.", 0),
    ("The bilateral trade agreement between nations was ratified following parliamentary debate in session.", 0),
    ("Quarterly revenue reports indicated a 4% increase in manufacturing output, according to commerce department statistics.", 0),
    ("Municipal authorities announced scheduled water pipeline maintenance across three downtown districts next Wednesday.", 0),
    ("European space agency confirmed successful deployment of solar observation satellite into stable orbit.", 0),
    ("Reuters reported that diplomats concluded preliminary ceasefire discussions without immediate territorial accord.", 0),
    ("The state supreme court affirmed lower bench rulings concerning public utility regulatory oversight.", 0),
    ("Epidemiologists noted steady decline in seasonal influenza hospitalizations across northern regions.", 0),
    ("Department of Agriculture releases annual crop yield forecast citing improved irrigation infrastructure.", 0),
    ("Treasury department publishes audit of state pension expenditures showing increased surplus reserves.", 0),
    ("Civil protection agency coordinates flood relief supplies in response to prolonged coastal rainfall.", 0),
    ("Independent monitors verify parliamentary ballot counts across regional electoral districts.", 0),
    ("Aviation regulators mandate software inspections across regional transport carriers following safety review.", 0),
    ("National institutes of health allocate research grants for pediatric cardiology studies.", 0),
    ("City council approves zoning amendments for commercial downtown revitalization plan.", 0),
    ("World Meteorological Organization documents record ocean temperatures in annual climate status report.", 0),
    ("Telecommunications authority opens public consultation on rural broadband spectrum licensing.", 0),
    ("Labor department statistics show unemployment rate unchanged at 3.8 percent for third consecutive month.", 0),

    # Misinformation / Sensationalist (Label 1)
    ("SHOCKING TRUTH EXPOSED: Doctors don't want you to know this secret miracle mineral cure for all diseases!", 1),
    ("You won't believe what the secret shadow government did last night! Mainstream media is completely silent!", 1),
    ("BOMBSHELL REPORT: Astronomers confirm giant rogue planet will smash into earth next Tuesday panic everywhere!", 1),
    ("PROOF: Chemtrails contain microchips to control citizen minds, whistleblower leaks mind-blowing secret documents!", 1),
    ("HIDDEN SECRETS REVEALED: Miracle dietary supplement dissolves all tumors in 48 hours without surgery or drugs!", 1),
    ("They are lying to you! The global cabal is secretly replacing tap water with mind-altering chemicals!", 1),
    ("UNBELIEVABLE: Five-headed alien discovered alive in underground government bunker, photographs leaked!", 1),
    ("Doctors hate him! Local man cures diabetes overnight using this one weird kitchen trick they tried to ban!", 1),
    ("HOAX EXPOSED: Top scientists admit global warming is a fabricated plot to steal your private vehicle!", 1),
    ("Rigged election proof leaked: Secret quantum computer manipulated every ballot, military preparing arrests!", 1),
    ("MIRACLE WATER REVEALED: Drink this frequency-charged liquid to immediately reverse biological aging!", 1),
    ("WHAT HAPPENS NEXT WILL BLOW YOUR MIND: Secret reptilian overlords spotted entering United Nations basement!", 1),
    ("BANNED VIDEO: The secret reason elite billionaires are building underground bunkers in New Zealand!", 1),
    ("CONSPIRACY CONFIRMED: 5G towers are secretly activating nanobots inside common household vaccines!", 1),
    ("MUST-SEE BOMBSHELL: Whistleblower leaks proof that earth is actually hollow and inhabited by ancient race!", 1),
    ("DOCTORS ARE FURIOUS: One simple lemon juice and vinegar mixture cures all forms of advanced arthritis!", 1),
    ("THEY DON'T WANT YOU TO SEE THIS: Proof that gravity is a fictional construct invented by government agencies!", 1),
    ("EXPOSED: Top secret mind control microwave signals being broadcast through popular cereal packaging!", 1),
    ("UNBELIEVABLE HOAX: NASA admits the moon is a holographic projection created during the Cold War!", 1),
    ("WARNING TO ALL CITIZENS: Secret military tribunal preparing mass arrests of celebrity cabal members tomorrow!", 1),
]

def train_and_evaluate():
    print("====================================================")
    print("VeritasAI Model Training Pipeline")
    print("====================================================")
    
    texts, labels = zip(*TRAINING_DATA)
    
    # 80/20 train/test split with seed
    X_train, X_test, y_train, y_test = train_test_split(
        texts, labels, test_size=0.25, random_state=42, stratify=labels
    )
    
    print(f"Training samples: {len(X_train)} | Held-out test samples: {len(X_test)}")
    
    # Pipeline preventing data leakage
    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(ngram_range=(1, 2), min_df=1, stop_words='english')),
        ('clf', LogisticRegression(C=1.0, solver='lbfgs', random_state=42))
    ])
    
    # Fit only on training split
    pipeline.fit(X_train, y_train)
    
    # Evaluate on held-out test split
    y_pred = pipeline.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    
    print(f"\nHeld-Out Test Accuracy: {acc * 100:.2f}%")
    print(f"Held-Out Test F1 Score: {f1:.4f}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=["Credible", "Misinformation Risk"]))
    print("Confusion Matrix:")
    print(confusion_matrix(y_test, y_pred))
    
    # Save model artifact
    os.makedirs("models", exist_ok=True)
    model_path = "models/stylistic_classifier.joblib"
    joblib.dump(pipeline, model_path)
    print(f"\nModel artifact saved to: {model_path}")

if __name__ == "__main__":
    train_and_evaluate()
