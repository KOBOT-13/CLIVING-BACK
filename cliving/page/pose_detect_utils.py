import cv2
import mediapipe as mp
from django.http import JsonResponse
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from datetime import datetime
from .models import Checkpoint, Video, FirstImage, Hold


def detect_pose(video, user):
    mp_pose = mp.solutions.pose

    start_checkpoints = []
    success_checkpoints = []
    failure_checkpoints = []

    is_started = False
    is_success = False
    skip_frames = 0
    frame_count = 0
    xcount = 0
    ycount = 0
    #내려오면서 start 찍히는것 개선 starting_point 받고 손 좌표로 로직 개선 / climbing 규칙을 제대로 ... 

    try:
        latest_first_image = FirstImage.objects.filter(video).latest("created_at")
        width = latest_first_image.width
        height = latest_first_image.height
    except FirstImage.DoesNotExist:
        return {"error": "No FirstImage found"}
    # 기본값 설정
    default_top = {"x1": 0.4, "x2": 0.6, "y1": 0.2, "y2": 0.4}
    default_bottom = {"x1": 0.1, "x2": 0.2, "y1": 0.1, "y2": 0.2}

    # Hold 객체에서 값을 가져오거나 기본값으로 설정
    start_hold = list(Hold.objects.filter(first_image=latest_first_image, is_start=True))
    print(len(start_hold))
    top_hold = Hold.objects.filter(first_image=latest_first_image, is_top=True).first()
    y5, y6, x5, x6 = (start_hold[0].x1/ height, start_hold[0].x2/ height, start_hold[0].y1/ width, start_hold[0].y2/ width)
    print(x5,x6,y5,y6)
    # y7, y8, x7, x8 = (start_hold[1].x1/ height, start_hold[1].x2/ height, start_hold[1].y1/ width, start_hold[1].y2/ width)
    # print(x7,x8,y7,y8)
    bottom_hold = Hold.objects.filter(
        first_image=latest_first_image, is_bottom=True
    ).first()
    top_values = {
        "y1": top_hold.x1 / height if top_hold else default_top["x1"],
        "y2": top_hold.x2 / height if top_hold else default_top["x2"],
        "x1": top_hold.y1 / width if top_hold else default_top["y1"],
        "x2": top_hold.y2 / width if top_hold else default_top["y2"],
    }
    # 그리고 비교 연산에서 문자열로 사용하지 않도록 변수로 할당
    x1 = top_values["x1"]
    x2 = top_values["x2"]
    y1 = top_values["y1"]
    y2 = top_values["y2"]
    print(x1,x2,y1,y2)
    y_fail_point2 = bottom_hold.x2 / height
    print(y_fail_point2)
    # bottom_values = {
    #     "x3": bottom_hold.x1 / width if bottom_hold else default_bottom["x1"],
    #     "x4": bottom_hold.x2 / width if bottom_hold else default_bottom["x2"],
    #     "y3": bottom_hold.y1 / height if bottom_hold else default_bottom["y1"],
    #     "y4": bottom_hold.y2 / height if bottom_hold else default_bottom["y2"],
    # }
    # x3 = bottom_values["x3"]
    # x4 = bottom_values["x4"]
    # y3 = bottom_values["y3"]
    # y4 = bottom_values["y4"]

    if not top_hold:
        print(
            "'custom_error': No top hold found for the latest first image. Using default values:     ",
            top_values,
        )

    # if not bottom_hold:
    #     print(
    #         "'custom_error': No bottom hold found for the latest first image. Using default values: ",
    #         bottom_values,
    #     )

    # y_fail_point2 값이 1을 초과할 때 y4 값으로 설정
    if "y_fail_point2" in locals() and y_fail_point2 > 1:
        y_fail_point2 = bottom_hold.y2

    cap = cv2.VideoCapture(video.videofile.path)
    with mp_pose.Pose(
        min_detection_confidence=0.5, min_tracking_confidence=0.5
    ) as pose:
        while cap.isOpened():
            fps = cap.get(cv2.CAP_PROP_FPS)  # fps 구하기 반올리해서 사용하기
            fps = int(fps)
            # print(type(fps))
            # 스킵 포인트 정적인 시간이 아닌 발을 기준으로 움직인 시간만큼 옮기기
            success, frame = cap.read()
            if not success:
                break
            if skip_frames > 0:
                skip_frames -= 1
                continue

            # MediaPipe 포즈 탐지 수행
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = pose.process(frame)

            # 특정 조건 확인
            if results.pose_landmarks:
                left_foot_y = None
                right_foot_y = None
                left_wrist = None
                right_wrist = None

            try:
                left_foot_y = results.pose_landmarks.landmark[
                    mp_pose.PoseLandmark.LEFT_FOOT_INDEX
                ].y
            except (IndexError, TypeError, AttributeError):
                # 왼쪽 발 탐지 실패 시 None으로 설정
                left_foot_y = None

            try:
                right_foot_y = results.pose_landmarks.landmark[
                    mp_pose.PoseLandmark.RIGHT_FOOT_INDEX
                ].y
            except (IndexError, TypeError, AttributeError):
                # 오른쪽 발 탐지 실패 시 None으로 설정
                right_foot_y = None

            try:
                left_wrist = results.pose_landmarks.landmark[
                    mp_pose.PoseLandmark.LEFT_WRIST
                ]
            except (IndexError, TypeError, AttributeError):
                # 왼쪽 손목 탐지 실패 시 None으로 설정
                left_wrist = None

            try:
                right_wrist = results.pose_landmarks.landmark[
                    mp_pose.PoseLandmark.RIGHT_WRIST
                ]
            except (IndexError, TypeError, AttributeError):
                # 오른쪽 손목 탐지 실패 시 None으로 설정
                right_wrist = None

            # start_hold가 1개일 때 2개일 때 다르게 적용
            if len(start_hold) == 1:
                y5, y6, x5, x6 = (start_hold[0].x1/ height, start_hold[0].x2/ height, start_hold[0].y1/ width, start_hold[0].y2/ width)
                if not is_started:
                    if left_wrist and right_wrist and (
                        ((x5 <= left_wrist.x <= x6 and y5 <= left_wrist.y <= y6) and
                        (x5 <= right_wrist.x <= x6 and y5 <= right_wrist.y <= y6))):
                        print("1")
                        frame_count += 1
                        
                    elif left_wrist is None and right_wrist and (
                        (x5 <= right_wrist.x <= x6 and y5 <= right_wrist.y <= y6)):
                        print("2")
                        frame_count += 1
                        
                    elif left_wrist and right_wrist is None and (
                        (x5 <= left_wrist.x <= x6 and y5 <= left_wrist.y <= y6)):
                        print("3")
                        frame_count += 1
                    # if left_wrist and right_wrist and (
                    #     (x5 <= left_wrist.x <= x6 and y5 <= left_wrist.y <= y6) or
                    #     (x5 <= right_wrist.x <= x6 and y5 <= right_wrist.y <= y6)):
                    #     # print(left_wrist.x)
                    #     frame_count += 1
                    #     if frame_count >= 60:
                    #         is_started = True
                    #         start_checkpoint = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000
                    #         start_checkpoint = start_checkpoint - 2
                    #         start_checkpoints.append(start_checkpoint)
                    #         frame_count = 0
                    # elif left_wrist or right_wrist and (
                    #     (left_wrist is not None and x5 <= left_wrist.x <= x6 and y5 <= left_wrist.y <= y6) or
                    #     (right_wrist is not None and x5 <= right_wrist.x <= x6 and y5 <= right_wrist.y <= y6)
                    # ):
                    if frame_count >= (fps / 2):
                        is_started = True
                        start_checkpoint = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000
                        start_checkpoint = start_checkpoint - 2
                        start_checkpoints.append(start_checkpoint)
                        frame_count = 0
                        
            else:
                y5, y6, x5, x6 = (start_hold[0].x1/ height, start_hold[0].x2/ height, start_hold[0].y1/ width, start_hold[0].y2/ width)
                y7, y8, x7, x8 = (start_hold[1].x1/ height, start_hold[1].x2/ height, start_hold[1].y1/ width, start_hold[1].y2/ width)
                xcount += 1
                
                if xcount >= 30:
                    ycount += 1
                    print(ycount)
                    if left_wrist:
                        print("left_wristx : ",left_wrist.x)
                        print("left_wristy : ",left_wrist.y)
                    # print("right_wrist : ",right_wrist)
                    xcount =0
                    
                if not is_started:
                    if left_wrist and right_wrist and (
                        ((x5 <= left_wrist.x <= x6 and y5 <= left_wrist.y <= y6) or
                        (x7 <= left_wrist.x <= x8 and y7 <= left_wrist.y <= y8)) and
                        ((x5 <= right_wrist.x <= x6 and y5 <= right_wrist.y <= y6) or
                        (x7 <= right_wrist.x <= x8 and y7 <= right_wrist.y <= y8)) ):
                        # and not
                        # ((x5 <= left_wrist.x <= x6 and y5 <= left_wrist.y <= y6) and
                        # (x5 <= right_wrist.x <= x6 and y5 <= left_wrist.y <= y6)) and not
                        # ((x7 <= left_wrist.x <= x8 and y7 <= left_wrist.y <= y8) and
                        # (x7 <= right_wrist.x <= x8 and y7 <= left_wrist.y <= y8))):
                        print("1")
                        frame_count += 1
                        
                    elif left_wrist is None and right_wrist and (
                        ((x5 <= right_wrist.x <= x6 and y5 <= right_wrist.y <= y6) or
                        (x7 <= right_wrist.x <= x8 and y7 <= right_wrist.y <= y8))):
                        print("2")
                        frame_count += 1
                        
                    elif left_wrist and right_wrist is None and (
                        ((x5 <= left_wrist.x <= x6 and y5 <= left_wrist.y <= y6) or
                        (x7 <= left_wrist.x <= x8 and y7 <= left_wrist.y <= y8))):
                        print("3")
                        frame_count += 1

                    if frame_count >= (fps / 2): 
                        is_started = True
                        start_checkpoint = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000
                        start_checkpoint = start_checkpoint - 2
                        start_checkpoints.append(start_checkpoint)
                        frame_count = 0
            if (
                is_started
                and not is_success):
                    if (left_wrist is not None
                        and x1 <= left_wrist.x <= x2
                        and y1 <= left_wrist.y <= y2):
                        frame_count += 1
                    elif (
                        right_wrist is not None
                        and x1 <= right_wrist.x <= x2
                        and y1 <= right_wrist.y <= y2
                    ): 
                        frame_count +=1
                    elif (
                        right_wrist and left_wrist 
                        and x1 <= left_wrist.x <= x2
                        and y1 <= left_wrist.y <= y2
                        and x1 <= right_wrist.x <= x2
                        and y1 <= right_wrist.y <= y2
                    ):
                        frame_count +=1
                    if frame_count >=fps :
                        is_success = True
                        frame_count = 0 
                        skip_frames = fps
                

            # is_started가 True일 때만 실패/성공 체크
            if is_started:
                # bottom_hold 의 가장 큰 y 좌표 범위를 지나가면 is_started를 False로 변경
                if (left_foot_y is not None and y_fail_point2 <= left_foot_y) or (
                    right_foot_y is not None and y_fail_point2 <= right_foot_y
                ):
                    timestamp = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000
                    if not timestamp - start_checkpoints[-1] <= 5:
                        if is_success:
                            success_checkpoint = timestamp
                            success_checkpoints.append(success_checkpoint)
                            is_success = False
                            is_started = False
                            skip_frames = 30
                            continue

                        is_started = False
                        failure_checkpoint = timestamp
                        failure_checkpoints.append(failure_checkpoint)
                        skip_frames = 60  # 60프레임 건너뛰기
                        continue
                    
                    else:
                        start_checkpoints.pop()
    cap.release()
    video_duration = video.duration
    # 시작점 체크포인트 저장
    for timestamp in start_checkpoints:
        Checkpoint.objects.create(
            video=video,
            time=datetime.utcfromtimestamp(timestamp).time(),
            type=0,  # 시작점 체크포인트
        )

    for timestamp in success_checkpoints:
        adjusted_time = timestamp + 2 # timestamp 의미 해석하기 
        if adjusted_time > video_duration:
            adjusted_time = video_duration
        Checkpoint.objects.create(
            video=video,
            time=datetime.utcfromtimestamp(adjusted_time).time(),
            type=1,  # 성공 체크포인트
        )

    for timestamp in failure_checkpoints:
        adjusted_time = timestamp + 2
        if adjusted_time > video_duration:
            adjusted_time = video_duration
        Checkpoint.objects.create(
            video=video,
            time=datetime.utcfromtimestamp(adjusted_time).time(),
            type=2,  # 실패 체크포인트
        )

    return {
        "start_checkpoints": start_checkpoints,
        "success_checkpoints": success_checkpoints,
        "failure_checkpoints": failure_checkpoints,
    }
