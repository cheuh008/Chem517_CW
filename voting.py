# ==============================================================================================================================================================================
# region Project Brief: Voting Mechanism
# ==============================================================================================================================================================================
# Implements various voting rule functions:
#  1. `dictatorship(preferences, agent)` -> int
#  2. `scoring_rule(preferences, score_vector, tie_break)` -> int
#  3. `plurality(preferences, tie_break)` -> int
#  4. `veto(preferences, tie_break)` -> int
#  5. `borda(preferences, tie_break)` -> int
#  6. `STV(preferences, tie_break)` -> int
#
# Documentation for this project and more details on the voting rules can be found at:
#  - [Voting Mechanism Docs](https://github.com/cheuh008/Comp517_CW/wiki)
#  - and refering to the docs as needed
#  - A cleaner version of the code without all the regions is avalibale on https://github.com/cheuh008/Comp517_CW (should be)
#
# Author: Harry Cheung, GitHub https://github.com/cheuh008/
# ==============================================================================================================================================================================
# endregion

# ==============================================================================================================================================================================
# region Preference Class Definition
# ==============================================================================================================================================================================
# Notes:
#   - The Preference class is an abstract base class for representing the preferences of voters over a set of candidates.
#   - It provides an interface via three methods: candidates, voters, and get_preference.
#   - Each method is meant to be implemented by a subclass that defines the specific structure and data of the preference profile.
#          - See below # Sanity check test code for example
#   - Each method will raises a "NotImplementedError" if not implemented by subclass.
# ==============================================================================================================================================================================
# endregion

class Preference:
    """
    Abstract base class for a preference interface.

    Methods:
        candidates(): Returns a list of candidates.
        voters(): Returns a list of distinct voters.
        get_preference(candidate, voter): Returns the rank of a candidate for a given voter,
                                           with 0 as the highest rank.
    Raises:
        NotImplementedError: if the subclass does not implement any of the methods.
    """
    def candidates(self):
        """Returns the list of candidates as [1, ..., n]. Must be implemented by subclass."""
        raise NotImplementedError
    def voters(self):
        """Returns the list of distinct voters as [1, ..., n]. Must be implemented by subclass."""
        raise NotImplementedError
    def get_preference(self, candidate, voter):
        """
        Returns the preference rank of a candidate for a given voter.
        
        Parameters:
            candidate: The candidate for whom the preference rank is requested.
            voter: The voter whose preference is being queried.

        Returns:
            int: Rank of the candidate for this voter (0 is the highest rank).
            
        """
        raise NotImplementedError

# ==============================================================================================================================================================================
# region Helper Function: Tie Break
# ==============================================================================================================================================================================
# Notes:
#   - Tie Break has been abstracted due to multi implementation, and is easier to just call rather than define again
#   - Resolves ties by returning the first candidate in the winners list.
#   - This function lets rules replace it with their own tie-breaking function if needed.
#   - next() is used as it after it identifies the first item, by iterating through each candidate "c" we try to match it to if they are in the list of winners
# ==============================================================================================================================================================================
# endregion
def tie_break(candidates, winners):                              # Helper Function which abstract tie breaking by Returning the first candiate in winners
    """
    Resolve ties by selecting the first candidate from winners.
    Parameters:
        candidates (list): List of all candidates in the election.
        winners (list): List of candidates who are potential winners (i.e., tied with the highest score).

    Returns:
        int or None: The first candidate found in `candidates` that also exists in `winners`.
                     If no match is found, returns `None`.
    """
    return next((c for c in candidates if c in winners), None)  # Returns first candiate that appears in winners 

# ==============================================================================================================================================================================
# region Helper Function: Calculate Points
# ==============================================================================================================================================================================
# Notes:
#   - Calculate Points is another helper function that is used by multiple voting mechanisms to tally scores and determine the winning candidate.
#   - As such it may not make sense until further down the code but Tl;DR...
#   - All the similarites between rules have been collated and abstracted to this but as each rule has a different scoring system...
#   - It aggregates scores based on a provided scoring_fn function.
#   - Each rule has its own unqie scoring_fn which determines how the scores are added up. But the intialisation of the scores dictionary and the way it finds a winner...
#   - Is the same for the 4 rule mechanisms (2-5) that uses it.
#   - This function abstracts the repetitive logic of scoring and tie-breaking, making the voting mechanism functions simpler and more modular.
#
# Steps:
#   1. dictionary comprehension is used to loop throguh each candidate as "c" defined as the keys : witha value of 0 tyo start off with
#   2. Iterate over each voter and apply the `scoring_fn` function to update scores.
#   3. Identifing and saving the highest score among all the candidates to match to a winner(s) 
#   4. The winning candidate(s) is found if their scores "s" matches the highest score. list comprehension iterates over each candidate
#   5. The winnning Cadidate (int) is then returned (unless theres a tie in which case it calls the tie_break() function)
# ==============================================================================================================================================================================
# endregion
def calculate_points(preferences, tie_break, scoring_fn):                                   # Helper Function which abstracts points calulating to find winning candidate
    """
    Calculates the points for each candidate based on the given scoring function to determine a winner.
    
    Parameters:
        preferences (Preference): The preference profile containing candidates and voters.
        tie_break (function): A function to determine the winner in case of a tie.
        scoring_fn (function): A function that defines how points are assigned to candidates based on voter preferences.

    Returns:
        int: Candidate with the highest score (winner), or finds it via tie-breaking function if needed.
    """
    scores = {c: 0 for c in preferences.candidates()}                                       # Step 1: dictionary saves and gives each candidate a score of 0 
    for voter in preferences.voters():                                                      # Step 2: Iterate over each voter to update the scores of each candidate
        scoring_fn(preferences, voter, scores)                                                  # By using the custom scoring function depending in the rule used
    highest_score = max(scores.values())                                                    # Step 3: Finding the highest score 
    winners = [c for c, s in scores.items() if s == highest_score]                          # Step 4: Match the candidate with the highest score as the winner(s)
    return tie_break(preferences.candidates(), winners) if len(winners) > 1 else winners[0] # Step 5. Return winning candidate, uses tie_break if needed

# ==============================================================================================================================================================================
# region Voting Mechanism 1. Dictatorship Function
# ==============================================================================================================================================================================
# Notes:
#   - A single agent (voter) choose winner where rank (pref.get_pref) == 0.
#   - This mechanism ignores the preferences of all other voters, relying solely on the preference of the specified "dictator."
#   - The winning candidate is the one ranked highest (rank 0) by the dictator.
# ==============================================================================================================================================================================
# endregion
def dictatorship(preferences, agent):                               # Voting Mechanism 1
    """
    Implements the Dictatorship voting mechanism, where a single agent (voter) unilaterally decides the winning candidate.
    
    Parameters:
        preferences (Preference): The preference profile containing candidates and voters.
        agent (int): The specific voter designated as the "dictator."

    Returns:
        int: The candidate that the dictator has ranked as their top choice (rank 0).

    Raises:
        ValueError: If the specified agent is not a valid voter.
    """
    if agent not in preferences.voters():                           # Step 1a: Check if the agent is valid (in voters).
        raise ValueError("Invalid agent")                           # Step 1b. raise error if not.
    return next((c for c in preferences.candidates()                # Step 2a: Iterates over candidate
            if preferences.get_preference(c, agent) == 0), None)    # Step 2b. Return the candidate ranked 0 by agent.

def scoring_rule(preferences, score_vector, tie_break_agent):   # Voting Mechanism 2. Scoring Rule
    """
    Scoring Rule: where each candidate receives points based on their rank position for each voter.

    Parameters:
        preferences (Preference): The preference profile containing candidates, voters, and rankings.
        score_vector (list): A list of integers representing scores for each rank (top rank has the highest score).
        tie_break (function): A function to resolve ties if multiple candidates have the highest score.

    Returns:
        int: The candidate with the highest total score according to the scoring rule, or tie-breaking if necessary.

    Raises:
        ValueError: If `score_vector` length does not match the number of candidates.
    """
    if len(score_vector) != len(preferences.candidates()):      # Step 1a. Validates score_vector is the same length as the number of candidates.
        raise ValueError("Score vector length mismatch")        # Step 1b. If lengths do not match, a ValueError is raised.
    
    def scoring_fn(preferences, voter, scores):                 # Rule based, abstracted scoring function, which is passed into the calculate function to return a winner
        sorted_candidates = sorted(preferences.candidates(),    # To match Points to candidates, they are sorted using...
            key=lambda c: preferences.get_preference(c, voter)) # A lambda (namless) function which sorts it via the ranking.
        for rank, candidate in enumerate(sorted_candidates):    # Enumerate is used to index the candidates  
            scores[candidate] += score_vector[rank]             # And the scores are assigned via rank (number of points), and index (to whom they belong)
    
    tie_break_fn = lambda c, w: tie_break(sorted(c,                         # As the candidates are sorted, the tie break function also needs to be sorted so that it returns the right candidate first
        key=lambda x: preferences.get_preference(x, tie_break_agent)), w)   # Same as before, but this time we use the tie_break_agent to get the winner
    return calculate_points(preferences, tie_break_fn, scoring_fn)          # the winning candidate is found by using the points calculator from above...

# ==============================================================================================================================================================================
# region Voting Mechanism 3. Plurality Function
# ==============================================================================================================================================================================
# Notes:
#   - Only the top-ranked candidate gets a point.
#   - scoring_fn is abstracted to a lambda function which passes in prefs, voter, scores 
#       - where the top choice is identidfied as prefs.get_preference() == 0 (rank 0 as refered to elsewhere in this code)
#       - and then it uses dictionary comprehesion to upddate and add 1 point to the candidate. 
#       - all within one line. but for sake of clarity, its been broken up by comments
#   - The calculate_points() funtion then returns the winning candidate with the highest score
# ==============================================================================================================================================================================
# endregion
def plurality(preferences, tie_break):
    """
    Plurality rule: each voter's top choice receives one point.

    Parameters:
        preferences (Preference): The preference profile containing candidates and voters.
        tie_break (function): Function to determine the winner if multiple candidates have the highest score.
    
    Returns:
        int: The candidate with the most points based on the plurality rule or the tie-breaker if needed.
    """

    scoring_fn = lambda prefs, voter, scores: scores.update(    # Abstratced scoring_fn as lambda function
        {c: scores[c] + 1 for c in prefs.candidates()           # loops through each candidate as "c" to award points
         if prefs.get_preference(c, voter) == 0})               # points only given if it is ranked as top choice by voter 
    return calculate_points(preferences, tie_break, scoring_fn) # returns winner via calculate_points

# ==============================================================================================================================================================================
# region Voting Mechanism 4. Veto Function
# ==============================================================================================================================================================================
# Notes:
#   - Veto voting rule, each voter assigns points to all candidates except their lowest-ranked choice.
#   - Similar to plurality rule scoring_fn is abstracted to a lambda function
#       - Except this time, 1 point is given to each candidate except for the one in last place
#       - Like plurality() it uses  dictionary comprehesion to update and add 1 point each candidate. 
#       - and as before this one line been broken up by comments for clarity
# ==============================================================================================================================================================================
# endregion
def veto(preferences, tie_break):                               # Voting Mechanism 4. Veto Function
    """
    Veto rule: all but the lowest-ranked candidate get points.
    
    Parameters:
        preferences (Preference): The preference profile with candidates, voters, and rankings.
        tie_break (function): Function to determine the winner in case of a tie.

    Returns:
        int: The candidate with the highest points after veto rule application or tie-breaking if necessary.
    """
    scoring_fn = lambda prefs, voter, scores: scores.update(    # Abstratced scoring_fn as lambda function
        {c: scores[c] + 1 for c in prefs.candidates()           # loops through each candidate as "c" to award points 
         if prefs.get_preference(c, voter)                      # This time each candidate gets a point                        
         != len(prefs.candidates()) - 1})                       # Except for the dude in last place
    return calculate_points(preferences, tie_break, scoring_fn) # returns winner via calculate_points

# ==============================================================================================================================================================================
# region Voting Mechanism 5. Borda Count Function
# ==============================================================================================================================================================================
# Notes:
#   - In Borda Count, candidates earn points inversely related to their rank.
#       - Where top rank == get_prefs() == 0 gets max points, next gets one less, and so on.
#       - As with the last 2 mechansims. the scoring function is updated to reflect Borda
#       - Points are calcualted as the  max number of point (from length of candidates) - 1 (as list starts from 0)
#       - and then taking away their ranking, ie top choice with rank = 0 lose only 1 points, 5th place loses 6 points.
# ==============================================================================================================================================================================
# endregion
def borda(preferences, tie_break):                              # Voting Mechanism 5. Borda Count Function
    """
    Borda rule: candidates receive points inversely proportional to their rank.
    
    Parameters:
        preferences (Preference): The preference profile with candidates and voters' rankings.
        tie_break (function): Function to resolve ties if candidates have equal highest scores.

    Returns:
        int: The candidate with the highest Borda score, or the tie-breaking choice if needed.
    """
    scoring_fn = lambda prefs, voter, scores: scores.update(    # Abstratced scoring_fn as lambda function
        {c: scores[c] + len(prefs.candidates()) - 1 - prefs.get_preference(c, voter) # Points are assigned inversely to rank ( - 1 as list starts at 0)
         for c in prefs.candidates()})                          # Loops through each candidate as "c" 
    return calculate_points(preferences, tie_break, scoring_fn) # returns winner via calculate_points

# ==============================================================================================================================================================================
# region Voting Mechanism 6. Single Transferable Vote (STV) Function 
# ==============================================================================================================================================================================
# Notes:
#   - STV eliminates candidates with the fewest top votes in rounds, each round voters can rechoose their top choice
#   - As elimantion is required, it is actually esier to not use calculate_points
#   - But to first make a set of all candidates (and voters whilst we're here)
#       - This way we can loop until the last remaining candidate
#           - and only assign 1 points to each candidate that was the voters first choice
#       - Like before we can save the scores as a dictionary of candidates and the scores (sum total of voters_first_choice)
#       - which lets us find, and eliminate the lowest scoring candidate, and iterate until theres only 1 iteration of candidate left as the winner
# ==============================================================================================================================================================================
# endregion
def STV(preferences, tie_break):                                                # Voting Mechanism 6 Single Transferable Vote (STV) Function
    """
    STV rule: candidates with fewest votes are iteratively eliminated until one remains.

    Parameters:
        preferences (Preference): The preference profile containing candidates and rankings.
        tie_break (int): Agent used for tie-breaking if necessary.

    Returns:
        int: The candidate who wins by the STV rule or is chosen via tie-break if needed.
    """
    candidates, voters = set(preferences.candidates()), preferences.voters()    # Step 1: Initialize set of candidates and voters (for easier candiadate elimination)                                           # Step 1: Initialize set of candidates and list of voters
    while len(candidates) > 1:                                                  # Step 2: Continue until theres only one candidate remaining
        scores = {c: sum(1 for v in voters                                      # Step 2a: scores are give to each candidate, and accumalted
            if preferences.get_preference(c, v) == 0)                           # Step 2ai: if they're ranked first by the voter and
            for c in candidates}                                                # Step 2aii: Iterate over each candidate per voter to find top choice
        min_count = min(scores.values())                                        # Step 2b: Find the lowest vote count
        candidates -= {c for c, count in scores.items() if count == min_count}  # Step 2c: Eliminate that candidate with the lowest votes
    return next(iter(candidates), None)                                         # Step 3: Return the last remaining candidate as the winner
