import numpy as np
import tensorflow as tf
import math
from sklearn.preprocessing import MinMaxScaler
# 정규화 테스트

# frame_num = 193
frame_num = 50
category = ['0', '0', '1', '2', '3', '4']

def get_distance(row):
    left = row[0:42]
    right = row[42:]
    dlist = []
    for i in range(0, len(left), 2):
        for j in range(i+2, len(left), 2):
            x1 = left[i]
            x2 = left[i+1]
            y1 = left[j]
            y2 = left[j+1]
            dlist.append(math.hypot(x2-x1, y2-y1))
    for i in range(0, len(right), 2):
        for j in range(i+2, len(right), 2):
            x1 = right[i]
            x2 = right[j]
            y1 = right[i+1]
            y2 = right[j+1]
            dlist.append(math.hypot(x2-x1, y2-y1))
    return dlist

def pred_word(keypoints):
    scaler = MinMaxScaler()

    ex = np.array(keypoints).reshape(-1, 84)
    distance_list = []
    for row in range(len(ex)):
        distance = get_distance(ex[row].tolist()) # 1 프레임
        distance2 = np.array(distance).reshape(-1,1)
        scaler.fit(distance2)
        distance2 = scaler.transform(distance2)
        distance2 = distance2.reshape(1,-1)[0]
        distance_list.extend(distance2.tolist())

    train_frame_len = frame_num * 420
    input_frame_len = len(distance_list)
    print(input_frame_len)
    if input_frame_len <= train_frame_len:
        # 0으로 padding
        distance_list = [0]*(train_frame_len-input_frame_len) + distance_list
    else:
        distance_list = distance_list[:train_frame_len]
    print(len(distance_list)/420)

    distance_list = np.array(distance_list).reshape(1, -1, 420)

    model = tf.keras.models.load_model('201218_LSTM_99.h5')
    prediction = model.predict(distance_list)
    idx = np.argmax(prediction)

    print(prediction)
    # print(category[idx])
    return category[idx]