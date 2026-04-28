import pandas as pd


class State:
    """Represents a student's current academic situation."""

    def __init__(self, attendance, missing, score, lms, study_hours, days, fatigue):
        self.attendance  = attendance
        self.missing     = missing
        self.score       = score
        self.lms         = lms
        self.study_hours = study_hours
        self.days        = days
        self.fatigue     = fatigue

    def __repr__(self):
        return (f"State(att={round(self.attendance, 2)}, "
                f"miss={self.missing}, "
                f"score={self.score}, "
                f"lms={round(self.lms, 2)}, "
                f"hrs={self.study_hours}, "
                f"days={self.days}, "
                f"fatigue={self.fatigue})")

    def __eq__(self, other):
        if not isinstance(other, State):
            return False
        return (round(self.attendance, 2) == round(other.attendance, 2) and
                self.missing     == other.missing and
                self.score       == other.score and
                round(self.lms, 2) == round(other.lms, 2) and
                self.study_hours == other.study_hours and
                self.days        == other.days and
                self.fatigue     == other.fatigue)

    def __hash__(self):
        return hash((round(self.attendance, 2), self.missing, self.score,
                     round(self.lms, 2), self.study_hours, self.days, self.fatigue))


# --------------- Risk Score & Goal ---------------

def risk_score(s):
    """
    7-component weighted risk score on a 0.0-1.0 scale. Lower is better.
    Includes deadline proximity and fatigue alongside the core academic metrics.

    Weights (sum to 1.0):
        attendance  0.22 | missing  0.24 | quiz  0.20 | lms   0.12
        study       0.10 | deadline 0.07 | fatigue 0.05
    """
    attendance_risk = 1.0 - s.attendance                         # s.attendance is 0.0–1.0
    missing_risk    = min(s.missing / 5.0, 1.0)
    quiz_risk       = (100 - s.score) / 100.0
    lms_risk        = 1.0 - s.lms                                # s.lms is 0.0–1.0
    study_risk      = max(0.0, (10 - s.study_hours) / 10.0)
    deadline_risk   = 1.0 if s.days <= 0 else 1.0 / (s.days + 1)
    fatigue_risk    = s.fatigue / 10.0

    return round(
        0.22 * attendance_risk
        + 0.24 * missing_risk
        + 0.20 * quiz_risk
        + 0.12 * lms_risk
        + 0.10 * study_risk
        + 0.07 * deadline_risk
        + 0.05 * fatigue_risk,
        4,
    )


RISK_THRESHOLD = 0.35


def is_goal(s):
    """Goal: no missing submissions and risk score below threshold."""
    return s.missing == 0 and risk_score(s) <= RISK_THRESHOLD


def heuristic(s):
    """
    6-component admissible heuristic estimating the minimum remaining cost
    to reach the goal state.

    Each component is a conservative lower-bound of the effort needed:
      - risk_gap     : excess risk scaled down (underestimates true reduction cost)
      - missing_part : each missing item needs >= 1 submit action costing >= 1.2
      - quiz_part    : score below 60 needs study/quiz actions (cheapest costs ~1.5/4pts)
      - attend_part  : attendance below 75% needs attend actions (cheapest costs ~2.0/5%)
      - lms_part     : low LMS activity needs engagement actions
      - study_part   : low study hours need improvement
      - deadline_part: urgent deadline with missing work adds minimum pressure cost
    Combined, this never overestimates the true path cost, keeping A* optimal.
    """
    risk_gap      = max(0.0, risk_score(s) - RISK_THRESHOLD)
    missing_part  = s.missing * 1.2
    quiz_part     = max(0.0, 60 - s.score) / 20.0
    attend_part   = max(0.0, 0.75 - s.attendance) / 0.15
    lms_part      = max(0.0, 0.6 - s.lms) * 2.5
    study_part    = max(0.0, 8 - s.study_hours) / 4.0
    deadline_part = 2.0 if s.days <= 1 and s.missing > 0 else 0.0

    return round(
        risk_gap * 8 + missing_part + quiz_part + attend_part + lms_part + study_part + deadline_part,
        3,
    )


# --------------- Deadline Penalty Helper Function---------------

def _deadline_penalty(s):
    """
    Soft cost penalty applied after an action if the deadline becomes critical.
    Encourages the planner to complete work before the deadline expires.
    """
    if s.days < 0:
        return 8.0
    if s.days == 0 and s.missing > 0:
        return 5.0
    return 0.0


# --------------- Actions (>= 6 required) ---------------
# Time-consuming actions (attend, submit, meet tutor, rest) decrement
# days_to_deadline by 1 to reflect that they consume a day slot.
# Self-paced actions (study, quiz) do not consume a full day.

def study_1_hour(s):
    """Study for one hour: improves score and LMS activity. Does not use a day slot."""
    if s.study_hours <= 0:
        return None
    if s.fatigue >= 10:
        return None
    new = State(s.attendance, s.missing, min(100, s.score + 4),
                min(1.0, s.lms + 0.1), s.study_hours - 1, s.days, s.fatigue + 2)
    cost = 1.5 + new.fatigue * 0.3 + _deadline_penalty(new)
    return new, round(cost, 3)


def attend_class(s):
    """Attend a class session: improves attendance and score. Consumes a day slot."""
    if s.attendance >= 1.0:
        return None
    if s.days <= 0:
        return None
    new = State(min(1.0, s.attendance + 0.05), s.missing, min(100, s.score + 2),
                min(1.0, s.lms + 0.1), s.study_hours, s.days - 1, s.fatigue + 1)
    cost = 2.0 + new.fatigue * 0.2 + _deadline_penalty(new)
    return new, round(cost, 3)


def submit_assignment(s):
    """Submit a missing assignment: reduces missing count. Consumes a day slot."""
    if s.missing <= 0:
        return None
    if s.days <= 0:
        return None
    new = State(s.attendance, s.missing - 1, min(100, s.score + 3),
                min(1.0, s.lms + 0.1), s.study_hours, s.days - 1, s.fatigue + 1)
    cost = 3.0 + new.fatigue * 0.4 + _deadline_penalty(new)
    return new, round(cost, 3)


def practice_quiz(s):
    """Practice a quiz: bigger score boost, improves LMS. Does not use a day slot."""
    if s.score >= 100 and s.lms >= 1.0:
        return None
    if s.fatigue >= 10:
        return None
    new = State(s.attendance, s.missing, min(100, s.score + 6),
                min(1.0, s.lms + 0.05), max(0, s.study_hours - 1), s.days, s.fatigue + 2)
    cost = 2.0 + new.fatigue * 0.3 + _deadline_penalty(new)
    return new, round(cost, 3)


def meet_tutor(s):
    """Meet a tutor: largest score boost, slight attendance lift. Consumes a day slot."""
    if s.days <= 0:
        return None
    if s.fatigue >= 10:
        return None
    new = State(min(1.0, s.attendance + 0.02), s.missing, min(100, s.score + 8),
                min(1.0, s.lms + 0.1), max(0, s.study_hours - 1), s.days - 1, s.fatigue + 1)
    cost = 2.5 + new.fatigue * 0.2 + _deadline_penalty(new)
    return new, round(cost, 3)


def rest(s):
    """Rest to recover fatigue. Consumes a day slot."""
    if s.fatigue == 0:
        return None
    if s.days <= 0:
        return None
    new = State(s.attendance, s.missing, min(100, s.score + 1),
                s.lms, s.study_hours, s.days - 1, max(0, s.fatigue - 3))
    cost = 1.0 + _deadline_penalty(new)
    return new, round(cost, 3)


ALL_ACTIONS = [study_1_hour, attend_class, submit_assignment, practice_quiz, meet_tutor, rest]

ACTION_DESCRIPTIONS = {
    'study_1_hour':      'Study for 1 Hour',
    'attend_class':      'Attend Class',
    'submit_assignment': 'Submit Assignment',
    'practice_quiz':     'Practice Quiz',
    'meet_tutor':        'Meet Tutor',
    'rest':              'Rest / Recover',
}


# --------------- Data Loading ---------------

def load_students_csv(filepath):
    """Load student data from CSV file."""
    df = pd.read_csv(filepath)
    required = ['attendance_rate', 'missing_submissions', 'avg_quiz_score',
                'lms_activity', 'study_hours_per_week', 'days_to_deadline']
    for col in required:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")
    return df


def state_from_row(row):
    """Create a State object from a DataFrame row."""
    att = float(row['attendance_rate'])
    lms = float(row['lms_activity'])
    # Support CSVs that store these as percentages (0–100) instead of fractions (0–1)
    if att > 1.0:
        att /= 100.0
    if lms > 1.0:
        lms /= 100.0
    return State(
        attendance=att,
        missing=int(row['missing_submissions']),
        score=float(row['avg_quiz_score']),
        lms=lms,
        study_hours=float(row['study_hours_per_week']),
        days=float(row['days_to_deadline']),
        fatigue=0,
    )


def generate_sample_data():
    """Generate sample student scenarios for testing."""
    data = {
        'student_name':         ['Alice', 'Bob', 'Carol', 'David', 'Eve',
                                 'Frank', 'Grace', 'Hana', 'Ivan', 'Judy'],
        'attendance_rate':      [0.50, 0.65, 0.40, 0.75, 0.55,
                                 0.30, 0.80, 0.60, 0.45, 0.70],
        'missing_submissions':  [3,    2,    4,    1,    3,
                                 5,    1,    2,    4,    2],
        'avg_quiz_score':       [55,   60,   45,   70,   50,
                                 40,   72,   58,   42,   65],
        'lms_activity':         [0.30, 0.50, 0.20, 0.60, 0.35,
                                 0.15, 0.65, 0.40, 0.25, 0.55],
        'study_hours_per_week': [10,   12,   8,    14,   10,
                                 6,    15,   11,   7,    13],
        'days_to_deadline':     [14,   10,   7,    21,   12,
                                 5,    18,   9,    6,    16],
    }
    return pd.DataFrame(data)
