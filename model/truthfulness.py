# truthfulness.py
import ollama

test_cases = [
    {
        "query": "blister blight high",
        "context": "Small, pinhole-sized translucent spots on young leaves (less than 1 month old); spots slightly enlarge but no blistering yet; mild on a few shoots; favored by cool (15-25°C), humid (>90% RH) conditions; initial crop loss <10%. Slight leaf depression on upper surface; no sporulation yet. Cultural: Improve air circulation through pruning and shade regulation (maintain 40-60% shade). Predictive spraying based on weather forecasts (e.g., if >80% RH for 3 days). No fungicide needed if caught early; monitor young shoots weekly. Biocontrol: Apply Trichoderma spp. or Bacillus-based bioagents as preventive foliar spray (1-2 g/L water, twice monthly). Avoid overhead irrigation to reduce humidity.",
        "response": """Hello! I'm here to help you with Blister Blight disease in your tea garden in Nuwara Eliya. This disease is quite common in high-altitude areas like ours.
        **Symptoms of Blister Blight:**
        • Severe blistering on leaves
        • Brown, dead blisters that can cover the entire leaf
        • Leaves curl up and drop off
        • Stem bending and dieback
        • More than 30% of shoots are affected
        **Treatments for Blister Blight:**
        • Urgent treatment with systemic fungicides like tridemorph or contaf every 5-7 days for 2-3 weeks.
        • Use triazoles (like hexaconazole) to avoid resistance.
        • Heavy pruning of infected shoots, cutting 15-20 cm below the symptoms.
        • Regulate nitrogen fertilizers to prevent succulent growth.
        **Practical Tips for Local Farmers:**
        * Keep a watchful eye on your tea plants and report any symptoms early.
        * Use bioagents like Bacillus + Trichoderma for long-term management.
        * Consider using resistance checks with experts to ensure the best treatment plan.
        **Safety Note:** Always wear protective gear when handling fungicides, and make sure to follow proper application instructions."""
    }
]


faithfulness_scores = []

judge_prompt_template = """
Score how faithful this response is to the context (0.00 to 1.00):
- 1.00 = response uses only facts from context
- 0.00 = many invented facts

Query: {query}
Context: {context}
Response: {response}

Output exactly this format:
Score: X.XX
"""

for case in test_cases:
    try:
        prompt = judge_prompt_template.format(**case) # Fill the prompt with real values from this case
        result = ollama.chat(model = 'llama3.1:8b', messages = [{'role': 'user', 'content': prompt}])
        text = result['message']['content'].strip() # Remove spaces from response

        # Import regular expression
        import re
        score_match = re.search(r'Score:\s*(\d\.\d{2})', text, re.IGNORECASE)
        if score_match is not None:
            # Get the first matched group and save it as a float
            extracted_value = score_match.group(1)
            score = float(extracted_value)
        else: # no match
            score = 0.0
        faithfulness_scores.append(score)

        print(f"Query: {case['query']}")
        print(f"Score: {score:.2f}")
        print(f"Raw judge output: {text}")
        print("-" * 60)

    except KeyError as e:
        print(f"Missing key in case '{case.get('query', 'unknown')}': {e}")
    except Exception as e:
        print(f"Error on '{case.get('query', 'unknown')}': {e}")

# Average faithfulness score
if faithfulness_scores:
    avg = sum(faithfulness_scores) / len(faithfulness_scores)
    print(f"\nAverage Faithfulness Score: {avg:.3f}")



