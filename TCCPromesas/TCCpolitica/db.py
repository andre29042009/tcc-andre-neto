import os
from datetime import datetime, timezone

from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class Politician(db.Model):
    __tablename__ = "politicians"

    id = db.Column(db.String(80), primary_key=True)
    name = db.Column(db.String(180), nullable=False)
    category = db.Column(db.String(40), nullable=False)
    office = db.Column(db.String(120), nullable=False)
    party = db.Column(db.String(80), nullable=False)
    state = db.Column(db.String(10), nullable=False)
    started_at = db.Column(db.String(10), nullable=False)
    source_url = db.Column(db.Text, nullable=False)
    promises = db.relationship("Promise", backref="politician", cascade="all, delete-orphan")


class Promise(db.Model):
    __tablename__ = "promises"

    id = db.Column(db.Integer, primary_key=True)
    politician_id = db.Column(db.String(80), db.ForeignKey("politicians.id"), nullable=False)
    source_id = db.Column(db.String(80), nullable=False)
    promise = db.Column(db.Text, nullable=False)
    summary = db.Column(db.Text, nullable=True)
    theme = db.Column(db.String(160), nullable=True)
    source_url = db.Column(db.Text, nullable=False)
    g1_status = db.Column(db.String(50), nullable=False, default="nao-avaliada")
    current_status = db.Column(db.String(50), nullable=False, default="nao verificada")
    current_explanation = db.Column(db.Text, nullable=True)
    last_checked_at = db.Column(db.DateTime(timezone=True), nullable=True)
    assessments = db.relationship("Assessment", backref="promise", cascade="all, delete-orphan")


class Assessment(db.Model):
    __tablename__ = "assessments"

    id = db.Column(db.Integer, primary_key=True)
    promise_id = db.Column(db.Integer, db.ForeignKey("promises.id"), nullable=False)
    status = db.Column(db.String(50), nullable=False)
    explanation = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    articles = db.relationship("AssessmentArticle", backref="assessment", cascade="all, delete-orphan")


class AssessmentArticle(db.Model):
    __tablename__ = "assessment_articles"

    id = db.Column(db.Integer, primary_key=True)
    assessment_id = db.Column(db.Integer, db.ForeignKey("assessments.id"), nullable=False)
    title = db.Column(db.Text, nullable=False)
    url = db.Column(db.Text, nullable=False)
    site = db.Column(db.String(180), nullable=True)
    summary = db.Column(db.Text, nullable=True)


def database_url():
    return os.getenv("DATABASE_URL", "sqlite:///mapc.sqlite3")
