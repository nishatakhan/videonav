
import numpy as np
import cv2
import csv
import time

blackrange=65
percentile=70

def colordetection(hsvimage,flag):
   if flag==0:
      #Threshold the HSV image, keep only the red pixels
      lower_red_hue_range=cv2.inRange(hsvimage, np.array((0, 100, 100),dtype = "uint8"), np.array((10, 255, 255),dtype = "uint8"));
      upper_red_hue_range=cv2.inRange(hsvimage, np.array((160, 100, 100),dtype = "uint8"), np.array((179, 255, 255),dtype = "uint8"));

      #Combine the above two images
      red_hue_image=cv2.addWeighted(lower_red_hue_range, 1.0, upper_red_hue_range, 1.0, 0.0);
      red_hue_image=cv2.GaussianBlur(red_hue_image, (9, 9), 2, 2);
      
      return red_hue_image

   else:
      #Threshold the HSV image, keep only the red pixels
      green_hue_range=cv2.inRange(hsvimage, np.array((50, 100, 100),dtype = "uint8"), np.array((95, 255, 255),dtype = "uint8"));
        
      green_hue_image=cv2.GaussianBlur(green_hue_range, (9, 9), 2, 2);

      return green_hue_image

def detectcircle(image):
   circles=cv2.HoughCircles(image, cv2.cv.CV_HOUGH_GRADIENT, 1, image.shape[0]/6,np.array([]),200, 15,5,10)
   return circles

def midpointcircledraw(x_c,y_c,r):
    point=[]
    x=0;
    y=r;
    
    point.append((x_c+x,y_c+y))
    point.append((x_c+x,y_c-y))
    point.append((x_c-x,y_c+y))
    point.append((x_c-x,y_c-y))
    point.append((x_c+y,y_c+x))
    point.append((x_c+y,y_c-x))
    point.append((x_c-y,y_c+x))
    point.append((x_c-y,y_c-x))
     
    #Initialising the value of D
    d = 5/4 - r
    while x < y:
        # Mid-point is inside or on the perimeter
        if (d < 0):
            d=d+2*x+1
        #Mid-point is outside the perimeter
        else:
            d=d+2*x-2*y+1
            y -=1
        x+=1
         
        #All the perimeter points have already been printed
         
        point.append((x_c+x,y_c+y))
        point.append((x_c+x,y_c-y))
        point.append((x_c-x,y_c+y))
        point.append((x_c-x,y_c-y))
        point.append((x_c+y,y_c+x))
        point.append((x_c+y,y_c-x))
        point.append((x_c-y,y_c+x))
        point.append((x_c-y,y_c-x))

    return point

def rectangle_per(hsvimage,x_c,y_c,r,flag):
   points=[]
   
   x_c=int(x_c)
   y_c=int(y_c)
   r=int(round(r))
   if flag==0:   
      ymin=y_c+r
      ymax=y_c+2*r+2
      xmin=x_c-r
      xmax=x_c+r
   if flag==1:
      ymin=y_c-r
      ymax=y_c+r
      xmin=x_c+r
      xmax=x_c+2*r
   if flag==2:
      ymin=y_c-2*r-2
      ymax=y_c-r
      xmin=x_c-r
      xmax=x_c+r
   if flag==3:
      ymin=y_c-r
      ymax=y_c+r
      xmin=x_c-2*r-2
      xmax=x_c-r
   for y in range(ymin, ymax+1):
      for x in range(xmin,xmax+1):
         points.append((x,y))
   color=[]
   count=0
   for i in range(0,len(points)):
      x,y=points[i]
      print x,y
      color=hsvimage[y,x]
      print color
      if color[2]<blackrange:
         count +=1
   return (count/float(len(points)))*100



def finaldata(circles_red,circles_green,shiftx,shifty):
   color=[]
   cir_pos=[]
   radi=[]

   if circles_red is not None:
      for circles in circles_red[0]:
         c=0
         [x_c,y_c,r]=circles
         x_c=int(x_c+shiftx)
         y_c=int(y_c+shifty)
         cir_pos.append((x_c,y_c))
         color.append(c)
         radi.append(r)

   if circles_green is not None:
      for circles in circles_green[0]:
         c=1
         [x_c,y_c,r]=circles
         x_c=int(x_c+shiftx)
         y_c=int(y_c+shifty)
         cir_pos.append((x_c,y_c))
         color.append(c)
         radi.append(r)

   return cir_pos,color,radi

def process_frame(org_image):
   image=cv2.medianBlur(org_image,3)
   hsvimage=cv2.cvtColor(image,cv2.COLOR_BGR2HSV);# Convert input image to HSV
   
   red_hue_image=colordetection(hsvimage,0)
   circles_red=detectcircle(red_hue_image)            
      
   green_hue_image=colordetection(hsvimage,1)
   circles_green=detectcircle(green_hue_image)


   return hsvimage,circles_red, circles_green



write_file=('walk_video/datanocrop_black.txt')
g = open(write_file, "wt")
header="frameno"+";"+"frametime"+";"+"radious"+";"+"cir_pos"+";"+"color\n"
g.write(header)


# Create a VideoCapture object and read from input file
cap = cv2.VideoCapture('walk_video/output_walk.avi')

# Check if camera opened successfully
if (cap.isOpened()== False): 
	print("Error opening video stream or file")

#The default resolutions are system dependent. We convert the resolutions from float to integer.
frame_width = int(cap.get(3))
frame_height = int(cap.get(4))
frame_rate=int(round(cap.get(cv2.cv.CV_CAP_PROP_FPS)))


# Define the codec and create VideoWriter object.
fourcc = cv2.cv.CV_FOURCC('M','J','P','G')
out = cv2.VideoWriter('walk_video/nocrp_black.avi',fourcc, frame_rate, (frame_width,frame_height))


frame_no=0
# Read until video is completed
while(cap.isOpened()):
   # Capture frame-by-frame
   ret, org_image = cap.read()
   if ret == False:
      break

   start_frame=time.time()
   hsvimage,circles_red,circles_green=process_frame(org_image)
   if circles_red is not None:
      for circles in circles_red[0]:
         [x_c,y_c,r]=circles
         bottom=rectangle_per(hsvimage,x_c,y_c,r,0)
         right=rectangle_per(hsvimage,x_c,y_c,r,1)
         upper=rectangle_per(hsvimage,x_c,y_c,r,2)
         left=rectangle_per(hsvimage,x_c,y_c,r,3)
         #print bottom,right,upper,left
         if bottom > percentile or right > percentile or upper > percentile or left > percentile:
            cv2.circle(org_image, (x_c, y_c), r, (255, 0, 0), 3)
            cv2.circle(org_image, (x_c, y_c), 1, (255, 0, 0), 1)
            cv2.putText(org_image,"red don't go",(int(x_c+10), int(y_c+10)),cv2.FONT_HERSHEY_SIMPLEX,0.5, (0,0,255), 2)

   if circles_green is not None:
      for circles in circles_green[0]:
         [x_c,y_c,r]=circles
         bottom=rectangle_per(hsvimage,x_c,y_c,r,0)
         right=rectangle_per(hsvimage,x_c,y_c,r,1)
         upper=rectangle_per(hsvimage,x_c,y_c,r,2)
         left=rectangle_per(hsvimage,x_c,y_c,r,3)
         #print bottom,right,upper,left
         if bottom > percentile or right > percentile or upper > percentile or left > percentile:
            cv2.circle(org_image, (x_c, y_c), r, (255, 0, 0), 3)
            cv2.circle(org_image, (x_c, y_c), 1, (255, 0, 0), 1)
            cv2.putText(org_image,"green go",(int(x_c+10),int(y_c+10)),cv2.FONT_HERSHEY_SIMPLEX,0.5, (255, 0, 0), 2)  


   cir_pos,color,radi=finaldata(circles_red,circles_green,0,0)
   frame_time=time.time()-start_frame
   out_str=str(frame_no)+";"+str(frame_time)+";\""+str(radi)+"\";\""+str(cir_pos)+"\";\""+str(color)+"\"\n"
   g.write(out_str)
   out.write(org_image)
   frame_no +=1
   
   if cv2.waitKey(25) & 0xFF == ord('q'):# Press Q on keyboard to  exit
      break 

# When everything done, release the video capture object
cap.release()
out.release()
g.close()
 
# Closes all the frames
cv2.destroyAllWindows()
