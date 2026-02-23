# generator_evaluation.py
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
from rouge_score import rouge_scorer

# Test cases with references
test_cases = [
    {
        "query": "blister blight high",
        "generated": """Hello! I'm here to help you manage Blister Blight in Nuwara Eliya's tea gardens. This high-severity disease causes big problems, but don't worry, we can control it.
        Symptoms:
        • Severe blistering on leaves and stems
        • Brown necrotic blisters that spread quickly
        • Leaves curl, distort, and drop off
        • Shoots bend, dieback, and weaken the bush
        • Widespread shoot dieback and secondary infections
        Treatments:
        • Use systemic fungicides like tridemorph (0.05%) or contaf (0.1%) every 5-7 days for 2-3 weeks
        • Alternate with triazoles (e.g., hexaconazole) to avoid resistance
        • Heavy pruning of infected shoots, removing 15-20 cm below symptoms
        • Regulate nitrogen fertilizers to prevent succulent growth
        Practical Tips:
        Inspect your tea gardens regularly for early signs of Blister Blight.
        Keep your garden clean and remove infected plants quickly.
        Safety Note: Always wear protective gear when handling fungicides, including gloves, masks, and eye protection. Follow the recommended application rates to avoid harming yourself or the environment.""",
        "reference": "For high severity Blister Blight in Nuwara Eliya, expect severe blistering, brown necrotic blisters; leaves fully necrose, curl, distort, and drop; stem distortion, bending, and dieback; affects >30% of shoots, leading to major defoliation and bush weakening; can cause 30-50% crop loss in epidemics. Widespread shoot dieback; secondary infections increase; common in high-altitude tea gardens (>1000m). Urgent: Multiple systemic fungicides like tridemorph (0.05%) or contaf (0.1%) alternated with triazoles (e.g., hexaconazole) to avoid resistance; apply every 5-7 days for 2-3 weeks. Cultural: Heavy pruning of infected shoots (remove 15-20 cm below symptoms); regulate nitrogen fertilizers to avoid succulent growth. Consult experts for resistance checks; use bioagents consortia (Bacillus + Trichoderma) for long-term management. Act fast in rainy season. Safety note: Consult local expert."
    }
]

scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer = True)
smooth = SmoothingFunction().method1

rouge1_scores, rouge2_scores, rougeL_scores = [], [], []
bleu_scores = []

for case in test_cases:
    generated = case["generated"]
    reference = case["reference"]

    rouge = scorer.score(reference, generated)
    rouge1_scores.append(rouge['rouge1'].fmeasure)
    rouge2_scores.append(rouge['rouge2'].fmeasure)
    rougeL_scores.append(rouge['rougeL'].fmeasure)

    bleu = sentence_bleu([reference.split()], generated.split(), smoothing_function = smooth)
    bleu_scores.append(bleu)

print("Generator Evaluation (ROUGE + BLEU)")
print(f"Average ROUGE-1 F1: {sum(rouge1_scores) / len(rouge1_scores):.4f}")
print(f"Average ROUGE-2 F1: {sum(rouge2_scores) / len(rouge2_scores):.4f}")
print(f"Average ROUGE-L F1: {sum(rougeL_scores) / len(rougeL_scores):.4f}")
print(f"Average BLEU: {sum(bleu_scores) / len(bleu_scores):.4f}")