# ==============================================================================================================================================================================
# Project Brief: Voting Mechanism
# ==============================================================================================================================================================================
# Implements various voting rule functions:
# - Refer to the GitHub Wiki for detailed explanations: 
#   https://github.com/cheuh008/Comp517_CW/wiki
#
# Author: Harry Cheung, GitHub https://github.com/cheuh008/
# ==============================================================================================================================================================================

class Preference:
    """Abstract base class for a preference interface."""
    
    def candidates(self):
        """Returns the list of candidates as [1, ..., n]."""
        raise NotImplementedError
    
    def voters(self):
        """Returns the list of distinct voters as [1, ..., n]."""
        raise NotImplementedError
    
    def get_preference(self, candidate, voter):
        """Returns the preference rank of a candidate for a given voter."""
        raise NotImplementedError

def tie_break(candidates, winners):
    """Resolve ties by selecting the first candidate from winners."""
    return next((c for c in candidates if c in winners), None)

def calculate_points(preferences, tie_break, scoring_fn):
    """Calculates points for each candidate based on a scoring function."""
    scores = {c: 0 for c in preferences.candidates()}
    for voter in preferences.voters():
        scoring_fn(preferences, voter, scores)
    highest_score = max(scores.values())
    winners = [c for c, s in scores.items() if s == highest_score]
    return tie_break(preferences.candidates(), winners) if len(winners) > 1 else winners[0]

def dictatorship(preferences, agent):
    """Dictatorship rule: one agent (voter) determines the winner."""
    if agent not in preferences.voters(): raise ValueError("Invalid agent")
    return next((c for c in preferences.candidates() if preferences.get_preference(c, agent) == 0), None)

def scoring_rule(preferences, score_vector, tie_break_agent):
    """Scoring rule: assign points based on rank."""
    if len(score_vector) != len(preferences.candidates()): raise ValueError("Score vector length mismatch")
    scoring_fn = lambda prefs, voter, scores: scores.update(
        {c: scores[c] + score_vector[rank] for rank, c in enumerate(
            sorted(prefs.candidates(), key=lambda c: prefs.get_preference(c, voter)))})
    tie_break_fn = lambda c, w: tie_break(
        sorted(c, key=lambda x: preferences.get_preference(x, tie_break_agent)), w)
    return calculate_points(preferences, tie_break_fn, scoring_fn)

def plurality(preferences, tie_break):
    """Plurality rule: top choice for each voter receives one point."""
    scoring_fn = lambda prefs, voter, scores: scores.update(
        {c: scores[c] + 1 for c in prefs.candidates() if prefs.get_preference(c, voter) == 0}
    )
    return calculate_points(preferences, tie_break, scoring_fn)

def veto(preferences, tie_break):
    """Veto rule: all but the lowest-ranked candidate get points."""
    scoring_fn = lambda prefs, voter, scores: scores.update(
        {c: scores[c] + 1 for c in prefs.candidates() if prefs.get_preference(c, voter) != len(prefs.candidates()) - 1}
    )
    return calculate_points(preferences, tie_break, scoring_fn)

def borda(preferences, tie_break):
    """Borda rule: candidates receive points inversely proportional to their rank."""
    scoring_fn = lambda prefs, voter, scores: scores.update(
        {c: scores[c] + len(prefs.candidates()) - 1 - prefs.get_preference(c, voter) for c in prefs.candidates()}
    )
    return calculate_points(preferences, tie_break, scoring_fn)

def STV(preferences, tie_break):
    """STV rule: candidates with fewest votes are iteratively eliminated until one remains."""
    candidates, voters = set(preferences.candidates()), preferences.voters()
    while len(candidates) > 1:
        scores = {c: sum(1 for v in voters if preferences.get_preference(c, v) == 0) for c in candidates}
        min_count = min(scores.values())
        candidates -= {c for c, count in scores.items() if count == min_count}
    return next(iter(candidates), None)
