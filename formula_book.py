"""
formula_book.py - High-Yield Student Formula & Reasoning Concept Handbook
Provides quick-reference formulas and reasoning rules directly inside the web app
for students preparing for school, college, and competitive exams (JEE, SSC, CAT, Olympiads).
"""

MATH_FORMULAS = {
    "Algebra & Progressions": [
        {"name": "Quadratic Formula", "formula": "$$x = \\frac{-b \\pm \\sqrt{b^2 - 4ac}}{2a}$$", "desc": "Roots of $ax^2 + bx + c = 0$. Discriminant $\\Delta = b^2 - 4ac$."},
        {"name": "Algebraic Identity 1", "formula": "$$(a+b)^2 = a^2 + 2ab + b^2, \\quad (a-b)^2 = a^2 - 2ab + b^2$$", "desc": "Standard expansion formulas."},
        {"name": "Algebraic Identity 2", "formula": "$$a^2 - b^2 = (a-b)(a+b), \\quad a^3+b^3 = (a+b)(a^2-ab+b^2)$$", "desc": "Difference of squares and cubes."},
        {"name": "Arithmetic Progression (AP)", "formula": "$$T_n = a + (n-1)d, \\quad S_n = \\frac{n}{2}[2a + (n-1)d]$$", "desc": "$a$ is first term, $d$ is common difference, $n$ is number of terms."},
        {"name": "Geometric Progression (GP)", "formula": "$$T_n = a r^{n-1}, \\quad S_n = \\frac{a(r^n - 1)}{r - 1} \\ (r \\neq 1)$$", "desc": "$a$ is first term, $r$ is common ratio. Sum to infinity $S_\\infty = \\frac{a}{1-r}$ for $|r|<1$."},
        {"name": "Logarithm Laws", "formula": "$$\\log(xy) = \\log x + \\log y, \\quad \\log(x/y) = \\log x - \\log y, \\quad \\log(x^k) = k \\log x$$", "desc": "Base change: $\\log_b a = \\frac{\\ln a}{\\ln b}$."}
    ],
    "Trigonometry": [
        {"name": "Pythagorean Identities", "formula": "$$\\sin^2 \\theta + \\cos^2 \\theta = 1, \\quad 1 + \\tan^2 \\theta = \\sec^2 \\theta, \\quad 1 + \\cot^2 \\theta = \\csc^2 \\theta$$", "desc": "Fundamental trigonometric identities."},
        {"name": "Compound Angles", "formula": "$$\\sin(A \\pm B) = \\sin A \\cos B \\pm \\cos A \\sin B$$", "desc": "$$\\cos(A \\pm B) = \\cos A \\cos B \\mp \\sin A \\sin B$$"},
        {"name": "Double Angle Formulas", "formula": "$$\\sin(2\\theta) = 2\\sin\\theta\\cos\\theta, \\quad \\cos(2\\theta) = \\cos^2\\theta - \\sin^2\\theta = 2\\cos^2\\theta-1$$", "desc": "$$\\tan(2\\theta) = \\frac{2\\tan\\theta}{1 - \\tan^2\\theta}$$"}
    ],
    "Calculus": [
        {"name": "Standard Derivatives", "formula": "$$\\frac{d}{dx}[x^n] = nx^{n-1}, \\quad \\frac{d}{dx}[e^x] = e^x, \\quad \\frac{d}{dx}[\\ln x] = \\frac{1}{x}$$", "desc": "Power rule and exponential derivatives."},
        {"name": "Product & Quotient Rule", "formula": "$$(uv)' = u'v + uv', \\quad \\left(\\frac{u}{v}\\right)' = \\frac{u'v - uv'}{v^2}$$", "desc": "Differentiation rules for composite products & fractions."},
        {"name": "Standard Integrals", "formula": "$$\\int x^n dx = \\frac{x^{n+1}}{n+1} + C \\ (n \\neq -1), \\quad \\int \\frac{1}{x} dx = \\ln|x| + C$$", "desc": "$$\\int e^x dx = e^x + C, \\quad \\int \\cos x dx = \\sin x + C$$"}
    ],
    "Probability & Combinatorics": [
        {"name": "Permutations & Combinations", "formula": "$$^nP_r = \\frac{n!}{(n-r)!}, \\quad ^nC_r = \\frac{n!}{r!(n-r)!}$$", "desc": "Arrangement vs Selection."},
        {"name": "Probability & Bayes Theorem", "formula": "$$P(A \\cup B) = P(A) + P(B) - P(A \\cap B), \\quad P(A|B) = \\frac{P(A \\cap B)}{P(B)}$$", "desc": "Conditional probability and union law."}
    ]
}

REASONING_CONCEPTS = {
    "Alphabetical & Alphanumeric": [
        {"name": "EJOTY Positioning Rule", "rule": "E=5, J=10, O=15, T=20, Y=25", "desc": "Quickly identify position of any letter in forward alphabetical order."},
        {"name": "Reverse Alphabetical Pairs (Sum = 27)", "rule": "A-Z, B-Y, C-X, D-W, E-V, F-U, G-T, H-S, I-R, J-Q, K-P, L-O, M-N", "desc": "Opposite letter positions always sum up to 27 (e.g. A(1) + Z(26) = 27)."},
        {"name": "Letter Shift Pattern", "rule": "Look for +1, +2, -3 or alternating shifts in coding-decoding puzzles.", "desc": "Always write down position numbers to spot mathematical progression in letters."}
    ],
    "Series & Sequences": [
        {"name": "Difference of Differences", "rule": "If 1st difference isn't constant, compute 2nd difference.", "desc": "Often reveals an AP or squares/cubes pattern (e.g., +3, +5, +7...)."},
        {"name": "Alternating Series", "rule": "Numbers at odd indices and even indices follow two independent logic rules.", "desc": "Check odd terms (1st, 3rd, 5th) and even terms (2nd, 4th, 6th) separately."},
        {"name": "Multiplication & Addition Combo", "rule": "Look for $\\times n + c$ patterns (e.g., $\\times 2 + 1, \\times 2 + 2, \\dots$).", "desc": "Commonly tested in banking, SSC, and CAT aptitude tests."}
    ],
    "Logical Deductions & Relations": [
        {"name": "Blood Relations Shorthand", "rule": "+ (Male), - (Female), = (Spouse), | (Parent-Child), -- (Siblings)", "desc": "Draw a quick family tree on scratchpad using standard pedigree symbols."},
        {"name": "Direction & Pythagoras Sense", "rule": "North is Up, South is Down, East is Right, West is Left.", "desc": "Shortest distance between start & end points: $D = \\sqrt{\\Delta x^2 + \\Delta y^2}$."},
        {"name": "Syllogisms Venn Logic", "rule": "Never assume anything beyond given premises. An answer is valid ONLY if true in ALL possible Venn cases.", "desc": "If 'Some A are B', that does NOT automatically imply 'Some A are not B'."}
    ]
}
