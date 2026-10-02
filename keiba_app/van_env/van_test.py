import win32com.client; jv = win32com.client.Dispatch("JVLink.JVLink.1"); print("SUCCESS: JRA-VAN IS CONNECTED!" if jv.Initialize("UNKNOWN", 1, 1, 0) == 0 else "ERROR: INITIALIZATION FAILED")  
