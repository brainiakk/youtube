import time
from voice import VoiceService

vs = VoiceService()
# vs.openvoice_v2()
# print("Openvoice starting...")
# start_time = time.time()
# vs.openvoice("Accessing alarm and interface settings, in this window you can set up your customized greeting and alarm preferences. Hello Sir, What can I do for you today?")
# end_time = time.time()
# print(f"⏰ Openvoice Execution Time: {end_time - start_time}")
# print("Openvoice ended")
print("PiperTTS starting...")
start_time1 = time.time()
vs.pipertts("Accessing alarm and interface settings, in this window you can set up your customized greeting and alarm preferences. Hello Sir, What can I do for you today?")
end_time1 = time.time()
print(f"⏰ PiperTTS Execution Time: {end_time1 - start_time1}")

# print("PiperTTS CLI starting...")
# start_time = time.time()
# vs.pipertts_cli("Accessing alarm and interface settings, in this window you can set up your customized greeting and alarm preferences. Hello Sir, What can I do for you today?")
# end_time = time.time()
# print(f"⏰ PiperTTS CLI Execution Time: {end_time - start_time}")

# print("Melotts starting...")
# start_time2 = time.time()
# vs.melotts("Accessing alarm and interface settings, in this window you can set up your customized greeting and alarm preferences. Hello Sir, What can I do for you today?")
# end_time2 = time.time()
# print(f"⏰ Melotts Execution Time: {end_time2 - start_time2}")