from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone

db = SQLAlchemy()


class Report(db.Model):
    __tablename__ = 'reports'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tracking_id = db.Column(db.String(20), unique=True, nullable=False)
    image_path = db.Column(db.String(255), nullable=False)
    location_text = db.Column(db.String(500), nullable=False)
    area_type = db.Column(db.String(50), nullable=False)

    # Gemini Role 1+2: Vision analysis + impact scoring
    issue_type = db.Column(db.String(100))
    severity = db.Column(db.Integer)
    description = db.Column(db.Text)
    department = db.Column(db.String(100))
    department_reasoning = db.Column(db.Text)
    impact_score = db.Column(db.Integer)
    impact_reasoning = db.Column(db.Text)
    confidence_score = db.Column(db.Float)

    # Gemini Role 3: Recurrence analysis
    is_recurring = db.Column(db.Boolean, default=False)
    recurrence_count = db.Column(db.Integer, default=0)
    recurrence_pattern = db.Column(db.Text)
    escalation_level = db.Column(db.String(20), default='standard')

    # Gemini Roles 4+5: Letters
    escalation_letter = db.Column(db.Text)
    followup_letter = db.Column(db.Text, nullable=True)
    followup_generated_at = db.Column(db.DateTime, nullable=True)
    escalation_due = db.Column(db.Boolean, default=False)

    # Map coordinates (user-provided, optional)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)

    # Status lifecycle
    status = db.Column(db.String(30), default='reported')
    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc)
    )

    __table_args__ = (
        db.Index('idx_location_issue', 'location_text', 'issue_type'),
        db.Index('idx_status_created', 'status', 'created_at'),
    )

    def __repr__(self):
        return f'<Report {self.tracking_id}: {self.issue_type}>'


class ChatMessage(db.Model):
    __tablename__ = 'chat_messages'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    report_id = db.Column(
        db.Integer,
        db.ForeignKey('reports.id'),
        nullable=False
    )
    role = db.Column(db.String(10), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc)
    )

    def __repr__(self):
        return f'<ChatMessage report={self.report_id} role={self.role}>'