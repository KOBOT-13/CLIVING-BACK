import cv2
import numpy as np
from time import time
import mediapipe as mp 
import matplotlib.pyplot as plt 

# MediaPipe Pose 세팅
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils
pose = mp_pose.Pose(static_image_mode=False, min_detection_confidence=0.5)

# 카메라 캡처 시작
cap = cv2.VideoCapture(0)  # '0'은 컴퓨터의 기본 카메라

try:
    while cap.isOpened():
        success, image = cap.read()
        if not success:
            print("Ignoring empty camera frame.")
            continue
        # 이미지에서 포즈 추정
        image.flags.writeable = False
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = pose.process(image)

        # 포즈 어노테이션을 이미지에 그리기
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

        # 클라이밍 성공/실패 판단 로직
        if results.pose_landmarks:
            landmarks = results.pose_landmarks.landmark
            left_hand = landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value]
            right_hand = landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value]
            left_foot = landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value]
            right_foot = landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value]
        # 타겟 좌표에 머물기 시작한 시간을 추적
    left_hand_start_time = None
    right_hand_start_time = None

    while True:
    # left_hand와 right_hand의 좌표를 받아오는 코드가 필요합니다
    # 예시: left_hand = get_left_hand_position()
    # 예시: right_hand = get_right_hand_position()

    # 왼손이 타겟 좌표 안에 있는지 확인
     if left_hand.y < 0.1 and left_hand.x < 0.1:
        if left_hand_start_time is None:
            left_hand_start_time = time.time()  # 타이머 시작
        else:
            left_hand_start_time = None  # 타겟 좌표를 벗어나면 타이머 리셋

    # 오른손이 타겟 좌표 안에 있는지 확인
        if right_hand.y < 0.1 and right_hand.x < 0.1:
            if right_hand_start_time is None:
                right_hand_start_time = time.time()  # 타이머 시작
            else:
                right_hand_start_time = None  # 타겟 좌표를 벗어나면 타이머 리셋

    # 두 손이 모두 타겟 좌표에 3초 이상 머물렀는지 확인
        if left_hand_start_time and right_hand_start_time:
            elapsed_time_left = time.time() - left_hand_start_time
            elapsed_time_right = time.time() - right_hand_start_time
            if elapsed_time_left >= 3 and elapsed_time_right >= 3:
                print("Climbing success!")
                break  # 성공 후 반복 종료

        time.sleep(0.1)  # 0.1초 단위로 위치를 체크
            # # 발이 맨 아래에 닿으면 실패
            #     elif left_foot.y > 0.9 or right_foot.y > 0.9:
            #         print("Climbing failed!")
            #     else:
            #         print("Keep trying!")
        ## 암반 끝 쪽의 y좌표를 정해두고 그 밑으로 떨어질시에 fail 처리, 그위로 올라가면 checkpoint == start
        # 화면에 결과 출력
        cv2.imshow('MediaPipe Pose', image)
        if cv2.waitKey(5) & 0xFF == 27:
            break
finally:
    cap.release()
    cv2.destroyAllWindows()
