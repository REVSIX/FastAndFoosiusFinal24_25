'''
This file is used to plot the data from KalmanMyLatop.py and the KalmanTable Data File
'''



import json
import matplotlib.pyplot as plt

# Load data from the JSON file
with open("kalman_data.json", "r") as f:
    data = json.load(f)

times = data["times"]
xVals = data["xVals"]
xpredictedVals = data["xpredictedVals"]
xcorrectedVals = data["xcorrectedVals"]
yVals = data["yVals"]
ypredictedVals = data["ypredictedVals"]
ycorrectedVals = data["ycorrectedVals"]
xvelcorrectedVals = data["xvelcorrectedVals"]
yvelcorrectedVals = data["yvelcorrectedVals"]

# Plot the data
fig, ax = plt.subplots(3, 1, figsize=(6, 6))
#print(times)
#print(xVals)
ax[0].plot(times, xVals)
ax[0].set_title('Measured X Values v. Time')
ax[0].grid()

ax[1].plot(times, xpredictedVals)
ax[1].set_title('Predicted X Values v. Time')
ax[1].grid()

ax[2].plot(times, xcorrectedVals)
ax[2].set_title('Corrected X Values v. Time')
ax[2].grid()

plt.tight_layout()




fig2, ax2 = plt.subplots(3, 1, figsize=(6, 6))

ax2[0].plot(times, yVals)
ax2[0].set_title('Measured Y Values v. Time')
ax2[0].grid()

ax2[1].plot(times, ypredictedVals)
ax2[1].set_title('Predicted Y Values v. Time')
ax2[1].grid()

ax2[2].plot(times, ycorrectedVals)
ax2[2].set_title('Corrected Y Values v. Time')
ax2[2].grid()

plt.tight_layout()


fig3, ax3 = plt.subplots(3, 1, figsize=(6, 6))
ax3[0].plot(xVals,yVals)
ax3[0].set_title('Measured Y v. X')
ax3[0].grid()

ax3[1].plot(xpredictedVals, ypredictedVals)
ax3[1].set_title('Predicted Y v. X')
ax3[1].grid()

ax3[2].plot(xcorrectedVals, ycorrectedVals)
ax3[2].set_title('Predicted Y v. X')
ax3[2].grid()

plt.tight_layout()


plt.figure(figsize=(6, 4))

plt.plot(times[20:],xVals[20:], label = "Measured X Vals")
plt.plot(times[20:],xpredictedVals[20:], label = "Predicted X Vals")
plt.plot(times[20:],xcorrectedVals[20:], label = "Corrected X Vals")
plt.legend()

plt.figure(figsize=(6, 4))

plt.plot(times[20:],yVals[20:], label = "Measured Y Vals")
plt.plot(times[20:],ypredictedVals[20:], label = "Predicted Y Vals")
plt.plot(times[20:],ycorrectedVals[20:], label = "Corrected Y Vals")
plt.legend()

fig4, ax4 = plt.subplots(3, 1, figsize=(6, 6))
ax4[0].plot(times, xvelcorrectedVals)
ax4[0].set_title("Corrected X Vel vs. Time")
ax4[1].plot(times, yvelcorrectedVals)
ax4[1].set_title("Corrected Y Vel vs. Time")
ax4[2].plot(xvelcorrectedVals,yvelcorrectedVals)
ax4[2].set_title("Y v. X Corrected Vels")

plt.tight_layout()
plt.show()