import cv2
import mediapipe as mp
import numpy as np
import pygame
import os

# Inisialisasi Pygame Mixer untuk Audio
pygame.mixer.init()

# Inisialisasi MediaPipe Pose
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
mp_drawing = mp.solutions.drawing_utils

def calculate_distance(p1, p2):
    return np.sqrt((p1.x - p2.x)**2 + (p1.y - p2.y)**2)

def check_trigger_pose(landmarks):
    if not landmarks:
        return False
    
    nose = landmarks[mp_pose.PoseLandmark.NOSE.value]
    l_wrist = landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value]
    r_wrist = landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value]
    l_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
    r_shoulder = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value]
    l_elbow = landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value]
    r_elbow = landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value]

    # UKURAN TUBUH (Body Scale) - Jarak antar bahu sebagai referensi fleksibilitas
    body_scale = calculate_distance(l_shoulder, r_shoulder)
    if body_scale < 0.05: body_scale = 0.1 # Minimal scale agar tidak pembagian nol

    # Threshold Fleksibel:
    # 1. Tangan di mulut: jarak tangan ke hidung < 70% lebar bahu
    mouth_threshold = body_scale * 0.7
    
    # 2. Tangan Menjauh: Cukup cek apakah tangan menjauh dari bahu secara 2D
    # Ini jauh lebih fleksibel daripada cek Z (kedalaman)
    ext_threshold = body_scale * 1.0

    # Skenario 1: Kiri di mulut, Kanan menjauh
    is_l_mouth = calculate_distance(l_wrist, nose) < mouth_threshold
    is_r_ext = calculate_distance(r_wrist, r_shoulder) > ext_threshold

    # Skenario 2: Kanan di mulut, Kiri menjauh
    is_r_mouth = calculate_distance(r_wrist, nose) < mouth_threshold
    is_l_ext = calculate_distance(l_wrist, l_shoulder) > ext_threshold

    return (is_l_mouth and is_r_ext) or (is_r_mouth and is_l_ext)

# Fungsi untuk melakukan overlay video green screen
def overlay_transparent_video(background_frame, video_frame, x_offset, y_offset):
    h_bg, w_bg, _ = background_frame.shape
    h_vid, w_vid, _ = video_frame.shape

    # Pastikan video tidak keluar dari batas frame background
    if y_offset + h_vid > h_bg or x_offset + w_vid > w_bg:
        return background_frame

    # Ambil Region of Interest (ROI) dari background
    roi = background_frame[y_offset:y_offset+h_vid, x_offset:x_offset+w_vid]

    # Convert frame video ke HSV untuk deteksi green screen
    hsv = cv2.cvtColor(video_frame, cv2.COLOR_BGR2HSV)
    
    # Range warna hijau untuk green screen
    lower_green = np.array([35, 40, 40])
    upper_green = np.array([85, 255, 255])
    
    # Buat mask (area hijau jadi putih/255, lainnya hitam/0)
    mask = cv2.inRange(hsv, lower_green, upper_green)
    # Inverse mask (karakter jadi putih/255, background hijau jadi hitam/0)
    mask_inv = cv2.bitwise_not(mask)

    # Ambil background asli pada area hijau
    bg_part = cv2.bitwise_and(roi, roi, mask=mask)
    # Ambil karakter dari video
    fg_part = cv2.bitwise_and(video_frame, video_frame, mask=mask_inv)

    # Gabungkan keduanya
    dst = cv2.add(bg_part, fg_part)
    
    # Masukkan kembali ke frame utama
    background_frame[y_offset:y_offset+h_vid, x_offset:x_offset+w_vid] = dst
    return background_frame

def main():
    # Setup Webcam
    cap = cv2.VideoCapture(0)
    
    # Setup Video Overlay
    video_path = 'assets/video/scuba_cat_dance.mp4'
    audio_path = 'assets/video/scuba_cat_dance.mp3'
    
    # Ekstrak Audio jika belum ada
    if not os.path.exists(audio_path):
        print("Mengekstrak audio dari video...")
        try:
            # Import dinamis untuk menangani perbedaan versi moviepy
            try:
                from moviepy.editor import VideoFileClip
            except ImportError:
                from moviepy.video.io.VideoFileClip import VideoFileClip
            
            video = VideoFileClip(video_path)
            video.audio.write_audiofile(audio_path, logger=None)
            video.close()
            print("Ekstrak audio berhasil!")
        except Exception as e:
            print(f"Gagal ekstrak audio: {e}")
            print("Pastikan moviepy sudah terinstall: uv pip install moviepy")

    # Load audio ke pygame
    if os.path.exists(audio_path):
        pygame.mixer.music.load(audio_path)

    vid_cap = cv2.VideoCapture(video_path)
    
    # Ukuran overlay video (dibuat lebih tinggi/panjang sesuai permintaan)
    overlay_width, overlay_height = 300, 700
    
    is_dancing = False
    cooldown_counter = 0

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            print("Gagal membaca webcam.")
            break

        # Flip frame agar seperti cermin
        frame = cv2.flip(frame, 1)
        
        # Proses Pose Detection
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(rgb_frame)

        # Cek apakah pose trigger terjadi
        if results.pose_landmarks:
            mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
            
            trigger_active = check_trigger_pose(results.pose_landmarks.landmark)
            
            if trigger_active:
                if not is_dancing:
                    # Mulai musik saat tarian baru terdeteksi
                    if os.path.exists(audio_path):
                        pygame.mixer.music.play(-1) # Loop
                is_dancing = True
                cooldown_counter = 30 # Video akan tampil selama 30 frame setelah trigger hilang
            elif cooldown_counter > 0:
                cooldown_counter -= 1
            else:
                if is_dancing:
                    pygame.mixer.music.stop()
                is_dancing = False

        # Jika sedang menari, overlay video di kiri bawah & kanan bawah
        if is_dancing:
            vid_success, vid_frame = vid_cap.read()
            # Jika video habis, ulang dari awal
            if not vid_success:
                vid_cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                vid_success, vid_frame = vid_cap.read()

            if vid_success:
                h_frame, w_frame, _ = frame.shape
                
                # PROTEKSI: Paksa tinggi video tidak melebihi frame kamera agar tidak error
                h_target = min(overlay_height, h_frame - 40)
                w_target = int(h_target * (overlay_width / overlay_height))

                vid_frame_resized = cv2.resize(vid_frame, (w_target, h_target))
                
                # Posisi Kiri Bawah
                y_pos = h_frame - h_target - 20
                frame = overlay_transparent_video(frame, vid_frame_resized, 20, y_pos)
                
                # Posisi Kanan Bawah
                x_right = w_frame - w_target - 20
                vid_frame_flipped = cv2.flip(vid_frame_resized, 1) 
                frame = overlay_transparent_video(frame, vid_frame_flipped, x_right, y_pos)
        else:
            # Reset video jika tidak menari agar saat mulai lagi dari awal
            vid_cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

        # Tampilkan status di layar
      #   status_text = "STATUS: DANCING!" if is_dancing else "STATUS: Waiting for Pose..."
      #   color = (0, 255, 0) if is_dancing else (0, 0, 255)
      #   cv2.putText(frame, status_text, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

        cv2.imshow('Dance Detector', frame)

        if cv2.waitKey(5) & 0xFF == 27: # Tekan ESC untuk keluar
            break

    cap.release()
    vid_cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
