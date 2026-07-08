# Classic mode: net WPM (gross WPM scaled down by accuracy^2) maps to a
# normalized score via a piecewise-linear curve.
CLASSIC_NET_WPM_FLOOR = 20.0
CLASSIC_NET_WPM_CEILING = 90.0

# Reaction mode: lines-per-minute maps through the same kind of curve, then
# blends with line-correctness. Accuracy is weighted higher per product intent.
REACTION_LPM_FLOOR = 4.0
REACTION_LPM_CEILING = 20.0
REACTION_ACCURACY_WEIGHT = 0.7
REACTION_SPEED_WEIGHT = 0.3
