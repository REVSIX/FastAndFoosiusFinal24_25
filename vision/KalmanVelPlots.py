'''
This file is used to plot the data from mainKalmanPlot
'''



import json
import matplotlib.pyplot as plt

# Load data from the JSON file
with open("kalman_vel_data.json", "r") as f:
    data = json.load(f)


pastVx = data["pastVx"]
pastVy = data["pastVy"]
kalmanVx = data["kalmanVx"]
kalmanVy = data["kalmanVy"]
times = data["times"]
#pastTimes = data["pastTimes"][1:]
yFinal = data["yFinal"]
motorDesiredData = data["motorDesiredData"]

print("times",len(times))
# print("times",times)
# print()
#print("pastTimes",len(pastTimes))
# print("pastTimes",pastTimes)
# print()
print("pastVx",len(pastVx))
# print()
print("pastVy",len(pastVy))
# print()
print("kalmanVx",len(kalmanVx))
# print()
print("kalmanVy",len(kalmanVy))
# # print()
# print("yFinal",len(yFinal))
# # print()
# print("motorDesiredData",len(motorDesiredData))


yFinalRod0 = [yArr[0] for yArr in yFinal]
yFinalRod1 = [yArr[1] for yArr in yFinal]
yFinalRod2 = [yArr[2] for yArr in yFinal]
yFinalRod3 = [yArr[3] for yArr in yFinal]


motorStepper1 = [mArr[0] for mArr in motorDesiredData]
motorStepper2 = [mArr[1] for mArr in motorDesiredData]
motorStepper3 = [mArr[2] for mArr in motorDesiredData]
motorStepper4 = [mArr[3] for mArr in motorDesiredData]



# print(yFinalRod0)
# print(motorDesiredData)

#print(times)


plt.figure(figsize=(6, 4))
#plt.plot(pastTimes,pastVx, label = "Past Vx")
plt.plot(times,kalmanVx, label = "Kalman Vx")
plt.ylabel("Velocity in X (pixels/s)")
plt.xlabel("Time(s)")
plt.title("X Velocity v. Time")
plt.legend()


plt.figure(figsize=(6, 4))
#plt.plot(pastTimes,pastVy, label = "Past Vy")
plt.plot(times,kalmanVy, label = "Kalman Vy")
plt.ylabel("Velocity in Y (pixels/s)")
plt.xlabel("Time(s)")
plt.title("Y Velocity v. Time")
plt.legend()


fig, axes = plt.subplots(4, 1)
axes[0].plot(times,motorStepper1)
axes[0].set_title("Stepper 1 v. Time")

axes[1].plot(times,motorStepper2)
axes[1].set_title("Stepper 2 v. Time")


axes[2].plot(times,motorStepper3)
axes[2].set_title("Stepper 3 v. Time")

axes[3].plot(times,motorStepper4)
axes[3].set_title("Stepper 4 v. Time")
plt.tight_layout()

fig, axes = plt.subplots(4, 1)
axes[0].plot(times,yFinalRod0)
axes[0].set_title("Rod 0 Y Final v. Time")

axes[1].plot(times,yFinalRod1)
axes[1].set_title("Rod 1 Y Final v. Time")


axes[2].plot(times,yFinalRod2)
axes[2].set_title("Rod 2 Y Final v. Time")

axes[3].plot(times,yFinalRod3)
axes[3].set_title("Rod 3 Y Final v. Time")
plt.tight_layout()



### 

minVal=  min(yFinalRod0)
maxVal = max(yFinalRod0)
normalizedyFinalRod0 = [(x-minVal)/(maxVal-minVal) for x in yFinalRod0]
fig, axes = plt.subplots(4, 1)

axes[0].plot(times,kalmanVx,label = "Kalman Vx")
axes[0].plot(times,kalmanVy,label = "Kalman Vy")
axes[0].legend()
axes[1].plot(times,yFinalRod0)
axes[1].set_title("Y Final Rod 0 v. Time")
axes[2].plot(times,normalizedyFinalRod0)
axes[2].set_title("Normalized Y Final Rod 0 v. Time")

#axes[0].plot(times,motorStepper1)
axes[3].plot(times,motorStepper1,label="mDes Step1")
axes[3].plot(times,normalizedyFinalRod0, label = "norm yF R0")
axes[3].legend(loc = "lower left")


# axes[1].plot(times,yFinalRod1)
# axes[1].plot(times,motorStepper2)



# axes[2].plot(times,yFinalRod2)
# axes[2].plot(times,motorStepper3)


# axes[3].plot(times,yFinalRod3)
# axes[3].plot(times,motorStepper4)

#print(yFinalRod0)
#print(motorStepper1)
#print(kalmanVx)
print(kalmanVy)

plt.tight_layout()
plt.show()





