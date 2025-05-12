# if abs(x3 - x_rod) <= 50:
#     # Trap logic based on direction (Rod 0)
#     if rod_index == 0 and kick_type == 4 and not trap_state[rod_index]:
#         # Check the ball's direction to decide trap behavior
#         if vx > 0:
#             # Ball is coming from the left
#             servoDesired[rod_index] = 4  # initiate trap from the left
#         elif vx < 0:
#             # Ball is coming from the right
#             servoDesired[rod_index] = 5  # initiate trap from the right (you could define another action)
        
#         trap_state[rod_index] = True
#         trap_start_time[rod_index] = time.time()

#     elif trap_state[rod_index]:
#         if abs(vx) < 0.5 and abs(vy) < 0.5:
#             if time.time() - trap_start_time[rod_index] >= trap_duration:
#                 # After trapping, perform a strong shot (e.g., from either side)
#                 if vx > 0:
#                     servoDesired[rod_index] = 2  # fire strong shot, direction depends on vx
#                 else:
#                     servoDesired[rod_index] = 2  # fire strong shot from the opposite direction
#                 trap_state[rod_index] = False
#         else:
#             trap_state[rod_index] = False  # Reset trap if ball moves
#     else:
#         # Normal kick logic (non-trap)
#         if kick_type != 4:  # Don't overwrite trap
#             servoDesired[rod_index] = float(kick_type)
