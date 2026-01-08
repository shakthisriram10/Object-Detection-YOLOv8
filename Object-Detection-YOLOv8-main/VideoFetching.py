import cv2

url = "http://192.168.137.137:6677"+"/videofeed?username=&password="


# Open the video stream
cap = cv2.VideoCapture(0)
print("Started")
while True:
    
    ret, frame = cap.read()

    if ret:
      
        cv2.imshow('Video Stream', frame)
      
        # Press 'q' to exit the loop
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    else:
        break

# Release the resources
print("Terminating")
cap.release()
cv2.destroyAllWindows()