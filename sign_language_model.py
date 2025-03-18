import cv2
import numpy as np
import mediapipe as mp
import base64
import logging

class SignLanguageModel:
    """
    Class to handle sign language recognition using MediaPipe for hand tracking
    and a rule-based system for ASL alphabet recognition.
    """
    
    def _init_(self):
        # Initialize MediaPipe Hands
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2, 
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        
        # Configure logging
        self.logger = logging.getLogger(_name_)
        
        # Sign positions and rules for ASL alphabet (a simplified version)
        self.asl_positions = self._initialize_asl_positions()
        
        # Track the last recognized sign to prevent flickering
        self.last_sign = None
        self.confidence_threshold = 0.7
        self.sign_stability_counter = 0
        self.stability_threshold = 3  # Number of consecutive frames with same sign
    
    def _initialize_asl_positions(self):
        """
        Initialize the rules for recognizing ASL alphabet.
        This is a simplified version focusing on hand shape.
        
        In a production system, this would be replaced by a trained ML model.
        """
        return {
            'A': self._check_a_sign,
            'B': self._check_b_sign,
            'C': self._check_c_sign,
            'D': self._check_d_sign,
            'E': self._check_e_sign,
            'F': self._check_f_sign,
            'G': self._check_g_sign,
            'H': self._check_h_sign,
            'I': self._check_i_sign,
            'J': self._check_j_sign,
            'K': self._check_k_sign,
            'L': self._check_l_sign,
            'M': self._check_m_sign,
            'N': self._check_n_sign,
            'O': self._check_o_sign,
            'P': self._check_p_sign,
            'Q': self._check_q_sign,
            'R': self._check_r_sign,
            'S': self._check_s_sign,
            'T': self._check_t_sign,
            'U': self._check_u_sign,
            'V': self._check_v_sign,
            'W': self._check_w_sign,
            'X': self._check_x_sign,
            'Y': self._check_y_sign,
            'Z': self._check_z_sign,
        }
    
    def process_frame(self, frame):
        """
        Process a video frame to detect and recognize sign language.
        
        Args:
            frame: Image frame from webcam
            
        Returns:
            text: Recognized sign language text
            confidence: Confidence level of recognition
            processed_image: Base64 encoded processed image with landmarks
        """
        # Convert the image to RGB for MediaPipe
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process the image with MediaPipe
        results = self.hands.process(frame_rgb)
        
        # Draw hand landmarks on the image
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                self.mp_drawing.draw_landmarks(
                    frame,
                    hand_landmarks,
                    self.mp_hands.HAND_CONNECTIONS,
                    self.mp_drawing_styles.get_default_hand_landmarks_style(),
                    self.mp_drawing_styles.get_default_hand_connections_style()
                )
            
            # Check for ASL signs
            # In this simplified version, we only use the first detected hand
            landmarks = results.multi_hand_landmarks[0]
            
            # Identify the sign
            sign, confidence = self._identify_sign(landmarks)
            
            # Implement stability for recognition
            if sign == self.last_sign and confidence > self.confidence_threshold:
                self.sign_stability_counter += a
            else:
                self.sign_stability_counter = 0
                
            if self.sign_stability_counter >= self.stability_threshold:
                recognized_sign = sign
                recognized_confidence = confidence
            else:
                recognized_sign = self.last_sign if self.last_sign else "Detecting..."
                recognized_confidence = 0.0
                
            self.last_sign = sign
        else:
            recognized_sign = "No hands detected"
            recognized_confidence = 0.0
            self.last_sign = None
            self.sign_stability_counter = 0
        
        # Add text to the image
        cv2.putText(
            frame, 
            f"Sign: {recognized_sign} ({recognized_confidence:.2f})", 
            (10, 30), 
            cv2.FONT_HERSHEY_SIMPLEX, 
            1, 
            (0, 255, 0), 
            2
        )
        
        # Convert the processed image to base64 for sending to client
        _, buffer = cv2.imencode('.jpg', frame)
        processed_image_base64 = "data:image/jpeg;base64," + base64.b64encode(buffer).decode('utf-8')
        
        return recognized_sign, recognized_confidence, processed_image_base64
        
    def _identify_sign(self, landmarks):
        """
        Identify the ASL sign from hand landmarks.
        
        Args:
            landmarks: MediaPipe hand landmarks
            
        Returns:
            sign: Recognized sign character
            confidence: Confidence level of recognition
        """
        best_match = None
        highest_confidence = 0.0
        
        # Check each ASL sign
        for sign, check_function in self.asl_positions.items():
            confidence = check_function(landmarks.landmark)
            if confidence > highest_confidence:
                highest_confidence = confidence
                best_match = sign
        
        if highest_confidence > self.confidence_threshold:
            return best_match, highest_confidence
        else:
            return "Unknown", highest_confidence
    
    # The following methods implement simplified checks for each ASL letter
    # In a real application, these would be replaced by a trained ML model
    # These are approximations based on relative finger positions
    
    def _check_a_sign(self, landmarks):
        # A sign: Fist with thumb on side
        thumb_tip = landmarks[4]
        index_tip = landmarks[8]
        middle_tip = landmarks[12]
        ring_tip = landmarks[16]
        pinky_tip = landmarks[20]
        
        index_mcp = landmarks[5]
        middle_mcp = landmarks[9]
        ring_mcp = landmarks[13]
        pinky_mcp = landmarks[17]
        
        # Check if fingers are curled (tips close to mcps)
        fingers_curled = (
            self._distance_3d(index_tip, index_mcp) < 0.1 and
            self._distance_3d(middle_tip, middle_mcp) < 0.1 and
            self._distance_3d(ring_tip, ring_mcp) < 0.1 and
            self._distance_3d(pinky_tip, pinky_mcp) < 0.1
        )
        
        # Check if thumb is sticking out to the side
        thumb_out = thumb_tip.x > index_mcp.x
        
        if fingers_curled and thumb_out:
            return 0.9
        return 0.0
    
    def _check_b_sign(self, landmarks):
        # B sign: Fingers straight up, thumb tucked
        thumb_tip = landmarks[4]
        index_tip = landmarks[8]
        middle_tip = landmarks[12]
        ring_tip = landmarks[16]
        pinky_tip = landmarks[20]
        
        wrist = landmarks[0]
        
        # Check if fingers are extended upward
        fingers_extended = (
            index_tip.y < wrist.y and
            middle_tip.y < wrist.y and
            ring_tip.y < wrist.y and
            pinky_tip.y < wrist.y
        )
        
        # Check if thumb is tucked
        thumb_tucked = thumb_tip.x < landmarks[5].x  # Thumb tip inside hand
        
        if fingers_extended and thumb_tucked:
            return 0.9
        return 0.0
    
    def _check_c_sign(self, landmarks):
        # C sign: Curved hand forming a C shape
        thumb_tip = landmarks[4]
        pinky_tip = landmarks[20]
        
        # Check if thumb and pinky form a C shape
        c_shape = (
            abs(thumb_tip.y - pinky_tip.y) < 0.2 and  # Similar height
            thumb_tip.x < pinky_tip.x  # Thumb left of pinky
        )
        
        if c_shape:
            return 0.9
        return 0.0
