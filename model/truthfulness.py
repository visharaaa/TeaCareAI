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
    },
    {
        "query": "blister blight medium",
        "context": "Spots enlarge to light brown depressions; blister-like swellings on lower leaf surface with white velvety sporulation; some leaf distortion, curling, and necrosis; affects 10-30% of tender shoots; can spread rapidly in misty, cool weather; yield loss 10-30%. Young stems may bend slightly; reduced plucking efficiency. Protective: Copper oxychloride (0.5-1% solution) or Bordeaux mixture (1:1:100) as foliar sprays every 7-10 days during rainy season. Systemic: Hexaconazole (0.1-0.2%) or propiconazole (0.05%) for 2-3 applications. Cultural: Regulate shade trees to 50% cover; improve ventilation by removing weeds. Biocontrol: Trichoderma harzianum (5 g/L) as alternative to chemicals for organic tea.",
        "response": """Hello! I'm a tea disease assistant here in Nuwara Eliya, Sri Lanka. If you're concerned about Blister Blight in your tea plantation, let me help you understand the symptoms and treatments.
        **Symptoms:**
        * Spots on leaves turn light brown and get depressed
        * Blisters or swellings with white, velvety growth appear on lower leaf surface
        * Leaves may curve or die back
        * Young shoots can bend slightly
        **Treatments:**
        * Protective measures:
            + Copper oxychloride (0.5-1% solution) or Bordeaux mixture as foliar sprays every 7-10 days during rainy season
        * Systemic treatments:
            + Hexaconazole (0.1-0.2%) or propiconazole (0.05%) for 2-3 applications
        * Cultural controls:
            + Regulate shade trees to 50% cover
            + Improve ventilation by removing weeds
        * Biocontrol: Trichoderma harzianum (5 g/L) as an alternative to chemicals for organic tea
        **Practical tips for local farmers:**
        * Regularly inspect your plantation, especially during rainy season.
        * Keep your farm clean and weed-free to improve air circulation.
        * Monitor temperature and humidity levels to predict disease outbreaks.
        **Safety note:** Always wear protective gear when handling chemical treatments. Follow the recommended application rates and take necessary precautions to avoid harming yourself or others."""
    },
    {
        "query": "blister blight low",
        "context": "Small, pinhole-sized translucent spots on young leaves (less than 1 month old); spots slightly enlarge but no blistering yet; mild on a few shoots; favored by cool (15-25°C), humid (>90% RH) conditions; initial crop loss <10%. Slight leaf depression on upper surface; no sporulation yet. Cultural: Improve air circulation through pruning and shade regulation (maintain 40-60% shade). Predictive spraying based on weather forecasts (e.g., if >80% RH for 3 days). No fungicide needed if caught early; monitor young shoots weekly. Biocontrol: Apply Trichoderma spp. or Bacillus-based bioagents as preventive foliar spray (1-2 g/L water, twice monthly). Avoid overhead irrigation to reduce humidity.",
        "response": """Hello there! I'm a helpful tea disease assistant from Nuwara Eliya, Sri Lanka. I'd be happy to assist you with Blister Blight on your tea plants.
        **Symptoms:**
        • Small, pinhole-sized spots on young leaves (less than 1 month old)
        • Spots slightly enlarge but no blistering yet
        • Mild on a few shoots
        • Favored by cool temperatures and high humidity
        **Treatments:**
        • **Cultural:** Prune and shade regulate to improve air circulation (40-60% shade).
        • **Predictive Spraying:** Spray based on weather forecasts (>80% RH for 3 days).
        • **No Fungicide Needed:** Catch it early; monitor young shoots weekly.
        • **Biocontrol:** Apply Trichoderma spp. or Bacillus-based bioagents as a preventive foliar spray (1-2 g/L water, twice monthly).
        **Practical Tips:**
        - Avoid overhead irrigation to reduce humidity
        - Maintain good air circulation by pruning and regulating shade
        - Monitor young shoots weekly for early detection
        **Safety Note:** Wear protective gear when handling chemicals. Always follow recommended application rates and guidelines. If you're unsure about any treatment, consult a local expert."""
    },
    {
        "query": "grey blight high",
        "context": "Widespread grey-brown lesions covering leaves and stalks; severe defoliation, shoot dieback; worsened by high humidity and stress; >30% loss, can lead to bush decline in African/Indian tea estates. Heavy spore production; secondary bacterial infections possible. Systemic: Hexaconazole (0.05%) or thiophanate methyl (0.1%) alternated to prevent resistance; apply 3-4 times at 7-day intervals. Biocontrol consortia (Trichoderma + Bacillus + Pseudomonas). Cultural: Ventilation improvement; remove infected parts; avoid wounding during harvest. Expert advice for integrated pest management (IPM).",
        "response": """Hello there! I'm a tea disease assistant here in Nuwara Eliya, Sri Lanka. I'd be happy to help you understand Grey Blight and how to manage it.
        **Symptoms of Grey Blight:**
        * Widespread grey-brown lesions on leaves and stalks
        * Severe defoliation (leaves falling off)
        * Shoot dieback (stems dying back)
        * Affected by high humidity and stress
        **Treatments for Grey Blight:**
        * Systemic treatments:
            + Use Hexaconazole (0.05%) or thiophanate methyl (0.1%)
            + Apply 3-4 times at 7-day intervals to prevent resistance
        * Biocontrol consortia:
            + Mix Trichoderma, Bacillus, and Pseudomonas bacteria
        * Cultural practices:
            + Improve ventilation in the tea estate
            + Remove infected parts
            + Avoid wounding plants during harvest
        **Practical Tips for Local Farmers:**
        * Regularly inspect your tea plants for signs of Grey Blight
        * Use a combination of systemic and biocontrol treatments for best results
        * Consider using integrated pest management (IPM) strategies to minimize chemical use
        **Safety Note:** Always wear protective gear, including gloves and masks, when handling chemicals or infected plant material."""
    },
    {
        "query": "grey blight medium",
        "context": "Lesions turn brown with concentric rings and tiny black acervuli (fruiting bodies); starting defoliation and shoot dieback; affects 10-30% of foliage; worsened by plant stress or mechanical damage; yield loss 10-20%. Increased on stalks and young shoots. Fungicides: Carbendazim (0.05-0.1%) or mancozeb (0.2%) sprays every 10-14 days. Biocontrol: Trichoderma harzianum or Pseudomonas fluorescens (2-5 g/L) as foliar application. Cultural: Reduce plant stress with balanced NPK fertilizers (e.g., 120:60:120 kg/ha/year); careful harvesting to minimize wounds.",
        "response": """Hello there, farmer! I'm here to help you understand Grey Blight disease in your tea plants in beautiful Nuwara Eliya, Sri Lanka.
        Symptoms:
        Lesions turn brown with concentric rings on leaves
        Tiny black spots (acervuli) appear
        Defoliation and shoot dieback start
        10-30% of foliage is affected
        Treatments:
        Fungicides:
        Carbendazim (0.05-0.1%) to spray every 10-14 days
        Mancozeb (0.2%) to spray every 10-14 days
        Copper-based fungicides similar to grey blight.
        Preventive measures:
        Apply after pruning or on young leaves.
        Biocontrol agents like Trichoderma (3-5 g/L) for healthy soil.
        Practical tips for local farmers:
        1. Monitor your tea plants regularly, especially after pruning.
        2. Use protective sprays every 10 days to prevent the spread of Brown Blight.
        3. Keep your farm clean and free from weeds to reduce stress on the tea plants.
        Remember to always follow safety guidelines when applying fungicides or biocontrol agents: wear protective clothing, gloves, and eyewear, and make sure children and pets stay away from treated areas."""
    },
    {
        "query": "grey blight low",
        "context": "Small greyish-white irregular lesions starting at leaf margins or wounds on mature leaves; no concentric rings yet; minor on old leaves; favored by warm, humid conditions (25-30°C, >80% RH); initial spread slow, loss <5%. Slight browning at edges; no defoliation. Cultural: Avoid mechanical harvesting wounds; improve air circulation by proper spacing (75-100 cm between bushes). No fungicide if isolated; monitor mature leaves bi-weekly. Preventive: Remove and burn infected debris to reduce inoculum; avoid overhead irrigation.",
        "response": """Hello! I'm here to help you with your tea plantation in beautiful Nuwara Eliya. We've got a case of Grey Blight, but don't worry, it's just a low-severity disease.
        Symptoms:
        Small greyish-white spots on mature leaves
        Lesions start at leaf margins or wounds
        No concentric rings yet
        Minor on old leaves
        Treatments:
        Improve air circulation by spacing bushes 75-100 cm apart
        Monitor mature leaves bi-weekly for new symptoms
        Remove and burn infected debris to reduce spread
        Avoid overhead irrigation
        If isolated, no fungicide is needed (yet!)
        Practical Tips:
        Be gentle when harvesting tea leaves to avoid making wounds that can help the disease spread.
        Keep your plantation well-maintained, including proper spacing between bushes.
        Safety Note: Remember to always wear protective gear and wash your hands before handling any plant materials. This will prevent accidental spreading of the disease to other parts of your plantation!"""
    },
    {
        "query": "brown blight high",
        "context": "Widespread necrotic lesions, heavy defoliation, twig dieback; stressed plants may die; >30% loss, common in low-altitude teas. Concentric rings prominent; secondary root rots possible. Copper-based (oxychloride) + triazoles (e.g., propiconazole 0.05%). Biocontrol: Trichoderma + Pseudomonas consortia. Cultural: Remove debris, urgent nutrition boost (potassium-rich fertilizers); avoid waterlogging.",
        "response": """Hello! I'm a tea disease assistant here in beautiful Nuwara Eliya, Sri Lanka. I'd like to help you understand and manage Brown Blight, a common issue affecting our tea plants.
        Symptoms:
        Widespread dead patches on leaves (necrotic lesions)
        Many leaves drop off (heavy defoliation)
        Twigs die back
        Plants under stress may die
        Treatments:
        Use copper-based treatment (oxychloride) + triazoles (like propiconazole 0.05%)
        Biocontrol with Trichoderma and Pseudomonas consortia
        Cultural practices:
        Remove debris
        Give plants a potassium-rich fertilizer boost ASAP
        Avoid waterlogging
        Practical Tips for Local Farmers:
        Be quick to remove diseased leaves to prevent the blight from spreading.
        Monitor your tea plants closely, especially after heavy rainfall.
        Consider consulting with experts or experienced farmers for guidance.
        Remember to follow all safety precautions when handling chemicals and fertilizers. Wear protective clothing, gloves, and masks to avoid exposure."""
    },
    {
        "query": "brown blight medium",
        "context": "Spots enlarge to brown/gray necrotic lesions with concentric rings and black dots (acervuli); affects stressed or mature leaves; 10-30% defoliation and twig dieback; yield loss 10-25%. Increased on young leaves after pruning. Fungicides: Mancozeb (0.2%) or carbendazim (0.05%) as protective sprays every 10 days. Copper-based similar to grey blight. Preventive: Apply after pruning or on young leaves; biocontrol agents like Trichoderma (3-5 g/L).",
        "response": """Hello! I'm here to help you understand Brown Blight, a common disease affecting tea plants in Nuwara Eliya, Sri Lanka.
        Symptoms:
        Spots on leaves turn brown or gray and form concentric rings.
        Black dots (acervuli) appear on the affected area.
        Stressed or mature leaves are affected first.
        Defoliation (10-30%) and twig dieback occur.
        Treatments:
        Fungicides:
        Mancozeb (0.2%): a protective spray every 10 days.
        Carbendazim (0.05%): another protective spray every 10 days.
        Copper-based fungicides similar to grey blight.
        Preventive measures:
        Apply after pruning or on young leaves.
        Biocontrol agents like Trichoderma (3-5 g/L) for healthy soil.
        Practical tips for local farmers:
        1. Monitor your tea plants regularly, especially after pruning.
        2. Use protective sprays every 10 days to prevent the spread of Brown Blight.
        3. Keep your farm clean and free from weeds to reduce stress on the tea plants.
        Remember to always follow safety guidelines when applying fungicides or biocontrol agents: wear protective clothing, gloves, and eyewear, and make sure children and pets stay away from treated areas."""
    },
    {
        "query": "brown blight low",
        "context": "Small oval pale yellow-green spots with yellow halo on leaves; no concentric rings yet; minor on stressed or mature leaves; favored by wet, warm weather (20-28°C); initial loss <5%. Slight halo around spots. Cultural: Proper nutrition (balanced NPK, avoid excess nitrogen); good drainage to reduce stress. Monitor only if isolated. Preventive: Avoid overhead irrigation; promote air flow with spacing.",
        "response": """Hello there, fellow tea farmer from Nuwara Eliya! I'm here to help you tackle the Brown Blight disease in your tea fields.
        Symptoms:
        Small oval pale yellow-green spots on leaves
        Yellow halo around spots (no concentric rings yet)
        Favorable weather conditions: wet and warm (20-28°C)
        Leaves affected are usually stressed or mature
        Initial loss of <5%
        Treatments:
        Cultural:
        Balanced nutrition (NPK) to promote healthy growth
        Good drainage to reduce stress on plants
        Preventive:
        Avoid overhead irrigation to prevent fungal growth
        Promote air flow by spacing tea plants
        Practical Tips for Local Farmers:
        Regularly inspect your fields for early signs of disease
        Use drip irrigation to conserve water and reduce fungal growth
        Encourage good farm hygiene practices, such as removing weeds and pruning infected areas
        Safety Note: Always wear protective clothing and use necessary precautions when handling chemicals or pesticides."""
    },
    {
        "query": "red rust high",
        "context": "Heavy reddish-brown velvety patches on leaves/branches; severe leaf distortion, premature drop, branch dieback; plant stunting and weakening; >30% loss, common in poorly drained Indian/Sri Lankan estates. Algal fructifications prominent; secondary fungal infections possible. Intensive: Copper-based fungicides + Bordeaux mixture (multiple sprays at 7-day intervals). Emerging biocontrol (Bacillus spp). Cultural: Improve drainage/air flow; balanced nutrition; shade regulation; remove/prune infected parts; expert consultation for IPM.",
        "response": """Hello! I'm here to help you understand Red Rust disease in Nuwara Eliya, Sri Lanka. 
        **Symptoms:**
        • Heavy reddish-brown patches on leaves and branches
        • Distorted leaves that drop early
        • Twigs and branches die quickly
        • Plant grows weakly
        • More than 30% of plants are affected
        **Treatments:**
        • Intensive care: Copper-based fungicides and Bordeaux mixture (spray every 7 days)
        • Emerging biocontrol method using Bacillus spp
        • Cultural practices:
            + Improve drainage in your estate
            + Balance nutrition for healthy growth
            + Regulate shade to prevent stress on plants
        **Tips for local farmers:**
        • Remove infected parts from the plant as soon as you spot them.
        • Consult an expert for integrated pest management (IPM) strategies.
        **Remember:** Always follow safety precautions when using fungicides and other chemicals. Wear protective gear, including gloves and masks, to avoid exposure."""
    },
    {
        "query": "red rust medium",
        "context": "More orange-red patches on upper leaf surface; some leaf distortion, premature drop, and branch weakening; 10-30% affected; epiphytic/parasitic alga spreads in wet seasons. Affects branches mildly. Copper oxychloride (0.5%) or Bordeaux mixture sprays (every 10-14 days). Avoid excess nitrogen fertilizers. Biocontrol: Emerging bacterial formulations (Bacillus paramycoides or Microbacterium barkeri, 2-3 applications).",
        "response": """Hello! I'm a tea disease assistant here in Nuwara Eliya, Sri Lanka. We've got some concerns about Red Rust on our tea plants. Let me break it down simply for you.
        Symptoms:
        More orange-red patches on the upper leaf surface
        Some leaf distortion
        Premature drop of leaves
        Branch weakening
        10-30% of the plant is affected
        These symptoms are especially noticeable in wet seasons when an epiphytic/parasitic alga spreads quickly.
        Treatments:
        Copper oxychloride (0.5%) spray every 10-14 days
        Bordeaux mixture sprays every 10-14 days
        Avoid excess nitrogen fertilizers, as this can worsen the disease
        Biocontrol methods:
        Emerging bacterial formulations like Bacillus paramycoides or Microbacterium barkeri (2-3 applications)
        Practical Tips for Local Farmers:
        Regularly inspect your tea plants and act quickly if you notice any symptoms.
        Maintain good hygiene in your plantation to prevent the spread of disease.
        Consider using integrated pest management techniques to minimize chemical use.
        Remember, it's essential to follow safety guidelines when handling chemicals. Always wear protective gear and ensure proper application procedures are followed."""
    },
    {
        "query": "red rust low",
        "context": "Few orange-red to reddish-brown velvety raised spots/patches on leaves and branches; circular to irregular, often on upper surface; no distortion yet; minor on stressed plants; algal, favored by poor drainage and high humidity; loss <5%. Velvety due to algal fructifications. Cultural: Improve drainage (raised beds) and air circulation; balanced fertilizers (avoid excess N). Monitor weekly. Preventive: Shade regulation (30-50% cover); remove minor spots manually.",
        "response": """Hello! I'm here to help you with Red Rust disease in Nuwara Eliya, Sri Lanka. Let's break down the symptoms and treatments:
        Symptoms:
        Orange-red or reddish-brown velvety spots on leaves and branches
        Circular to irregular shapes, mostly on the upper surface
        No distortion yet
        Minor on stressed plants
        Favored by poor drainage and high humidity
        Treatments:
        Cultural:
        Improve drainage (raised beds)
        Increase air circulation
        Balanced fertilizers (avoid excess N)
        Monitor weekly
        Preventive:
        Shade regulation (30-50% cover)
        Remove minor spots manually
        As a local farmer, remember to:
        Keep your plants well-drained and aerated.
        Use balanced fertilizers to avoid over-fertilizing with nitrogen.
        Regularly inspect your plants for any signs of disease.
        Safety Note: Always wear protective gloves when handling plants and tools to prevent any potential health risks."""
    },
    {
        "query": "red spider high",
        "context": "Widespread bronzing/yellowing of leaves; heavy webbing covering leaves/stems; severe leaf curling, hardening, drop, and defoliation; bush weakening/stunting; mites in large colonies; >30% loss, common in dry seasons or unshaded tea gardens. Urgent: Rotate acaricides like propargite 57EC (0.1%) or abamectin (0.005%); 3-4 applications at 7-day intervals to avoid resistance. Biocontrol: Release predatory mites (Neoseiulus spp.) + Beauveria bassiana fungus. Cultural: Urgent irrigation/humidity increase; heavy pruning of infested areas; IPM with expert monitoring.",
        "response": """Hello there! I'm a helpful tea disease assistant here in beautiful Nuwara Eliya, Sri Lanka. We're dealing with a serious issue - Red Spider infestation.
        **Symptoms:**
        * Leaves turn yellow or bronze all over
        * Heavy webs cover leaves and stems
        * Leaves curl up tightly and harden
        * Many leaves drop off the bush
        * Bushes become weak and stunted
        **Treatments:**
        * Use acaricides like propargite 57EC (0.1%) or abamectin (0.005%) urgently
            + Spray 3-4 times, every 7 days to prevent resistance
        * Release predatory mites (Neoseiulus spp.) and Beauveria bassiana fungus for biocontrol
        * Improve irrigation and humidity levels in the garden
        * Prune heavily infested areas
        * Implement Integrated Pest Management (IPM) with expert monitoring
        **Practical Tips:**
        * Keep your tea gardens shaded to prevent Red Spider infestation
        * Monitor your plants regularly for any signs of disease
        * Use a combination of treatments for better results
        **Safety Note:** Always wear protective gear, including gloves and masks, when handling chemicals. Be cautious when applying acaricides, as they can be toxic if not used properly."""
    },
    {
        "query": "red spider medium",
        "context": "Stippling turns to bronze/rusty discoloration on upper leaf surface; fine silk webbing on undersides; leaves curl, harden, and some drop; tiny red mites visible with lens; affects 10-30% of foliage; worsened by drought or nitrogen excess; yield loss 10-25%. Acaricides: Fenpyroximate 5EC (0.05%) or dicofol 18.5EC (0.2%) sprays every 10-14 days. Biocontrol: Predatory mites (Phytoseiulus persimilis) or ladybugs; neem oil (0.5-1%). Cultural: Increase humidity with overhead sprinkling; balanced fertilizers.",
        "response": """Hello! I'm here to help you with Red Spider disease, which affects tea plants in Nuwara Eliya, Sri Lanka. Let me explain the symptoms and treatments:
        Symptoms:
        Stippling on upper leaf surface turns to bronze/rusty discoloration
        Fine silk webbing on undersides of leaves
        Leaves curl, harden, and some drop
        Tiny red mites visible with a lens
        Treatments:
        Acaricides:
        Fenpyroximate 5EC (0.05%) spray every 10-14 days
        Dicofol 18.5EC (0.2%) spray every 10-14 days
        Biocontrol:
        Introduce predatory mites (Phytoseiulus persimilis) or ladybugs
        Use neem oil (0.5-1%)
        Cultural:
        Increase humidity with overhead sprinkling
        Use balanced fertilizers
        Practical Tips for Local Farmers:
        Avoid excessive nitrogen fertilizers, which can worsen the disease.
        Monitor your tea plants regularly to catch the disease early.
        Consider using biocontrol methods as a more environmentally friendly option.
        Safety Note: Always follow the recommended dosages and safety precautions when using chemical treatments."""
    },
    {
        "query": "red spider low",
        "context": "Small yellow/white stippling (flecks/dots) on upper leaf surface from sap sucking; leaves look dusty or speckled; no bronzing or webbing yet; minor on mature leaves; favored by hot, dry weather (25-35°C, <60% RH); initial spread slow, crop loss <5-10%; no defoliation. Cultural: Improve air circulation and humidity (mist irrigation); monitor upper leaves weekly; remove minor infested leaves. No acaricide if isolated; avoid dust and stress from low water.",
        "response": """Hello! I'm a tea disease assistant here in Nuwara Eliya, Sri Lanka. If you're seeing some issues with your tea plants, it might be Red Spider.
        What to look for:
        Small yellow/white dots on the upper leaf surface (called stippling)
        Leaves look dusty or speckled
        No bronzing or webbing yet
        How to treat:
        Improve air circulation and humidity (use mist irrigation)
        Monitor upper leaves weekly
        Remove minor infested leaves
        For local farmers in Nuwara Eliya:
        Practical tip 1: Keep an eye on the temperature and relative humidity, as Red Spider likes hot and dry weather.
        Practical tip 2: Regularly clean your tea plants to prevent dust from accumulating and stressing them out.
        Practical tip 3: Make sure to remove any minor infested leaves before they spread to other parts of the plant.
        Remember: If you find a severe infestation, contact us or a local expert for assistance."""
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



