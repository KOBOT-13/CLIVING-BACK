import cv2
import mediapipe as mp
from django.http import JsonResponse
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from datetime import datetime


def detect_pose(request):
    if request.method == 'POST' and request.FILES['video']:
        video = request.FILES['video']
        video_path = default_storage.save('uploads/video.mp4', ContentFile(video.read()))

        mp_drawing = mp.solutions.drawing_utils
        mp_pose = mp.solutions.pose

        success_checkpoints = []
        failure_checkpoints = []
        is_started = False

        cap = cv2.VideoCapture(video_path)

        # 데이터베이스에서 좌표값 가져오기
        checkpoint = Checkpoint.objects.first()
        if checkpoint:
            x1, x2 = checkpoint.x1, checkpoint.x2
            y1, y2 = checkpoint.y1, checkpoint.y2
        else:
            # 좌표값이 없는 경우 기본값 설정
            x1, x2 = 0.4, 0.6
            y1, y2 = 0.2, 0.4

        with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
            while cap.isOpened():
                success, image = cap.read()
                if not success:
                    break

                # MediaPipe 포즈 탐지 수행
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                results = pose.process(image)

                # 두 개의 Y축 선 그리기
                # height, width, _ = image.shape
                # cv2.line(image, (0, int(height * 0.3)), (width, int(height * 0.3)), (0, 255, 0), 2)
                # cv2.line(image, (0, int(height * 0.7)), (width, int(height * 0.7)), (0, 0, 255), 2)

                # 특정 조건 확인
                if results.pose_landmarks:
                    # 스타팅 포인트 넘으면 is_started를 True로 변경
                    if not is_started and results.pose_landmarks.landmark[mp_pose.PoseLandmark.NOSE].y < 0.3:
                        is_started = True

                    # is_started가 True일 때만 실패/성공 체크
                    if is_started:
                        # 특정 y축 밑으로 떨어지면 실패
                        if results.pose_landmarks.landmark[mp_pose.PoseLandmark.NOSE].y > 0.7:
                            failure_checkpoints.append(cap.get(cv2.CAP_PROP_POS_MSEC) / 1000)

                        # 왼손 또는 오른손이 특정 좌표 범위에 닿으면 성공
                        left_wrist = results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_WRIST]
                        right_wrist = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_WRIST]
                        if (x1 < left_wrist.x < x2 and y1 < left_wrist.y < y2) or \
                           (x1 < right_wrist.x < x2 and y1 < right_wrist.y < y2):
                            success_checkpoints.append(cap.get(cv2.CAP_PROP_POS_MSEC) / 1000)

        cap.release()

        # 데이터베이스에 결과 저장
        pose_detection_result = PoseDetectionResult(
            video_path=video_path,
            success_checkpoints=','.join(map(str, success_checkpoints)),
            failure_checkpoints=','.join(map(str, failure_checkpoints))
        )
        pose_detection_result.save()

        # 결과 반환
        result = {
            'success_checkpoints': success_checkpoints,
            'failure_checkpoints': failure_checkpoints
        }
        return JsonResponse(result)
    else:
        return JsonResponse({'error': 'Invalid request'}, status=400)