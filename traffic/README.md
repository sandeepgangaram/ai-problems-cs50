# Neural Network Classification Experiments on Traffic Signs Classification Problem

This document summarizes the iterative experimentation process for building and tuning a convolutional neural network (CNN) for a classification task. The primary evaluation metrics used were **accuracy** and **loss** on the validation/test set.

Our goal was to find the optimal architecture based on performance metrics while gradually increasing complexity.

## Experiment Summary

| #   | Architecture Summary                       | Hidden Layer | Dropout | Accuracy   | Loss       | Remarks                              |
| --- | ------------------------------------------ | ------------ | ------- | ---------- | ---------- | ------------------------------------ |
| 1   | 1x Conv (32 filters) + 2x2 MaxPool         | 128          | 0.4     | 0.5700     | 1.3987     | Slightly better than random guessing |
| 2   | 2x Conv (32 filters) + 2x2 MaxPool         | 256          | 0.5     | 0.9100     | 0.3158     | Significant improvement              |
| 3   | 2x Conv (48 filters) + 2x2 MaxPool         | 256          | 0.5     | **0.9619** | **0.1658** | ✅ Best model so far                 |
| 4   | 3x Conv (36 filters) + 2x2 MaxPool         | 256          | 0.5     | 0.9538     | 0.1714     | Performance dropped slightly         |
| 5   | 3x Conv (52, 48, 32 filters) + 2x2 MaxPool | 256          | 0.5     | 0.8770     | 0.4336     | Performance degraded                 |
| 6   | 2x Conv (48 filters) + 2x2 MaxPool         | 280          | 0.5     | 0.8986     | 0.3595     | Increased neurons didn’t help        |

## Conclusion

The best performing model was **Experiment #3** with:

- Two convolutional layers (48 filters each)
- 2x2 MaxPooling
- A dense hidden layer of 256 units
- Dropout of 0.5  
  This architecture achieved the highest accuracy of **96.19%** and the lowest loss of **0.1658**.
