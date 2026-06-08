import cv2
import time
import mediapipe as mp
import pyautogui
import math




pyautogui.PAUSE    = 0
pyautogui.FAILSAFE = True





def main():
    cap  = cv2.VideoCapture(0)

    if not cap.isOpened():
        print(" Error:Could not open webcam.")
        return





    screen_width, screen_height  =pyautogui.size()
    smooth_factor  = 0.25  
    

    prev_avail     = False
    cloc_x, cloc_y = 0,0  
    
    
    left_mouse_down = False  
    right_clicking  = False
    

    scroll_anchor_y  = None    
    scroll_dead_zone = 15     
    

    zoom_anchor_y    = None
    zoom_dead_zone   = 15
     


    mp_hands   = mp.solutions.hands
    mp_drawing = mp.solutions.drawing_utils
    hands  =mp_hands.Hands(
        static_image_mode = False,
        max_num_hands = 1,
        min_detection_confidence=0.75,
        min_tracking_confidence=0.75
    )



    prev_time  =  0
 

    while True:
        success, frame  = cap.read()
        if not success:
            break




        frame     = cv2.flip(frame,1)
        h, w, c   = frame.shape
        

        rgb_frame = cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
        results   = hands.process(rgb_frame)

       



        current_mode = "HOVER /MOVE"
        mode_color   = (255,255,255)



        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                
                

                thumb_tip  = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
                index_tip  = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
                middle_tip = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
                ring_tip   = hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_TIP] # NEW
                
                

                cx_thumb, cy_thumb   = int(thumb_tip.x  * w), int( thumb_tip.y * h)
                cx_index, cy_index   = int(index_tip.x  * w), int(index_tip.y *h)
                cx_middle, cy_middle = int(middle_tip.x * w), int( middle_tip.y * h)
                cx_ring, cy_ring     = int(ring_tip.x   * w), int(ring_tip.y *h)

                
                

                left_click_dist  = math.hypot(cx_index -cx_thumb, cy_index  - cy_thumb)
                right_click_dist = math.hypot(cx_middle - cx_thumb, cy_middle - cy_thumb)
                zoom_dist        = math.hypot(cx_ring  - cx_thumb, cy_ring  - cy_thumb) # NEW
                two_finger_dist  = math.hypot(cx_index -cx_middle, cy_index - cy_middle)



                click_threshold = 40
                
                
            

                if left_mouse_down and left_click_dist >= click_threshold:
                    pyautogui.mouseUp(button='left')
                    left_mouse_down = False

              


                if zoom_dist < click_threshold:
                    current_mode = "ZOOMING"
                    mode_color = (255, 0, 255) # Purple
                    
                    scroll_anchor_y = None 
                    
                    if zoom_anchor_y is None:
                        zoom_anchor_y = cy_ring
                    
                   


                    cv2.circle(frame, (cx_ring, zoom_anchor_y), 6, (255, 0, 255), cv2.FILLED)
                    cv2.line(frame, (cx_ring, zoom_anchor_y), (cx_ring, cy_ring), (255, 0, 255), 2)
                    
                    offset_y = cy_ring - zoom_anchor_y
                    if abs(offset_y) > zoom_dead_zone:
                        # Calculate zoom speed
                        zoom_speed = int(offset_y  // 5) 
                        
                        


                        pyautogui.keyDown('ctrl')
                        pyautogui.scroll(-zoom_speed)
                        pyautogui.keyUp('ctrl')
                        
                        cv2.putText(frame, f"Rate: {abs(zoom_speed)}",  (cx_ring +  20, cy_ring), cv2.FONT_HERSHEY_SIMPLEX,  0.6, (255, 0, 255),2)


                        cv2.putText(frame, f"Rate: {abs(zoom_speed)}",  (cx_ring +  20, cy_ring), cv2.FONT_HERSHEY_SIMPLEX,  0.6, (255, 0, 255),2)

                 


                elif two_finger_dist  <  click_threshold and  left_click_dist >  click_threshold  and right_click_dist >  click_threshold:
                    current_mode = "SCROLLING"
                    mode_color = (0, 255, 255) 
                   
                    
                    zoom_anchor_y = None # Reset zoom anchor
                    
                    if scroll_anchor_y is None:
                        scroll_anchor_y = cy_index
                    
                    # Draw Scroll UI
                    cv2.circle(frame, (cx_index, scroll_anchor_y), 6, (0, 255, 255), cv2.FILLED)
                    cv2.line(frame, (cx_index, scroll_anchor_y), (cx_index, cy_index), (0, 255, 255), 2)
                    
                    offset_y = cy_index - scroll_anchor_y
                    if abs(offset_y) > scroll_dead_zone:
                        scroll_speed = int(offset_y // 3)
                        pyautogui.scroll(-scroll_speed)
                        
                



                else:
                    
                    scroll_anchor_y = None 
                    zoom_anchor_y   = None
                    
                    
                    target_x  = int(index_tip.x * screen_width)
                    target_y  = int(index_tip.y  * screen_height)
                    

                    if not prev_avail:
                        cloc_x, cloc_y = target_x,  target_y
                        prev_avail     = True

                    else:
                        cloc_x = ploc_x  + smooth_factor * (target_x  - ploc_x)
                        cloc_y = ploc_y + smooth_factor  * (target_y - ploc_y)
                    


                    pyautogui.moveTo(int(cloc_x), int(cloc_y))
                    ploc_x, ploc_y = cloc_x, cloc_y
 


                    if left_click_dist < click_threshold:
                        current_mode = "DRAGGING / LEFT CLICK"
                        mode_color = (0, 255, 0)  

                        cv2.circle(frame, (cx_index, cy_index), 12, (0, 255, 0), cv2.FILLED)
                        


                        if not left_mouse_down:
                            pyautogui.mouseDown(button='left')
                            left_mouse_down = True

                   


                    elif right_click_dist < click_threshold:
                        current_mode = "RIGHT CLICK"
                        mode_color = (255, 0, 0)  

                        cv2.circle(frame, (cx_middle, cy_middle), 12, (255, 0, 0), cv2.FILLED)
                        


                        if not right_clicking:
                            pyautogui.click(button = 'right')
                            right_clicking =  True

                    else:
                        right_clicking  = False




        else:
            prev_avail      = False
            scroll_anchor_y = None
            zoom_anchor_y   = None

            if left_mouse_down:
                pyautogui.mouseUp(button ='left')
                left_mouse_down  = False

         

        cv2.putText(frame, f"MODE: {current_mode}", (w // 2  - 150, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, mode_color,  2)
        
    
        current_time  = time.time()
        fps  = 1 / (current_time  - prev_time) if (current_time -  prev_time) > 0 else 0
        prev_time = current_time

        cv2.putText(frame, f"FPS: {int(fps)}", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        cv2.imshow("Air Touch Control System", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break


 

    if left_mouse_down:
        pyautogui.mouseUp(button='left')

    cap.release()
    cv2.destroyAllWindows()
    hands.close()



if __name__ == "__main__":
    main()