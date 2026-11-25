"""Seeded demo cases for mock mode.

Each case pairs a short original reading with a deliberately unsatisfactory
first answer, reproducing the failure types from Assignment 1 (too technical,
too long, missing the key point). This makes demonstrations repeatable and lets
the app run with no API key. All texts were written for this project.
"""

SAMPLES = [
    {
        "id": "too-technical",
        "title": "Too technical: photosynthesis",
        "failure": "Uses jargon a first-year student will not follow.",
        "mode": "summarise",
        "request": "Summarise this for a first-year student in about 80 words.",
        "source": (
            "Plants make their own food through photosynthesis. Inside leaf "
            "cells, structures called chloroplasts contain a green pigment, "
            "chlorophyll, which absorbs light. The plant uses this light energy "
            "to combine carbon dioxide from the air with water from the soil, "
            "producing glucose, a sugar the plant uses for energy and growth. "
            "Oxygen is released as a by-product, which is why plants are "
            "essential for the air animals breathe. Photosynthesis happens in "
            "two stages. In the first, light energy is captured and stored in "
            "energy-carrying molecules. In the second, that stored energy is "
            "used to build glucose. Because the process depends on light, its "
            "rate falls in low light and rises as light increases, up to a limit."
        ),
        "bad_output": (
            "Photosynthesis comprises light-dependent reactions in the thylakoid "
            "membranes, generating ATP and NADPH via photophosphorylation, and "
            "light-independent reactions in the stroma, where these reducing "
            "equivalents drive carbon fixation into glucose. Chlorophyll-mediated "
            "photon absorption initiates electron transport, with O2 evolved as "
            "a by-product of water photolysis. The process exhibits light-"
            "saturation kinetics, whereby the rate plateaus above a limiting "
            "irradiance."
        ),
    },
    {
        "id": "too-long",
        "title": "Too long: cognitive load",
        "failure": "Far longer than the requested 60 words.",
        "mode": "summarise",
        "request": "Give me a 60-word summary.",
        "source": (
            "Cognitive load theory explains why some learning materials are "
            "harder to use than others. Working memory can hold only a few "
            "items at once, so every task competes for limited space. The "
            "theory separates three kinds of load. Intrinsic load comes from "
            "the difficulty of the topic itself. Germane load is the useful "
            "effort of building understanding. Extraneous load is caused by "
            "poor design, such as cluttered pages or instructions split across "
            "several places. Designers cannot remove intrinsic load, but they "
            "can reduce extraneous load, freeing capacity for learning. For "
            "example, placing a label directly on a diagram, rather than in a "
            "separate key, saves the reader from holding information in mind "
            "while looking back and forth."
        ),
        "bad_output": (
            "Cognitive load theory is a framework that seeks to explain why "
            "certain learning materials are more difficult for learners to use "
            "than other materials. At the heart of the theory is the idea that "
            "working memory has a limited capacity and can only hold a small "
            "number of items at any one time, which means that every task a "
            "learner performs is in competition for this limited space. The "
            "theory distinguishes between three different kinds of load. The "
            "first is intrinsic load, which arises from the inherent difficulty "
            "of the subject matter being learned. The second is germane load, "
            "which refers to the productive mental effort involved in building "
            "understanding and forming schemas. The third is extraneous load, "
            "which is caused by poor instructional design choices, such as "
            "cluttered pages or instructions that are split across several "
            "locations. While designers are unable to remove intrinsic load, "
            "they are able to reduce extraneous load, which frees up capacity "
            "for learning. An example of this would be placing a label directly "
            "onto a diagram instead of in a separate key."
        ),
    },
    {
        "id": "missing-point",
        "title": "Missing the key point: urban heat islands",
        "failure": "Describes the problem but leaves out the solutions, "
                   "which the request asked for.",
        "mode": "summarise",
        "request": "Summarise the causes and what cities can do about it.",
        "source": (
            "Cities are often several degrees warmer than the countryside "
            "around them, an effect known as the urban heat island. Dark "
            "surfaces such as roads and roofs absorb sunlight during the day "
            "and release heat at night. Buildings block wind and trap warm air, "
            "and there are fewer trees and plants to provide shade and cool the "
            "air through evaporation. Waste heat from cars and air conditioning "
            "adds to the problem. Hotter cities increase energy use and can "
            "harm health during heatwaves. Cities can respond in several ways: "
            "planting trees and creating parks, painting roofs in light colours "
            "so they reflect sunlight, adding green roofs covered with plants, "
            "and using paving materials that stay cooler."
        ),
        "bad_output": (
            "Urban heat islands are areas where cities are warmer than nearby "
            "countryside. This happens because dark roads and roofs absorb "
            "sunlight and release heat at night, buildings block wind and trap "
            "warm air, and cities have fewer trees and plants. Waste heat from "
            "cars and air conditioning also contributes. As a result, hotter "
            "cities use more energy and can be harmful to health during heatwaves."
        ),
    },
]

_BY_SOURCE = {s["source"].strip(): s for s in SAMPLES}


def find_sample(source_text: str):
    """Return the seeded case whose source matches exactly, if any."""
    return _BY_SOURCE.get(source_text.strip())


def public_samples() -> list[dict]:
    """Samples as sent to the browser (the bad output stays server-side)."""
    return [
        {k: s[k] for k in ("id", "title", "failure", "mode", "request", "source")}
        for s in SAMPLES
    ]


# Canned revisions for the demo paths shown in the storyboards. Keys are
# (sample id, button id). Anything else falls back to a simple, clearly
# labelled mock transformation in llm.MockClient.
CANNED_REVISIONS = {
    ("too-technical", "simpler"): (
        "Plants make their own food using sunlight. Inside their leaves is a "
        "green substance called chlorophyll, which soaks up light. The plant "
        "uses that light energy to turn carbon dioxide from the air and water "
        "from the soil into sugar, which it uses to grow. Oxygen is given off "
        "as a by-product, which is why plants matter for the air we breathe. "
        "The process works faster in brighter light, up to a limit."
    ),
    # A correction that makes things worse: shorter, but still full of jargon.
    # Used in the storyboard where the person undoes and types a correction.
    ("too-technical", "shorter"): (
        "Photosynthesis uses light-dependent reactions in the thylakoids to make "
        "ATP and NADPH, which drive carbon fixation into glucose in the stroma, "
        "releasing O2 from water photolysis."
    ),
    ("too-technical", "example"): (
        "Photosynthesis comprises light-dependent reactions in the thylakoid "
        "membranes, generating ATP and NADPH via photophosphorylation, and "
        "light-independent reactions in the stroma, where these reducing "
        "equivalents drive carbon fixation into glucose. For example, the "
        "source notes that the rate falls in low light and rises as light "
        "increases, up to a limit."
    ),
    ("too-long", "shorter"): (
        "Cognitive load theory says working memory is limited, so tasks compete "
        "for space. It separates three kinds of load: intrinsic (the topic's "
        "difficulty), germane (useful effort to understand) and extraneous "
        "(caused by poor design). Designers cannot remove intrinsic load but can "
        "cut extraneous load, for example by putting labels directly on a diagram."
    ),
    ("missing-point", "missing"): (
        "Urban heat islands are cities that are warmer than the countryside "
        "around them. Dark roads and roofs absorb sunlight and release heat at "
        "night, buildings trap warm air, there are fewer trees for shade, and "
        "cars and air conditioning add waste heat. Cities can respond by "
        "planting trees and parks, painting roofs light colours, adding green "
        "roofs and using cooler paving materials."
    ),
    ("missing-point", "detail"): (
        "Urban heat islands are areas where cities are several degrees warmer "
        "than nearby countryside. This happens because dark roads and roofs "
        "absorb sunlight during the day and release heat at night, buildings "
        "block wind and trap warm air, and cities have fewer trees and plants "
        "to provide shade and cool the air through evaporation. Waste heat from "
        "cars and air conditioning also contributes. As a result, hotter cities "
        "use more energy and can be harmful to health during heatwaves."
    ),
}


# Scripted Auto-fix proposals for the demo cases, and the answer each demo
# produces once a rewritten request is approved and run.
AUTOFIX = {
    "too-technical": {
        "proposal": {
            "diagnosis": "The answer uses technical terms (ATP, thylakoid, "
                         "photophosphorylation) that a first-year student is "
                         "unlikely to know.",
            "rewritten_request": "Summarise this for a first-year student with no "
                                 "biology background, in about 80 words of plain "
                                 "everyday language. Avoid technical terms, or "
                                 "explain any you must use in simple words.",
            "changes": [
                "Added: the reader has no biology background.",
                "Added: use plain everyday language.",
                "Added: avoid technical terms or explain them simply.",
            ],
            "assumptions": [
                "You have no biology background.",
                "About 80 words is still the length you want.",
            ],
        },
        "output": (
            "Plants make their own food from sunlight. A green substance in "
            "their leaves, chlorophyll, captures light, and the plant uses that "
            "energy to turn carbon dioxide from the air and water from the soil "
            "into sugar for growth. Oxygen is released along the way, which is "
            "why plants matter for the air we breathe. This happens in two "
            "steps: first the light energy is captured, then it is used to make "
            "sugar. More light speeds it up, but only to a point."
        ),
    },
    "too-long": {
        "proposal": {
            "diagnosis": "The answer is about 190 words, far longer than the "
                         "60 words requested.",
            "rewritten_request": "Give me a summary of no more than 60 words. Keep "
                                 "only the main idea and the three kinds of load; "
                                 "leave out examples.",
            "changes": [
                "Changed: 'a 60-word summary' to a strict limit of no more than 60 words.",
                "Added: keep the main idea and the three kinds of load.",
                "Added: leave out examples.",
            ],
            "assumptions": [
                "The three kinds of load are the part you need most.",
                "You do not need the diagram example.",
            ],
        },
        "output": (
            "Cognitive load theory says working memory is limited, so learning "
            "tasks compete for space. Intrinsic load comes from the topic, "
            "germane load from building understanding, and extraneous load from "
            "poor design. Designers can reduce extraneous load to free capacity "
            "for learning."
        ),
    },
    "missing-point": {
        "proposal": {
            "diagnosis": "The answer explains the causes but leaves out what "
                         "cities can do, which the request asked for.",
            "rewritten_request": "Summarise the causes of urban heat islands and, "
                                 "in a separate sentence or two, list what cities "
                                 "can do about them, as described in the text.",
            "changes": [
                "Added: name urban heat islands explicitly.",
                "Added: give the solutions their own sentence or two so they are not dropped.",
                "Added: use only the solutions described in the text.",
            ],
            "assumptions": [
                "You want both causes and solutions with similar weight.",
            ],
        },
        "output": (
            "Cities are warmer than the countryside because dark roads and roofs "
            "absorb heat, buildings trap warm air, there are fewer trees for "
            "shade, and cars and air conditioning add waste heat. To cool down, "
            "cities can plant trees and create parks, paint roofs in light "
            "colours, add green roofs, and use paving that stays cooler."
        ),
    },
}


# Scripted own-words correction for the storyboard path "a fix does not help,
# so the person undoes it and writes their own correction". Used only when the
# correction contains all the keywords; anything else gets the generic mock.
CANNED_CORRECTIONS = {
    "too-technical": {
        "keywords": ["plain", "oxygen"],
        "output": (
            "Plants make their own food using light. A green pigment in their "
            "leaves, chlorophyll, captures the light, and the plant uses that "
            "energy to turn carbon dioxide and water into sugar. As this "
            "happens, plants release oxygen, which is why they matter for the "
            "air we breathe. More light makes the process faster, but only up "
            "to a limit."
        ),
    },
}
