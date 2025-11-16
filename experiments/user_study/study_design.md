# User Study Design: Explainability in Chess AI

## Research Question
**Primary**: Do visual explanations (Grad-CAM/attention heatmaps) improve human understanding of chess tactics compared to text-only explanations?

**Secondary**: Which explanation modality is most effective for chess learning?

---

## Study Design

### Experimental Conditions (Between-Subjects)

| Group | Condition | What They See |
|-------|-----------|---------------|
| **Control** | Engine Only | Best move + evaluation score |
| **Group A** | Text Only | Best move + LLM explanation |
| **Group B** | Visual Only | Best move + heatmap overlay |
| **Group C** | Combined | Best move + heatmap + LLM explanation |

### Participants
- **Target**: 30-40 participants (7-10 per group)
- **Recruitment**: Online chess communities, university chess club
- **Skill level**: Intermediate (1200-1800 ELO)
  - Ensures understanding of tactics without ceiling effects
- **Exclusion**: Chess masters (>2000 ELO) - too expert

### Tasks

#### Phase 1: Training (5 positions)
- Participants see 5 example positions with explanations
- Goal: Familiarize with the explanation format
- No data collected

#### Phase 2: Main Study (20 positions)
For each position:
1. **Show position** (15 seconds to analyze)
2. **Question 1**: "What is the best move?" (forced choice from 4 options)
3. **Show explanation** (according to assigned condition)
4. **Question 2**: "Why is this the best move?" (open-ended, 1-2 sentences)
5. **Question 3**: "How confident are you?" (1-5 Likert scale)
6. **Record time spent**

#### Phase 3: Transfer Test (5 positions)
- **Novel positions** (similar tactics, different pieces)
- No explanations shown
- Tests learning transfer

---

## Positions Selection

### Tactical Themes (balanced across study)
- Fork (4 positions)
- Pin (4 positions)
- Discovered attack (3 positions)
- Deflection (3 positions)
- Skewer (3 positions)
- Mixed (3 positions)

### Difficulty Levels
- Easy (8 positions): 1-2 move tactics
- Medium (9 positions): 2-3 move tactics
- Hard (3 positions): 3+ move tactics

### Selection Criteria
- Clear best move (Stockfish advantage > 2.0)
- Single tactical theme (for easy interpretation)
- Realistic positions (from actual games)
- Not too famous (avoid memorization)

---

## Dependent Variables (What We Measure)

### Primary Outcomes
1. **Move Accuracy**: Percentage of correct moves selected
2. **Explanation Quality**: Human-rated quality of participant explanations (1-5)
   - Accuracy: Does explanation identify correct tactic?
   - Completeness: Are key elements mentioned?
   - Clarity: Is explanation understandable?
3. **Transfer Performance**: Accuracy on novel positions (Phase 3)

### Secondary Outcomes
4. **Time to Decision**: Seconds to select move
5. **Confidence**: Self-reported confidence (1-5)
6. **Subjective Ratings** (post-study questionnaire):
   - "The explanations were easy to understand" (1-7 Likert)
   - "The explanations helped me learn" (1-7 Likert)
   - "I would use this tool to improve my chess" (1-7 Likert)

---

## Hypotheses

**H1**: Combined explanations (visual + text) will yield highest move accuracy
- Reasoning: Dual coding theory - visual and verbal channels reinforce learning

**H2**: Visual explanations alone will outperform text alone
- Reasoning: Chess is inherently spatial; heatmaps map directly to board

**H3**: All explanation groups will outperform control (engine only)
- Reasoning: Any explanation provides more information than score alone

**H4**: Explanation quality (how participants explain moves) will be higher in visual conditions
- Reasoning: Heatmaps make important squares explicit

**H5**: Transfer test performance will be highest in combined condition
- Reasoning: Better understanding leads to better generalization

---

## Statistical Analysis Plan

### Primary Analysis
**ANOVA**: Move accuracy ~ Condition (Control, Text, Visual, Combined)
- Follow-up: Tukey HSD post-hoc tests
- Effect size: Cohen's d for pairwise comparisons

### Secondary Analyses
1. **Explanation Quality**: ANOVA + qualitative coding
2. **Time Analysis**: Mixed ANOVA (Condition × Position Difficulty)
3. **Transfer**: ANOVA on Phase 3 accuracy
4. **Correlation**: Confidence vs Accuracy (does visual calibrate confidence?)

### Statistical Power
- α = 0.05
- Power = 0.80
- Expected effect size: d = 0.5 (medium)
- Required n ≈ 30-40 total (7-10 per group)

---

## Implementation

### Web Interface Components

#### 1. Consent & Demographics
```
- Age
- Chess experience (years)
- Approximate ELO rating
- Consent form
```

#### 2. Training Phase
```
- 5 practice positions
- Full explanations (regardless of condition)
- No performance measurement
```

#### 3. Main Study
```
- Randomized position order
- Timer for each question
- Force next after timeout
- Save all responses to database
```

#### 4. Post-Study Questionnaire
```
- Subjective ratings
- Open-ended feedback
- Debrief message
```

### Data Collection
```json
{
  "participant_id": "P001",
  "condition": "combined",
  "demographics": {
    "age": 25,
    "elo": 1500,
    "years_experience": 3
  },
  "trials": [
    {
      "position_id": "pos_001",
      "fen": "...",
      "theme": "fork",
      "difficulty": "medium",
      "correct_move": "Nf3",
      "participant_move": "Nf3",
      "is_correct": true,
      "time_to_decision": 8.5,
      "confidence": 4,
      "explanation": "Knight forks king and rook",
      "explanation_quality": 5
    }
  ],
  "transfer_test": [...],
  "post_survey": {...}
}
```

---

## Ethics Considerations

### IRB Approval
- **Required if**: Study involves human subjects at academic institution
- **Exemption possible**: Anonymous online study, minimal risk
- **Consult**: University research ethics board

### Consent
- Informed consent before study
- Right to withdraw anytime
- Data anonymization
- No deception

### Data Privacy
- No personally identifiable information
- Secure storage (encrypted database)
- Aggregate reporting only
- Option to delete data post-study

---

## Timeline (8 Weeks)

| Week | Activity |
|------|----------|
| 1 | Select and validate 25 positions |
| 2 | Build web interface for study |
| 3 | Pilot study (n=5) + refinements |
| 4-5 | Data collection (n=30-40) |
| 6 | Code open-ended responses |
| 7 | Statistical analysis |
| 8 | Write results section |

---

## Expected Results

### If H1 Confirmed (Combined best):
**Conclusion**: "Multimodal explanations combining visual attention heatmaps with natural language significantly improve tactical understanding (p<0.05, d=0.6), suggesting XAI systems should leverage multiple modalities."

### If H2 Confirmed (Visual > Text):
**Conclusion**: "Visual attention mechanisms provide more effective explanations than text for spatial reasoning tasks like chess, supporting direct perceptual grounding over linguistic abstraction."

### If No Differences:
**Conclusion**: "All explanation modalities improved performance over baseline (p<0.05), but did not differ significantly from each other, suggesting explanation presence matters more than format."

---

## Contingency Plans

### Low Recruitment?
- Extend recruitment period
- Offer small incentive (€5 Amazon voucher)
- Partner with online chess platforms

### Technical Issues?
- Pilot test thoroughly
- Have backup data collection method (manual)
- Monitor server logs during study

### Results Not Significant?
- Increase sample size (power analysis)
- Focus on qualitative insights
- Exploratory subgroup analyses (by skill level)

---

## Deliverables

1. **Paper Section**: "Human Evaluation Study"
2. **Figures**: 
   - Bar chart: Move accuracy by condition
   - Box plot: Explanation quality by condition
   - Scatter: Confidence vs accuracy
3. **Tables**:
   - ANOVA results
   - Post-hoc comparisons
   - Descriptive statistics
4. **Supplementary**:
   - All 25 positions used
   - Anonymized raw data
   - Coding rubric for explanation quality

---

## References

- Samek, W., & Müller, K. R. (2019). Towards Explainable Artificial Intelligence. In Explainable AI.
- Zhou, J., et al. (2021). Evaluating the Quality of Machine Learning Explanations. Electronics.
- Miller, T. (2019). Explanation in Artificial Intelligence: Insights from the Social Sciences. AIJ.

