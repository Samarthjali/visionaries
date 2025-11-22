import numpy as np
from sklearn.linear_model import LogisticRegression

class AIPredictor:
    def __init__(self):
        # Dummy model: classify based on transaction amount
        self.model = LogisticRegression()
        X = np.array([[10], [100], [500], [1000], [5000]])
        y = [0, 0, 1, 1, 1]  # 0 = Safe, 1 = Risky
        self.model.fit(X, y)

    def predict(self, amount):
        return self.model.predict([[amount]])[0]

