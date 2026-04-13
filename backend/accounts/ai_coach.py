"""
AI Coach chat handler.
Returns contextual fitness coaching responses.
Replace the rule-based logic with an actual LLM API (OpenAI, etc.) when ready.
"""
import json
import random

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST


# ── Contextual response templates ─────────────────────────────────────────
RESPONSES = {
    'workout': [
        {
            'text': "Based on your current training split, I recommend a **Push Day** today:\n\n"
                    "1. Barbell Bench Press — 4×8\n"
                    "2. Overhead Press — 3×10\n"
                    "3. Incline Dumbbell Press — 3×12\n"
                    "4. Lateral Raises — 4×15\n"
                    "5. Tricep Pushdowns — 3×12\n\n"
                    "Rest 90s between sets. Aim for RPE 8.",
            'macros': None,
        },
        {
            'text': "Here's a quick **15-min HIIT** you can do anywhere:\n\n"
                    "• 30s Burpees → 30s Rest\n"
                    "• 30s Mountain Climbers → 30s Rest\n"
                    "• 30s Jump Squats → 30s Rest\n"
                    "• 30s High Knees → 30s Rest\n"
                    "• Repeat 3 rounds\n\n"
                    "Estimated burn: **180–220 kcal**.",
            'macros': {'calories': '~200 kcal', 'duration': '15 min'},
        },
        {
            'text': "Your legs need attention. Try this **Lower Body** session:\n\n"
                    "1. Back Squats — 4×6 (heavy)\n"
                    "2. Romanian Deadlifts — 3×10\n"
                    "3. Walking Lunges — 3×12 each leg\n"
                    "4. Leg Press — 3×15\n"
                    "5. Calf Raises — 4×20\n\n"
                    "Focus on controlled eccentric phases.",
            'macros': None,
        },
    ],
    'nutrition': [
        {
            'text': "For dinner tonight, I suggest **Grilled Salmon with Quinoa & Asparagus**.\n\n"
                    "This hits your remaining macros perfectly — high omega-3s for recovery, "
                    "complex carbs for glycogen replenishment, and fiber to keep you satiated.",
            'macros': {'calories': '520 kcal', 'protein': '42g', 'carbs': '38g', 'fats': '18g'},
        },
        {
            'text': "Here's a solid **post-workout shake** recipe:\n\n"
                    "• 1 scoop whey protein\n"
                    "• 1 banana\n"
                    "• 1 tbsp peanut butter\n"
                    "• 250ml oat milk\n"
                    "• Ice\n\n"
                    "Blend and drink within 30 minutes of training for optimal recovery.",
            'macros': {'calories': '380 kcal', 'protein': '32g', 'carbs': '42g', 'fats': '10g'},
        },
        {
            'text': "To stay on track with your cutting phase, keep tonight's meal under 500 kcal. "
                    "Try **Chicken Stir-Fry with Vegetables**:\n\n"
                    "• 150g chicken breast\n"
                    "• Mixed bell peppers, broccoli, snap peas\n"
                    "• 1 tbsp soy sauce + ginger\n"
                    "• Serve over 80g brown rice\n\n"
                    "High volume, high protein, low calorie density.",
            'macros': {'calories': '440 kcal', 'protein': '45g', 'carbs': '35g', 'fats': '12g'},
        },
    ],
    'form': [
        {
            'text': "**Squat Form Check — Key Cues:**\n\n"
                    "1. **Feet** — Shoulder-width, toes slightly out (15–30°)\n"
                    "2. **Brace** — Deep breath, brace core like you're about to be punched\n"
                    "3. **Descent** — Break at hips AND knees simultaneously\n"
                    "4. **Depth** — Hip crease below knee (parallel minimum)\n"
                    "5. **Drive** — Push through mid-foot, knees track over toes\n\n"
                    "Common fix: If your heels rise, try elevating them on small plates until ankle mobility improves.",
            'macros': None,
        },
        {
            'text': "**Deadlift Form Tips:**\n\n"
                    "1. Bar over mid-foot\n"
                    "2. Grip just outside knees\n"
                    "3. Chest up, lats engaged (\"protect your armpits\")\n"
                    "4. Push the floor away — don't pull the bar\n"
                    "5. Lock out with glutes, not lower back\n\n"
                    "Record yourself from the side and I can help analyze further.",
            'macros': None,
        },
    ],
    'macro': [
        {
            'text': "**Macro Tracking 101:**\n\n"
                    "Your daily targets should be based on your goals:\n\n"
                    "• **Protein**: 1.6–2.2g per kg bodyweight (muscle building/retention)\n"
                    "• **Fats**: 0.7–1.2g per kg (hormonal health)\n"
                    "• **Carbs**: Fill remaining calories (performance fuel)\n\n"
                    "Hit protein first, then fats, then fill with carbs. Consistency > perfection.",
            'macros': None,
        },
    ],
    'general': [
        {
            'text': "That's a great question. Based on your current training data and goals, "
                    "I'd recommend focusing on **progressive overload** this week. "
                    "Try adding 2.5kg to your compound lifts or 1–2 extra reps per set.\n\n"
                    "Remember: recovery is where gains happen. Are you getting 7–9 hours of sleep?",
            'macros': None,
        },
        {
            'text': "Here's a tip for staying consistent: **track your wins**, not just your workouts.\n\n"
                    "Each day you show up is a data point proving you're building the habit. "
                    "Your consistency rate this month is looking solid. Keep the momentum going.",
            'macros': None,
        },
        {
            'text': "I'm here to help with:\n\n"
                    "• **Workout plans** — custom routines for any goal\n"
                    "• **Nutrition advice** — meal suggestions, macro breakdowns\n"
                    "• **Form guidance** — cues and corrections\n"
                    "• **Recovery protocols** — sleep, stretching, mobility\n\n"
                    "What would you like to dive into?",
            'macros': None,
        },
    ],
}

# Keywords → category mapping
KEYWORD_MAP = {
    'workout': ['workout', 'exercise', 'training', 'hiit', 'routine', 'session',
                'lift', 'push', 'pull', 'leg', 'upper', 'lower', 'split', 'gym'],
    'nutrition': ['meal', 'eat', 'food', 'dinner', 'lunch', 'breakfast', 'snack',
                  'recipe', 'cook', 'diet', 'calorie', 'shake', 'protein shake',
                  'nutrition', 'nutrient'],
    'form': ['form', 'squat', 'deadlift', 'bench', 'technique', 'posture',
             'fix', 'correct', 'cue'],
    'macro': ['macro', 'protein', 'carb', 'fat', 'track', 'counting',
              'deficit', 'surplus', 'bulk', 'cut'],
}


def classify_message(text: str) -> str:
    """Simple keyword-based intent classification."""
    text_lower = text.lower()
    scores = {}
    for category, keywords in KEYWORD_MAP.items():
        scores[category] = sum(1 for kw in keywords if kw in text_lower)
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else 'general'


@login_required
@require_POST
def ai_chat(request):
    """Handle AI chat messages and return a coaching response."""
    try:
        body = json.loads(request.body)
        message = body.get('message', '').strip()
    except (json.JSONDecodeError, AttributeError):
        return JsonResponse({'error': 'Invalid request body.'}, status=400)

    if not message:
        return JsonResponse({'error': 'Message cannot be empty.'}, status=400)

    if len(message) > 2000:
        return JsonResponse({'error': 'Message too long (max 2000 chars).'}, status=400)

    category = classify_message(message)
    response_pool = RESPONSES.get(category, RESPONSES['general'])
    chosen = random.choice(response_pool)

    return JsonResponse({
        'reply': chosen['text'],
        'macros': chosen.get('macros'),
        'category': category,
    })
