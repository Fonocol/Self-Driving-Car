import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import pickle
import os

data = pd.read_csv("player_car_data.csv")

y = data['action'].map({'forward': 0, 'backward': 1, 'rotate_left': 2, 'rotate_right': 3})

y = y.fillna(0)

X = data[['front_dist', 'back_dist', 'left_dist', 'right_dist', 
          'left_font_dist', 'right_font_dist', 'left_back_dist', 
          'right__back_dist', 'angle', 'speed', 'collision', 'finish_distance']]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = RandomForestClassifier(n_estimators=100, random_state=42)

model.fit(X_train, y_train)

y_pred = model.predict(X_test)
print(f'Précision du modèle: {accuracy_score(y_test, y_pred):.4f}')

if not os.path.exists('.model'):
    os.makedirs('.model')

with open('.model/random_forest_model.pkl', 'wb') as f:
    pickle.dump(model, f)

print("Modèle sauvegardé sous '.model/random_forest_model.pkl'")

with open('.model/random_forest_model.pkl', 'rb') as f:
    loaded_model = pickle.load(f)

new_state = [[0.22699463, 0.5010836,  0.02731471, 0.01977962, 0.02825659, 0.03767546 ,0.03955923, 0.02731471, 0.5, 1.0,0.0,0.25356907]]


predicted_action = loaded_model.predict(new_state)
print(f'L\'action prédite est: {predicted_action}')
